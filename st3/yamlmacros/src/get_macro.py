from inspect import signature, isgenerator
from ruamel.yaml import Node

from .macro_options import get_macro_options
from .util import apply, run_coroutine


def get_macro(function):
    if getattr(function, 'raw', False):
        # Legacy raw macro
        def wrapped(loader, node):
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
    function,
    *,
    raw=False,
    apply_args=True
):
    def macro(loader, node):
        if raw:
            args = loader.construct_raw(node)
        else:
            args = loader.construct_object_ignore_tag(node)

        if apply_args:
            result = apply(function, args)
        else:
            result = function(args)

        def callback(value):
            if value is None:
                return loader
            elif value is node:
                return loader.construct_object_ignore_tag(value)
            elif isinstance(value, Node):
                return loader.construct_object(value)
            elif isinstance(value, dict):
                return loader.set_context(**value)
            else:
                raise TypeError('Yielded {!r}.'.format(value))

        if isgenerator(result):
            return run_coroutine(result, callback)
        else:
            return result

    return macro
