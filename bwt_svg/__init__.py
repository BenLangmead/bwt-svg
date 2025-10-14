"""
BWT-SVG: Burrows-Wheeler Transform Visualization Package
"""

from bwt import BwtSuite
from svgize import render, print_arrays, main
from .version import __version__
__author__ = "Ben Langmead"
__all__ = ["BwtSuite", "render", "print_arrays", "main"]
