# -*- coding: utf-8 -*-
"""Pure, importable peptide physicochemical-property functions for cNPDB.

This module is the single source of truth for property calculations. The
Streamlit Tools page (``pages/2_Tools.py``) and the QC / curation scripts both
import from here so the app, the database, and the tests can never drift apart.

No Streamlit or I/O imports live here on purpose -- everything is a pure
function so it can be unit-tested in isolation.
"""
from __future__ import annotations

from Bio.SeqUtils.ProtParam import ProteinAnalysis

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
STANDARD_AA = set("ACDEFGHIKLMNPQRSTVWY")

# Residues counted as hydrophobic for "% Hydrophobic Residue".
HYDROPHOBIC_RESIDUES = set("AILMFWYV")

# Boman index scale (kcal/mol), Boman 2003.
BOMAN_SCALE = {
    'A': 0.17, 'C': 0.41, 'D': -0.07, 'E': -0.07, 'F': 1.13,
    'G': 0.01, 'H': 0.17, 'I': 1.31, 'K': 0.99, 'L': 1.25,
    'M': 1.27, 'N': 0.42, 'P': -0.45, 'Q': 0.58, 'R': 0.81,
    'S': 0.13, 'T': 0.14, 'V': 1.09, 'W': 2.65, 'Y': 1.61,
}

# Monoisotopic residue masses (Da) for the 20 standard amino acids.
MONOISOTOPIC_RESIDUE_MASS = {
    'G': 57.02146, 'A': 71.03711, 'S': 87.03203, 'P': 97.05276,
    'V': 99.06841, 'T': 101.04768, 'C': 103.00919, 'L': 113.08406,
    'I': 113.08406, 'N': 114.04293, 'D': 115.02694, 'Q': 128.05858,
    'K': 128.09496, 'E': 129.04259, 'M': 131.04049, 'H': 137.05891,
    'F': 147.06841, 'R': 156.10111, 'Y': 163.06333, 'W': 186.07931,
}
MONO_WATER = 18.010565
PROTON = 1.007276

# Common PTM monoisotopic mass shifts (Da). Keys are matched case-insensitively
# as substrings of the free-text PTM column, so "Pyro-Glu from E" matches
# "pyro-glu from e".
PTM_MASS_SHIFT = {
    'amidation': -0.984016,
    'sulfation': 79.956815,
    'phospho': 79.966331,
    'acetyl': 42.010565,
    'oxidation': 15.994915,
    'pyro-glu from e': -18.010565,
    'pyro-gln from q': -17.026549,
    'pyroglutamate': -17.026549,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def normalize_sequence(sequence: str) -> str:
    """Upper-case and strip whitespace/newlines from a raw sequence string."""
    return str(sequence).upper().replace(" ", "").replace("\n", "")


def aliphatic_index(sequence: str) -> float:
    """Ikai (1980) aliphatic index expressed on a 0-100+ scale."""
    seq = normalize_sequence(sequence)
    length = len(seq)
    if length == 0:
        return 0.0
    nA, nV, nI, nL = seq.count('A'), seq.count('V'), seq.count('I'), seq.count('L')
    return (nA + 2.9 * nV + 3.9 * (nI + nL)) / length * 100


def boman_index(sequence: str) -> float:
    seq = normalize_sequence(sequence)
    length = len(seq)
    if length == 0:
        return 0.0
    return sum(BOMAN_SCALE.get(aa, 0) for aa in seq) / length


def percent_hydrophobic(sequence: str) -> float:
    seq = normalize_sequence(sequence)
    length = len(seq)
    if length == 0:
        return 0.0
    count = sum(1 for aa in seq if aa in HYDROPHOBIC_RESIDUES)
    return count / length * 100


def ptm_mass_shift(ptm: str) -> tuple[float, list[str]]:
    """Sum the monoisotopic shift for a free-text PTM description.

    Returns ``(total_shift_da, unrecognized_tokens)``. Tokens are split on
    ``;`` and ``,``. Unrecognized tokens are returned so callers can decide
    whether a mass discrepancy is explained.
    """
    text = str(ptm).strip().lower()
    if text in ("", "nan", "none"):
        return 0.0, []
    total = 0.0
    unknown: list[str] = []
    for token in [t.strip() for t in text.replace(",", ";").split(";")]:
        if not token:
            continue
        matched = False
        for key, shift in PTM_MASS_SHIFT.items():
            if key in token:
                total += shift
                matched = True
                break
        if not matched:
            unknown.append(token)
    return total, unknown


def monoisotopic_mass(sequence: str, ptm: str = "", charged: bool = True) -> float:
    """Theoretical monoisotopic mass of a peptide.

    ``charged=True`` returns the singly-protonated [M+H]+ m/z (the convention
    stored in the cNPDB "Monoisotopic Mass" column); ``False`` returns the
    neutral monoisotopic mass. Raises ``ValueError`` on non-standard residues.
    """
    seq = normalize_sequence(sequence)
    bad = set(seq) - STANDARD_AA
    if bad:
        raise ValueError(f"non-standard residue(s) {sorted(bad)} in {seq!r}")
    mass = sum(MONOISOTOPIC_RESIDUE_MASS[aa] for aa in seq) + MONO_WATER
    mass += ptm_mass_shift(ptm)[0]
    if charged:
        mass += PROTON
    return mass


# ---------------------------------------------------------------------------
# Public API used by the Tools page
# ---------------------------------------------------------------------------
def calculate_properties(sequence: str) -> dict:
    """Compute the full property panel shown on the cNPDB Tools page.

    Mirrors the calculation used across the database. ``Molecular Weight`` is
    the average mass from BioPython; monoisotopic [M+H]+ is available via
    :func:`monoisotopic_mass`.
    """
    seq = normalize_sequence(sequence)
    analysis = ProteinAnalysis(seq)
    length = len(seq)

    instability_val = analysis.instability_index()
    instability_status = "stable" if instability_val < 40 else "unstable"

    return {
        "Peptide Sequence": seq,
        "Molecular Weight": round(analysis.molecular_weight(), 3),
        "Length": length,
        "GRAVY Score": round(analysis.gravy(), 3),
        "% Hydrophobic Residue": round(percent_hydrophobic(seq), 2),
        "Instability Index": f"{round(instability_val, 3)} ({instability_status})",
        "Isoelectric Point (pI)": round(analysis.isoelectric_point(), 2),
        "Net Charge (pH 7.0)": round(analysis.charge_at_pH(7.0), 2),
        "Aliphatic Index": round(aliphatic_index(seq), 2),
        "Boman Index": round(boman_index(seq), 3),
    }
