# $ python setup.py build_ext --inplace

from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize(['converter.pyx', 'determiner.pyx', 'distributor.pyx', 'generator.pyx', 'isolator.pyx', 'lowercase.pyx', 'proposer.pyx', 'reader.pyx', 'remover.pyx', 'sorter.pyx', 'writer.pyx'])
)