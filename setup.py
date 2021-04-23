from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='sierra-pywr',
    # cmdclass = {'build_ext': build_ext},
    # ext_modules = cythonize("/sierra/base_parameters/*.pyx", compiler_dirctives={'language_level': 3}),
    ext_modules = cythonize(["*.pyx"])
    ext_modules = cythonize("/sierra-cython/*")
    # zip_safe = False,
)