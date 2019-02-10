ATTRIBUTE = '_macro_options'

try:
    from typing import Callable, TypeVar
    _T = TypeVar('_T')
except ImportError:
    pass


__all__ = ['macro_options', 'get_macro_options']


def macro_options(**kwargs: bool) -> 'Callable[[_T], _T]':
    def decorator(function: '_T') -> '_T':
        setattr(function, ATTRIBUTE, kwargs)
        return function

    return decorator


def get_macro_options(function: 'Callable') -> dict:
    return getattr(function, ATTRIBUTE, {})
