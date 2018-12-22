import sublime

from yamlmacros import process_macros, macro_options

from yamlmacros.src.util import merge


__all__ = ['include', 'include_resource']


@macro_options(raw=True)
def include(node):
    path_str = yield node

    with open(path_str, 'r') as file:
        return process_macros(
            file.read(),
            arguments=merge((yield).context, {"file_path": path_str}),
        )


@macro_options(raw=True)
def include_resource(node):
    path = yield node
    return process_macros(
        sublime.load_resource(path),
        arguments=merge((yield).context, {"file_path": path}),
    )
