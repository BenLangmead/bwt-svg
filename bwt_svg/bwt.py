#!/usr/bin/env python3

"""
Functionality for building the BWT and various other arrays and functions that
are useful both in text space (Phi, Phi-inverse, ISA, PLCP, etc) and in lex
space (SA, LF, LCP, LCS, etc).

No attempt is made to make these methods efficient.  This code is intended to
be simple and used only for examples that are small enough to be displayed.

Author: Ben Langmead
Date: 10/7/2025
"""

def lf_fl_from_sa_isa(sa, isa):
    """ Use steps through SA and ISA to derife LF and FL """
    n = len(sa)
    assert n == len(isa)
    lf_pair = list((isa[((sa[i] or n)-1)], i) for i in range(len(sa)))
    lf = list(map(lambda x: x[0], lf_pair))
    lf_pair.sort()
    return lf, list(map(lambda x: x[1], lf_pair))


def lcp_from_t_sa(t, sa):
    """ Typical quadratic-time algorithm with random T access """
    def _lcp(t, i, j):
        lcp_len = 0
        while i + lcp_len < len(t) and \
              j + lcp_len < len(t) and \
              t[i+lcp_len] == t[j+lcp_len]:
            lcp_len += 1
        return lcp_len
    lcp_arr = [0]
    for i in range(1, len(sa)):
        lcp_arr.append(_lcp(t, sa[i-1], sa[i]))
    return lcp_arr


def lcs_from_bwm(bwm):
    """ Compute LCS from BWM """
    def _lcs(s1, s2):
        lcs_len = 0
        len_i, len_j = len(s1), len(s2)
        while (lcs_len < len_i and lcs_len < len_j and
               s1[len_i - lcs_len - 1] == s2[len_j - lcs_len - 1]):
            lcs_len += 1
        return lcs_len
    lcs_arr = [0]
    for i in range(1, len(bwm)):
        lcs_arr.append(_lcs(bwm[i-1], bwm[i]))
    return lcs_arr


def invert(array):
    """ Invert offsets/values for given array """
    n = len(array)
    inverted = [0] * n
    for i, s in enumerate(array):
        inverted[s] = i
    return inverted


def permute(array, order):
    """ Return elements of array in order of order """
    return [array[order[i]] for i in range(len(array))]


def thresholds_in_gap(lcps):
    """ Compute up/down/equal jumps according to min LCPs """
    cum_min_fw, cum_min_bw = [], []
    thresholds = []
    for i, lcp in enumerate(lcps):
        cum_min_fw.append(lcp if i == 0 else min(cum_min_fw[-1], lcp))
    for i, lcp in enumerate(lcps[::-1]):
        cum_min_bw.append(lcp if i == 0 else min(cum_min_bw[-1], lcp))
    for i, (fw, bw) in enumerate(zip(cum_min_fw, cum_min_bw[::-1])):
        if fw == bw:
            thresholds.append('=')
        else:
            thresholds.append('v' if fw < bw else '^')
    # Create a run-length-compressed version of thresholds
    rlthresholds = []
    if thresholds:
        prev = thresholds[0]
        count = 1
        for val in thresholds[1:]:
            if val == prev:
                count += 1
            else:
                rlthresholds.append((prev, count))
                prev = val
                count = 1
        rlthresholds.append((prev, count))
    assert len(rlthresholds) <= 3
    return thresholds[:-1], rlthresholds


class BwtSuite:
    """A class that computes all BWT-related arrays for a given text."""

    def __init__(self, t):
        """Compute all BWT-related arrays for text t."""
        assert t[-1] < min(t[:-1])
        self.t = t
        self.n = n = len(t)
        self.sa = self._compute_sa()
        self.isa = invert(self.sa)
        self.da, self.num_docs = self._compute_da()
        self.alphabet = list(sorted(set(t)))
        self.bwm, self.bwt = self._compute_bwm_and_bwt()
        self.lcp = lcp_from_t_sa(t, self.sa)
        self.lcs = lcs_from_bwm(self.bwm)
        self.plcp = permute(self.lcp, self.isa)
        self.plcs = permute(self.lcs, self.isa)
        self.lf, self.fl = lf_fl_from_sa_isa(self.sa, self.isa)
        self.phi = list(self.sa[((self.isa[i] or n)-1)] for i in range(n))
        self.phiinv = list(
            self.sa[(-1 if (self.isa[i] == n-1) else self.isa[i]) + 1] for i in range(n)
        )
        self.thresholds = self._compute_thresholds()

    def _compute_sa(self):
        """Compute suffix array."""
        satups = sorted([(self.t[i:], i) for i in range(self.n)])
        return list(map(lambda x: x[1], satups))

    def _compute_thresholds(self):
        thresholds = {}
        for c in self.alphabet:
            thresholds[c] = []
            before_first_c_run = True
            in_c_run = False
            lcps = []
            for i, bwtc in enumerate(self.bwt):
                if before_first_c_run:
                    if bwtc == c:
                        in_c_run = True
                        before_first_c_run = False
                        thresholds[c].append(' ')
                    else:
                        thresholds[c].append('v')
                    continue
                if in_c_run:
                    if bwtc != c:
                        in_c_run = False
                        lcps = [self.lcp[i]]
                    else:
                        thresholds[c].append(' ')
                else:
                    if bwtc == c:
                        in_c_run = True
                        lcps.append(self.lcp[i])
                        thresh, _ = thresholds_in_gap(lcps)
                        thresholds[c].extend(thresh)
                        thresholds[c].append(' ')
                        lcps = []
                    else:
                        lcps.append(self.lcp[i])
            for _ in range(len(lcps)):
                thresholds[c].append('^')
        return thresholds


    def _compute_bwm_and_bwt(self):
        """Compute Burrows-Wheeler Matrix and BWT (last column of BWM)."""
        bwm, bwt_chars = [], []
        for i in self.sa:
            row = self.t[i:] + self.t[:i]
            bwm.append(row)
            bwt_chars.append(row[-1])
        return bwm, ''.join(bwt_chars)

    def _compute_da(self):
        """Compute DA array."""
        da = [0] * len(self.t)
        doc_id = 0
        for i, char in enumerate(self.t):
            if char in ('$', '#'):
                da[self.isa[i]] = doc_id
                doc_id += 1
            else:
                da[self.isa[i]] = doc_id
        return da, doc_id

    def find_mums(self):
        """
        Find maximal unique matches (assuming $ separator between sequences)
        Returns a list of tuples (start, end) of ranges in the SA that are MUMs
        """
        mums = []
        for i in range(self.n - self.num_docs):
            lcp = min(self.lcp[i + 1 : i + self.num_docs])
            lcp_interval = lcp > self.lcp[i] and lcp > self.lcp[i + self.num_docs]
            bwt_distinct = len(set(self.bwt[i : i + self.num_docs])) != 1
            da_distinct = len(set(self.da[i : i + self.num_docs])) == self.num_docs
            if lcp_interval and bwt_distinct and da_distinct:
                mums.append((i, i + self.num_docs))
        return mums
