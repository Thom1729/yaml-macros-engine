from inspect import signature, isgenerator
from collections.abc import Mapping
from ruamel.yaml import Node

from .macro_options import get_macro_options
from .util import apply, run_coroutine

from .compat.typing import Callable
from .custom_constructor import CustomConstructor
from .types import MacroType


def get_macro(function: Callable) -> MacroType:
    if getattr(function, 'raw', False):
        # Legacy raw macro
        def wrapped(loader: 'CustomConstructor', node: Node) -> object:
            kwargs = {
                'loader': loader,
                'eval': loader.construct_object,
                'arguments': loader.context,
            }

            return function(node, **{
                key: value
                for key, value in kwargs.items()
                if key in signature(function).parameters
            })

        return wrapped

    return get_macro_x(function, **get_macro_options(function))


def get_macro_x(
    function: Callable,
    *,
    raw: bool = False,
    apply_args: bool = True
) -> MacroType:
    def macro(loader: 'CustomConstructor', node: Node) -> object:
        if raw:
            args = loader.construct_raw(node)
        else:
            args = loader.construct_object_ignore_tag(node)

        if apply_args:
            result = apply(function, args)
        else:
            result = function(args)

        def callback(value: object) -> object:
            if value is None:
                return loader
            elif isinstance(value, Node):
                if value is node:
                    return loader.construct_object_ignore_tag(value)
                else:
                    return loader.construct_object(value)
            elif isinstance(value, Mapping):
                return loader.set_context(**value)
            else:
                raise TypeError('Yielded {!r}.'.format(value))

        if isgenerator(result):
            return run_coroutine(result, callback)
        else:
            return result

    return macro
