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

        displays = []
        for format in formats:
            displays.append(base.publish_empty(format))

        flat_formats, sizes = base.flatten_formats(formats)

        results, file_results = self.caller.call(
                cell, flat_formats, files=(), blocking=False)

        results = base.unflatten_results(results, sizes, self.caller)

        for disp, output, format in zip(displays, results, formats):
            output.add_done_callback(base.publish_data(disp, format))

    @base.arguments_default
    @base.arguments_display_save
    @magic.line_cell_magic
    def call_latex_standalone(self, line, cell=None):
        """Call LaTeX using the *standalone* documentclass.

        """

        # TODO: argument for loading preamble from file (without storing in
        #       instance)

        args = base.parse_arguments(self.call_latex_standalone, line, cell)

        if cell is None:
            # TODO
            return line

        formats = base.check_display(args)

        # TODO: display data and file names intermixed in the given order?

        format_handles = []
        for format in formats:
            format_handles.append(base.publish_empty(format))

        # TODO writing vs. overwriting?

        files = args.save
        file_handles = []
        for file in files:
            file_handles.append(base.publish_creating_file(file))

        # TODO: Jinja
        # TODO: store Jinja result to file if requested

        flat_formats, nested_lengths = base.flatten_formats(formats)

        format_results, file_results = self.caller.call_standalone(
            cell, flat_formats, files, blocking=False)

        format_results = base.unflatten_results(
                format_results, nested_lengths, self.caller)

        for handle, future, format in zip(format_handles, format_results,
                                          formats):
            future.add_done_callback(base.publish_data(handle, format))

        for handle, future in zip(file_handles, file_results):
            future.add_done_callback(base.publish_file(handle))

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

        displays = []
        for format in formats:
            displays.append(base.publish_empty(format))

        flat_formats, sizes = base.flatten_formats(formats)

        format_results, file_results = self.caller.call_tikzpicture(
            cell, flat_formats, files=(), blocking=False)

        format_results = base.unflatten_results(format_results, sizes,
                                                self.caller)

        # TODO: store LaTeX content of environment (with Jinja replacements)

        for disp, output, format in zip(displays, format_results, formats):
            output.add_done_callback(base.publish_data(disp, format))

        # TODO: return something? probably for debugging?
