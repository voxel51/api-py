from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='voxel51-api',  # Required

    version='1.0',  # Required

    description='Python client library for accessing the Voxel51 ETA API.',

    long_description=long_description,  # Optional

    url='http://api.voxel51.com',  # Optional

    author='Voxel51, LLC',  # Optional

    author_email='david@voxel51.com',  # Optional

    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='voxel51 api video analytics',  # Optional

    py_modules=["voxel51/api"],

    install_requires=['requests'],  # Optional
)
