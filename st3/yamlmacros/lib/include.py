import sublime

from yamlmacros import process_macros, macro_options

from yamlmacros.src.util import merge


__all__ = ['include', 'include_resource']


def include(path):
    with open(path, 'r') as file:
        return process_macros(
            file.read(),
            arguments=merge((yield).context, {"file_path": path}),
        )


def include_resource(path):
    return process_macros(
        sublime.load_resource(path),
        arguments=merge((yield).context, {"file_path": path}),
    )
