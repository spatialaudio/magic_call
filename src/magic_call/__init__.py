"""

https://magic_call.readthedocs.io/

"""
from ._base import *

__version__ = '0.0.0'

# TODO: allow generic calls to user-defined tools?


def load_ipython_extension(ipython):
    """Hook function for IPython.

    All available extensions can be loaded at the same time via
    ``%load_ext magic_call` or individually with
    ``%load_ext magic_call.latex` etc.
    The extensions can also be configured to be autoloaded by IPython at
    startup time.

    If you don't want to use IPython magics, just ignore this function.

    """
    # TODO: Don't load modules, provide %%call_generic?
    from importlib import import_module
    submodules = '.latex',
    for module in submodules:
        import_module(module, 'magic_call').load_ipython_extension(ipython)
