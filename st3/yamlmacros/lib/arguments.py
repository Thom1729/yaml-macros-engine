from yamlmacros import apply as _apply, raw_macro

import copy


__all__ = ['argument', 'if_', 'foreach', 'format']


@raw_macro
def argument(name, default=None):
    loader = yield
    arguments = loader.context
    if name.value in arguments:
        return arguments[name.value]
    elif default:
        return loader.construct_object(default)
    else:
        return None


@raw_macro
def if_(condition, then, else_=None):
    loader = yield
    if loader.load_object(condition):
        return loader.load_object(then)
    elif else_:
        return loader.load_object(else_)
    else:
        return None
if_.raw = True


@raw_macro
def foreach(in_, value, *, as_=None):
    loader = yield
    collection = loader.construct_object(in_, deep=True)

    if isinstance(collection, dict):
        items = collection.items()
    elif isinstance(collection, list):
        items = list(enumerate(collection))
    else:
        raise TypeError('Invalid collection.')

    key_binding = 'key'
    value_binding = 'value'

    if as_:
        as_ = loader.construct_object(as_, deep=True)

        if isinstance(as_, dict):
            key_binding = as_.get('key', None)
            value_binding = as_.get('value', None)
        elif isinstance(as_, list):
            if len(as_) == 1:
                key_binding = None
                value_binding = as_[0]
            elif len(as_) == 2:
                key_binding = as_[0]
                value_binding = as_[1]
        else:
            key_binding = None
            value_binding = as_
    else:
        key_binding = 'key'
        value_binding = 'value'

    return [
        _with(loader, copy.deepcopy(value), {
            key_binding: k,
            value_binding: v,
        })
        for k, v in items
    ]


def _with(loader, node, arguments):
    with loader.set_context(**arguments):
        return loader.construct_object(node, deep=True)


def format(string, bindings=None):
    loader = yield
    if bindings:
        pass
    else:
        bindings = loader.context

    return _apply(string.format, bindings)
