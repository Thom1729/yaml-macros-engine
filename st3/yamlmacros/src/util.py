import keyword
from functools import wraps
from ruamel.yaml import ScalarNode, SequenceNode, MappingNode
from inspect import signature, Parameter


__all__ = ['apply', 'deprecated', 'raw_macro']


def fix_keywords(d):
    return {
        (k + '_' if keyword.iskeyword(k) else k): v
        for k, v in d.items()
    }


def apply(fn, args):
    if isinstance(args, dict):
        return fn(**fix_keywords(args))
    elif isinstance(args, list):
        return fn(*args)
    else:
        return fn(args)


def deprecated(*args):
    def _deprecated(f, message=None):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print('Warning: {name} is deprecated.{message}'.format(
                name=f.__name__,
                message=(' ' + message) if message else '',
            ))
            return f(*args, **kwargs)

        return wrapper

    if len(args) == 1 and callable(args[0]):
        return _deprecated(args[0])
    else:
        return lambda f: _deprecated(f, *args)


def flatten(*args):
    for arg in args:
        if isinstance(arg, list):
            yield from flatten(*arg)
        elif arg is not None:
            yield arg


def merge(*dicts):
    ret = {}
    for d in dicts:
        ret.update(d)
    return ret


def run_coroutine(generator, callback):
    try:
        result = next(generator)

        while True:
            try:
                value = callback(result)
            except Exception as ex:
                result = generator.throw(ex)
            else:
                result = generator.send(value)
    except StopIteration as ex:
        return ex.value


def raw_macro(function):
    function.raw = True
    return function

def is_raw_macro(function):
    return getattr(function, 'raw', False)
