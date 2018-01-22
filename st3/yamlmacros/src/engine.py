import os
import sys
import io
from inspect import signature, Parameter
import importlib
import ruamel.yaml
import functools

from yamlmacros.src.yaml_provider import get_yaml_instance
from yamlmacros.src.context import get_context
from yamlmacros.src.context import set_context
from yamlmacros.src.util import apply, merge

class MacroError(Exception):
    def __init__(self, message, node):
        self.message = message
        self.node = node
        self.context = get_context()

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
        def eval(node, arguments=None):
            if arguments:
                with set_context(**arguments):
                    return eval(node)

            return loader.construct_object(node, deep=True)

        eval.loader = loader

        return transform(node, arguments=get_context(), eval=eval)
    else:
        if isinstance(node, ruamel.yaml.ScalarNode):
            args = loader.construct_scalar(node)
        elif isinstance(node, ruamel.yaml.SequenceNode):
            args = list(loader.construct_yaml_seq(node))[0]
        elif isinstance(node, ruamel.yaml.MappingNode):
            args = list(loader.construct_yaml_map(node))[0]

            if any(
                param.kind == Parameter.VAR_POSITIONAL
                for name, param in signature(transform).parameters.items()
            ):
                # Before Python 3.6, **kwargs will not preserve order.
                args = list(args.items())
        else:
            args = node

        return apply(transform, args)

def macro_multi_constructor(macros):
    def multi_constructor(loader, suffix, node):
        names = suffix.split(':')

        ret = node

        for name in reversed(names):
            try:
                macro = macros[name]
            except KeyError as e:
                raise MacroError('Unknown macro "%s".' % name, ret) from e

            try:
                ret = apply_transformation(loader, ret, macro)
            except Exception as e:
                raise MacroError('Error in macro execution.', ret) from e

        return ret

    return multi_constructor

# @functools.lru_cache(maxsize=16)
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
    with set_context(**arguments):
        tree, macros = get_parse(input)

        yaml = get_yaml_instance()

        for handle, macro_path in macros:
            macros = merge(*[load_macros(path) for path in macro_path.split(',')])

            yaml.Constructor.add_multi_constructor(handle,
                macro_multi_constructor(macros)
            )

        return yaml.constructor.construct_document(tree)

def build_yaml_macros(input, output=None, context=None):
    syntax = process_macros(input, context)
    yaml = get_yaml_instance()

    yaml.dump(syntax, stream=output)
