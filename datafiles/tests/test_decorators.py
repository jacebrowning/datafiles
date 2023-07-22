# pylint: disable=unused-variable

from dataclasses import dataclass, is_dataclass

from datafiles import decorators


def describe_datafile():
    def it_turns_normal_class_into_dataclass(expect):
        class Normal:
            pass

        cls = decorators.datafile("<pattern>")(Normal)

        expect(is_dataclass(cls)).is_(True)

    def it_can_reuse_existing_dataclass(expect):
        @dataclass
        class Existing:
            pass

        cls = decorators.datafile("")(Existing)

        expect(id(cls)) == id(Existing)

    def it_maps_to_dataclass_without_parentheses(expect):
        class Sample:
            pass

        cls = decorators.datafile(Sample)

        expect(is_dataclass(cls)).is_(True)

    def it_forwards_arguments_dataclass_decorator(expect):
        class Sample:
            pass

        cls = decorators.datafile(order=True)(Sample)

        expect(is_dataclass(cls)).is_(True)


def describe_sync():
    def it_turns_dataclass_instance_into_model_instance(expect):
        @dataclass
        class Existing:
            count: int = 42

        instance = Existing()

        decorators.sync(instance, "tmp/example.yml", defaults=True)

        expect(instance.datafile.data) == {"count": 42}  # type: ignore
