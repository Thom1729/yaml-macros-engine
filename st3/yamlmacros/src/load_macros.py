import sys
from importlib.abc import Loader
from importlib.util import module_for_loader
from contextlib import contextmanager

try:
    from typing import Generator
    from types import ModuleType
except ImportError:
    pass


class TemporaryPackageLoader(Loader):
    def __init__(self, path: str) -> None:
        self.path = path

    @module_for_loader
    def load_module(self, module: 'ModuleType') -> 'ModuleType':
        module.__file__ = self.path
        module.__path__ = [self.path]  # type: ignore
        return module

    def is_package(self, fullname: str) -> bool:
        return True

    def module_repr(self, module: 'ModuleType') -> str:
        return '<module {!r} from {!r}>'.format(module.__name__, self.path)


@contextmanager
def temporary_package(name: str, path: str) -> 'Generator[None, None, None]':
    TemporaryPackageLoader(path).load_module(name)
    yield
    sys.modules.pop(name, None)
