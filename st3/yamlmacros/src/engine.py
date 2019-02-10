from .yaml_provider import get_yaml_instance
from .macro_provider import MacroProvider

try:
    from typing import Any, Optional
    from ruamel.yaml import Node
    from ruamel.yaml.compat import StreamTextType, StreamType
    from .custom_constructor import CustomConstructor
    from .types import ContextType
except ImportError:
    pass


__all__ = ['MacroError', 'process_macros']


class MacroError(Exception):
    def __init__(self, message: str, node: 'Node', context: 'ContextType' = None) -> None:
        self.message = message
        self.node = node
        self.context = context


def process_macros(
    input: 'StreamTextType',
    arguments: 'ContextType' = {},
    *,
    macros_root: str = None
) -> 'Any':
    yaml = get_yaml_instance()

    provider = MacroProvider(macros_root)

    def multi_constructor(loader: 'CustomConstructor', suffix: str, node: 'Node') -> object:
        def error(message: str) -> MacroError:
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


def build_yaml_macros(
    input: 'StreamTextType',
    output: 'Optional[StreamType]' = None,
    context: 'ContextType' = {}
) -> None:
    syntax = process_macros(input, context)
    yaml = get_yaml_instance()

    yaml.dump(syntax, stream=output)
