"""Tools for Calling LaTeX from Python.

https://magic_call.readthedocs.io/

"""
import os as _os

from . import _base

# TODO: are multiple LaTeX runs ever needed?
#       if yes, the user can use latexmk?

DEFAULT_COMMANDS = [
    ('dvi', 'latex --halt-on-error --output-format=dvi --jobname={}'),
    ('xdv', ''),   # TODO: show in docs
    ('dvi2svg', ' '.join([
        # NB: dvisvgm doesn't support lualatex yet!
        # NB: dvisvgm doesn't report errors for non-existing input files!

        # --no-fonts (characters as paths)
        # --bbox=preview (cf. [preview] option to standalone?)
        # --bbox=A4
        # --bbox=letter etc.
        'dvisvgm',
        #'--bbox=dvi',  # border too large
        #'--bbox=none',  # useless
        '--bbox=papersize',  # no border on "normal" article
        #'--bbox=preview',  # same as default?
        #'--bbox=A4',
        #'--no-fonts',
        '--font-format=woff,autohint',
        '--exact',  # TODO: does this cause a runtime penalty?
        '{}',
        '--output={}',
    ])),
    ('pdf', 'latex --halt-on-error --output-format=pdf --jobname={}'),
    ('pdf2png', 'convert {} {}'),
    # TODO: pdf2svg
    #('pdf2svg', 'pdf2svg {} {}'),
    # TODO dvipng
    # dvipng options: --picky (don't ignore warnings)
    #                 -T bbox, -T tight, -D 150 (density)
]


# TODO: pstricks option, border option?
def standalone_header(tikz=False):
    #class options
    #dvisvgm,
    #%border=0pt,  % default 0pt

    options = []
    if tikz:
        options.append('tikz')
        #options.append('dvisvgm')
    if options:
        options = '[' + ','.join(options) + ']'
    else:
        options = ''

    return r"""\documentclass%(options)s{standalone}
\ifdefined\pdfpagewidth
\else
  \let\pdfpagewidth\pagewidth
  \let\pdfpageheight\pageheight
\fi
""" % locals()


class Caller(_base.Caller):
    """LaTeX Caller.

    """

    def __init__(self, commands=()):
        commands = list(commands)
        for name, command in DEFAULT_COMMANDS:
            if not any(k == name for k, v in commands):
                commands.append((name, command))

        env = _os.environ.copy()
        # NB: The final ':' makes LaTeX also look in the default paths
        env['TEXINPUTS'] = _os.pathsep.join([
            # NB: Appending '//' would make LaTeX search recursively
            _os.getcwd(),
            env.get('TEXINPUTS', ''),
        ])
        _base.Caller.__init__(self, commands, env=env)

    def call_latex_standalone(self, source, formats=(), files=(), tikz=False,
                              blocking=True):
        document = '\n'.join([
            standalone_header(tikz=tikz),
            *self.preambles,
            r'\begin{document}',
            source,
            r'\end{document}',
        ])
        return self.call(document, formats, files, blocking)

    def call_latex_tikzpicture(self, source, formats=(), files=(),
                               blocking=True):
        tikzpicture = '\n'.join([
            r'\begin{tikzpicture}',
            source,
            r'\end{tikzpicture}',
        ])
        return self.call_latex_standalone(
            tikzpicture, formats, files, tikz=True, blocking=blocking)


def load_ipython_extension(ipython):
    """Hook function for IPython.

    The extension can be loaded via ``%load_ext magic_call.latex` or
    it can be configured to be autoloaded by IPython at startup time.

    If you don't want to use IPython magics, just ignore this function.

    """
    from . import _magic_latex
    ipython.register_magics(_magic_latex.CallLatex)


if __name__ == '__main__':
    # TODO: convert from file/stdin to file(s)/stdout
    # TODO: select full/standalone/tikzpicture/...
    # TODO: configuration file (ini file?) to specify programs
    # TODO: flag to list programs
    print('TODO: implement me!')
