from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

NAME = 'eyes_soatra'
VERSION = '100.0.0'
DESCRIPTION = 'Eyes'

AUTHOR_NAME = 'Soatra'
AUTHOR_EMAIL = 'johnsoatra@gmail.com'

# Setting up
setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'requests',
        'lxml',
        'jellyfish',
        'translate',
    ],
    keywords=[
        'python',
        'crawler',
        'scanner',
        'requests',
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)