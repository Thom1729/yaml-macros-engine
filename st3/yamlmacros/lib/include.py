import sublime

from yamlmacros import process_macros

from yamlmacros.src.util import merge


__all__ = ['include', 'include_resource']


def include(path):
    with open(path, 'r') as file:
        return process_macros(
            file.read(),
            arguments=merge((yield).context, {"file_path": path}),
        )


def include_resource(path):
    try:
        text = sublime.load_resource(path)
    except IOError:
        raise FileNotFoundError(path)

    return process_macros(
        text,
        arguments=merge((yield).context, {"file_path": path}),
    )
