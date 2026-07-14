"""Unit tests for utils.sequence_utils."""
import pytest

from utils import sequence_utils as su


def test_clean_sequence_strips_fasta_header_and_joins():
    assert su.clean_sequence(">peptide 1\nYSFG\nLRF\n") == "YSFGLRF"


def test_clean_sequence_uppercases():
    assert su.clean_sequence("ysfgl") == "YSFGL"


def test_strip_inline_modifications():
    assert su.strip_inline_modifications("QVF(d)DQACK") == "QVFDQACK"
    assert su.strip_inline_modifications("A(d)B(d)C") == "ABC"


def test_inline_modifications_detected():
    assert su.inline_modifications("QVF(d)DQACK") == ["(d)"]
    assert su.inline_modifications("PLAINSEQ") == []


def test_calculate_percent_identity_full_and_partial():
    assert su.calculate_percent_identity("ABCD", "ABCD") == 100.0
    assert su.calculate_percent_identity("ABCD", "ABXD") == pytest.approx(75.0)


def test_calculate_percent_identity_empty():
    assert su.calculate_percent_identity("", "ABC") == 0.0


def test_is_valid_sequence():
    assert su.is_valid_sequence("YSFGL")
    assert not su.is_valid_sequence("YSFGLX")
    assert not su.is_valid_sequence("")


def test_is_valid_sequence_inline_mod_handling():
    # (d) is tolerated when inline mods are allowed, rejected otherwise.
    assert su.is_valid_sequence("QVF(d)DQACK", allow_inline_mods=True)
    assert not su.is_valid_sequence("QVF(d)DQACK", allow_inline_mods=False)


def test_nonstandard_residues():
    assert su.nonstandard_residues("YSFGL") == set()
    assert su.nonstandard_residues("YSFGLXZ") == {"X", "Z"}
