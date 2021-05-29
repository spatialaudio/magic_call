from subprocess import check_output

extensions = [
    'nbsphinx',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_last_updated_by_git',
]

autoclass_content = 'init'
autodoc_member_order = 'bysource'

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
}

authors = 'Matthias Geier'
project = 'magic_call'

try:
    today = check_output(['git', 'show', '-s', '--format=%ad', '--date=short'])
    today = today.decode().strip()
    release = check_output(['git', 'describe', '--tags', '--always'])
    release = release.decode().strip()
except Exception:
    today = '<unknown date>'
    release = '<unknown>'

default_role = 'any'

html_theme = 'insipid'
html_title = project + ', version ' + release
html_permalinks_icon = '§'
html_favicon = 'favicon.svg'
html_domain_indices = False
html_show_copyright = False
html_copy_source = False

latex_elements = {
    'papersize': 'a4paper',
    'printindex': '',
}
latex_documents = [(
    'index', 'magic_call.tex', 'The Python package \\texttt{magic\\_call}',
    authors, 'howto')]
latex_show_urls = 'footnote'
latex_domain_indices = False
