from ruamel.yaml.constructor import RoundTripConstructor
from contextlib import contextmanager

class CustomConstructor(RoundTripConstructor):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.contexts = [{}]

    @contextmanager
    def set_context(self, **kwargs):
        new = self.contexts[-1].copy()
        new.update(**kwargs)
        self.contexts.append(new)
        yield
        self.contexts.pop()