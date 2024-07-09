from setuptools import setup, find_packages
import pathlib

__version__ = "0.0.2"

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name='OlxPyApi',
    version=__version__,

    url='https://github.com/Vladislavus1/OlxPyApi',
    author='Vladislavus1',
    author_email='vlydgames@gmail.com',

    description='This package simplifies the extraction of data from OLX websites.',
    long_description=README,
    long_description_content_type='text/markdown',

    packages=find_packages(),
    install_requires=[
        'beautifulsoup4==4.12.3',
        'requests==2.31.0',
        'lxml==5.2.2'
    ],
)