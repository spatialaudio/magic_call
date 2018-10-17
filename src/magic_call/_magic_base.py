import shlex
import urllib

from IPython.core.error import UsageError
import IPython.core.magic_arguments as ma
from IPython.display import publish_display_data, display

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
# application/pdf
# image/png
# image/jpeg
# image/svg+xml


def flatten_formats(formats):
    """

    In the Jupyter notebook, we can have multiple outputs with multiple
    alternative formats each, i.e. a nested list of formats.

    This functions creates a flat list from them and some information to
    un-flatten their results again.

    """
    flattened_formats = []
    nested_lengths = []
    for item in formats:
        assert not isinstance(item, str)
        assert len(item) != 0
        flattened_formats.extend(item)
        nested_lengths.append(len(item))
    return flattened_formats, nested_lengths


def unflatten_results(results, nested_lengths, caller):
    """

    Turn a flat list of futures into a list of (fewer) futures containing
    sub-lists of the results of the original futures.

    """
    results = results.copy()
    nested_results = []
    for length in nested_lengths:
        task = caller.scheduler.create_task(
                lambda _, futures: [f.result() for f in futures],
                results[:length])
        nested_results.append(task.future)
        results = results[length:]
    return nested_results


# TODO: does this need to be public?
def publish(formats, results):
    # TODO: somehow use a IPython.utils.capture.RichOutput?
    display_data = {}
    results, = results
    formats, = formats
    for format, result in zip(formats, results.result()):
        display_data[_MIME_TYPES[format]] = result

    # TODO: latex has higher priority than png!
    # TODO: is a plain text representation necessary?
    #'text/plain': 'text',
    #'text/latex': 'TODO: much latex code!',
    # TODO: DOCs: mention that jpeg is not available?
    #'image/jpeg': '',

    # https://github.com/jupyterlab/jupyterlab/pull/3135
    # https://github.com/jupyterlab/jupyterlab/issues/3038

    # TODO: metadata?
    # "metadata" : {
    #   "image/png": {
    #     "width": 640,
    #     "height": 480,
    #   },
    # },
    return publish_display_data(display_data)


def publish_empty(formats):
    assert not isinstance(formats, str)
    data = {}
    for format in formats:
        data[_MIME_TYPES[format]] = ''
    return display(data, raw=True, display_id=True)


def publish_data(disp, format):
    assert isinstance(format, (list, tuple))

    def callback(future):
        output = future.result()
        assert isinstance(output, (list, tuple))
        data = {}
        for f, o in zip(format, output):
            data[_MIME_TYPES[f]] = o
        disp.update(data, raw=True)

    return callback


def publish_creating_file(name):
    message = {
        'text/plain': 'creating file: {!r}'.format(name),
        'text/markdown': 'creating file: {}'.format(name),
    }
    return display(message, raw=True, display_id=True)


def publish_file(disp):

    def callback(future):
        name = str(future.result())
        message = {
            'text/plain': 'created file: {!r}'.format(name),
            'text/markdown': 'created file: [{}]({})'.format(
                name, urllib.parse.quote(name)),
        }
        disp.update(message, raw=True)

    return callback


#def arguments_default(func):
#    func = ma.argument('--load', help='load stuff')(func)
#    #func = ma.argument('--save', help='save stuff')(func)
#    #func = ma.kwds(epilog='I am the epilog.')(func)
#    return ma.magic_arguments()(func)


def arguments_display_save_assign(func):
    func = ma.argument(
        '--assign', nargs=2, action='append', default=[],
        metavar=('FORMAT', 'VARIABLE'),
        help=''
        'Assigns data of the given format to the given variable. '
        'Can be used multiple times, but each time only with a single format. '
        # TODO:
        'Implies --no-display '
        '(if no --display option is used at the same time). '
    )(func)
    func = ma.argument(
        '--save', metavar='FILENAME', action='append', default=[],
        help=''
        'Save the result to the given file name. '
        'The format is selected by the file suffix. '
        'This can be used repeatedly to save multiple files. '
        'If a file with the same name already exists, it is overwritten! '
    )(func)
    func = ma.argument(
        '-n', '--no-display', action='store_true',
        help=''
        "Don't display anything. "
    )(func)
    func = ma.argument(
        '-d', '--display', metavar='FORMAT', action='append', default=[],
        help=''
        'Select format(s) to display. '
        'Can be used repeatedly to generate multiple outputs. '
        'If no formats are selected, default values are used. '
        'Use --no-display to display nothing. '
        'TODO: Explain semicolon, comma, dot.'
    )(func)
    return func


def parse_arguments(func, line, cell=None):

    # NB: IPython's parse_argstring() keeps quotes, shlex removes them.
    # See https://github.com/ipython/ipython/issues/2001
    args = func.parser.parse_args(shlex.split(line))

    # TODO if line magic, there is no save
    if cell is None:
        print('I am a line magic')
    return args


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
    # TODO: get default formats from config
    display_formats = [['png']]

    # TODO: error if --no-display and no --assign and no --save

    assign_formats = []  # TODO

    return display_formats, assign_formats, args.save
