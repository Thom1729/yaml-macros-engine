from yamlmacros import apply as _apply
from yamlmacros import raw_macro

import copy

@raw_macro
def argument(name, default=None, *, eval, loader):
    arguments = loader.context
    if name.value in arguments:
        return arguments[name.value]
    elif default:
        return eval(default)
    else:
        return None

@raw_macro
def if_(condition, then, else_=None, *, eval):
    if eval(condition):
        return eval(then)
    elif else_:
        return eval(else_)
    else:
        return None

@raw_macro
def foreach(in_, value, *, as_=None, loader):
    collection = loader.construct_object(in_)

    if isinstance(collection, dict):
        items = collection.items()
    elif isinstance(collection, list):
        items = enumerate(collection)
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

@raw_macro
def format(string, bindings=None, *, eval, loader):
    if bindings:
        bindings = eval(bindings)
    else:
        bindings = loader.context

    return _apply(string.value.format, bindings)
