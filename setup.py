#!/usr/bin/env python

from setuptools import setup
import luthor

setup(name='luthor',
      version=luthor.__version__,
      description='A simple library to parse XML',
      author='bbrodriges',
      author_email='bender.rodriges@gmail.com',
      url='https://github.com/bbrodriges/luthor',
      requires=['lxml'],
      py_modules=["luthor"],
    )
