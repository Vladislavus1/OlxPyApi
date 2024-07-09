from setuptools import setup, find_packages

__version__ = "0.0.2alpha"

setup(
    name='OlxPyApi',
    version=__version__,

    url='https://github.com/Vladislavus1/OlxPyApi',
    author='Vladislavus1',
    author_email='vlydgames@gmail.com',

    packages=find_packages(),
    install_requires=[
        'beautifulsoup4==4.12.3',
        'requests==2.31.0'
    ],
)