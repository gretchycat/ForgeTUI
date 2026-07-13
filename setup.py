#!/usr/bin/python3
from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='forgetui',
    version='0.0.4',
    license='GPL3',
    url='https://github.com/gretchycat/ForgeTUI',
    author='Gretchen Maculo',
    author_email='gretchen.maculo@gmail.com',
    description='python tui framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'libAnsiScreen',
    ],
    tests_require=[
    ],
)
