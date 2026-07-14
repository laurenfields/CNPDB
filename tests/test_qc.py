"""Unit tests for the QC engine (DataCuration.cnpdb_qc) on synthetic frames."""
import pandas as pd
import pytest

from DataCuration import cnpdb_qc as qc


def _row(**overrides):
    """A minimal, internally-consistent database row for cNPDB ID 1 (YSFGL amide)."""
    base = {
        "ID": ">cNP|0001",
        "Sequence": "YSFGL",
        "Active Sequence": "YSFGLamide",
        "cNPDB ID": 1,
        "Family": "RYamide",
        "OS": "HoA",
        "Existence": "MSMS",
        "Monoisotopic Mass": 585.30312,
        "Length": 5,
        "GRAVY": 0.82,
        "% Hydrophobic Residue": 60.0,
        "PTM": "Amidation",
        "Instability Index": "8.0 (Stable)",
        "Instability Index Value": 8.0,
        "Isoelectric Point (pI)": 5.52,
        "Net Charge (pH 7.0)": 0.0,
        "Boman Index": 0.826,
        "Aliphatic Index": 78.0,
        "DOI": "10.1/x",
    }
    base.update(overrides)
    return base


def _df(rows):
    return pd.DataFrame(rows)


def test_clean_row_passes_all_checks():
    df = _df([_row()])
    issues = qc.run_all(df)
    # A hand-built clean row should not trip mass/length/missing/duplicate checks.
    assert issues[issues["category"] == "mass_discrepancy"].empty
    assert issues[issues["category"] == "length_mismatch"].empty
    assert issues[issues["category"] == "missing_required"].empty
    assert issues[issues["category"] == "duplicate"].empty


def test_detects_duplicate_sequence():
    df = _df([_row(), _row(**{"cNPDB ID": 2})])
    dup = qc.check_duplicates(df)
    assert any(i["category"] == "duplicate" for i in dup)


def test_detects_length_mismatch():
    df = _df([_row(Length=99)])
    issues = qc.check_length(df)
    assert issues and issues[0]["category"] == "length_mismatch"


def test_detects_inline_modification():
    row = _row()
    row["Sequence"] = "QVF(d)DQ"
    row["Length"] = 6
    issues = qc.check_sequences(_df([row]))
    assert any(i["category"] == "inline_modification_in_Sequence" for i in issues)


def test_detects_mass_discrepancy():
    df = _df([_row(**{"Monoisotopic Mass": 9999.0})])
    issues = qc.check_mass(df)
    assert issues and issues[0]["category"] == "mass_discrepancy"
    assert issues[0]["severity"] == "high"  # >50 Da off


def test_mass_check_accepts_declared_sulfation():
    # Neutral sulfated mass should validate when PTM declares sulfation.
    from utils.peptide_properties import monoisotopic_mass
    m = monoisotopic_mass("DYDDSDVE", "Sulfation", charged=True)
    df = _df([_row(Sequence="DYDDSDVE", **{"Monoisotopic Mass": round(m, 4)},
                   PTM="Sulfation", Length=8, Family="F", **{"Active Sequence": "DYDDSDVE"})])
    assert qc.check_mass(df) == []


def test_detects_missing_required_and_annotation():
    df = _df([_row(OS="", Family=None)])
    issues = qc.check_missing(df)
    cats = {i["category"] for i in issues}
    assert "missing_required" in cats  # Family blank
    assert "missing_OS" in cats


def test_detects_instability_text_mismatch():
    df = _df([_row(**{"Instability Index": "8.0 (Unstable)"})])  # value 8 -> should be Stable
    issues = qc.check_instability_consistency(df)
    assert issues and issues[0]["category"] == "instability_text"


def test_id_integrity_gap_and_duplicate():
    df = _df([_row(**{"cNPDB ID": 1}), _row(**{"cNPDB ID": 3, "Sequence": "AAAA",
                                               "Active Sequence": "AAAA", "Length": 4})])
    issues = qc.check_id_integrity(df)
    assert any("gap" in i["detail"] for i in issues)


def test_summarize_empty():
    assert qc.summarize(pd.DataFrame(columns=["cNPDB ID", "category", "severity", "detail"])) \
        == "No issues found."
