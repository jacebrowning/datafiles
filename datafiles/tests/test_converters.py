# pylint: disable=unused-variable

from dataclasses import dataclass
from typing import ByteString, Dict, List, Optional

import pytest
from ruamel.yaml.scalarstring import LiteralScalarString

from datafiles import converters


@dataclass
class MyDataclass:
    foobar: int
    flag: bool = False


class MyNonDataclass:
    pass


class MyNonDataclass2:
    pass


IntegerList = converters.List.subclass(converters.Integer)
StringList = converters.List.subclass(converters.String)
MyDict = converters.Dictionary.subclass(converters.String, converters.Integer)
MyDataclassConverter = converters.map_type(MyDataclass)
MyDataclassConverterList = converters.map_type(List[MyDataclass])


def describe_map_type():
    def it_handles_extended_types(expect):
        converter = converters.map_type(converters.Number)
        expect(converter.__name__) == 'Number'

    def it_handles_list_annotations(expect):
        converter = converters.map_type(List[str])
        expect(converter.__name__) == 'StringList'
        expect(converter.CONVERTER) == converters.String

    def it_handles_list_annotations_of_dataclasses(expect):
        converter = converters.map_type(List[MyDataclass])
        expect(converter.__name__) == 'MyDataclassConverterList'
        expect(converter.CONVERTER.__name__) == 'MyDataclassConverter'

    def it_requires_list_annotations_to_have_a_type(expect):
        with expect.raises(TypeError, "Type is required with 'List' annotation"):
            converters.map_type(List)

    def it_handles_dict_annotations(expect):
        converter = converters.map_type(Dict[str, int])
        expect(converter.__name__) == 'StringIntegerDict'

    def it_handles_dataclasses(expect):
        converter = converters.map_type(MyDataclass)
        expect(converter.__name__) == 'MyDataclassConverter'
        expect(converter.CONVERTERS) == {
            'foobar': converters.Integer,
            'flag': converters.Boolean,
        }

    def it_handles_optionals(expect):
        converter = converters.map_type(Optional[str])
        expect(converter.__name__) == 'OptionalString'
        expect(converter.TYPE) == str
        expect(converter.DEFAULT) == None

    def it_handles_string_type_annotations(expect):
        converter = converters.map_type('float')
        expect(converter.TYPE) == float

    def it_rejects_unknown_types(expect):
        with expect.raises(
            TypeError,
            "Could not map type: <class 'datafiles.tests.test_converters.MyNonDataclass'>",
        ):
            converters.map_type(MyNonDataclass)

    def it_rejects_non_types(expect):
        with expect.raises(TypeError, "Annotation is not a type: 'foobar'"):
            converters.map_type("foobar")

    def it_rejects_unhandled_type_annotations(expect):
        with expect.raises(
            TypeError,
            "Unsupported container type: <class 'collections.abc.ByteString'>",
        ):
            converters.map_type(ByteString)


def describe_converter():
    def describe_to_python_value():
        @pytest.mark.parametrize(
            'converter, data, value',
            [
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
            ],
        )
        def when_immutable(expect, converter, data, value):
            expect(converter.to_python_value(data)) == value

        @pytest.mark.parametrize(
            'converter, data, value',
            [
                (IntegerList, [], []),
                (IntegerList, '1, 2.3', [1, 2]),
                (IntegerList, '42', [42]),
                (IntegerList, 42, [42]),
                (IntegerList, None, []),
                (IntegerList, [42], [42]),
                (IntegerList, [None], []),
                (IntegerList, [None, None], []),
                (MyDict, None, {}),
                (MyDict, {}, {}),
                (MyDict, {'a': 1}, {'a': 1}),
                (MyDataclassConverter, None, MyDataclass(foobar=0)),
                (MyDataclassConverterList, None, []),
                (MyDataclassConverterList, 42, [MyDataclass(foobar=0)]),
            ],
        )
        def when_mutable(expect, converter, data, value):
            expect(converter.to_python_value(data, target_object=None)) == value

        def when_number(expect):
            convert = converters.Number.to_python_value
            expect(convert(1.23)).isinstance(float)
            expect(convert(42)).isinstance(int)

        def when_text(expect):
            convert = converters.Text.to_python_value
            expect(convert("")) == ""
            expect(convert("Hello, world!")) == "Hello, world!"
            expect(convert("Line 1\nLine 2\n")) == "Line 1\nLine 2\n"

        def when_invalid(expect):
            message = "invalid literal for int() with base 10: 'a'"
            with expect.raises(ValueError, message):
                converters.Integer.to_python_value('a')

        def when_list_of_dataclasses(expect):
            converter = converters.map_type(List[MyDataclass])

            data = [{'foobar': 1}, {'foobar': 2}, {'foobar': 3}]
            value = [MyDataclass(1), MyDataclass(2), MyDataclass(3)]

            expect(converter.to_python_value(data, target_object=None)) == value

        def with_existing_list(expect):
            orginal = [1, 2]

            value = IntegerList.to_python_value("3, 4", target_object=orginal)

            expect(value) == [3, 4]
            expect(id(value)) == id(orginal)

        def when_existing_dict(expect):
            orginal = {'a': 1}

            value = MyDict.to_python_value({'b': 2}, target_object=orginal)

            expect(value) == {'b': 2}
            expect(id(value)) == id(orginal)

        def with_existing_dataclass(expect):
            orginal = MyDataclass(foobar=1)

            value = MyDataclassConverter.to_python_value(
                {'foobar': 2}, target_object=orginal
            )

            expect(value) == MyDataclass(foobar=2)
            expect(id(value)) == id(orginal)

    def describe_to_preserialization_data():
        @pytest.mark.parametrize(
            'converter, value, data',
            [
                # Builtins
                (converters.Boolean, None, False),
                (converters.Float, None, 0.0),
                (converters.Integer, None, 0),
                (converters.String, None, ''),
                # Lists
                (StringList, 'ab', ['ab']),
                (StringList, ('b', 1, 'A'), ['b', '1', 'A']),
                (StringList, {'b', 1, 'A'}, ['1', 'A', 'b']),
                (StringList, 42, ['42']),
                (StringList, [123, True, False], ['123', 'True', 'False']),
                (StringList, [], [None]),
                (StringList, None, [None]),
                # Dataclasses
                (MyDataclassConverter, None, {'foobar': 0, 'flag': False}),
                (MyDataclassConverter, {'foobar': 42}, {'foobar': 42, 'flag': False}),
                (MyDataclassConverterList, None, [None]),
                (MyDataclassConverterList, 42, [{'foobar': 0, 'flag': False}]),
            ],
        )
        def when_nominal(expect, converter, value, data):
            expect(converter.to_preserialization_data(value)) == data

        def when_number(expect):
            convert = converters.Number.to_preserialization_data
            expect(convert(1.23)).isinstance(float)
            expect(convert(42)).isinstance(int)

        def when_text(expect):
            convert = converters.Text.to_preserialization_data
            expect(convert("")) == ""
            expect(convert("Hello, world!")) == "Hello, world!"
            expect(convert("Line 1\nLine 2")) == "Line 1\nLine 2\n"
            expect(convert("Line 1\nLine 2")).isinstance(LiteralScalarString)

        def when_invalid(expect):
            message = "invalid literal for int() with base 10: 'a'"
            with expect.raises(ValueError, message):
                converters.Integer.to_preserialization_data('a')

        def when_list_of_dataclasses(expect):
            converter = converters.map_type(List[MyDataclass])

            value = [MyDataclass(1), MyDataclass(2), MyDataclass(3)]
            data = [
                {'foobar': 1, 'flag': False},
                {'foobar': 2, 'flag': False},
                {'foobar': 3, 'flag': False},
            ]

            expect(converter.to_preserialization_data(value)) == data
            expect(converter.to_preserialization_data(data)) == data

        def when_list_with_default(expect):
            data = IntegerList.to_preserialization_data([1], default_to_skip=[1])
            expect(data) == [None]

            data = IntegerList.to_preserialization_data([2], default_to_skip=[1])
            expect(data) == [2]

        def when_dict_with_default(expect):
            data = MyDict.to_preserialization_data({'a': 1}, default_to_skip={'a': 1})
            expect(data) == {}

            data = MyDict.to_preserialization_data({'b': 2}, default_to_skip={'a': 1})
            expect(data) == {'b': 2}

        def when_dataclass_with_default(expect):
            data = MyDataclassConverter.to_preserialization_data(
                MyDataclass(1), default_to_skip=MyDataclass(1)
            )
            expect(data) == {}

            data = MyDataclassConverter.to_preserialization_data(
                MyDataclass(2), default_to_skip=MyDataclass(1)
            )
            expect(data) == {'foobar': 2}

            data = MyDataclassConverter.to_preserialization_data(
                MyDataclass(1, flag=True), default_to_skip=MyDataclass(1)
            )
            expect(data) == {'flag': True}


def describe_register():
    def with_new_type(expect):
        converters.register(MyNonDataclass2, converters.String)
        converter = converters.map_type(MyNonDataclass2)
        expect(converter) == converters.String
