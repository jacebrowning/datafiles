# pylint: disable=unused-variable

from typing import Dict, List

import pytest

from datafiles import fields


class MyCustomNonDataclass:
    pass


def describe_map_type():
    def it_handles_list_annotations(expect):
        field = fields.map_type(List[str])
        expect(field.__name__) == 'StringList'
        expect(field.__field__) == fields.String

    def it_requires_list_annotations_to_have_a_type(expect):
        with expect.raises(TypeError):
            fields.map_type(List)

    def it_rejects_unknown_types(expect):
        with expect.raises(TypeError):
            fields.map_type(MyCustomNonDataclass)

    def it_rejects_unhandled_type_annotations(expect):
        with expect.raises(TypeError):
            fields.map_type(Dict[str, int])


def describe_field():
    @pytest.mark.parametrize(
        'field, preserialization_data, python_value',
        [
            (fields.Boolean, '0', False),
            (fields.Boolean, '1', True),
            (fields.Boolean, 'disabled', False),
            (fields.Boolean, 'enabled', True),
            (fields.Boolean, 'F', False),
            (fields.Boolean, 'false', False),
            (fields.Boolean, 'N', False),
            (fields.Boolean, 'no', False),
            (fields.Boolean, 'off', False),
            (fields.Boolean, 'on', True),
            (fields.Boolean, 'T', True),
            (fields.Boolean, 'true', True),
            (fields.Boolean, 'Y', True),
            (fields.Boolean, 'yes', True),
            (fields.Boolean, 0, False),
            (fields.Boolean, 1, True),
            (fields.Float, 4, 4.0),
            (fields.Integer, 4.2, 4),
            (fields.String, 4.2, '4.2'),
            (fields.String, 42, '42'),
            (fields.String, False, 'False'),
            (fields.String, True, 'True'),
        ],
    )
    def to_python_value(field, preserialization_data, python_value, expect):
        expect(field.to_python_value(preserialization_data)) == python_value

    @pytest.mark.parametrize(
        'field, python_value, preserialization_data',
        [
            (fields.Boolean, None, False),
            (fields.Float, None, 0.0),
            (fields.Integer, None, 0),
            (fields.String, None, ''),
            (
                fields.List.of_field_type(fields.String),  # type: ignore
                ['abc', 123, True, False],
                ['abc', '123', 'True', 'False'],
            ),
        ],
    )
    def to_preserialization_data(
        field, python_value, preserialization_data, expect
    ):
        expect(
            field.to_preserialization_data(python_value)
        ) == preserialization_data
