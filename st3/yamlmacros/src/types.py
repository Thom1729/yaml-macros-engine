from typing import Callable
from collections.abc import Mapping

from ruamel.yaml import Node
from .custom_constructor import CustomConstructor

ContextType = Mapping[str, object]
MacroType = Callable[[CustomConstructor, Node], object]


__all__ = ['ContextType', 'MacroType']
