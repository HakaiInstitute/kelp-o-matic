# -*- coding: utf-8 -*-
import re

from setuptools import find_packages, setup

PACKAGE_NAME = 'hakai_segmentation'
SOURCE_DIRECTORY = 'hakai_segmentation'
SOURCE_PACKAGE_REGEX = re.compile(rf'^{SOURCE_DIRECTORY}')

packages = find_packages(where=SOURCE_DIRECTORY)
package_dirs = {'': 'hakai_segmentation'}

install_requires = [
    'fire>=0.4.0,<0.5.0',
    'numpy>=1.22.2,<2.0.0',
    'rasterio>=1.2.10,<2.0.0',
    'torch>=1.10.2,<2.0.0',
    'torchvision>=0.11.3,<0.12.0',
    'tqdm>=4.62.3,<5.0.0'
]

entry_points = {
    'console_scripts': [
        'kom = hakai_segmentation.cli:cli'
    ]
}

setup_kwargs = {
    'name': PACKAGE_NAME,
    'version': '0.1.0rc2',
    'description': 'Segmentation Tools for Remotely Sensed RPAS Imagery',
    'long_description': 'Hakai Segmentation\n==================\n\n.. image:: https://github.com/tayden/hakai-segmentation/actions/workflows/test.yml/badge.svg\n  :target: https://github.com/tayden/hakai-segmentation/actions/workflows/test.yml\n  :alt: Test Status\n\n.. image:: https://readthedocs.org/projects/hakai-segmentation/badge/?version=latest\n  :target: https://hakai-segmentation.readthedocs.io/en/latest/?badge=latest\n  :alt: Documentation Status\n\nSegmentation tools for remotely sensed RPAS imagery\n\n\n`Read the Docs <http://hakai-segmentation.readthedocs.io/>`_\n',
    'author': 'Taylor Denouden',
    'author_email': 'taylordenouden@gmail.com',
    'url': 'https://github.com/hakaiInstitute/hakai-segmentation',
    'packages': packages,
    'package_dir': package_dirs,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.10',
}

setup(**setup_kwargs)
