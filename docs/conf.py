import os
import sys
# Path to the python directory containing the package
sys.path.insert(0, os.path.abspath('../native_fisher_py/python'))

project = 'native-fisher-py'
copyright = '2026, falk'
author = 'falk'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

autodoc_mock_imports = ["native_fisher_py.native_fisher_py_backend", "native_fisher_py_backend"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
