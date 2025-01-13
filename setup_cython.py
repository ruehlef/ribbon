import setuptools
from Cython.Build import cythonize

# setuptools.setup(
#     ext_modules=cythonize("src/rw.pyx")
# )

# need to add language level for python 3.11 or higher
setuptools.setup(
    ext_modules=cythonize(
        "src/rw.pyx",  # Path to your Cython file
        language_level="3",  # Set language level explicitly to match Python 3.x
    )
)