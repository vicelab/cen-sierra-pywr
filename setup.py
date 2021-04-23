from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension

# extensions = [Extension("*", ["*.pyx"])]

setup(
    name='sierra-pywr',
    ext_modules = cythonize("sierra_cython/models/{}", ["*.pyx"]),
    zip_safe = False,
)