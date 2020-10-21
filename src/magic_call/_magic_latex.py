from IPython.core import magic

from . import latex
from . import _magic_base as base

# TODO: is it possible to use LaTeX syntax highlighting for cell magics?

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


def arguments_preamble(func):
    func = base.ma.argument(
        '--preamble', metavar='FILENAME', action='append', default=[],
        help=
        'Load a file to be used as part of the preamble. '
        'This can be used repeatedly to load multiple files. '
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

    # TODO: create base class for code re-use with other magics

    def __init__(self, **kwargs):
        super(CallLatex, self).__init__(**kwargs)
        # TODO: get settings and pass them on?
        self.caller = latex.Caller()
        # TODO: better heuristics to check if running interactively:
        self.blocking = not self.shell.get_parent()['content']['allow_stdin']
        print('blocking', self.blocking)

    # TODO: %%tikzset magic?

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

    @base.ma.magic_arguments()
    @base.arguments_display_assign_save
    @arguments_preamble
    @magic.line_cell_magic
    def call_latex(self, line, cell=None):
        """Call LaTeX and pass the contents of the current cell.

        """
        args = base.parse_arguments(self.call_latex, line, cell)
        source = base.check_source(args, cell)
        handler = base.Handler(args, self.caller.scheduler)
        results, file_results = self.caller.call(
                source, handler.formats, handler.files, blocking=self.blocking)
        handler.update(results, file_results, blocking=self.blocking)

    @base.ma.magic_arguments()
    @base.arguments_display_assign_save
    @arguments_preamble
    @magic.line_cell_magic
    def call_latex_standalone(self, line, cell=None):
        """Call LaTeX using the *standalone* documentclass."""
        args = base.parse_arguments(self.call_latex_standalone, line, cell)

        # TODO: check argument for loading preamble from file (without storing
        #       in instance)

        source = base.check_source(args, cell)

        # TODO: better name
        handler = base.Handler(args, self.caller.scheduler)

        # TODO: Jinja
        # TODO: store Jinja result to file if requested

        # TODO: don't use Jinja in line magic?

        # TODO: intercept .tex data/files

        format_results, file_results = self.caller.call_standalone(
            source, handler.formats, handler.files, blocking=self.blocking)

        # TODO: add .tex content

        # TODO: allow tex and txt for display
        # TODO: tex: text/latex + dummy HTML
        # TODO: txt: text/plain
        # TODO: disallow txt as file suffix?

        handler.update(format_results, file_results, blocking=self.blocking)

    # TODO: magic for pstricks?

    # TODO: %%call_latex_pgfplot

    @base.ma.magic_arguments()
    @base.arguments_display_assign_save
    @arguments_preamble
    @magic.line_cell_magic
    def call_latex_tikzpicture(self, line, cell=None):
        """Call LaTeX using a *tikzpicture* environment.

        """
        args = base.parse_arguments(self.call_latex_tikzpicture, line, cell)
        source = base.check_source(args, cell)
        handler = base.Handler(args, self.caller.scheduler)
        format_results, file_results = self.caller.call_tikzpicture(
            source, handler.formats, handler.files, blocking=self.blocking)
        handler.update(format_results, file_results, blocking=self.blocking)
