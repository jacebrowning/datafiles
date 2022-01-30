# pylint: disable=unused-variable,unused-argument

from typing import Generic, List, TypeVar

from datafiles import converters

T = TypeVar("T")


class Fibonacci(Generic[T], converters.Converter):
    def __init__(self, first: T, second: T):
        self.first = first
        self.second = second

    def next(self) -> T:
        self.first, self.second = self.second, self.first + self.second  # type: ignore
        return self.second

    @classmethod
    def to_python_value(cls, deserialized_data, *, target_object=None):
        return cls(*deserialized_data)

    @classmethod
    def to_preserialization_data(cls, python_value, *, default_to_skip=None):
        return [python_value.first, python_value.second]


def describe_generic_type():
    def it_handles_generic_int(expect):
        converter = converters.map_type(Fibonacci[int])
        expect(converter.__name__) == "GenericIntegerFibonacci"

    def it_handles_generic_str(expect):
        converter = converters.map_type(Fibonacci[str])
        expect(converter.__name__) == "GenericStringFibonacci"

    def it_handles_generic_list_float(expect):
        converter = converters.map_type(Fibonacci[List[float]])
        expect(converter.__name__) == "GenericFloatListFibonacci"


def describe_converter():
    def describe_to_python_value():
        def when_generic(expect):
            convert = Fibonacci.as_generic([converters.Integer]).to_python_value
            fib = convert([1, 2])
            expect(fib).isinstance(Fibonacci)
            expect(fib.next()) == 3
            expect(fib.next()).isinstance(int)
            fib = convert("ab")
            expect(fib.next()) == "ab"
            expect(fib.next()) == "bab"
            expect(fib.next()) == "abbab"

    def describe_to_preserialization_data():
        def when_generic(expect):
            convert = Fibonacci.as_generic(
                [converters.Integer]
            ).to_preserialization_data
            expect(convert(Fibonacci[int](1, 2))) == [1, 2]
