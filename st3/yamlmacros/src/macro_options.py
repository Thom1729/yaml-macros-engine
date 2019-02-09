ATTRIBUTE = '_macro_options'


def macro_options(**kwargs):
    def decorator(function):
        setattr(function, ATTRIBUTE, kwargs)
        return function

    return decorator


def get_macro_options(function):
    return getattr(function, ATTRIBUTE, {})
