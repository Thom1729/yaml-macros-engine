from ruamel.yaml import ScalarNode, SequenceNode, MappingNode
from ruamel.yaml.constructor import RoundTripConstructor

from contextlib import contextmanager


__all__ = ['CustomConstructor']


class CustomConstructor(RoundTripConstructor):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.yaml_constructors = RoundTripConstructor.yaml_constructors.copy()
        self.yaml_multi_constructors = RoundTripConstructor.yaml_multi_constructors.copy()

        self.contexts = [{}]

    def add_constructor(self, tag, f):
        self.yaml_constructors[tag] = f

    def add_multi_constructor(self, tag, f):
        self.yaml_multi_constructors[tag] = f

    @property
    def context(self):
        return self.contexts[-1]

    @contextmanager
    def set_context(self, **kwargs):
        new = self.contexts[-1].copy()
        new.update(**kwargs)
        self.contexts.append(new)
        yield
        self.contexts.pop()

    def construct_value_ignore_tag(self, node):
        if isinstance(node, ScalarNode):
            return self.construct_scalar(node)
        elif isinstance(node, SequenceNode):
            return list(self.construct_yaml_seq(node))[0]
        elif isinstance(node, MappingNode):
            return list(self.construct_yaml_map(node))[0]
