from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='sierra-pywr',
    # cmdclass = {'build_ext': build_ext},
    ext_modules = cythonize("/sierra/base_parameters/*.pyx", compiler_directives={'language_level': 3}),
    zip_safe = False,
)