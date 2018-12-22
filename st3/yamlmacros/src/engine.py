import io
from inspect import signature, isgenerator
import importlib
from functools import partial, lru_cache
from uuid import uuid4

from ruamel.yaml import Node

from .yaml_provider import get_yaml_instance, get_constructor
from .util import apply, merge, run_coroutine, public_members
from .load_macros import temporary_package


__all__ = ['MacroError', 'process_macros']


class MacroError(Exception):
    def __init__(self, message, node, context=None):
        self.message = message
        self.node = node
        self.context = context


def load_macros(macro_path, macros_root):
    package_name = 'yaml_macros_engine_{!s}'.format(uuid4())

    with temporary_package(package_name, macros_root):
        module = importlib.import_module(macro_path, package_name)

        return {
            name.rstrip('_'): get_macro(func)
            for name, func in public_members(module).items()
        }


def get_macro(function):
    options = getattr(function, '_macro_options', {})

    if getattr(function, 'raw', False):
        # Legacy raw macro
        def wrapped(node):
            loader = yield
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

        return get_macro(wrapped)

    def macro(node, loader):
        if options.get('raw', False):
            args = loader.construct_raw(node)
        else:
            args = loader.construct_object_ignore_tag(node)

        if options.get('apply_args', True):
            return apply(function, args)
        else:
            return function(args)

    return macro


def macros_constructor(macros, loader, suffix, node):
    try:
        macro = macros[suffix]
    except KeyError as e:
        raise MacroError('Unknown macro "%s".' % suffix, node, context=loader.context) from e

    try:
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

        result = macro(node, loader)
        if isgenerator(result):
            return run_coroutine(result, callback)
        else:
            return result
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
