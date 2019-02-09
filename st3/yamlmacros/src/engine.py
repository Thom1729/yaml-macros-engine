from .yaml_provider import get_yaml_instance, get_constructor
from .macro_provider import MacroProvider


__all__ = ['MacroError', 'process_macros']


class MacroError(Exception):
    def __init__(self, message, node, context=None):
        self.message = message
        self.node = node
        self.context = context


def process_macros(input, arguments={}, *, macros_root=None):
    yaml = get_constructor()

    provider = MacroProvider(macros_root)

    def multi_constructor(loader, suffix, node):
        def error(message):
            return MacroError(message, node, context=loader.context)

        try:
            macro = provider.get_macro(suffix)
        except Exception as ex:
            raise error('Unknown macro {!r}.'.format(suffix)) from ex

        try:
            return macro(loader, node)
        except Exception as ex:
            raise error('Error in macro execution.') from ex

    yaml.constructor.add_multi_constructor('tag:yaml-macros:', multi_constructor)

    with yaml.constructor.set_context(**arguments):
        return yaml.load(input)


def build_yaml_macros(input, output=None, context=None):
    syntax = process_macros(input, context)
    yaml = get_yaml_instance()

    yaml.dump(syntax, stream=output)
