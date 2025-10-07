#!/usr/bin/env python3
"""
Setup script for bwt-svg package.
"""

import os
import re
from setuptools import setup, find_packages

# Read version from version.py without importing
def get_version():
    """ Get version from version.py """
    version_file = os.path.join(os.path.dirname(__file__), 'bwt_svg', 'version.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'__version__ = ["\']([^"\']*)["\']', content)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string")

__version__ = get_version()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bwt-svg",
    version=__version__,
    author="Ben Langmead",
    author_email="ben.langmead@gmail.com",
    description="Burrows-Wheeler Transform visualization with SVG output",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/langmead/bwt-svg",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "bwt-svg=bwt_svg.svgize:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
