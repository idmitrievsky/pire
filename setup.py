# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_ = f.read()

setup(
    name='pire',
    version='0.1.0',
    description='Erlang-style supervisor error handling for Python',
    long_description=readme,
    author='Ivan Dmitrievsky',
    author_email='ivan.dmitrievsky+python@gmail.com',
    url='https://github.com/idmit/pire',
    install_requires=[
        
    ],
    license=license_,
    packages=find_packages(exclude=('tests', 'docs'))
)
