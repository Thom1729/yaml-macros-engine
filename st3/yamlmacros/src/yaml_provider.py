from ruamel.yaml import YAML
from ruamel.yaml.representer import RoundTripRepresenter
from ruamel.yaml.parser import Parser
from collections import OrderedDict

from .macro_provider import MacroProvider
from .custom_constructor import CustomConstructor

from .compat.typing import Any
from .types import ContextType, VersionType


__all__ = ['get_yaml_instance']


class CustomRepresenter(RoundTripRepresenter):
    pass


CustomRepresenter.add_representer(
    OrderedDict,
    lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data)
)


def get_yaml_instance(
    version: VersionType = (1, 2),
    indent: Any = {'mapping': 2, 'sequence': 4, 'offset': 2},
    **kwargs: Any
) -> YAML:
    yaml = YAML(**kwargs)

    yaml.version = version  # type: ignore
    yaml.Representer = CustomRepresenter

    yaml.indent(**indent)

    return yaml


def get_loader(macros_root: str = None, context: ContextType = {}) -> YAML:
    yaml = YAML()
    yaml.version = (1, 2)  # type: ignore

    yaml.Parser = Parser
    yaml._constructor = CustomConstructor(  # type: ignore
        yaml,
        # macros_root=macros_root,
        macro_provider=MacroProvider(macros_root).get_macro,
        context=context
    )

    return yaml
