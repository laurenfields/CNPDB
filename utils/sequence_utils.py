# -*- coding: utf-8 -*-
"""Sequence-handling utilities shared by the app, QC, and curation scripts."""
from __future__ import annotations

import re

from utils.peptide_properties import STANDARD_AA

# Matches inline lowercase modification annotations such as "(d)" used to mark
# D-amino acids, e.g. "QVF(d)DQACK...".
INLINE_MOD_RE = re.compile(r"\([a-z]\)")


def clean_sequence(seq: str) -> str:
    """Strip FASTA header lines and whitespace, returning a bare upper-case
    sequence. Mirrors the helper used on the Tools page."""
    lines = str(seq).strip().splitlines()
    clean_lines = [line.strip() for line in lines if not line.startswith(">")]
    return "".join(clean_lines).upper()


def strip_inline_modifications(seq: str) -> str:
    """Remove inline modification annotations like ``(d)`` from a sequence,
    leaving only residue letters. Use before computing length/mass/FASTA."""
    return INLINE_MOD_RE.sub("", str(seq))


def inline_modifications(seq: str) -> list[str]:
    """Return any inline modification annotations found in a sequence."""
    return INLINE_MOD_RE.findall(str(seq))


def calculate_percent_identity(seqA: str, seqB: str) -> float:
    """Percent identity across the aligned columns of two equal-length strings."""
    if not seqA:
        return 0.0
    matches = sum(1 for a, b in zip(seqA, seqB) if a == b)
    return matches / len(seqA) * 100


def is_valid_sequence(seq: str, allow_inline_mods: bool = True) -> bool:
    """True if ``seq`` contains only standard amino-acid letters (optionally
    after stripping inline modification annotations)."""
    s = strip_inline_modifications(seq) if allow_inline_mods else str(seq)
    s = s.upper()
    return len(s) > 0 and not (set(s) - STANDARD_AA)


def nonstandard_residues(seq: str, allow_inline_mods: bool = True) -> set[str]:
    """Set of characters in ``seq`` that are not standard amino acids."""
    s = strip_inline_modifications(seq) if allow_inline_mods else str(seq)
    return set(s.upper()) - STANDARD_AA
