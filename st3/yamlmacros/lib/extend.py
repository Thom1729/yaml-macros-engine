from collections import OrderedDict
from functools import reduce

from yamlmacros import get_yaml_instance
from ..src.util import deprecated, flatten


__all__ = ['merge', 'prepend', 'all', 'apply', 'extend']


class Operation():
    def __init__(self, extension):
        self.extension = extension


class Merge(Operation):
    def apply(self, base):
        ret = base.copy()

        for key, value in self.extension.items():
            if key in base and isinstance(value, Operation):
                ret[key] = value.apply(base[key])
            else:
                ret[key] = value

        return ret


class Prepend(Operation):
    def apply(self, base):
        return self.extension + base


class All(Operation):
    def apply(self, base):
        return reduce(
            lambda ret, ext: ext.apply(ret),
            flatten(*self.extension),
            base,
        )


def merge(*items):
    return Merge(OrderedDict(items))


def prepend(*items):
    return Prepend(list(items))


def all(*items):
    return All(list(items))


def apply(base, *extensions):
    return all(*extensions).apply(base)
