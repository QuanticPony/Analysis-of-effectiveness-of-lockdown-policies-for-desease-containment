from setuptools import setup
from Cython.Build import cythonize

setup(
    name='my_simulation',
    ext_modules=cythonize("cython/cppmain.py"),
    zip_safe=False,
)