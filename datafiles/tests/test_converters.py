# pylint: disable=unused-variable

from dataclasses import dataclass
from typing import Dict, List, Optional

import pytest

from datafiles import converters
from datafiles.models import create_model


@dataclass
class MyCustomDataclass:
    foobar: int


class MyCustomNonDataclass:
    pass


IntegerList = converters.List.of_converters(converters.Integer)  # type: ignore
StringList = converters.List.of_converters(converters.String)  # type: ignore


def describe_map_type():
    def it_handles_list_annotations(expect):
        converter = converters.map_type(List[str])
        expect(converter.__name__) == 'StringList'
        expect(converter.ELEMENT_CONVERTER) == converters.String

    def it_handles_list_annotations_of_dataclasses(expect):
        converter = converters.map_type(
            List[MyCustomDataclass], create_model=create_model
        )
        expect(converter.__name__) == 'MyCustomDataclassList'
        expect(converter.ELEMENT_CONVERTER) == MyCustomDataclass

    def it_requires_list_annotations_to_have_a_type(expect):
        with expect.raises(TypeError):
            converters.map_type(List)

    def it_handles_optionals(expect):
        converter = converters.map_type(Optional[str])
        expect(converter.__name__) == 'OptionalString'
        expect(converter.TYPE) == str
        expect(converter.DEFAULT) == None

    def it_rejects_unknown_types(expect):
        with expect.raises(TypeError):
            converters.map_type(MyCustomNonDataclass)

    def it_rejects_unhandled_type_annotations(expect):
        with expect.raises(TypeError):
            converters.map_type(Dict[str, int])


def describe_converter():
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
            (IntegerList, [], []),
            (IntegerList, '1, 2.3', [1, 2]),
            (IntegerList, '42', [42]),
            (IntegerList, 42, [42]),
            (IntegerList, None, []),
            (IntegerList, [42], [42]),
        ],
    )
    def to_python_value(expect, converter, data, value):
        expect(converter.to_python_value(data)) == value

    def to_python_value_when_invalid(expect):
        message = "invalid literal for int() with base 10: 'a'"
        with expect.raises(ValueError, message):
            converters.Integer.to_python_value('a')

    def to_python_value_when_list_of_dataclasses(expect):
        converter = converters.map_type(
            List[MyCustomDataclass], create_model=create_model
        )

        data = [{'foobar': 1}, {'foobar': 2}, {'foobar': 3}]
        value = [
            MyCustomDataclass(1),
            MyCustomDataclass(2),
            MyCustomDataclass(3),
        ]

        expect(converter.to_python_value(data)) == value

    @pytest.mark.parametrize(
        'converter, value, data',
        [
            (converters.Boolean, None, False),
            (converters.Float, None, 0.0),
            (converters.Integer, None, 0),
            (converters.String, None, ''),
            (StringList, 'ab', ['ab']),
            (StringList, ('b', 1, 'A'), ['b', '1', 'A']),
            (StringList, {'b', 1, 'A'}, ['1', 'A', 'b']),
            (StringList, 42, ['42']),
            (StringList, [123, True, False], ['123', 'True', 'False']),
            (StringList, [], []),
            (StringList, None, []),
        ],
    )
    def to_preserialization_data(expect, converter, value, data):
        expect(converter.to_preserialization_data(value)) == data

    def to_preserialization_data_when_invalid(expect):
        message = "invalid literal for int() with base 10: 'a'"
        with expect.raises(ValueError, message):
            converters.Integer.to_preserialization_data('a')

    def to_preserialization_data_when_list_of_dataclasses(expect):
        converter = converters.map_type(
            List[MyCustomDataclass], create_model=create_model
        )

        value = [
            MyCustomDataclass(1),
            MyCustomDataclass(2),
            MyCustomDataclass(3),
        ]
        data = [{'foobar': 1}, {'foobar': 2}, {'foobar': 3}]

        expect(converter.to_preserialization_data(value)) == data
        expect(converter.to_preserialization_data(data)) == data
