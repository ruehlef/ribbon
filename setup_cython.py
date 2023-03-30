import setuptools
from Cython.Build import cythonize

setuptools.setup(
    ext_modules=cythonize("src/rw.pyx")
)
