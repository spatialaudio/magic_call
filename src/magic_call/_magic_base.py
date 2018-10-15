import shlex

import IPython.core.magic_arguments as ma
from IPython.display import publish_display_data, display

_MIME_TYPES = {
    'png': 'image/png',
    'svg': 'image/svg+xml',
    'pdf': 'application/pdf',
}


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
    if isinstance(formats, str):
        formats = [formats]
    data = {}
    for format in formats:
        data[_MIME_TYPES[format]] = ''
    return display(data, raw=True, display_id=True)


def publish_update(disp, format):
    if not isinstance(format, (list, tuple)):
        format = [format]

    def callback(future):
        output = future.result()
        if not isinstance(output, (list, tuple)):
            output = [output]
        data = {}
        for f, o in zip(format, output):
            data[_MIME_TYPES[f]] = o
        disp.update(data, raw=True)

    return callback


def arguments_default(func):
    func = ma.argument('--load', help='load stuff')(func)
    #func = ma.argument('--save', help='save stuff')(func)
    #func = ma.argument('--format', help='select format(s)')(func)
    #func = ma.kwds(epilog='I am the epilog.')(func)
    return ma.magic_arguments()(func)


def arguments_display_save(func):
    func = ma.argument(
        '--save', metavar='FILENAME', action='append', default=[],
        help=
        'Save the result to the given file name. '
        'The format is selected by the file suffix. '
        'This can be used repeatedly to save multiple files. '
        'If a file with the same name already exists, it is overwritten! '
    )(func)
    func = ma.argument(
        '-n', '--no-display', action='store_true',
        help=
        "Don't display anything. "
    )(func)
    func = ma.argument(
        '-d', '--display', metavar='FORMAT', action='append', default=[],
        help=
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


def check_display(args):
    # TODO: DOC:
    # semicolon: multiple outputs
    # comma: one output with multiple alternatives
    # dot: specify tool chain
    if args.no_display:
        if args.display:
            raise TypeError(
                '--display and --no-display are mutually exclusive')
        return [[]]
    if args.display:
        formats = []
        for disp in args.display:
            for semicolon_part in disp.split(';'):
                formats.append(semicolon_part.split(','))
        return formats
    # TODO: get default formats from config
    formats = [['png']]
    return formats
