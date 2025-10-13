#!/bin/bash
# Generate example SVG files for the BWT-SVG project
# This script creates various example visualizations

echo "Generating BWT-SVG examples..."

set -ex

# Set background color for all examples
BG_COLOR="--background-color #ffffff"

# Create examples directory if it doesn't exist
mkdir -p examples

# Basic examples
echo "Generating basic examples..."
python3 -m bwt_svg render 'GATTACA$' \
    $BG_COLOR \
    --output examples/gattaca.svg
python3 -m bwt_svg render 'how$now$brown$cow$#' \
    $BG_COLOR \
    --output examples/brown_cow.svg

# Examples with thresholds
echo "Generating examples with thresholds..."
python3 -m bwt_svg render 'GATTACA$' \
    $BG_COLOR \
    --show-thresholds \
    --output examples/gattaca_thresholds.svg
python3 -m bwt_svg render 'how$now$brown$cow$#' \
    $BG_COLOR \
    --show-thresholds \
    --output examples/brown_cow_thresholds.svg

# Examples with MUMs (multi-document)
echo "Generating examples with MUMs..."
python3 -m bwt_svg render 'how$now$brown$cow$#' \
    $BG_COLOR \
    --show-mums \
    --output examples/brown_cow_mums.svg
python3 -m bwt_svg render 'how$now$brown$cow$#' \
    $BG_COLOR \
    --show-mums --show-thresholds \
    --output examples/brown_cow_mums_thresholds.svg

# Examples with guidelines
echo "Generating examples with guidelines..."
python3 -m bwt_svg render 'GATTACA$' \
    $BG_COLOR \
    --show-guidelines \
    --output examples/gattaca_guidelines.svg
python3 -m bwt_svg render 'how$now$brown$cow$#' \
    $BG_COLOR \
    --show-guidelines \
    --output examples/brown_cow_guidelines.svg

# Complex example with all features
echo "Generating complex example with all features..."
python3 -m bwt_svg render 'how$now$brown$cow$#' \
    $BG_COLOR \
    --show-mums --show-thresholds --show-guidelines \
    --output examples/brown_cow_all.svg

# Bigger examples
echo "Generating big examples..."
python3 -m bwt_svg render 'row_row_row_your_boat$row_row_row_your_boat$row_row_row_your_boat$#' \
    $BG_COLOR \
    --show-mums --show-thresholds \
    --output examples/row_row_row_mums_thresholds.svg
python3 -m bwt_svg render 'row_row_row_your_boat$row_row_row_your_boat$row_row_row_your_boat$#' \
    $BG_COLOR \
    --output examples/row_row_row.svg

echo "All examples generated successfully!"
echo "Generated files:"
ls -la examples/*.svg