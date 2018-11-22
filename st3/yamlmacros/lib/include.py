import sublime

from yamlmacros import process_macros
from yamlmacros import raw_macro

from yamlmacros.src.util import merge


__all__ = ['include', 'include_resource']


@raw_macro
def include(path, *, loader):
    path_str = loader.construct_scalar(path)

    with open(path_str, 'r') as file:
        return process_macros(
            file.read(),
            arguments=merge(loader.context, { "file_path": path_str }),
        )

@raw_macro
def include_resource(resource, *, loader):
    path = loader.construct_scalar(resource)
    return process_macros(
        sublime.load_resource(path),
        arguments=merge(loader.context, { "file_path": path }),
    )
