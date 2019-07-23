from .compat.typing import Callable, Mapping

from ruamel.yaml import Node

try:
    from ruamel.yaml.compat import StreamTextType, StreamType, VersionType
except ImportError:
    StreamTextType = None  # type: ignore
    StreamType = None  # type: ignore
    VersionType = None  # type: ignore

# from .custom_constructor import CustomConstructor

__all__ = ['ContextType', 'MacroType']

ContextType = Mapping[str, object]
MacroType = Callable[['CustomConstructor', Node], object]
