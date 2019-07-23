from ruamel.yaml import Node
from .types import ContextType


__all__ = ['MacroError']


class MacroError(Exception):
    def __init__(self, message: str, node: Node, context: ContextType = None) -> None:
        self.message = message
        self.node = node
        self.context = context
