from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'sierra-pywr',
  ext_modules = cythonize(["*.pyx"]),
)