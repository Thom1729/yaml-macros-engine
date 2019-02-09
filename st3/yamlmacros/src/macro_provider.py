import importlib
from uuid import uuid4

from .load_macros import temporary_package
from .get_macro import get_macro


def public_members(module):
    if hasattr(module, '__all__'):
        is_public = lambda name: name in module.__all__
    else:
        is_public = lambda name: not name.startswith('_')

    return {
        name: value
        for name, value in module.__dict__.items()
        if is_public(name)
    }


def load_macros(macro_path, macros_root):
    package_name = 'yaml_macros_engine_{!s}'.format(uuid4())

    with temporary_package(package_name, macros_root):
        module = importlib.import_module(macro_path, package_name)

        return {
            name.rstrip('_'): get_macro(func)
            for name, func in public_members(module).items()
        }


class MacroProvider():
    def __init__(self, macros_root):
        self.macros_root = macros_root
        self.modules = {}

    def get_module(self, path):
        if path not in self.modules:
            self.modules[path] = load_macros(path, self.macros_root)
        return self.modules[path]

    def get_macro(self, suffix):
        macro_path, macro_name = suffix.split(':')

        for path in macro_path.split(','):
            module = self.get_module(path)
            if macro_name in module:
                return module[macro_name]

        raise LookupError(macro_name)
