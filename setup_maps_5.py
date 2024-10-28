from setuptools import setup
from setuptools.command.install import install
import os, shutil, platform, sys

package = "uniquebible"

# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
setup(
    name=f"{package}_maps_5",
    version="0.0.3",
    python_requires=">=3.8, <3.13",
    description="Map images for UniqueBible App. Read more at https://github.com/eliranwong/UniqueBible",
    long_description="Map images for UniqueBible App. Read more at https://github.com/eliranwong/UniqueBible",
    author="Eliran Wong",
    author_email="support@marvel.bible",
    packages=[
        #f"{package}.htmlResources.images",
        #f"{package}.htmlResources.images.exlbl", # size too large
        f"{package}.htmlResources.images.exlbl_largeHD_3", # size too large
        #f"{package}.htmlResources.images.exlbl_large", # size too large
    ],
    package_data={
        #f"{package}.htmlResources.images": ["*.*"],
        #f"{package}.htmlResources.images.exlbl": ["*.*"], # size too large
        f"{package}.htmlResources.images.exlbl_largeHD_3": ["*.*"], # size too large
        #f"{package}.htmlResources.images.exlbl_large": ["*.*"], # size too large
    },
    license="GNU General Public License (GPL)",
    #install_requires=[],
    #extras_require={},
    #entry_points={},
    keywords="bible scripture na28 bsha hebrew greek ai marvelbible biblebento uba uniquebible",
    url="https://www.uniquebible.app/",
    project_urls={
        "Source": "https://github.com/eliranwong/UniqueBible",
        "Tracker": "https://github.com/eliranwong/UniqueBible/issues",
        "Documentation": "https://github.com/eliranwong/UniqueBible/wiki",
        "Funding": "https://www.paypal.me/MarvelBible",
    },
    classifiers=[
        # Reference: https://pypi.org/classifiers/

        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
