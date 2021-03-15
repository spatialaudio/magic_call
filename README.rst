The Python package ``magic_call``
=================================

https://magic_call.readthedocs.io/

Python package for passing some text to a chain of external programs and getting
the result(s) back.

For Python version 3.5 and newer.

Includes "magic" functions for IPython, but it can also be used without IPython.

https://github.com/mkrphys/ipython-tikzmagic/

https://github.com/robjstan/tikzmagic

TODO: add to https://github.com/ipython/ipython/wiki/Extensions-Index

What if a program generates two different things at once?
e.g. Score + MIDI, multiple Metapost graphics


SVG to PNG:
inkscape filename.svg --export-png=filename.png

img2pdf:
https://gitlab.mister-muffin.de/josch/img2pdf


Asymptote
^^^^^^^^^

Uses ImageMagick to convert to PNG?

https://github.com/jrjohansson/ipython-asymptote

http://nbviewer.jupyter.org/github/jrjohansson/ipython-asymptote/blob/master/examples/asymptote_magic_examples.ipynb

http://nbviewer.jupyter.org/github/azjps/ipython-asymptote/blob/master/examples/scrape_asymptote_gallery.ipynb

::

    asy -noView -f fmt -o img_file asy_file

There is also http://emmett.ca/PyAsy/.


Graphviz/dot
^^^^^^^^^^^^

https://github.com/cjdrake/ipython-magic

::

    layout_engine='dot'
    cmd = ['dot', '-Tsvg', '-K', layout_engine, '-o', outfile]

https://github.com/tkf/ipython-hierarchymagic


PlantUML
^^^^^^^^

http://plantuml.com/

https://github.com/jbn/IPlantUML


blockdiag.com
^^^^^^^^^^^^^

http://blockdiag.com/en/

https://bitbucket.org/vladf/ipython-diags

https://github.com/innovationOUtside/ipython_magic_blockdiag

SoX?
^^^^

::

    IPython.display.Audio(b'...')._repr_html_()

DTMF example: https://cloudacm.com/?p=2976

csound magic already exists: https://github.com/ldo/ipy_magics

PIC
^^^

https://en.wikipedia.org/wiki/Pic_language

``pic``, ``dpic``, ``tpic2pdftex``, ...

https://pikchr.org/

Lilypond
^^^^^^^^

https://sphinx-notes.github.io/lilypond/
(including audio output generated with TiMidity++)
