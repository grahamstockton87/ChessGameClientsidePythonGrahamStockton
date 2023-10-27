#  Copyright (c) 2023.

from setuptools import setup

with open('requirements.txt') as f:
    required_packages = f.read().splitlines()
    print(required_packages)

setup(
    name='chess-game',
    version='1.0',
    packages=[''],
    install_requires=required_packages,  # Set the install_requires parameter
    url='',
    license='',
    author='Graham Stockton',
    author_email='grahamstockton6@gmail.com',
    description='Python Chess Game with C++ Server'
)

