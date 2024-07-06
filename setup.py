from setuptools import setup

from parser import __version__

setup(
    name='OlxPyApi',
    version=__version__,

    url='https://github.com/Vladislavus1/OlxPyApi',
    author='Vladislavus1',
    author_email='vlydgames@gmail.com',

    py_modules=['parser', 'exceptions'],
    install_requires=[
        'bs4==0.0.2',
        'requests==2.31.0'
    ],
)