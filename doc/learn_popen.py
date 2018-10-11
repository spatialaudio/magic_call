from pathlib import Path as _Path
import subprocess as _subprocess
import tempfile as _tempfile

_DVI_NAME = 'dvi-job'
_PDF_NAME = 'pdf-job'
_SOURCE_NAME = 'source.tex'

formats = 'pdf', 'svg', 'png'

source = open('mini.tex').read()

def run_latex(source, formats):

    proc = {}
    data = {}

    with _tempfile.TemporaryDirectory() as cwd:
        cwd = _Path(cwd)
        (cwd / _SOURCE_NAME).write_text(source)

        def run(*args):
            return _subprocess.Popen(
                args,
                cwd=cwd,
                stdout=_subprocess.PIPE,
                stderr=_subprocess.STDOUT,
                universal_newlines=True,
            )

        # TODO: configurable command(s)?

        # TODO: print LaTeX code (plus terminal messages) on error?
        # TODO: print contents (and name) of temp directory on error?

        if 'svg' in formats:
            proc['dvi'] = run(
                'lualatex', '--halt-on-error', '--output-format=dvi',
                '--jobname', _DVI_NAME, _SOURCE_NAME)

        if {'pdf', 'png'}.intersection(formats):
            proc['pdf'] = run(
                'lualatex', '--halt-on-error', '--output-format=pdf',
                '--jobname', _PDF_NAME, _SOURCE_NAME)

        if 'dvi' in proc and (proc['dvi'].wait() != 0 or
                not (cwd / _DVI_NAME).with_suffix('.dvi').is_file()):
            raise RuntimeError(
                'Error creating DVI file:\n' + proc['dvi'].stdout.read())

        if 'svg' in formats:
            proc['svg'] = run('dvisvgm', _DVI_NAME)

        if 'pdf' in proc and (proc['pdf'].wait() != 0 or
                not (cwd / _PDF_NAME).with_suffix('.pdf').is_file()):
            raise RuntimeError(
                'Error creating PDF file:\n' + proc['pdf'].stdout.read())

        if 'png' in formats:
            proc['png'] = run(
                'convert', _PDF_NAME + '.pdf', _PDF_NAME + '.png')

        if 'pdf' in formats:
            data['pdf'] = (cwd / _PDF_NAME).with_suffix('.pdf').read_bytes()

        if 'svg' in proc and (proc['svg'].wait() != 0 or
                not (cwd / _DVI_NAME).with_suffix('.svg').is_file()):
            # NB: dvisvgm doesn't report errors for non-existing input files!
            raise RuntimeError(
                'Error creating SVG file:\n' + proc['svg'].stdout.read())

        if 'svg' in formats:
            # NB: This is stored in text mode
            data['svg'] = (cwd / _DVI_NAME).with_suffix('.svg').read_text()

        if 'png' in proc and (proc['png'].wait() != 0 or
                not (cwd / _PDF_NAME).with_suffix('.png').is_file()):
            raise RuntimeError(
                'Error creating PNG file:\n' + proc['png'].stdout.read())

        if 'png' in formats:
            data['png'] = (cwd / _PDF_NAME).with_suffix('.png').read_bytes()

    return data

run_latex(source, formats)
