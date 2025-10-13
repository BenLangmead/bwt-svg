# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project strives to adhere to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2025-10-13

### Added
- MUM support in print mode with --show-mums flag
- Guidelines in render mode with --show-guidelines flag; useful for debugging
- Example generation script + more examples

### Changes
- Improved layout to make things fit across various input sizes

## [0.1.0] - 2025-10-07

### Added
- Burrows-Wheeler Transform visualization with SVG output
- Support for multiple BWT-related data structures:
  - Suffix Array (SA) and Inverse Suffix Array (ISA)
  - Burrows-Wheeler Transform (BWT) and Burrows-Wheeler Matrix (BWM)
  - Longest Common Prefix (LCP) and Longest Common Suffix (LCS) arrays
  - Last-First (LF) and First-Last (FL) mappings
  - Phi (φ) and Phi-inverse (φ⁻¹) functions
  - Permuted LCP (PLCP) and Permuted LCS (PLCS) arrays
- Visual highlighting of common prefixes (blue) and suffixes (red)
- Visual highlighting compressible portions of numeric arrays
- Threshold visualization for character-specific LCP analysis (preliminary)
- Maximal Unique Match (MUM) detection and highlighting (preliminary)
- Layered SVG output for selective viewing in graphics editors
- Command-line interface with render and print modes
- Pytest suite for BwtSuite

### Technical Details
- Pure Python implementation using only standard library
- No external dependencies
- MIT License
