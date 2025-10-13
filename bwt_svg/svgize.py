#!/usr/bin/env python3

"""
This program accepts an input string and produces a rendered SVG image of the
Burrows Wheeler matrix of the string along with several associated structures.
These structures include: the suffix array (SA), longest common prefix (LCP)
array, longest common suffix (LCS) array, last-first mapping (LF), first-last
mapping (FL, also called Psi), inverted SA (ISA, SA), Phi (ϕ), inverse Phi
(ϕ⁻¹), permuted LCP (PLCP) array, and permuted LCS (PLCS) array.

The common prefixes and suffixes that give the LCPs and LCSs are highlighted
with red and blue rectangles respectively in the Burrows-Wheeler matrix.

Compressible stretches of the numeric arrays (e.g. maximal stretches of length
2 or greater where the value repeatedly increases by 1 or decreases by 1) are
also highlighted.

The code is also capable of outputting thresholds (--show-thresholds) and
maximal unique matches (MUMs, via --show-mums).

Example usage:
python3 -m bwt_svg render 'GATTACA$' --show-thresholds
python3 -m bwt_svg render 'how$now$brown$cow$#' --show-mums
python3 -m bwt_svg print 'GATTACA$' --show-thresholds

Note that the use of single quotes is important, otherwise the shell will try
to interpret the dollar signs.

"render" mode outputs an SVG image file to bwt_diagram.svg.  This is a vector
graphics file that can be loaded into Inkscape, Adobe Illustrator, Affinity
Designer, or similar.  If you load the SVG file into those programs, you will
notice that the graphics are bundled into a hierarchy of SVG "groups" ("layers"
in the editing programs), allowing for some parts of the diagram to be
selectively hidden/shown.

"print" mode simply prints the relevant arrays and matrices to stdout.

Author: Ben Langmead
Date: 10/7/2025
"""

import argparse
from contextlib import contextmanager
from .bwt import BwtSuite


@contextmanager
def svg_group(content, transform=None, **attrs):
    """Context manager for SVG groups to reduce boilerplate."""
    attrs_str = ' '.join(f'{k}="{v}"' for k, v in attrs.items())
    transform_str = f' transform="{transform}"' if transform else ''
    content.append(f'  <g{transform_str} {attrs_str}>\n')
    yield
    content.append('  </g>\n')


def render(t, show_mums=False,
           filename="bwt_diagram.svg",
           monospace_font="Consolas",
           label_font="Times",
           background_color=None,
           show_thresholds=False,
           guidelines=False):
    """ Make SVG out of all the BWT structures """
    # Create BwtSuite to compute all arrays
    suite = BwtSuite(t)
    if show_mums:
        mums = suite.find_mums()
    else:
        mums = []
    # Extract arrays from suite
    mysa = suite.sa
    mybwm = suite.bwm
    bwt = suite.bwt
    lcp = suite.lcp
    lcs = suite.lcs
    isa = suite.isa
    phi = suite.phi
    phiinv = suite.phiinv
    plcp = suite.plcp
    plcs = suite.plcs
    lf = suite.lf
    fl = suite.fl
    if show_mums:
        da = suite.da  # Only extract DA when showing MUMs
    off = list(range(len(t)))
    rank = list(range(len(mysa)))
    thresholds = suite.thresholds

    # === LAYOUT CONSTANTS ===
    n = len(t)
    ch_wd = 30            # Character width
    ch_ht = 35            # Character height
    padding = 60          # Canvas padding
    space = 10 if show_mums else 0  # Space between columns
    label_offset = 40     # Space for labels
    label_shift = 15      # Right shift for labels
    threshold_shift = 25 if show_thresholds else 0

    # BWM section positions
    t_right_edge = 2*padding + label_offset + label_shift + len(t) * ch_wd
    bwm_narrow_col_wd = 13

    # IF YOU ADD A NEW ELEMENT to the diagram, please include its contribution
    # here.  This allows us to size the overall image correctly.
    vertical_contributions = [
        {
            't': ch_ht, 'off': ch_ht, 'isa': ch_ht,
            'phi': ch_ht, 'phiinv': ch_ht, 'plcp': ch_ht,
            'plcs': ch_ht, 'extra': ch_ht
        },
        {
            'bwm_total': ch_ht * (len(t) + 3)
        }
    ]

    horizontal_contributions = [
        {
            't_total': t_right_edge + 15 + ch_wd + space
        },
        {
            'da': ch_wd if show_mums else 0,
            'sa': ch_wd,
            'lf': 1.5 * ch_wd,
            'lcs': 1.5 * ch_wd,
            'l': ch_wd * 1.8,
            'bwm': bwm_narrow_col_wd * (len(t) - 2),
            'f': ch_wd * 1.8,
            'lcp': ch_wd * 1.5,
            'fl': ch_wd * 1.5,
            'rank': ch_wd * 1.5,
            'thresholds': (ch_wd * len(suite.alphabet)) if show_thresholds else 0,
            'extra': padding
        }
    ]

    top_height = sum(x for x in vertical_contributions[0].values())
    bottom_height = sum(x for x in vertical_contributions[1].values())

    top_width = sum(x for x in horizontal_contributions[0].values())
    bottom_width = sum(x for x in horizontal_contributions[1].values())

    overall_width = max(top_width, bottom_width)
    overall_height = top_height + bottom_height

    def _svg_header():
        lcp_highlight = "#c3d9ff"
        lcs_highlight = "#ffc3c3"
        lcp_opacity = lcs_opacity = "0.5"

        # To set total width, we need to measure both the width of the
        # horizontally oriented top part (T and friends), but also the width of
        # the vertically oriented part (BWM, F, L and friends).
        
        # The width needs to be something like the maximum of those two widths.

        rect_tag = ""
        if background_color is not None:
            rect_tag = (
                f'  <rect width="{overall_width}" height="{overall_height}" '
                f'fill="{background_color}"/>\n'
            )

        return f'''<?xml version="1.0" encoding="UTF-8"?>
            <svg width="{overall_width}" height="{overall_height}" xmlns="http://www.w3.org/2000/svg">
            {rect_tag}  <defs>
                <style>
                .monospace {{ font-family: '{monospace_font}', monospace; font-size: 18px; }}
                .label {{ font-family: '{label_font}', sans-serif; font-size: 16px; font-weight: bold; }}
                .f-column {{ fill: #e6e6e6; stroke: none; }}
                .l-column {{ fill: #e6e6e6; stroke: none; }}
                .blue-highlight {{ fill: {lcp_highlight}; stroke: none; opacity: {lcp_opacity}; }}
                .blue-outline {{ fill: none; stroke: #000066; stroke-width: 2; opacity: {lcp_opacity}; }}
                .red-highlight {{ fill: {lcs_highlight}; stroke: none; opacity: {lcs_opacity}; }}
                .green-highlight {{ fill: #c3ffc3; stroke: none; opacity: 0.5; }}
                .red-outline {{ fill: none; stroke: #660000; stroke-width: 2; opacity: {lcs_opacity}; }}
                .plum-highlight {{ fill: #f0e6f0; stroke: #8b008b; stroke-width: 1; opacity: 0.6; }}
                .teal-highlight {{ fill: #d3f3f9; stroke: #006666; stroke-width: 1; opacity: 0.6; }}
                .medgray-highlight {{ fill: #e0e0e0; stroke: none; }}
                .lightgray-highlight {{ fill: #f0f0f0; stroke: none; }}
                .bwt-separator {{ stroke: #666; stroke-width: 1; fill: none; }}
                .arrow {{ stroke: #333; stroke-width: 2; fill: none; }}
                .arrow-label {{ font-family: 'Courier New', monospace; font-size: 14px; font-weight: bold; }}
                </style>
            </defs>
            '''

    svg_content = _svg_header()

    if guidelines:
        # Draw a horizontal guideline at 'top_height' from the top across the
        # full width of the image (thicker)
        svg_content += (
            f'  <line x1="0" y1="{top_height}" x2="{overall_width}" y2="{top_height}" '
            f'style="stroke:#bbb;stroke-width:3;stroke-dasharray:4,4"/>\n'
        )
        # Draw a vertical guideline at 'top_width' from the left across the
        # full height of the image (thicker)
        svg_content += (
            f'  <line x1="{top_width}" y1="0" x2="{top_width}" y2="{overall_height}" '
            f'style="stroke:#bbb;stroke-width:3;stroke-dasharray:4,4"/>\n'
        )
        # Draw a vertical *blue* guideline at 'bottom_width' from the left across
        # the full height of the image (thicker and blue)
        svg_content += (
            f'  <line x1="{bottom_width}" y1="0" x2="{bottom_width}" y2="{overall_height}" '
            f'style="stroke:#38f;stroke-width:3;stroke-dasharray:4,4"/>\n'
        )



    mono = 'class="monospace"'
    anc_end = 'text-anchor="end"'
    lab = 'class="label"'

    def _text(x, y, lab, anc, content, spaces=4):
        sp = ' ' * spaces
        return f'{sp}<text x="{x}" y="{y}" {lab} {anc}>{content}</text>\n'

    def _rect(x, y, width, height, class_name, spaces=4):
        sp = ' ' * spaces
        return (f'{sp}<rect x="{x}" y="{y}" width="{width}" '
                f'height="{height}" class="{class_name}"/>\n')

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    # HORIZONTAL ELEMENTS
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    horizontal_label_rhs = 2 * padding
    from_top = 1

    #
    # T
    #
    t_group = []
    with svg_group(t_group, id="T"):
        label_wd = ch_wd  # width of "T" label as multiple of char width
        x = horizontal_label_rhs - label_wd
        t_group.append(_text(x, from_top * ch_ht, lab, anc_end, 'T'))
        for i, char in enumerate(t):
            x = horizontal_label_rhs + (i+0.2) * ch_wd
            t_group.append(_text(x, from_top * ch_ht, mono, '', char))
    svg_content += ''.join(t_group)
    from_top += 1

    #
    # Offsets
    #
    off_group = []
    with svg_group(off_group, id="Offset"):
        label_wd = 1.1 * ch_wd  # width of "Offset" label as multiple of char width
        x = horizontal_label_rhs - label_wd
        off_group.append(_text(x, from_top * ch_ht, lab, anc_end, 'Off'))
        for i, off_val in enumerate(off):
            x = horizontal_label_rhs + (i+0.5) * ch_wd
            off_group.append(_text(x, from_top * ch_ht, lab, anc_end, off_val))
    svg_content += ''.join(off_group)
    from_top += 1

    #
    # ISA
    #
    isa_group = []
    with svg_group(isa_group, id="ISA"):
        label_wd = 1 * ch_wd  # width of "ISA" label as multiple of char width
        x = horizontal_label_rhs - label_wd
        isa_group.append(_text(x, from_top * ch_ht, lab, anc_end, 'ISA'))
        for i, isa_val in enumerate(isa):
            x = horizontal_label_rhs + (i+0.5) * ch_wd
            isa_group.append(_text(x, from_top * ch_ht, lab, anc_end, isa_val))
    svg_content += ''.join(isa_group)
    from_top += 1

    # Helper function to draw highlighting rectangles for maximal intervals
    def _draw_horiz_highlight_rects(
         group, arr, x, y, 
         direction=1,  # +1 for ascending, -1 for descending
         class_name="plum-highlight"
     ):
        i = 0
        rect_x_off = 8
        ht_wd_addend = -5
        while i < len(arr):
            if i == 0 or arr[i] != arr[i-1] + direction:
                start_i = i
                while i + 1 < len(arr) and arr[i+1] == arr[i] + direction:
                    i += 1
                if i - start_i + 1 >= 2:
                    rect_x = x + (start_i-1) * ch_wd + rect_x_off
                    rect_y = y - (ch_ht  * 0.6)
                    rect_ht = ch_ht + ht_wd_addend
                    rect_wd = (i - start_i + 1) * ch_wd + ht_wd_addend
                    group.append(_rect(rect_x, rect_y, rect_wd, rect_ht, class_name))
            i += 1

    horiz_rect_x = horizontal_label_rhs + 0.5 * ch_wd

    #
    # Phi, values and rectangles
    #
    phi_group = []
    with svg_group(phi_group, id="Phi"):
        # Draw Phi highlighting rectangles for maximal intervals where values increase by 1
        phi_rect_group = []
        with svg_group(phi_rect_group, id="PhiRects"):
            _draw_horiz_highlight_rects(phi_rect_group, phi, horiz_rect_x, from_top * ch_ht,
                direction=1, class_name="plum-highlight")
        phi_group.extend(phi_rect_group)

        # Draw phi label and values
        phi_vals_group = []
        with svg_group(phi_vals_group, id="PhiVals"):
            label_wd = 1 * ch_wd  # width of "φ" label as multiple of char width
            x = horizontal_label_rhs - label_wd
            phi_vals_group.append(_text(x, from_top * ch_ht, lab, anc_end, 'φ'))
            for i, phi_val in enumerate(phi):
                x = horizontal_label_rhs + (i+0.5) * ch_wd
                phi_vals_group.append(_text(x, from_top * ch_ht, lab, anc_end, phi_val))
        phi_group.extend(phi_vals_group)
    svg_content += ''.join(phi_group)
    from_top += 1

    #
    # Phi-inverse, values and rectangles
    #
    phiinv_group = []
    with svg_group(phiinv_group, id="PhiInv"):
        # Draw Phi-inverse highlighting rectangles for maximal ascending intervals
        phiinv_rect_group = []
        with svg_group(phiinv_rect_group, id="PhiInvRects"):
            _draw_horiz_highlight_rects(phiinv_rect_group, phiinv, horiz_rect_x, from_top * ch_ht,
                direction=1, class_name="plum-highlight")
        phiinv_group.extend(phiinv_rect_group)

        # Draw phiinv label and values
        phiinv_vals_group = []
        with svg_group(phiinv_vals_group, id="PhiInvVals"):
            label_wd = 1.05 * ch_wd  # width of "φ-1" label as multiple of char width
            x = horizontal_label_rhs - label_wd
            phiinv_vals_group.append(_text(x, from_top * ch_ht, lab, anc_end, 'φ⁻¹'))
            for i, phiinv_val in enumerate(phiinv):
                x = horizontal_label_rhs + (i+0.5) * ch_wd
                phiinv_vals_group.append(_text(x, from_top * ch_ht, lab, anc_end, phiinv_val))
        phiinv_group.extend(phiinv_vals_group)
    svg_content += ''.join(phiinv_group)
    from_top += 1

    #
    # PLCP, values and rectangles
    #
    def _add_plcp():
        plcp_group = []
        with svg_group(plcp_group, id="PLCP"):
            # Draw PLCP highlighting rectangles for maximal descending intervals
            plcp_rect_group = []
            with svg_group(plcp_rect_group, id="PLCPrects"):
                _draw_horiz_highlight_rects(plcp_rect_group, plcp, horiz_rect_x, from_top * ch_ht,
                    direction=-1, class_name="plum-highlight")
            plcp_group.extend(plcp_rect_group)

            # Draw PLCP label and values
            plcp_vals_group = []
            with svg_group(plcp_vals_group, id="PLCPvals"):
                label_wd = 1 * ch_wd  # width of "φ-1" label as multiple of char width
                x = horizontal_label_rhs - label_wd
                plcp_vals_group.append(_text(x, from_top * ch_ht, lab, anc_end, 'PLCP'))
                for i, plcp_val in enumerate(plcp):
                    x = horizontal_label_rhs + (i+0.5) * ch_wd
                    plcp_vals_group.append(_text(x, from_top * ch_ht, lab, anc_end, plcp_val))
            plcp_group.extend(plcp_vals_group)
        return ''.join(plcp_group)

    svg_content += _add_plcp()
    from_top += 1

    #
    # PLCS, values and rectangles
    #
    def _add_plcs():
        plcs_group = []
        with svg_group(plcs_group, id="PLCS"):
            # Draw PLCS highlighting rectangles for maximal ascending intervals
            plcs_rect_group = []
            with svg_group(plcs_rect_group, id="PLCSrect"):
                _draw_horiz_highlight_rects(plcs_rect_group, plcs, horiz_rect_x, from_top * ch_ht,
                    direction=1, class_name="plum-highlight")
            plcs_group.extend(plcs_rect_group)

            plcs_vals_group = []
            with svg_group(plcs_vals_group, id="PLCSvals"):
                # Draw PLCS label and values
                label_wd = 1 * ch_wd  # width of "PLCS" label as multiple of char width
                x = horizontal_label_rhs - label_wd
                plcs_vals_group.append(_text(x, from_top * ch_ht, lab, anc_end, 'PLCS'))
                for i, plcs_val in enumerate(plcs):
                    x = horizontal_label_rhs + (i+0.5) * ch_wd
                    plcs_vals_group.append(_text(x, from_top * ch_ht, lab, anc_end, plcs_val))
            plcs_group.extend(plcs_vals_group)
        return ''.join(plcs_group)

    svg_content += _add_plcs()
    from_top += 1

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    # VERTICAL ELEMENTS
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Calculate threshold width if thresholds are shown
    threshold_width = 0
    if show_thresholds:
        num_threshold_cols = len(suite.alphabet) - 1  # Omit smallest character
        threshold_width = num_threshold_cols * (ch_wd + 5)

    bwm_start_y = 10 * ch_ht + padding - 30
    from_right = 0
    right_hand_reference = overall_width - space

    #
    # DA (if MUMs are shown)
    #
    if show_mums:
        from_right += ch_wd
        da_st_x = right_hand_reference - from_right
        da_lab_y = bwm_start_y - (ch_ht * 1.2)
        da_group = []
        with svg_group(da_group, id="DA"):
            da_group.append(_text(da_st_x, da_lab_y, lab, anc_end, 'DA'))
            for i, da_val in enumerate(da):
                y = da_lab_y + (i+1) * ch_ht
                da_group.append(_text(da_st_x, y, lab, anc_end, da_val))
        svg_content += ''.join(da_group)

    #
    # SA
    #
    def _add_sa():
        sa_group = []
        sa_st_x = right_hand_reference - from_right  # SA starts one char width before right edge
        with svg_group(sa_group, id="SA"):
            sa_lab_y = bwm_start_y - (ch_ht * 1.2)
            sa_group.append(_text(sa_st_x, sa_lab_y, lab, anc_end, 'SA'))
            for i, sa_val in enumerate(mysa):
                y = sa_lab_y + (i+1) * ch_ht
                sa_group.append(_text(sa_st_x, y, lab, anc_end, sa_val))
        return sa_st_x, ''.join(sa_group)

    from_right += ch_wd
    sa_st_x, content = _add_sa()
    svg_content += content

    #
    # LF, values and rectangles
    #
    def _add_lf():
        lf_st_x = right_hand_reference - from_right
        lf_group = []
        with svg_group(lf_group, id="LF"):
            # Draw LF highlighting rectangles for maximal ascending intervals
            lf_rects_group = []
            with svg_group(lf_rects_group, id="LFrects"):
                i = 0
                while i < len(lf):
                    if i == 0 or lf[i] != lf[i-1] + 1:
                        # Find start, end of potential interval
                        start_i = i
                        while i + 1 < len(lf) and lf[i+1] == lf[i] + 1:
                            i += 1
                        if i - start_i + 1 >= 2:
                            nudge_smaller = 4
                            rect_ht = (i - start_i + 1) * ch_ht - nudge_smaller
                            rect_x = lf_st_x - 0.85 * ch_wd
                            rect_y = bwm_start_y + start_i * ch_ht - 0.85 * ch_ht
                            rect_wd = ch_wd - nudge_smaller
                            lf_rects_group.append(
                                _rect(
                                    rect_x + (nudge_smaller / 2),
                                    rect_y + (nudge_smaller / 2),
                                    rect_wd,
                                    rect_ht,
                                    'teal-highlight'
                                )
                            )
                    i += 1
            lf_group.extend(lf_rects_group)

            lf_vals_group = []
            with svg_group(lf_vals_group, id="LF"):
                lf_lab_y = bwm_start_y - (ch_ht * 1.2)
                lf_vals_group.append(_text(lf_st_x, lf_lab_y, lab, anc_end, 'LF'))
                for i, lf_val in enumerate(lf):
                    y = lf_lab_y + (i+1) * ch_ht
                    lf_vals_group.append(_text(lf_st_x, y, lab, anc_end, lf_val))
            lf_group.extend(lf_vals_group)
        return ''.join(lf_group)

    from_right += (1.5 * ch_wd)
    svg_content += _add_lf()

    # We've only increased "from_right" for LF and SA and DA so far.  Now we
    # need to inccrease it for LCS and L, so there's an extra - (2 *1.5 * ch_wd)
    # term below

    # The LCS, L, BWM, F and LCP elwements are somewhat intertwined, so we have
    # to define some of these shape variables here
    bwm_start_x = (
        right_hand_reference - from_right - (2 * 1.5 * ch_wd) - (2 * ch_wd) - (n - 2) * bwm_narrow_col_wd
    )

    #
    # LCS column, values
    #
    def _add_lcs():
        lcs_group = []
        lcs_st_x = right_hand_reference - from_right
        with svg_group(lcs_group, id="LCS"):
            lcs_vals_group = []
            with svg_group(lcs_vals_group, id="LCSvals"):
                lcs_lab_y = bwm_start_y - (ch_ht * 1.2)
                lcs_vals_group.append(_text(lcs_st_x, lcs_lab_y, lab, anc_end, 'LCS'))
                for i, lcs_val in enumerate(lcs):
                    y = lcs_lab_y + (i+1) * ch_ht
                    lcs_vals_group.append(_text(lcs_st_x, y, lab, anc_end, lcs_val))
            lcs_group.extend(lcs_vals_group)
        return ''.join(lcs_group)

    #
    # LCS rectangles on top of the BWM
    #
    def _add_lcs_rects():
        lcs_group = []
        with svg_group(lcs_group, id="LCSrects"):
            y_addend = 5
            lcs_rect1_group = []
            with svg_group(lcs_rect1_group, id="LCSrect1"):
                for i, row in enumerate(mybwm):
                    y = bwm_start_y + (i-1) * ch_ht + y_addend
                    lcs_val = lcs[i] if i < len(lcs) else 0
                    if lcs_val > 0:
                        lcs_width = ch_wd + lcs_val * bwm_narrow_col_wd
                        lcs_offset = (len(row) - lcs_val + 1) * bwm_narrow_col_wd
                        this_lcs_start_x = bwm_start_x + lcs_offset
                        lcs_rect1_group.append(
                            _rect(this_lcs_start_x, y, lcs_width, ch_ht, 'red-highlight'))
            lcs_group.extend(lcs_rect1_group)

            lcs_rect2_group = []
            with svg_group(lcs_rect2_group, id="LCSrect2"):
                for i, row in enumerate(mybwm):
                    y = bwm_start_y + (i-2) * ch_ht + y_addend
                    lcs_val = lcs[i] if i < len(lcs) else 0
                    if lcs_val > 0:
                        lcs_width = ch_wd + lcs_val * bwm_narrow_col_wd
                        lcs_offset = (len(row) - lcs_val + 1) * bwm_narrow_col_wd
                        if i > 0:
                            this_lcs_start_x = bwm_start_x + lcs_offset
                            lcs_rect2_group.append(
                                _rect(this_lcs_start_x, y, lcs_width, ch_ht, 'red-outline'))
            lcs_group.extend(lcs_rect2_group)
        return ''.join(lcs_group)

    from_right += 1.5 * ch_wd
    svg_content += _add_lcs()

    #
    # L column, letters and backgorund rectangle
    #
    def _add_l():
        l_group = []
        with svg_group(l_group, id="L"):
            l_col_x = right_hand_reference - from_right
            l_lab_y = bwm_start_y - (ch_ht * 1.2)
            l_rect_y = l_lab_y + ch_ht * 0.35
            l_group.append(_rect(l_col_x - (ch_wd * 0.45), l_rect_y, ch_wd, n * ch_ht, 'l-column'))
            l_group.append(_text(l_col_x  + ch_wd * 0.2, l_lab_y, lab, anc_end, 'L'))
            for i, row in enumerate(mybwm):
                y = l_lab_y + (i+1) * ch_ht
                lcs_val = lcs[i] if i < len(lcs) else 0
                color = "red" if lcs_val > 0 else "black"
                l_group.append(_text(l_col_x - ch_wd * 0.1, y, mono, f'fill="{color}"', row[-1]))
        return ''.join(l_group)

    from_right += 1.8 * ch_wd
    svg_content += _add_l()

    #
    # BWM, with character coloring according to LCP/LCS.
    # Excluding F and L columns
    #
    def _add_bwm():
        bwm_group = []
        with svg_group(bwm_group, id="BWM"):
            for j in range(len(mybwm[0]) - 1):  # Exclude last character (L column)
                row_i_group = []
                with svg_group(row_i_group, id=f"BWMCol{j}"):
                    for i, row in enumerate(mybwm):
                        y = bwm_start_y + (i-0.2) * ch_ht
                        lcp_val = lcp[i] if i < len(lcp) else 0
                        lcs_val = lcs[i] if i < len(lcs) else 0
                        char = row[j]
                        x = bwm_start_x + j * ch_wd
                        if j != 0:
                            x -= (j - 1) * (ch_wd - bwm_narrow_col_wd)
                        # Determine color: blue for LCP prefix, red for LCS suffix, black otherwise
                        color = "black"
                        if j < lcp_val:
                            color = "blue"
                        elif j >= len(row) - lcs_val and lcs_val > 0:
                            color = "red"
                        row_i_group.append(_text(x, y, mono, f'fill="{color}"', char))
                bwm_group.extend(row_i_group)
        return ''.join(bwm_group)

    svg_content += _add_bwm()
    svg_content += _add_lcs_rects()

    #
    # F column, letters and backgorund rectangle
    #
    def _add_f():
        f_group = []
        with svg_group(f_group, id="F"):
            f_lab_y = bwm_start_y - (ch_ht * 1.2)
            f_lab_x = bwm_start_x + ch_wd * 0.3
            f_rect_y = f_lab_y + ch_ht * 0.35
            f_group.append(_rect(f_lab_x - (ch_wd * 0.45), f_rect_y, ch_wd, n * ch_ht, 'f-column'))
            f_group.append(_text(f_lab_x + ch_wd * 0.2, f_lab_y, lab, anc_end, 'F'))
            for i, row in enumerate(mybwm):
                y = f_lab_y + (i+1) * ch_ht
                lcp_val = lcp[i] if i < len(lcp) else 0
                # Determine color: blue for LCP prefix, black otherwise
                color = "blue" if lcp_val > 0 else "black"
                f_group.append(_text(f_lab_x - ch_wd * 0.1, y, mono, f'fill="{color}"', row[0]))
        return ''.join(f_group)

    svg_content += _add_f()

    #
    # LCP column, values and then rectangles on top of the BWM
    #
    def _add_lcp(lcp_start_x):
        lcp_group = []
        with svg_group(lcp_group, id="LCP"):
            lcp_vals_group = []
            with svg_group(lcp_vals_group, id="LCPvals"):
                lcp_lab_y = bwm_start_y - (ch_ht * 1.2)
                lcp_vals_group.append(_text(lcp_start_x, lcp_lab_y, lab, anc_end, 'LCP'))
                for i, lcp_val in enumerate(lcp):
                    y = lcp_lab_y + (i+1) * ch_ht
                    lcp_vals_group.append(_text(lcp_start_x, y, lab, anc_end, lcp_val))
            lcp_group.extend(lcp_vals_group)
        return ''.join(lcp_group)

    def _add_lcp_rects():
        lcp_group = []
        with svg_group(lcp_group, id="LCPrects"):
            # Draw LCP highlighting rectangles; these are the solid rectangles over the
            # bottom rotation involved in the LCP
            y_addend = 5
            lcp_rect1_group = []
            rect_x = bwm_start_x - 0.1 * ch_wd
            with svg_group(lcp_rect1_group, id="LCPrect1"):
                for i in range(len(mybwm)):
                    y = bwm_start_y + (i-1) * ch_ht + y_addend
                    lcp_val = lcp[i] if i < len(lcp) else 0
                    if lcp_val > 0:
                        lcp_width = lcp_val * ch_wd - (lcp_val - 1) * bwm_narrow_col_wd
                        lcp_rect1_group.append(_rect(rect_x, y, lcp_width, ch_ht, 'blue-highlight'))
            lcp_group.extend(lcp_rect1_group)

            # Draw LCP highlighting rectangles; these are the open rectangles over the
            # top rotation involved in the LCP
            lcp_rect2_group = []
            with svg_group(lcp_rect2_group, id="LCPrect2"):
                for i in range(len(mybwm)):
                    y = bwm_start_y + (i-2) * ch_ht + y_addend
                    lcp_val = lcp[i] if i < len(lcp) else 0
                    if lcp_val > 0:
                        lcp_width = lcp_val * ch_wd - (lcp_val - 1) * bwm_narrow_col_wd
                        if i > 0:
                            lcp_rect2_group.append(
                                _rect(rect_x, y, lcp_width, ch_ht, 'blue-outline'))
            lcp_group.extend(lcp_rect2_group)
        return ''.join(lcp_group)

    lcp_start_x = bwm_start_x - ch_wd - 2 + space - threshold_width + threshold_shift

    svg_content += _add_lcp(lcp_start_x)
    svg_content += _add_lcp_rects()

    #
    # FL: values and rectangles
    #
    def _add_fl(fl_start_x):
        fl_group = []
        with svg_group(fl_group, id="FL"):
            # Draw FL highlighting rectangles for maximal ascending intervals
            fl_rects_group = []
            with svg_group(fl_rects_group, id="FLrects"):
                i = 0
                while i < len(fl):
                    if i == 0 or fl[i] != fl[i-1] + 1:
                        start_i = i
                        while i + 1 < len(fl) and fl[i+1] == fl[i] + 1:
                            i += 1
                        if i - start_i + 1 >= 2:
                            nudge_smaller = 4
                            rect_ht = (i - start_i + 1) * ch_ht - nudge_smaller
                            rect_x = fl_start_x - 0.85 * ch_wd
                            rect_y = bwm_start_y + start_i * ch_ht - 0.85 * ch_ht
                            rect_wd = ch_wd - nudge_smaller
                            fl_rects_group.append(
                                _rect(rect_x + (nudge_smaller / 2), rect_y + (nudge_smaller / 2),
                                rect_wd, rect_ht, 'teal-highlight'))
                    i += 1
            fl_group.extend(fl_rects_group)

            fl_vals_group = []
            with svg_group(fl_vals_group, id="FLvals"):
                fl_lab_y = bwm_start_y - (ch_ht * 1.2)
                fl_vals_group.append(_text(fl_start_x, fl_lab_y, lab, anc_end, 'FL'))
                for i, fl_val in enumerate(fl):
                    y = fl_lab_y + (i+1) * ch_ht
                    fl_vals_group.append(_text(fl_start_x, y, lab, anc_end, fl_val))
            fl_group.extend(fl_vals_group)
        return ''.join(fl_group)

    fl_start_x = lcp_start_x - ch_wd - 15 + space

    svg_content += _add_fl(fl_start_x)

    #
    # Rank array
    #
    def _add_rank(rank_start_x):
        rank_group = []
        with svg_group(rank_group, id="Rank"):
            rank_lab_y = bwm_start_y - (ch_ht * 1.2)
            rank_group.append(_text(rank_start_x, rank_lab_y, lab, anc_end, 'Rank'))
            for i, rank_val in enumerate(rank):
                y = rank_lab_y + (i+1) * ch_ht
                rank_group.append(_text(rank_start_x, y, lab, anc_end, rank_val))
        return ''.join(rank_group)

    rank_start_x = fl_start_x - ch_wd - 20 + space
    svg_content += _add_rank(rank_start_x)


    #
    # Thresholds columns (if requested)
    #
    if show_thresholds:
        threshold_group = []
        with svg_group(threshold_group, id="Thresholds"):
            threshold_start_x = fl_start_x + ch_wd + threshold_shift  # Start after FL column
            threshold_chars = suite.alphabet[1:]  # Omit F character
            for j, char in enumerate(threshold_chars):
                threshold_x = threshold_start_x + (j+0.8) * ch_wd
                threshold_group.append(
                    _text(threshold_x, bwm_start_y - 1.25*ch_ht, lab, anc_end, char))
                # Draw rectangles for consecutive stretches of '=', '^', and 'v'
                i = 0
                while i < len(thresholds[char]):
                    if thresholds[char][i] in ['=', '^', 'v']:
                        # Find the end of this stretch
                        start_i = i
                        char_type = thresholds[char][i]
                        while i < len(thresholds[char]) and thresholds[char][i] == char_type:
                            i += 1
                        # Draw rectangle for this stretch
                        if i - start_i >= 1:
                            nudge_smaller = 4
                            rect_y = bwm_start_y + start_i * ch_ht - (0.8*ch_ht) + nudge_smaller/2
                            rect_height = (i - start_i) * ch_ht - nudge_smaller
                            rect_width = ch_wd - nudge_smaller
                            rect_x = threshold_x - (0.7*ch_wd) + nudge_smaller/2
                            fill_color = {
                                '=': "medgray-highlight",    # Medium gray
                                '^': "lightgray-highlight",  # Light gray
                                'v': "lightgray-highlight"   # Light gray
                            }[char_type]
                            threshold_group.append(
                                _rect(rect_x, rect_y, rect_width, rect_height, fill_color))
                    else:
                        i += 1

                # Draw threshold values
                for i, threshold_val in enumerate(thresholds[char]):
                    y = bwm_start_y + (i-0.3) * ch_ht
                    # Replace characters with Unicode arrows
                    display_val = threshold_val
                    if threshold_val == '^':
                        display_val = '↑'  # Unicode up arrow
                    elif threshold_val == 'v':
                        display_val = '↓'  # Unicode down arrow
                    threshold_group.append(_text(threshold_x, y, lab, anc_end, display_val))
        svg_content += ''.join(threshold_group)

    #
    # Separator lines between BWT runs
    #
    bwm_group = []
    with svg_group(bwm_group, id="RunLines"):
        for i in range(len(mybwm)):
            y = bwm_start_y + i * ch_ht
            if i > 0 and bwt[i] != bwt[i-1]:
                line_x1 = rank_start_x - 1.8 * ch_wd
                line_x2 = sa_st_x + ch_wd
                line_y = y - (0.85*ch_ht)
                bwm_group.append(
                    f'  <line x1="{line_x1}" y1="{line_y}" '
                    f'x2="{line_x2}" y2="{line_y}" '
                    f'class="bwt-separator"/>\n'
                )
    svg_content += ''.join(bwm_group)

    #
    # MUMs
    #
    def _add_mums():
        mum_group = []
        with svg_group(mum_group, id="MUMs"):
            for i in range(len(mybwm)):
                y = bwm_start_y + i * ch_ht
                # Draw MUM highlighting rectangles for this row
                for mum_start, mum_end in mums:
                    if mum_start == i:
                        # Highlight only the LCP column for MUM ranges
                        height = (
                            ch_ht * (mum_end - mum_start - 1) +
                            ((ch_ht) * (mum_end - mum_start - 1.5))
                        )
                        mum_group.append(
                            _rect(
                                lcp_start_x, y - ch_ht,
                                ch_wd, height, 'green-highlight')
                        )
                        break  # One MUM box per row
        return ''.join(mum_group)

    svg_content += _add_mums()

    svg_content += '</svg>'

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg_content)

    print(f"SVG saved to {filename}")


def print_arrays(t, show_thresholds=False, show_mums=False):
    """Print all BWT-related arrays for the given text."""
    suite = BwtSuite(t)
    print(f"Text: {t}")
    print(f"Length: {len(t)}")
    print()
    print("Suffix Array (SA):")
    print(suite.sa)
    print()
    print("Inverse Suffix Array (ISA):")
    print(suite.isa)
    print()
    print("Burrows-Wheeler Transform (BWT):")
    print(suite.bwt)
    print()
    print("Longest Common Prefix (LCP):")
    print(suite.lcp)
    print()
    print("Longest Common Suffix (LCS):")
    print(suite.lcs)
    print()
    print("Permuted LCP (PLCP):")
    print(suite.plcp)
    print()
    print("Permuted LCS (PLCS):")
    print(suite.plcs)
    print()
    print("LF mapping:")
    print(suite.lf)
    print()
    print("FL mapping:")
    print(suite.fl)
    print()
    print("Phi (φ):")
    print(suite.phi)
    print()
    print("Phi-inverse (φ⁻¹):")
    print(suite.phiinv)
    
    # Print MUMs if requested and there are multiple documents
    if show_mums and suite.num_docs > 1:
        print()
        print("Maximal Unique Matches (MUMs):")
        mums = suite.find_mums()
        if mums:
            for i, (start, end) in enumerate(mums):
                print(f"  MUM {i+1}: SA[{start}:{end}] (length {end-start})")
                # Show the actual suffixes for this MUM range
                for j in range(start, end):
                    suffix_start = suite.sa[j]
                    suffix = suite.t[suffix_start:]
                    print(f"    SA[{j}] = {suffix_start}: {suffix}")
        else:
            print("  No MUMs found")
    
    if show_thresholds:
        print()
        print("Thresholds:")
        for char in suite.alphabet:
            print(f"  {char}: {suite.thresholds[char]}")


def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(description='BWT analysis and visualization tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Print subcommand
    print_parser = subparsers.add_parser('print', help='Print all BWT-related arrays')
    print_parser.add_argument('text', help='Input text (must end with terminator)')
    print_parser.add_argument('--show-thresholds', action='store_true',
                              help='Show threshold arrays for each alphabet character')
    print_parser.add_argument('--show-mums', action='store_true',
                              help='Show Maximal Unique Matches (MUMs)')

    # Render subcommand
    render_parser = subparsers.add_parser('render', help='Generate SVG visualization')
    render_parser.add_argument('text', help='Input text (must end with terminator)')
    render_parser.add_argument('--output', '-o', default='bwt_diagram.svg',
                              help='Output SVG filename (default: bwt_diagram.svg)')
    render_parser.add_argument('--background-color', default=None,
                              help='Background color (e.g., #ffffff) or None for transparent')
    render_parser.add_argument('--monospace-font', default='Courier New',
                              help='Monospace font family (default: Courier New)')
    render_parser.add_argument('--label-font', default='Times',
                              help='Label font family (default: Times)')
    render_parser.add_argument('--show-mums', action='store_true',
                              help='Show MUMs')
    render_parser.add_argument('--show-thresholds', action='store_true',
                              help='Show threshold arrays for each alphabet character')
    render_parser.add_argument('--show-guidelines', action='store_true',
                              help='Show guidelines in the SVG output')

    args = parser.parse_args()

    if args.command == 'print':
        print_arrays(args.text, show_thresholds=args.show_thresholds, show_mums=args.show_mums)
    elif args.command == 'render':
        render(args.text,
               filename=args.output,
               background_color=args.background_color,
               monospace_font=args.monospace_font,
               label_font=args.label_font,
               show_mums=args.show_mums,
               show_thresholds=args.show_thresholds,
               guidelines=args.show_guidelines)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
