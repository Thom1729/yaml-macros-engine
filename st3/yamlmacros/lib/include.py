from yamlmacros import process_macros
from yamlmacros import get_st_resource

def include(path):
    with open(path, 'r') as file:
        return process_macros(
            file.read(),
            arguments={ "file_path": path },
        )

def include_resource(resource):
    file_path, file_contents = get_st_resource(resource)
    return process_macros(
        file_contents,
        arguments={ "file_path": file_path },
    )
