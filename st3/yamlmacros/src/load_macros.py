import sys
import imp
from contextlib import contextmanager


@contextmanager
def temporary_package(name, path):
    module = imp.new_module(name)
    module.__path__ = [path]
    module.__parent__ = ''
    sys.modules[name] = module
    yield
    sys.modules.pop(name, None)
