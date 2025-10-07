#!/usr/bin/env python3

"""
Tests for the BWT functions.

Author: Ben Langmead
Date: 9/15/2025
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from bwt_svg.bwt import BwtSuite


def test_bwt_1():
    """Test basic BWT functionality."""
    # 0 6 $abaaba
    # 1 5 a$abaab
    # 2 2 aaba$ab
    # 3 3 aba$aba
    # 4 0 abaaba$
    # 5 4 ba$abaa
    # 6 1 baaba$a
    suite = BwtSuite('abaaba$')
    assert suite.bwt == 'abba$aa'


def test_sa_and_isa_1():
    """Test basic SA and ISA functionality."""
    suite = BwtSuite('abaaba$')
    assert suite.sa == [6, 5, 2, 3, 0, 4, 1]
    assert suite.isa == [4, 6, 2, 3, 5, 1, 0]


def test_bwt_permutation_1():
    """Test whether we get the right BWT permutation"""
    suite = BwtSuite('abaaba$')
    # The perm array is computed as: perm[(sa[i] or n)-1] = i
    # This is the original logic from isa_perm_from_sa
    n = len(suite.sa)
    perm = [0] * n
    for i, s in enumerate(suite.sa):
        perm[(s or n)-1] = i
    assert perm == [6, 2, 3, 5, 1, 0, 4]


def test_lf_fl_from_sa_isa_1():
    """Test LF mapping"""
    suite = BwtSuite('abaaba$')
    # i F  L LF[i]
    # 0 $  a     1
    # 1 a  b     5
    # 2 a  b     6
    # 3 a  a     2
    # 4 a  $     0
    # 5 b  a     3
    # 6 b  a     4
    assert suite.lf == [1, 5, 6, 2, 0, 3, 4]
    assert suite.fl == [4, 0, 3, 5, 6, 1, 2]


def test_phi_phiinv_from_sa_isa_1():
    """Test Phi and Phi-1 """
    suite = BwtSuite('abaaba$')
    # $              6
    # a $            5
    # a a b a $      2
    # a b a $        3
    # a b a a b a $  0
    # b a $          4
    # b a a b a $    1
    assert suite.phi == [3, 4, 5, 2, 0, 6, 1]
    assert suite.phiinv == [4, 6, 3, 0, 1, 2, 5]


def test_lcp_from_t_sa_1():
    """Test LCP from T and SA"""
    suite = BwtSuite('abaaba$')
    assert suite.lcp == [0, 0, 1, 1, 3, 0, 2]


def test_gattacat_3():
    t = 'gattacat$gattacgt$attcgt$#'
    suite = BwtSuite(t)
    assert suite.sa == [25, 24, 17, 8, 4, 13, 6, 1, 10, 18, 5, 21, 14, 0, 9, 22,
                        15, 23, 16, 7, 3, 12, 20, 2, 11, 19]
    assert suite.lcp == [0, 0, 1, 1, 0, 2, 1, 2, 5, 3, 0, 1, 4, 0, 6, 1, 3, 0, 2, 2,
                         1, 3, 1, 1, 4, 2]


def test_bwt_suite_1():
    """Test BwtSuite class with basic functionality."""
    suite = BwtSuite('abaaba$')
    
    # Test that all arrays are computed correctly
    assert suite.sa == [6, 5, 2, 3, 0, 4, 1]
    assert suite.bwt == 'abba$aa'
    assert suite.isa == [4, 6, 2, 3, 5, 1, 0]
    assert suite.lf == [1, 5, 6, 2, 0, 3, 4]
    assert suite.fl == [4, 0, 3, 5, 6, 1, 2]
    assert suite.phi == [3, 4, 5, 2, 0, 6, 1]
    assert suite.phiinv == [4, 6, 3, 0, 1, 2, 5]
    assert suite.lcp == [0, 0, 1, 1, 3, 0, 2]
    
    # Test that BWM is computed correctly
    expected_bwm = ['$abaaba', 'a$abaab', 'aaba$ab', 'aba$aba', 
                    'abaaba$', 'ba$abaa', 'baaba$a']
    assert suite.bwm == expected_bwm


def test_bwt_suite_2():
    """Test BwtSuite class with larger example."""
    t = 'gattacat$gattacgt$attcgt$#'
    suite = BwtSuite(t)
    
    # Test that all arrays have the correct length
    assert len(suite.sa) == len(t)
    assert len(suite.bwt) == len(t)
    assert len(suite.bwm) == len(t)
    assert len(suite.isa) == len(t)
    assert len(suite.lcp) == len(t)
    assert len(suite.lcs) == len(t)
    assert len(suite.lf) == len(t)
    assert len(suite.fl) == len(t)
    assert len(suite.phi) == len(t)
    assert len(suite.phiinv) == len(t)
    
    # Test that permuted arrays are computed
    assert len(suite.plcp) == len(suite.lcp)
    assert len(suite.plcs) == len(suite.lcs)
    assert len(suite.lf) == len(suite.sa)
    assert len(suite.fl) == len(suite.sa)
