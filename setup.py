# -*- coding: utf-8 -*-
from setuptools import setup

PACKAGE_NAME = 'kelp-o-matic'
VERSION = '0.5.4rc1'

packages = [
    'kelp_o_matic',
    'kelp_o_matic.data',
    'kelp_o_matic.geotiff_io'
]

package_data = {
    '': ['*']
}

install_requires = [
    'numpy~=1.24',
    'rasterio~=1.3',
    'torchvision~=0.15',
    'torch~=2.0',
    'tqdm~=4.65',
    'typer~=0.7',
]

entry_points = {
    'console_scripts': ['kom = kelp_o_matic.cli:cli']
}

setup_kwargs = {
    'name': PACKAGE_NAME,
    'version': VERSION,
    'description': 'Segmentation Tools for Remotely Sensed RPAS Imagery',
    'author': 'Taylor Denouden',
    'author_email': 'taylordenouden@gmail.com',
    'url': 'https://github.com/HakaiInstitute/kelp-o-matic',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '~=3.8,<=3.11',
}

setup(**setup_kwargs)
