from keyword import iskeyword

try:
    from typing import Callable, Generator, TypeVar
except ImportError:
    pass
else:
    _YieldType = TypeVar('_YieldType')
    _SendType = TypeVar('_SendType')
    _ReturnType = TypeVar('_ReturnType')


__all__ = [
    'fix_keywords', 'apply', 'flatten', 'merge', 'run_coroutine'
]


def fix_keywords(d: dict) -> dict:
    return {
        (k + '_' if iskeyword(k) else k): v
        for k, v in d.items()
    }


def apply(fn: 'Callable[..., _ReturnType]', args: object) -> '_ReturnType':
    if isinstance(args, dict):
        return fn(**fix_keywords(args))
    elif isinstance(args, list):
        return fn(*args)
    else:
        return fn(args)


def flatten(*args: object) -> 'Generator':
    for arg in args:
        if isinstance(arg, list):
            yield from flatten(*arg)
        elif arg is not None:
            yield arg


def merge(*dicts: dict) -> dict:
    ret = {}
    for d in dicts:
        ret.update(d)
    return ret


def run_coroutine(
    generator: 'Generator[_YieldType, _SendType, _ReturnType]',
    callback: 'Callable[[_YieldType], _SendType]'
) -> '_ReturnType':
    try:
        result = next(generator)

        while True:
            try:
                value = callback(result)
            except Exception as ex:
                result = generator.throw(type(ex), ex, ex.__traceback__)
            else:
                result = generator.send(value)
    except StopIteration as ex:
        return ex.value
