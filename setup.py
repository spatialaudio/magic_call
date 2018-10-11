from setuptools import setup

setup(
    name='magic_call',
    version='0.0.0',
    package_dir={'': 'src'},
    packages=['magic_call'],
    author='Matthias Geier',
    author_email='Matthias.Geier@gmail.com',
    description='Python package for passing some text to a chain of external '
                'programs and getting the result(s) back',
    long_description=open('README.rst').read(),
    license='MIT',
    keywords='IPython LaTeX'.split(),
    url='https://magic_call.readthedocs.io/',
    platforms='any',
    classifiers=[
        'Framework :: IPython',
        'Framework :: Jupyter',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
    zip_safe=True,
)
