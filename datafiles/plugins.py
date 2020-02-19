# pylint: disable=no-name-in-module,no-self-use,unused-argument

from typing import Callable, Optional

from mypy.nodes import MDEF, SymbolTableNode, Var
from mypy.plugin import ClassDefContext, Plugin
from mypy.plugins.dataclasses import DataclassTransformer
from mypy.types import AnyType, TypeOfAny


class DatafilesPlugin(Plugin):
    def get_class_decorator_hook(
        self, fullname: str
    ) -> Optional[Callable[[ClassDefContext], None]]:
        if fullname.endswith('.datafile'):
            return datafile_class_maker_callback
        return None


def datafile_class_maker_callback(ctx: ClassDefContext) -> None:
    # Inherit all type definitions from dataclasses
    DataclassTransformer(ctx).transform()

    # Define 'objects' as a class propery
    var = Var('objects', AnyType(TypeOfAny.unannotated))
    var.info = ctx.cls.info
    var.is_property = True
    ctx.cls.info.names[var.name] = SymbolTableNode(MDEF, var)

    # Define 'datafile' as an instance property
    var = Var('datafile', AnyType(TypeOfAny.unannotated))
    var.info = ctx.cls.info
    var.is_property = True
    ctx.cls.info.names[var.name] = SymbolTableNode(MDEF, var)


def mypy(version: str):
    return DatafilesPlugin
