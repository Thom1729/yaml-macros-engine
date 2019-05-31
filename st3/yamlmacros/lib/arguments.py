from yamlmacros import apply as _apply, macro_options

import copy


__all__ = ['argument', 'if_', 'with_', 'foreach', 'format']


@macro_options(raw=True)
def argument(name, default=None):
    arguments = (yield).context
    try:
        return arguments[(yield name)]
    except KeyError:
        if default is not None:
            return (yield default)
        else:
            return None


@macro_options(raw=True)
def with_(context, value):
    with (yield (yield context)):
        return (yield value)


@macro_options(raw=True)
def if_(condition, then, else_=None):
    if (yield condition):
        return (yield then)
    elif else_:
        return (yield else_)
    else:
        return None


@macro_options(raw=True)
def foreach(in_, value, *, as_=None):
    collection = yield in_

    if isinstance(collection, dict):
        items = collection.items()
    elif isinstance(collection, list):
        items = list(enumerate(collection))
    else:
        raise TypeError('Invalid collection {!r}.'.format(collection))

    if as_:
        binding_names = yield as_

        if isinstance(binding_names, dict):
            key_binding = binding_names.get('key', None)
            value_binding = binding_names.get('value', None)
        elif isinstance(binding_names, list):
            if len(binding_names) == 1:
                key_binding = None
                value_binding, = binding_names
            elif len(binding_names) == 2:
                key_binding, value_binding = binding_names
        else:
            key_binding = None
            value_binding = binding_names
    else:
        key_binding = 'key'
        value_binding = 'value'

    ret = []
    for k, v in items:
        with (yield {
            key_binding: k,
            value_binding: v,
        }):
            ret.append((yield copy.deepcopy(value)))
    return ret


def format(string, bindings=None):
    if bindings is None:
        bindings = (yield).context

    return _apply(string.format, bindings)
