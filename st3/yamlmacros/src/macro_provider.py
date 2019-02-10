import importlib
from uuid import uuid4

from .load_macros import temporary_package
from .get_macro import get_macro

try:
    from types import ModuleType
    from typing import Callable, Dict, Optional
except ImportError:
    pass


def public_members(module: 'ModuleType') -> 'Dict[str, Callable]':
    if hasattr(module, '__all__'):
        is_public = lambda name: name in module.__all__  # type: ignore
    else:
        is_public = lambda name: not name.startswith('_')

    return {
        name: value
        for name, value in module.__dict__.items()
        if is_public(name)
    }


def macros_from_module(module: 'ModuleType') -> 'Dict[str, Callable]':
    return {
        name.rstrip('_'): get_macro(func)
        for name, func in public_members(module).items()
    }


class MacroProvider():
    def __init__(self, macros_root: 'Optional[str]') -> None:
        self.macros_root = macros_root
        self.modules = {}  # type: Dict[str, Dict[str, Callable]]

    def load_module(self, path: str) -> 'Dict[str, Callable]':
        if self.macros_root is None:
            module = importlib.import_module(path)

            return macros_from_module(module)
        else:
            package_name = 'yaml_macros_engine_{!s}'.format(uuid4())
            with temporary_package(package_name, self.macros_root):
                module = importlib.import_module(path, package_name)

                return macros_from_module(module)

    def get_module(self, path: str) -> 'Dict[str, Callable]':
        if path not in self.modules:
            self.modules[path] = self.load_module(path)
        return self.modules[path]

    def get_macro(self, suffix: str) -> 'Callable':
        macro_path, macro_name = suffix.split(':')

        for path in macro_path.split(','):
            module = self.get_module(path)
            if macro_name in module:
                return module[macro_name]

        raise LookupError(macro_name)
