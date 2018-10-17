import os
from subprocess import check_output
import sys

sys.path.insert(0, os.path.abspath('../src'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

autoclass_content = 'init'
autodoc_member_order = 'bysource'

authors = 'Matthias Geier'
project = 'magic_call'
copyright = '2018, ' + authors

try:
    today = check_output(['git', 'show', '-s', '--format=%ad', '--date=short'])
    today = today.decode().strip()
    release = check_output(['git', 'describe', '--tags', '--always'])
    release = release.decode().strip()
except Exception:
    today = '<unknown date>'
    release = '<unknown>'

master_doc = 'index'
default_role = 'any'

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'collapse_navigation': False,
}
html_title = project + ', version ' + release
html_domain_indices = False
html_show_sourcelink = True

latex_elements = {
    'papersize': 'a4paper',
    'printindex': '',
}
latex_documents = [(
    'index', 'magic_call.tex', 'The Python package \\texttt{magic\\_call}',
    authors, 'howto')]
latex_show_urls = 'footnote'
latex_domain_indices = False
