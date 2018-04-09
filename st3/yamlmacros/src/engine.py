import os
import sys
import io
from inspect import signature, Parameter
import importlib
import functools

from .yaml_provider import get_yaml_instance, get_constructor
from .util import apply, merge, call_with_known_arguments

class MacroError(Exception):
    def __init__(self, message, node, context=None):
        self.message = message
        self.node = node
        self.context = context

def load_macros(macro_path):
    sys.path.append(os.getcwd())
    try:
        module = importlib.import_module(macro_path)

        return {
            name.rstrip('_'): func
            for name, func in module.__dict__.items()
            if callable(func) and not name.startswith('_')
        }
    finally:
        sys.path.pop()

def apply_transformation(loader, node, transform):
    if getattr(transform, 'raw', False):
        return call_with_known_arguments(transform,
            node=node,
            loader=loader,

            # Deprecated arguments
            eval=loader.construct_object,
            arguments=loader.context,
        )
    else:
        args = loader.construct_value_ignore_tag(node)

        if isinstance(args, dict) and any(
            param.kind == Parameter.VAR_POSITIONAL
            for name, param in signature(transform).parameters.items()
        ):
            # Before Python 3.6, **kwargs will not preserve order.
            args = list(args.items())

        return apply(transform, args)

def macro_multi_constructor(macros):
    def multi_constructor(loader, suffix, node):
        try:
            macro = macros[suffix]
        except KeyError as e:
            raise MacroError('Unknown macro "%s".' % suffix, node, context=loader.context) from e

        try:
            return apply_transformation(loader, node, macros[suffix])
        except Exception as e:
            raise MacroError('Error in macro execution.', node, context=loader.context) from e

    return multi_constructor

@functools.lru_cache(maxsize=16)
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

def process_macros(input, arguments={}):
    tree, macros = get_parse(input)

    constructor = get_constructor()

    for handle, macro_path in macros:
        macros = merge(*[load_macros(path) for path in macro_path.split(',')])

        constructor.add_multi_constructor(handle,
            macro_multi_constructor(macros)
        )

    with constructor.set_context(**arguments):
        return constructor.construct_document(tree)

def build_yaml_macros(input, output=None, context=None):
    syntax = process_macros(input, context)
    yaml = get_yaml_instance()

    yaml.dump(syntax, stream=output)
