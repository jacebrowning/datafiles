# pylint: disable=unused-variable

from dataclasses import dataclass
from typing import Dict, List, Optional

import pytest

from datafiles import converters


@dataclass
class MyDataclass:
    foobar: int


class MyNonDataclass:
    pass


IntegerList = converters.List.subclass(converters.Integer)
StringList = converters.List.subclass(converters.String)
MyDataclassConverter = converters.map_type(MyDataclass)
MyDataclassConverterList = converters.map_type(List[MyDataclass])


def describe_map_type():
    def it_handles_list_annotations(expect):
        converter = converters.map_type(List[str])
        expect(converter.__name__) == 'StringList'
        expect(converter.CONVERTER) == converters.String

    def it_handles_list_annotations_of_dataclasses(expect):
        converter = converters.map_type(List[MyDataclass])
        expect(converter.__name__) == 'MyDataclassConverterList'
        expect(converter.CONVERTER.__name__) == 'MyDataclassConverter'

    def it_requires_list_annotations_to_have_a_type(expect):
        with expect.raises(TypeError):
            converters.map_type(List)

    def it_handles_dataclasses(expect):
        converter = converters.map_type(MyDataclass)
        expect(converter.__name__) == 'MyDataclassConverter'
        expect(converter.CONVERTERS) == {'foobar': converters.Integer}

    def it_handles_optionals(expect):
        converter = converters.map_type(Optional[str])
        expect(converter.__name__) == 'OptionalString'
        expect(converter.TYPE) == str
        expect(converter.DEFAULT) == None

    def it_rejects_unknown_types(expect):
        with expect.raises(TypeError):
            converters.map_type(MyNonDataclass)

    def it_rejects_unhandled_type_annotations(expect):
        with expect.raises(TypeError):
            converters.map_type(Dict[str, int])


def describe_converter():
    def describe_to_python_value():
        @pytest.mark.parametrize(
            'converter, data, value',
            [
                # Builtins
                (converters.Boolean, '1', True),
                (converters.Boolean, '0', False),
                (converters.Boolean, 'enabled', True),
                (converters.Boolean, 'disabled', False),
                (converters.Boolean, 'T', True),
                (converters.Boolean, 'F', False),
                (converters.Boolean, 'true', True),
                (converters.Boolean, 'false', False),
                (converters.Boolean, 'Y', True),
                (converters.Boolean, 'N', False),
                (converters.Boolean, 'yes', True),
                (converters.Boolean, 'no', False),
                (converters.Boolean, 'on', True),
                (converters.Boolean, 'off', False),
                (converters.Boolean, 0, False),
                (converters.Boolean, 1, True),
                (converters.Float, 4, 4.0),
                (converters.Integer, 4.2, 4),
                (converters.String, 4.2, '4.2'),
                (converters.String, 42, '42'),
                (converters.String, True, 'True'),
                (converters.String, False, 'False'),
                # Containers
                (IntegerList, [], []),
                (IntegerList, '1, 2.3', [1, 2]),
                (IntegerList, '42', [42]),
                (IntegerList, 42, [42]),
                (IntegerList, None, []),
                (IntegerList, [42], [42]),
                (IntegerList, [None], []),
                (IntegerList, [None, None], []),
                (MyDataclassConverter, None, MyDataclass(foobar=0)),
                (MyDataclassConverterList, None, []),
                (MyDataclassConverterList, 42, [MyDataclass(foobar=0)]),
            ],
        )
        def when_nominal(expect, converter, data, value):
            expect(converter.to_python_value(data, value=None)) == value

        def when_invalid(expect):
            message = "invalid literal for int() with base 10: 'a'"
            with expect.raises(ValueError, message):
                converters.Integer.to_python_value('a')

        def when_list_of_dataclasses(logbreak, expect):
            converter = converters.map_type(List[MyDataclass])

            logbreak()
            data = [{'foobar': 1}, {'foobar': 2}, {'foobar': 3}]
            value = [MyDataclass(1), MyDataclass(2), MyDataclass(3)]

            expect(converter.to_python_value(data, value=None)) == value

        def with_existing_list(expect):
            value = [1, 2]

            value2 = IntegerList.to_python_value("3, 4", value=value)

            expect(value2) == [3, 4]
            expect(id(value2)) == id(value)

        def with_existing_dataclass(expect):
            value = MyDataclass(foobar=1)

            value2 = MyDataclassConverter.to_python_value(
                {'foobar': 2}, value=value
            )

            expect(value2) == MyDataclass(foobar=2)
            expect(id(value2)) == id(value)

    def describe_to_preserialization_data():
        @pytest.mark.parametrize(
            'converter, value, data',
            [
                # Builtins
                (converters.Boolean, None, False),
                (converters.Float, None, 0.0),
                (converters.Integer, None, 0),
                (converters.String, None, ''),
                # Containers
                (StringList, 'ab', ['ab']),
                (StringList, ('b', 1, 'A'), ['b', '1', 'A']),
                (StringList, {'b', 1, 'A'}, ['1', 'A', 'b']),
                (StringList, 42, ['42']),
                (StringList, [123, True, False], ['123', 'True', 'False']),
                (StringList, [], []),
                (StringList, None, []),
                (MyDataclassConverter, None, {'foobar': 0}),
                (MyDataclassConverterList, None, []),
                (MyDataclassConverterList, 42, [{'foobar': 0}]),
            ],
        )
        def when_nominal(expect, converter, value, data):
            expect(converter.to_preserialization_data(value)) == data

        def when_invalid(expect):
            message = "invalid literal for int() with base 10: 'a'"
            with expect.raises(ValueError, message):
                converters.Integer.to_preserialization_data('a')

        def when_list_of_dataclasses(logbreak, expect):
            converter = converters.map_type(List[MyDataclass])

            logbreak()
            value = [MyDataclass(1), MyDataclass(2), MyDataclass(3)]
            data = [{'foobar': 1}, {'foobar': 2}, {'foobar': 3}]

            expect(converter.to_preserialization_data(value)) == data
            expect(converter.to_preserialization_data(data)) == data
