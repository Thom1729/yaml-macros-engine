from yamlmacros import process_macros
from yamlmacros import get_st_resource
from yamlmacros import raw_macro

from yamlmacros.src.util import merge

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
    file_path, file_contents = get_st_resource(loader.construct_scalar(resource))
    return process_macros(
        file_contents,
        arguments=merge(loader.context, { "file_path": file_path }),
    )
