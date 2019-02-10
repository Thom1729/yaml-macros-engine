from ruamel.yaml import Node, ScalarNode, SequenceNode, MappingNode
from ruamel.yaml.constructor import RoundTripConstructor

from contextlib import contextmanager
from .util import fix_keywords

try:
    from typing import Any, Callable, Generator, List
    from .types import ContextType, MacroType
    MultiConstructorType = 'Callable[[CustomConstructor, str, Node], object]'
except ImportError:
    pass


__all__ = ['CustomConstructor']


class CustomConstructor(RoundTripConstructor):
    _contexts = None  # type: List[ContextType]

    def __init__(self, *args: 'Any', **kwargs: 'Any') -> None:
        super().__init__(*args, **kwargs)

        self.yaml_constructors = RoundTripConstructor.yaml_constructors.copy()
        self.yaml_multi_constructors = RoundTripConstructor.yaml_multi_constructors.copy()

        self._contexts = [{}]

    def add_constructor(self, tag: 'str', constructor: 'MacroType') -> None:
        self.yaml_constructors[tag] = constructor

    def add_multi_constructor(self, tag: 'str', constructor: 'MultiConstructorType') -> None:
        self.yaml_multi_constructors[tag] = constructor

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
