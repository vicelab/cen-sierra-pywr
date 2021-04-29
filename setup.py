from distutils.core import setup
from Cython.Build import cythonize

main_path = './sierra_cython'
base_paraemters_path = '{}/base_parameters/*.pyx'.format(main_path)
models_path = '{}/models/'.format(main_path)

merced_path = '{}/merced/_parameters/*.pyx'.format(models_path)
tuolumne_path = '{}/tuolumne/_parameters/*.pyx'.format(models_path)
usj_path = '{}/upper_san_joaquin/_parameters/*.pyx'.format(models_path)
stanislaus_path = '{}/stanislaus/_parameters/*.pyx'.format(models_path)

setup(
  name = 'sierra-pywr',
  ext_modules = cythonize([
    base_paraemters_path,
    merced_path,
    tuolumne_path,
    usj_path,
    stanislaus_path,
  ]),
)