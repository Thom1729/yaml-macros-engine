from ruamel.yaml import Node, ScalarNode, SequenceNode, MappingNode
from ruamel.yaml.constructor import RoundTripConstructor

from .macro_provider import MacroProvider
from .macro_error import MacroError

from contextlib import contextmanager
from .util import fix_keywords

try:
    from typing import Any, Callable, Generator, List
    from .types import ContextType, MacroType
    MultiConstructorType = 'Callable[[CustomConstructor, str, Node], object]'
except ImportError:
    pass


__all__ = ['CustomConstructor']


def macro_constructor(loader: 'CustomConstructor', suffix: str, node: 'Node'):
    def error(message: str) -> MacroError:
        return MacroError(message, node, context=loader.context)

    try:
        macro = loader.macro_provider.get_macro(suffix)
    except Exception as ex:
        raise error('Unknown macro {!r}.'.format(suffix)) from ex

    try:
        return macro(loader, node)
    except Exception as ex:
        raise error('Error in macro execution.') from ex


class CustomConstructor(RoundTripConstructor):
    _contexts = None  # type: List[ContextType]

    def __init__(self, loader, *, macros_root = None, context = {}) -> None:
        super().__init__(loader=loader)

        self._contexts = [context]

        self.macro_provider = MacroProvider(macros_root)

        self.yaml_multi_constructors = {
            'tag:yaml-macros:': macro_constructor
        }

    @property
    def context(self) -> 'ContextType':
        return self._contexts[-1]

    @contextmanager
    def set_context(self, **kwargs: object) -> 'Generator':
        m = dict(self.context.items())
        m.update(**kwargs)
        self._contexts.append(m)
        yield
        self._contexts.pop()

    def construct_object_ignore_tag(self, node: Node) -> object:
        if isinstance(node, ScalarNode):
            return self.construct_scalar(node)
        elif isinstance(node, SequenceNode):
            return list(self.construct_yaml_seq(node))[0]
        elif isinstance(node, MappingNode):
            return list(self.construct_yaml_map(node))[0]
        else:
            raise TypeError("{!r}".format(node))

    def construct_raw(self, node: Node) -> object:
        if isinstance(node, ScalarNode):
            return node
        elif isinstance(node, SequenceNode):
            return node.value
        elif isinstance(node, MappingNode):
            return fix_keywords({
                self.construct_object(k, deep=True): v
                for k, v in node.value
            })
        else:
            raise TypeError("{!r}".format(node))
