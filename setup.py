from setuptools import setup

__version__ = "1.0.0.0"

setup(
    name='OlxPyApi',
    version=__version__,

    url='https://github.com/Vladislavus1/OlxPyApi',
    author='Vladislavus1',
    author_email='vlydgames@gmail.com',

    py_modules=['parser', 'exceptions'],
    install_requires=[
        'beautifulsoup4==4.12.3',
        'requests==2.31.0'
    ],
)