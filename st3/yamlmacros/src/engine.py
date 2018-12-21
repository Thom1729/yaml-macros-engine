import io
from inspect import signature, Parameter
import importlib
from functools import partial, lru_cache

from .yaml_provider import get_yaml_instance, get_constructor
from .util import apply, merge
from .load_macros import temporary_package


__all__ = ['MacroError', 'process_macros']


class MacroError(Exception):
    def __init__(self, message, node, context=None):
        self.message = message
        self.node = node
        self.context = context


def load_macros(macro_path, macros_root):
    from uuid import uuid4
    package_name = 'yaml_macros_engine_{!s}'.format(uuid4())

    with temporary_package(package_name, macros_root):
        module = importlib.import_module(macro_path, package_name)

        if hasattr(module, '__all__'):
            return {
                name.rstrip('_'): get_macro(func)
                for name, func in module.__dict__.items()
                if name in module.__all__
            }
        else:
            return {
                name.rstrip('_'): get_macro(func)
                for name, func in module.__dict__.items()
                if callable(func) and not name.startswith('_')
            }


def get_macro(function):
    parameters = signature(function).parameters
    if getattr(function, 'raw', False):
        def macro(node, loader):
            kwargs = {
                'loader': loader,
                'eval': partial(loader.construct_object, deep=True),
                'arguments': loader.context,
            }

            return function(node, **{
                key: value
                for key, value in kwargs.items()
                if key in parameters
            })
        return macro
    else:
        def macro(node, loader):
            args = loader.construct_value_ignore_tag(node)

            if isinstance(args, dict) and any(
                param.kind == Parameter.VAR_POSITIONAL
                for param in parameters.values()
            ):
                # Before Python 3.6, **kwargs will not preserve order.
                args = list(args.items())

            return apply(function, args)

        return macro


def macros_constructor(macros, loader, suffix, node):
    try:
        macro = macros[suffix]
    except KeyError as e:
        raise MacroError('Unknown macro "%s".' % suffix, node, context=loader.context) from e

    try:
        return macro(node, loader)
    except Exception as e:
        raise MacroError('Error in macro execution.', node, context=loader.context) from e


@lru_cache(maxsize=16)
def get_parse(input):
    yaml = get_yaml_instance()
    stream = io.StringIO(input)

    yaml.get_constructor_parser(stream)
    tree = yaml.composer.get_single_node()
    macros = [
        (handle, tag.split(':')[2])
        for handle, tag in yaml.parser.tag_handles.items()
        if tag.startswith('tag:yaml-macros:')
    ]

    return (tree, macros)


def process_macros(input, arguments={}, *, macros_root=None):
    tree, macros = get_parse(input)

    constructor = get_constructor()

    for handle, macro_path in macros:
        macros = merge(*(
            load_macros(path, macros_root)
            for path in macro_path.split(',')
        ))

        constructor.add_multi_constructor(
            handle,
            partial(macros_constructor, macros)
        )

    with constructor.set_context(**arguments):
        return constructor.construct_document(tree)


def build_yaml_macros(input, output=None, context=None):
    syntax = process_macros(input, context)
    yaml = get_yaml_instance()

    yaml.dump(syntax, stream=output)
