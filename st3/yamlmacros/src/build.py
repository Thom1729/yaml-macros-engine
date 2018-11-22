import traceback
import time
from os import path

from .engine import process_macros
from .yaml_provider import get_yaml_instance
from .engine import MacroError


__all__ = ['build']


def build(source_text, destination_path, error_stream, arguments):
    t0 = time.perf_counter()

    def out(*args):
        print(*args, file=error_stream)

    out('Building %s... (%s)' % (path.basename(arguments['file_path']), arguments['file_path']))

    def done(message):
        out('[{message} in {time:.2f} seconds.]\n'.format(
            message=message,
            time = time.perf_counter() - t0
        ))

    def handle_error(e):
        if isinstance(e, MacroError):
            out()
            out(e.message)
            out(e.node.start_mark)
            out(e.context)

            if e.__cause__:
                handle_error(e.__cause__)
        else:
            out()
            out(''.join(traceback.format_exception(None, e, e.__traceback__)))

    try:
        result = process_macros(source_text, arguments=arguments)
    except Exception as e:
        handle_error(e)
        done('Failed')
        return

    serializer = get_yaml_instance()

    with open(destination_path, 'w') as output_file:
        serializer.dump(result, stream=output_file)
        out('Compiled to %s. (%s)' % (path.basename(destination_path), destination_path))
        done('Succeeded')
