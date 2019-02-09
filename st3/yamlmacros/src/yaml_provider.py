from ruamel.yaml import YAML
from ruamel.yaml.representer import RoundTripRepresenter
from ruamel.yaml.parser import Parser
from collections import OrderedDict

from .custom_constructor import CustomConstructor


__all__ = ['get_yaml_instance', 'get_constructor']


class CustomRepresenter(RoundTripRepresenter):
    pass


CustomRepresenter.add_representer(
    OrderedDict,
    lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data)
)


def get_yaml_instance(
    version=(1, 2),
    indent={'mapping': 2, 'sequence': 4, 'offset': 2},
    **kwargs
):
    yaml = YAML(**kwargs)

    yaml.Representer = CustomRepresenter

    yaml.version = version
    yaml.indent(**indent)

    return yaml


def get_constructor():
    yaml = YAML()
    yaml.Parser = Parser
    yaml._constructor = CustomConstructor(loader=yaml)
    yaml.version = (1, 2)

    return yaml
