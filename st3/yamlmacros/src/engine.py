from .yaml_provider import get_yaml_instance, get_loader
from .macro_provider import MacroProvider

try:
    from typing import Any, Optional
    from ruamel.yaml.compat import StreamTextType, StreamType
    from .types import ContextType
except ImportError:
    pass


__all__ = ['process_macros']


def process_macros(
    input: 'StreamTextType',
    arguments: 'ContextType' = {},
    *,
    macros_root: str = None
) -> 'Any':
    yaml = get_loader(macros_root=macros_root, context=arguments)

    return yaml.load(input)


def build_yaml_macros(
    input: 'StreamTextType',
    output: 'Optional[StreamType]' = None,
    context: 'ContextType' = {}
) -> None:
    syntax = process_macros(input, context)
    yaml = get_yaml_instance()

    yaml.dump(syntax, stream=output)
