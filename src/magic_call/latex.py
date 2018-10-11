"""Tools for Calling LaTeX from Python.

http://magic_call.readthedocs.io/

"""
# https://ipython.readthedocs.io/en/latest/config/custommagics.html

from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor
import os as _os
from pathlib import Path as _Path
import shlex as _shlex
import shutil as _shutil
import subprocess as _subprocess
import sys as _sys
import tempfile as _tempfile

# https://doc.sagemath.org/html/en/reference/misc/sage/misc/latex.html
# https://github.com/sagemath/sage/blob/master/src/sage/misc/latex.py
# https://github.com/brendano/runlatex/blob/master/runlatex.py
# https://vog.github.io/texcaller/
# https://github.com/mbr/latex

# %config InlineBackend.figure_formats=['svg']

_BASENAME = 'magic_call'
DEFAULT_COMMANDS = [
('tex2dvi', 'latex --halt-on-error --output-format=dvi --jobname={}'),
('tex2xdv', ''),   # TODO: show in docs
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
('tex2pdf', 'latex --halt-on-error --output-format=pdf --jobname={}'),
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


class LatexCaller:

    # TODO: DOC: "tex." is not part of the chain, it's implied
    # TODO: DOC: the "best" chain is not the one with the fewest stages,
    #       but the one that needs to go least far in the list of commands.
    # TODO: DOC: Explicit tool chain can be specified: ps.pdf.png, dvi.png
    # TODO: DOC: How to decide between pdf.svg and dvi.svg?
    def __init__(self, commands=()):
        """

        The order of *commands* matters!

        """
        self.preambles = []
        self.commands = list(commands)
        for name, command in DEFAULT_COMMANDS:
            if not any(k == name for k, v in self.commands):
                self.commands.append((name, command))
        # TODO: specify number of threads?

    def call_latex(self, source, formats=(), files=()):
        if isinstance(formats, str):
            formats = [formats]
            single_format = True
        else:
            single_format = False
        chains = self._formats_and_files2chains(formats, files)
        results = self._run_all(source.encode(), chains)
        if single_format:
            results, = results
        return results

    def call_latex_standalone(self, source, formats=(), files=(), tikz=False):
        document = '\n'.join([
            standalone_header(tikz=tikz),
            *self.preambles,
            r'\begin{document}',
            source,
            r'\end{document}',
        ])
        return self.call_latex(document, formats, files)

    def call_latex_tikzpicture(self, source, formats=(), files=()):
        tikzpicture = '\n'.join([
            r'\begin{tikzpicture}',
            source,
            r'\end{tikzpicture}',
        ])
        return self.call_latex_standalone(
            tikzpicture, formats, files, tikz=True)

    def get_default_chains(self):
        """Populate dictionary of default tool chains by suffix.

        This works through the current list of `commands` to calculate
        the "best" tool chain for each possible suffix.

        """
        partial_chains = []
        chains = {}
        for name, command in self.commands:
            src, _, dst = name.partition('2')
            if {src, dst} & {'', '.'}:
                raise ValueError('Invalid command name: ' + repr(name))
            src = '.' + src
            dst = '.' + dst
            if dst in chains:
                pass  # There is already an earlier chain to create "dst"
            elif src == '.tex':
                assert dst not in chains
                chains[dst] = [dst]
                old_partial_chains = partial_chains
                partial_chains = []
                for chain in old_partial_chains:
                    if chain[0] == dst:
                        if chain[-1] in chains:
                            continue  # There is already an earlier chain
                        # *Move* chain from old_partial_chains to chains
                        chains[chain[-1]] = chain
                    elif chain[-1] == dst:
                        # Current command is better than this partial chain
                        continue
                    else:
                        partial_chains.append(chain)
            elif src in chains:
                assert dst not in chains
                chains[dst] = chains[src] + [dst]
            else:
                partial_chains.append([src, dst])
                for chain in partial_chains.copy():
                    if chain[-1] == src:
                        partial_chains.append(chain + [dst])
                    if chain[0] == dst:
                        partial_chains.append([src] + chain)
        return chains

    def _run_all(self, source_bytes, chains):
        # Group by first format in chain, typically pdf or dvi
        groups = {}
        for i, chain in enumerate(chains):
            groups.setdefault(chain[0], []).append((i, chain[1:]))
        tasks = []
        indices = []  # Positions in the original list of formats

        def func(task):
            suffix, ch = task
            return self._run_latex_and_more(source_bytes, suffix, ch)

        for dst, numbered_chains in groups.items():
            idx, chains = zip(*numbered_chains)
            tasks.append((dst,  chains))
            indices.append(idx)

        executor = _ThreadPoolExecutor(max_workers=len(tasks))
        nested_results = executor.map(func, tasks)

        flat_results = []
        for idx, result in zip(indices, nested_results):
            flat_results.extend(zip(idx, result))
        flat_results.sort()  # Restore original order of formats
        return [data for _, data in flat_results]

    def _run_latex_and_more(self, source_bytes, dst, chains):
        with _tempfile.TemporaryDirectory(prefix=_BASENAME) as cwd:
            cwd = _Path(cwd)
            self._run_latex(cwd, source_bytes, _BASENAME, dst)
            # TODO: use return value for something?
            results = self._handle_chains(cwd, _BASENAME, dst, chains)
            # TODO: copy/move the files somewhere if requested?
        return results

    def _run_latex(self, cwd, source_bytes, basename, dst):

        # TODO: are multiple LaTeX runs ever needed?
        #       if yes, the user can use latexmk as tex2pdf?

        command = self._get_command('tex2' + dst[1:], basename)
        result_name = basename + dst

        env = _os.environ.copy()
        # NB: The final ':' makes LaTeX also look in the default paths
        env['TEXINPUTS'] = _os.pathsep.join([
            # NB: Appending '//' would make LaTeX search recursively
            _os.getcwd(),
            env.get('TEXINPUTS', ''),
        ])

        # TODO: use creationflags=0x08000000 on Windows (CREATE_NO_WINDOW)?
        process = _subprocess.run(
            _shlex.split(command),
            input=source_bytes,
            cwd=cwd,
            env=env,
            stdout=_subprocess.PIPE,
            stderr=_subprocess.STDOUT)
        if process.returncode or not (cwd / result_name).is_file():
            raise RuntimeError('\n'.join([
                'Error running {!r} to create {!r} from this source:'.format(
                    command, result_name),
                source_bytes.decode(),
                '#' * 80,
                process.stdout.decode(),
            ]))
        # TODO: return something?

    def _handle_chains(self, cwd, basename, suffix, chains):
        generated_file = cwd / (basename + suffix)
        target_files = []
        all_results = []

        # Group by first suffix in chain (for non-empty chains)
        groups = {}
        for i, chain in enumerate(chains):
            if not chain:
                # Chain is finished, load data from file
                if suffix == '.svg':
                    data = generated_file.read_text()
                else:
                    data = generated_file.read_bytes()
                # NB: If the same suffix is requested multiple times, the same
                #     file is read and appended multiple times
                all_results.append((i, data))
                continue
            if len(chain) == 1 and isinstance(chain[0], _Path):
                # NB: We are moving files away, but we do it below when
                #     everything that might depend on them is already done.
                target_files.append(chain[0])
                continue
            groups.setdefault(chain[0], []).append((i, chain[1:]))
        tasks = []
        indices = []

        def func(task):
            dst, chains = task
            return self._run_converter(cwd, basename, suffix, dst, chains)

        for dst, numbered_chains in groups.items():
            idx, chains = zip(*numbered_chains)
            tasks.append((dst, chains))
            indices.append(idx)

        if tasks:
            executor = _ThreadPoolExecutor(max_workers=len(tasks))
            nested_results = executor.map(func, tasks)
            for idx, result in zip(indices, nested_results):
                all_results.extend(zip(idx, result))
            all_results.sort()  # Restore original order of chains

        # TODO: Exception might be raised on Windows if target file exists!?!

        # NB: It's quite unlikely that a user requests multiple file names for
        #     the exact same file type, but we have to handle it anyway:
        for target_file in target_files[:-1]:
            _shutil.copy2(generated_file, target_file)
        # The last (and probably only) file can be moved:
        for target_file in target_files[-1:]:
            # NB: This is done after all converters are done with the file:
            _shutil.move(generated_file, target_file)
        return [data for _, data in all_results]

    def _run_converter(self, cwd, basename, src, dst, chains):
        srcfile = basename + src
        # NB: The destination file has both suffixes!
        dstfile = srcfile + dst
        command = self._get_command(src[1:] + '2' + dst[1:], srcfile, dstfile)
        process = _subprocess.run(
            _shlex.split(command),
            cwd=cwd,
            stdout=_subprocess.PIPE,
            stderr=_subprocess.STDOUT)
        if process.returncode or not (cwd / dstfile).is_file():
            raise RuntimeError('\n'.join([
                'Error running {!r} to create {!r}:'.format(command, dstfile),
                process.stdout.decode(),
            ]))
        return self._handle_chains(cwd, srcfile, dst, chains)

    def _formats_and_files2chains(self, formats, files):
        """Convert formats to full tool chains."""
        # NB: Calling this every time is horribly inefficient, but the list of
        # commands is typically very short, so it doesn't take much time.
        default_chains = self.get_default_chains()

        def expand_chain(chain):
            first, chain = chain[0], chain[1:]
            if first == '.tex':
                raise ValueError('Don\'t use "tex" in format specification')
            try:
                prefix = default_chains[first]
            except KeyError:
                raise RuntimeError(
                    'No programs found to generate {!r} files'.format(first))
            return prefix + chain

        chains = []
        for format in formats:
            suffixes = ['.' + s for s in format.split('.')]
            if set(suffixes) & {'.'}:
                raise ValueError('Invalid format: ' + repr(format))
            chains.append(expand_chain(suffixes))
        for file in files:
            file = _Path(file)
            # Extract formats from given files
            suffixes = file.suffixes
            if not suffixes or set(suffixes) & {'.'}:
                raise ValueError('Invalid suffix in file: ' + repr(file.name))
            chains.append(expand_chain(suffixes + [file]))
        return chains

    def _get_command(self, name, *args):
        try:
            command = next(v for k, v in self.commands if k == name)
        except StopIteration:
            raise RuntimeError('Command not found: ' + name)
        return command.format(*args)


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
