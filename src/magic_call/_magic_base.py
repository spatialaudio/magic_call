import pathlib
import shlex
import urllib

from IPython.core.error import UsageError
from IPython.core.magic_arguments import argument, magic_arguments
from IPython.display import display

# TODO: support output formats txt and tex?
# TODO: support jpe?g
# TODO: force formats to lowercase?

_MIME_TYPES = {
    'png': 'image/png',
    'svg': 'image/svg+xml',
    'pdf': 'application/pdf',
}

# text/plain
# text/html
# text/markdown
# text/latex
# application/json
# application/javascript
# image/jpeg


class Handler:

    def __init__(self, args, scheduler):
        self.scheduler = scheduler
        self._nested_formats, assign_formats, self.files = \
            check_display_assign_save(args)

        self._format_handles = []
        for format in self._nested_formats:
            self._format_handles.append(publish_empty(format))

        # TODO writing vs. overwriting?

        self._file_handles = []
        for file in self.files:
            self._file_handles.append(publish_creating_file(file))

        self.formats = []
        self._nested_lengths = []
        for item in self._nested_formats:
            assert not isinstance(item, str)
            assert len(item) != 0
            self.formats.extend(item)
            self._nested_lengths.append(len(item))

    def update(self, format_results, file_results, blocking=True):
        format_results = format_results.copy()
        nested_results = []
        for length in self._nested_lengths:
            chunk = format_results[:length]
            if blocking:
                nested_results.append(chunk)
            else:
                task = self.scheduler.create_task(
                        lambda _, futures: [f.result() for f in futures],
                        chunk)
                nested_results.append(task.future)
            format_results = format_results[length:]

        for handle, results, formats in zip(self._format_handles,
                                           nested_results,
                                           self._nested_formats):
            if blocking:
                publish_data(handle, formats, results)
            else:
                results.add_done_callback(
                    publish_data_callback(handle, formats))

        for handle, result in zip(self._file_handles, file_results):
            if blocking:
                publish_file(handle, result)
            else:
                result.add_done_callback(publish_file_callback(handle))

        # TODO: assign
        #get_ipython().push({'myvar': value})


def flatten_formats(formats):
    """

    In the Jupyter notebook, we can have multiple outputs with multiple
    alternative formats each, i.e. a nested list of formats.

    This functions creates a flat list from them and some information to
    un-flatten their results again.

    """


def unflatten_results(results, nested_lengths, scheduler):
    """

    Turn a flat list of futures into a list of (fewer) futures containing
    sub-lists of the results of the original futures.

    """


## TODO: does this need to be public?
#def publish(formats, results):
#    # TODO: somehow use a IPython.utils.capture.RichOutput?
#    display_data = {}
#    results, = results
#    formats, = formats
#    for format, result in zip(formats, results.result()):
#        display_data[_MIME_TYPES[format]] = result
#
#    # TODO: latex has higher priority than png!
#    # TODO: is a plain text representation necessary?
#    #'text/plain': 'text',
#    #'text/latex': 'TODO: much latex code!',
#    # TODO: DOCs: mention that jpeg is not available?
#    #'image/jpeg': '',
#
#    # https://github.com/jupyterlab/jupyterlab/pull/3135
#    # https://github.com/jupyterlab/jupyterlab/issues/3038
#
#    # TODO: metadata?
#    # "metadata" : {
#    #   "image/png": {
#    #     "width": 640,
#    #     "height": 480,
#    #   },
#    # },
#    return publish_display_data(display_data)


def publish_empty(formats):
    assert not isinstance(formats, str)
    data = {}
    for format in formats:
        data[_MIME_TYPES[format]] = ''
    return display(data, raw=True, display_id=True)


def publish_data(disp, formats, output):
    assert isinstance(output, (list, tuple))
    data = {}
    for f, o in zip(formats, output):
        data[_MIME_TYPES[f]] = o
    disp.update(data, raw=True)


def publish_data_callback(disp, formats):
    assert isinstance(formats, (list, tuple))

    def callback(future):
        output = future.result()
        publish_data(disp, formats, output)

    return callback


def publish_creating_file(name):
    message = {
        'text/plain': 'creating file: {!r}'.format(name),
        'text/markdown': 'creating file: {}'.format(name),
    }
    return display(message, raw=True, display_id=True)


def publish_file(disp, result):
    name = str(result)
    message = {
        'text/plain': 'created file: {!r}'.format(name),
        'text/markdown': 'created file: [{}]({})'.format(
            name, urllib.parse.quote(name)),
    }
    disp.update(message, raw=True)


def publish_file_callback(disp):

    def callback(future):
        publish_file(disp, future.result())

    return callback


def arguments_display_assign_save(func):
    func = argument(
        '--save', metavar='FILENAME', action='append', default=[],
        help=''
        'Save the result to the given file name. '
        'The format is selected by the file suffix. '
        'This can be used repeatedly to save multiple files. '
        'If a file with the same name already exists, it is overwritten! '
    )(func)
    func = argument(
        '--assign', nargs=2, action='append', default=[],
        metavar=('FORMAT', 'VARIABLE'),
        help=''
        'Assigns data of the given format to the given variable. '
        'Can be used multiple times, but each time only with a single format. '
        # TODO:
        'Implies --no-display '
        '(if no --display option is used at the same time). '
        # TODO: always blocking!
    )(func)
    func = argument(
        '-n', '--no-display', action='store_true',
        help=''
        "Don't display anything. "
    )(func)
    func = argument(
        '-d', '--display', metavar='FORMAT', action='append', default=[],
        help=''
        'Select format(s) to display. '
        'Can be used repeatedly to generate multiple outputs. '
        'If no formats are selected, default values are used. '
        'Use --no-display to display nothing. '
        'TODO: Explain semicolon, comma, dot.'
    )(func)
    func = argument(
        'input_file', metavar='FILENAME', nargs='?',
        help=''
        'Load source text from the given file. '
        'This is only allowed when used as a line magic. '
        'The cell magic uses the cell content as source text. '
    )(func)
    return func


def parse_arguments(func, line, cell=None):
    # NB: IPython's parse_argstring() keeps quotes, shlex removes them.
    # See https://github.com/ipython/ipython/issues/2001
    return func.parser.parse_args(shlex.split(line))


def check_source(args, cell):
    if cell is None:
        if not args.input_file:
            raise UsageError('Positional argument is required in line magic')
        cell = pathlib.Path(args.input_file).read_text()
    else:
        if args.input_file:
            raise UsageError(
                'Positional argument is not allowed in cell magic')
    return cell


def check_display_assign_save(args):
    # TODO: DOC:
    # semicolon: multiple outputs
    # comma: one output with multiple alternatives
    # dot: specify tool chain

    display_formats = []
    if args.display and args.no_display:
        raise UsageError('--display and --no-display are mutually exclusive')
    if args.display:
        for disp in args.display:
            for semicolon_part in disp.split(';'):
                display_formats.append(semicolon_part.split(','))
    else:
        # TODO: get default formats from config
        display_formats = [['png']]

    # TODO: error if --no-display and no --assign and no --save

    assign_formats = []  # TODO

    return display_formats, assign_formats, args.save
