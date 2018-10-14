import shlex

from IPython.core import magic
import IPython.core.magic_arguments as ma
from IPython.display import publish_display_data, display

from . import latex

# TODO: is it possible to use LaTeX syntax highlighting for cell magics?

# %config InlineBackend.figure_formats=['svg']

_MIME_TYPES = {
    'png': 'image/png',
    'svg': 'image/svg+xml',
    'pdf': 'application/pdf',
}

# escape_latex() from PyLaTeX:
#    '&': r'\&',
#    '%': r'\%',
#    '$': r'\$',
#    '#': r'\#',
#    '_': r'\_',
#    '{': r'\{',
#    '}': r'\}',
#    '~': r'\textasciitilde{}',
#    '^': r'\^{}',
#    '\\': r'\textbackslash{}',
#    '\n': '\\newline%\n',
#    '-': r'{-}',
#    '\xA0': '~',  # Non-breaking space
#    '[': r'{[}',
#    ']': r'{]}',

# Jinja for LaTeX from http://flask.pocoo.org/snippets/55/
#
#app = Flask(__name__)
#
#LATEX_SUBS = (
#    (re.compile(r'\\'), r'\\textbackslash'),
#    (re.compile(r'([{}_#%&$])'), r'\\\1'),
#    (re.compile(r'~'), r'\~{}'),
#    (re.compile(r'\^'), r'\^{}'),
#    (re.compile(r'"'), r"''"),
#    (re.compile(r'\.\.\.+'), r'\\ldots'),
#)
#
#def escape_tex(value):
#    newval = value
#    for pattern, replacement in LATEX_SUBS:
#        newval = pattern.sub(replacement, newval)
#    return newval
#
#texenv = app.create_jinja_environment()
#texenv.block_start_string = '((*'
#texenv.block_end_string = '*))'
#texenv.variable_start_string = '((('
#texenv.variable_end_string = ')))'
#texenv.comment_start_string = '((='
#texenv.comment_end_string = '=))'
#texenv.filters['escape_tex'] = escape_tex
#
#template = texenv.get_template('template.tex')
#template.render(name='Tom')


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


def _arguments_default(func):
    func = ma.argument('--load', help='load stuff')(func)
    #func = ma.argument('--save', help='save stuff')(func)
    #func = ma.argument('--format', help='select format(s)')(func)
    #func = ma.kwds(epilog='I am the epilog.')(func)
    return ma.magic_arguments()(func)


def _arguments_display_save(func):
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


@magic.magics_class
class CallLatex(magic.Magics):
    """

    An instance of this class is available in IPython::

        get_ipython().magics_manager.registry['CallLatex']


    """
    # TODO: use InlineBackend.figure_formats?
    # TODO: cfg = InlineBackend.instance(parent=shell)
    # TODO: set_matplotlib_formats: https://github.com/ipython/ipython/blob/master/IPython/core/display.py#L1359
    # TODO: select_figure_formats: https://github.com/ipython/ipython/blob/master/IPython/core/pylabtools.py#L202
    # TODO: store mime types in instance: defaults from InlineBackend, how to
    #       override?

    def __init__(self, **kwargs):
        super(CallLatex, self).__init__(**kwargs)
        # TODO: get settings and pass them on?
        self.caller = latex.Caller()

    @magic.line_cell_magic
    def call_latex_preamble(self, line, cell=None):

        # TODO: if LaTeX output is selected -> publish_display_data()?

        # TODO: option --overwrite to clear old preambles
        #       or option --clear that does the same (and can be used on its
        #       own in line magic)

        if cell is None:
            # TODO
            return line

        self.caller.preambles.append(cell)

    # TODO: pgfplot with inline table data from NumPy array
    # TODO:     structured array, dict, list, ...

    # TODO: cell magic to define function that can be called to generate
    #       drawing (display and optionally save to file)

    # TODO: options, parse_options(), argparse?
    # scale, size, f (= format), --scale 2 --size 300,300

    # TODO: option in line magics: load from file
    # TODO: option in cell magics: save to file

    # TODO: options --show pdf --save tex
    #       --show ps.pdf,svg
    #       --show tex -> "rendered" LaTeX; --show txt -> plain text
    #       PNG has lower priority than LaTeX in notebook app (and HTML export)

    # TODO: Jinja template: filter escape_latex from PyLaTeX

    # TODO: --debug flag that shows build messages
    #       --show txt for showing the LaTeX source
    # TODO: "tex" format (will be rendered if possible)?

    # TODO: option in cell magics (except call_latex): load preamble from file?

    # TODO: non-option arguments are added to preamble?

    @magic.line_cell_magic
    def call_latex(self, line, cell=None):
        """Call LaTeX and pass the contents of the current cell.

        """
        if cell is None:
            # TODO
            return line

        # TODO: get formats
        #formats = ['svg']
        formats = [['svg', 'pdf', 'png']]
        results = self.caller.call(cell, formats, blocking=False)
        publish(formats, results)

    # TODO: move down
    def _parse_arguments(self, func, line, cell=None):

        # NB: IPython's parse_argstring() keeps quotes, shlex removes them.
        # See https://github.com/ipython/ipython/issues/2001
        args = func.parser.parse_args(shlex.split(line))

        # TODO if line magic, there is no save
        if cell is None:
            print('I am a line magic')
        return args

    # TODO: move down
    def _check_display(self, args):
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

    @_arguments_default
    @_arguments_display_save
    @ma.kwds(epilog='I am the epilog.')
    @magic.line_cell_magic
    def call_latex_standalone(self, line, cell=None):
        """Call LaTeX using the *standalone* documentclass.

        """

        # TODO: argument for loading preamble from file (without storing in
        #       instance)

        args = self._parse_arguments(self.call_latex_standalone, line, cell)

        if cell is None:
            # TODO
            return line

        formats = self._check_display(args)

        displays = []
        for format in formats:
            displays.append(publish_empty(format))

        files = args.save

        # TODO: Jinja
        # TODO: store Jinja result to file if requested

        results = self.caller.call_standalone(
            cell, formats, files, blocking=False)

        for disp, output, format in zip(displays, results, formats):
            output.add_done_callback(publish_update(disp, format))

    # TODO: magic for pstricks?

    # TODO: line magic for a single line of TikZ code? or combine with below?

    @magic.line_cell_magic
    def call_latex_tikzpicture(self, line, cell=None):
        """Call LaTeX using a *tikzpicture* environment.

        """
        if cell is None:
            # TODO: load code from .tex file
            # TODO: if no file is given, use "line" as TikZ command?
            return line

        # TODO: use cell text, file input is not allowed (except for preamble)

        # TODO: get only the necessary formats
        #formats = ['svg']
        formats = [['svg', 'pdf', 'png']]

        results = self.caller.call_tikzpicture(
            cell, formats, blocking=False)

        # TODO: store LaTeX content of environment (with Jinja replacements)

        publish(formats, results)

        # TODO: return something? probably for debugging?
        return None
