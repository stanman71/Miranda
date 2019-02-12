# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='SmartHome',
    version='0.5.0',
    description='Package to get smart home functions',
    long_description=readme,
    author='Martin Stan',
    author_email='martin.stan@gmx.de',
    url='https://github.com/stanman71/Python_Projects/SmartHome',
    license=license,
    packages=find_packages(exclude=('arduino', 'static', 'templates'))
)
