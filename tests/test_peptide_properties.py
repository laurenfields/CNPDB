"""Unit tests for utils.peptide_properties."""
import math

import pytest

from utils import peptide_properties as pp


def test_normalize_sequence_strips_and_uppercases():
    assert pp.normalize_sequence(" ys fgl\n") == "YSFGL"


def test_scales_are_complete():
    for aa in pp.STANDARD_AA:
        assert aa in pp.BOMAN_SCALE
        assert aa in pp.MONOISOTOPIC_RESIDUE_MASS


@pytest.mark.parametrize("seq,length", [("YSFGL", 5), ("A", 1), ("RFLRFG", 6)])
def test_calculate_properties_length(seq, length):
    assert pp.calculate_properties(seq)["Length"] == length


def test_calculate_properties_known_values():
    # YSFGL is cNPDB ID 3 (bare form of YSFGLamide).
    props = pp.calculate_properties("YSFGL")
    assert props["GRAVY Score"] == pytest.approx(0.82, abs=0.01)
    assert props["Isoelectric Point (pI)"] == pytest.approx(5.52, abs=0.05)
    assert "stable" in props["Instability Index"].lower()


def test_instability_status_threshold():
    # Status flips at 40; the label must agree with the numeric value.
    props = pp.calculate_properties("YSFGL")
    val = float(props["Instability Index"].split()[0])
    status = "unstable" if val >= 40 else "stable"
    assert status in props["Instability Index"]


def test_aliphatic_index_manual():
    # For "AVIL": (1 + 2.9*1 + 3.9*(1+1)) / 4 * 100 = 292.5
    assert pp.aliphatic_index("AVIL") == pytest.approx(292.5, abs=0.01)


def test_percent_hydrophobic():
    # "AGAG": A,A hydrophobic (2/4) -> 50%
    assert pp.percent_hydrophobic("AGAG") == pytest.approx(50.0, abs=0.01)


def test_boman_index_matches_scale():
    seq = "AC"
    expected = (pp.BOMAN_SCALE["A"] + pp.BOMAN_SCALE["C"]) / 2
    assert pp.boman_index(seq) == pytest.approx(expected, abs=1e-9)


def test_empty_sequence_edge_cases():
    assert pp.aliphatic_index("") == 0.0
    assert pp.boman_index("") == 0.0
    assert pp.percent_hydrophobic("") == 0.0


def test_monoisotopic_mass_amidated_matches_database():
    # YSFGLamide is stored as 585.30312 [M+H]+ in cNPDB.
    assert pp.monoisotopic_mass("YSFGL", "Amidation") == pytest.approx(585.30312, abs=1e-3)


def test_monoisotopic_mass_neutral_vs_charged_differ_by_proton():
    charged = pp.monoisotopic_mass("SEDER", charged=True)
    neutral = pp.monoisotopic_mass("SEDER", charged=False)
    assert charged - neutral == pytest.approx(pp.PROTON, abs=1e-6)


def test_monoisotopic_mass_rejects_nonstandard():
    with pytest.raises(ValueError):
        pp.monoisotopic_mass("YSFGLX")


@pytest.mark.parametrize("ptm,expected", [
    ("", 0.0),
    ("nan", 0.0),
    ("Amidation", -0.984016),
    ("Amidation; Sulfation", -0.984016 + 79.956815),
    ("Pyro-Glu from E", -18.010565),
])
def test_ptm_mass_shift(ptm, expected):
    shift, unknown = pp.ptm_mass_shift(ptm)
    assert shift == pytest.approx(expected, abs=1e-6)
    assert unknown == []


def test_ptm_mass_shift_flags_unknown():
    shift, unknown = pp.ptm_mass_shift("Glycosylation")
    assert unknown == ["glycosylation"]
