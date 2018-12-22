import keyword
from functools import wraps


__all__ = [
    'fix_keywords', 'apply', 'deprecated', 'flatten', 'merge', 'run_coroutine',
    'macro_options', 'public_members'
]


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


def macro_options(**kwargs):
    def decorator(function):
        function._macro_options = kwargs
        return function

    return decorator


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
