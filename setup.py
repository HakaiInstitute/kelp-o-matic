# -*- coding: utf-8 -*-
from setuptools import setup

PACKAGE_NAME = 'hakai-segmentation'
VERSION = '0.1.5'

packages = [
    'hakai_segmentation',
    'hakai_segmentation.data',
    'hakai_segmentation.geotiff_io'
]

package_data = {
    '': ['*']
}

install_requires = [
    'fire>=0.4.0,<0.5.0',
    'numpy>=1.21.2,<2.0.0',
    'torch>=1.10.2,<2.0.0',
    'rasterio>=1.2.10,<2.0.0',
    'torchvision>=0.11.3,<0.12.0',
    'tqdm>=4.62.3,<5.0.0'
]

entry_points = {
    'console_scripts': ['kom = hakai_segmentation.cli:cli']
}

setup_kwargs = {
    'name': PACKAGE_NAME,
    'version': VERSION,
    'description': 'Segmentation Tools for Remotely Sensed RPAS Imagery',
    'author': 'Taylor Denouden',
    'author_email': 'taylordenouden@gmail.com',
    'url': 'https://github.com/hakaiInstitute/hakai-segmentation',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '~=3.7,<3.10',
}

setup(**setup_kwargs)
