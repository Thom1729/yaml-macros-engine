import traceback
import time
from os import path

from .engine import process_macros
from .yaml_provider import get_yaml_instance
from .engine import MacroError

def build(source_text, destination_path, error_stream, arguments, error_highlighter=None):
    t0 = time.perf_counter()

    error_stream.write('Building %s... (%s)\n' % (path.basename(arguments['file_path']), arguments['file_path']))

    def done(message):
        error_stream.write('[{message} in {time:.2f} seconds.]\n\n'.format(
            message=message,
            time = time.perf_counter() - t0
        ))

    def handle_error(e):
        if isinstance(e, MacroError):
            error_stream.write('\n')
            error_stream.write(e.message + '\n')
            error_stream.write(str(e.node.start_mark) + '\n')

            if e.__cause__:
                handle_error(e.__cause__)

            if error_highlighter:
                error_highlighter.highlight(
                    e.context.get('file_path'),
                    e.node.start_mark.index,
                    e.node.end_mark.index,
                    e.message,
                )
        else:
            error_stream.write('\n')
            error_stream.write(''.join(traceback.format_exception(None, e, e.__traceback__)) + '\n')

    try:
        result = process_macros(source_text, arguments=arguments)
    except Exception as e:
        handle_error(e)
        done('Failed')
        return

    serializer = get_yaml_instance()

    with open(destination_path, 'w') as output_file:
        serializer.dump(result, stream=output_file)
        error_stream.write('Compiled to %s. (%s)\n' % (path.basename(destination_path), destination_path))
        done('Succeeded')