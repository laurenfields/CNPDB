"""Unit tests for DataCuration.backfill (pure logic; no network)."""
import pandas as pd
import pytest

from DataCuration import backfill as bf
from utils import peptide_properties as pp


@pytest.mark.parametrize("npep_family,name,expected", [
    ("Orcokinin", "", "Orcokinin"),
    ("Pyrokinin", "", "Pyrokinin"),
    ("FMRFamide related peptide", "", "RFamide"),
    ("Arthropod PDH", "", "PDH"),
    ("Tachykinin", "", "Tachykinin"),
    ("NPY", "", "NPF"),
    ("", "", "Others"),
    ("nan", "", "Others"),
    ("Something unmapped", "", "Others"),
])
def test_map_family_basic(npep_family, name, expected):
    assert bf.map_family(npep_family, name) == expected


def test_map_family_allatostatin_subtypes():
    assert bf.map_family("Allatostatin", "Allatostatin A") == "Allatostatin-A_type"
    assert bf.map_family("Allatostatin", "Allatostatin B") == "Allatostatin-B_type"
    assert bf.map_family("Allatostatin", "Allatostatin C") == "Allatostatin-C_type"
    assert bf.map_family("Allatostatin", "") == "Allatostatin-A_type"  # default


def test_map_family_chh_superfamily():
    fam = "Arthropod CHH/MIH/GIH/VIH hormone"
    assert bf.map_family(fam, "Crustacean hyperglycemic hormone") == "CHH"
    assert bf.map_family(fam, "Molt-inhibiting hormone") == "MIH"
    assert bf.map_family(fam, "Mandibular organ-inhibiting hormone") == "MOIH"


def test_likely_amidated():
    assert bf.likely_amidated("RFamide")
    assert bf.likely_amidated("PDH")
    assert not bf.likely_amidated("Orcokinin")   # orcokinins are not amidated
    assert not bf.likely_amidated("CHH")


def test_make_id_header_format():
    hdr = bf.make_id_header(1517, "RFamide", "Lva", "MSMS", 1234.5, "PO", "APERNFLRF")
    assert hdr.startswith(">cNP|1517 ")
    assert "Family=RFamide" in hdr and "OS=Lva" in hdr and "Seq=APERNFLRF" in hdr


def test_make_id_header_marks_unverified_fields():
    hdr = bf.make_id_header(1517, "RFamide", "Lva", "", 1.0, "", "AAAAA")
    assert "Existence=VERIFY" in hdr and "Tissue=VERIFY" in hdr


def _staging(seq="APERNFLRF", family="FMRFamide related peptide"):
    db = pd.DataFrame({"cNPDB ID": [1516]})
    over = pd.DataFrame([{"Sequence": seq, "Species": "Litopenaeus_vannamei",
                          "OS_abbr": "Lva", "Family": family, "Name": "", "PMID": "1"}])
    return bf.build_staging(over, db, resolve=False)


def test_build_staging_assigns_next_id_and_computes_properties():
    s = _staging()
    assert len(s) == 1
    r = s.iloc[0]
    assert r["cNPDB ID"] == 1517                      # continues from max 1516
    assert r["Length"] == len("APERNFLRF")
    assert r["Family"] == "RFamide"
    assert r["Source"] == "NeuroPep"
    # properties agree with the shared module
    assert r["GRAVY"] == pp.calculate_properties("APERNFLRF")["GRAVY Score"]


def test_build_staging_leaves_unknowable_fields_blank_and_flags_them():
    r = _staging().iloc[0]
    assert r["PTM"] == "" and r["Existence"] == "" and r["Tissue"] == ""
    assert "PTM" in r["_VERIFY"] and "Existence" in r["_VERIFY"]


def test_build_staging_mass_is_unmodified_but_amidated_alternative_offered():
    r = _staging().iloc[0]
    seq = "APERNFLRF"
    assert r["Monoisotopic Mass"] == pytest.approx(
        pp.monoisotopic_mass(seq, "", charged=True), abs=1e-3)
    assert r["_likely_amidated"]                       # RFamide family
    assert r["_mass_if_amidated"] == pytest.approx(
        pp.monoisotopic_mass(seq, "Amidation", charged=True), abs=1e-3)
    # The two masses must differ by the amidation shift.
    assert r["Monoisotopic Mass"] - r["_mass_if_amidated"] == pytest.approx(0.984, abs=0.01)


def test_finalize_recomputes_mass_from_confirmed_ptm():
    s = _staging()
    s.loc[0, "PTM"] = "Amidation"
    s.loc[0, "Existence"] = "MSMS"
    s.loc[0, "Tissue"] = "PO"
    out = bf.finalize(s)
    r = out.iloc[0]
    assert r["Monoisotopic Mass"] == pytest.approx(
        pp.monoisotopic_mass("APERNFLRF", "Amidation", charged=True), abs=1e-3)
    assert r["Active Sequence"] == "APERNFLRFamide"
    assert "Existence=MSMS" in r["ID"] and "Tissue=PO" in r["ID"]
    # review-only columns are dropped
    assert not [c for c in out.columns if c.startswith("_")]


def test_finalize_no_ptm_keeps_unmodified_mass_and_sequence():
    s = _staging(seq="NFDEIDRAGF", family="Orcokinin")
    out = bf.finalize(s)
    r = out.iloc[0]
    assert r["Active Sequence"] == "NFDEIDRAGF"       # no 'amide' suffix
    assert r["Monoisotopic Mass"] == pytest.approx(
        pp.monoisotopic_mass("NFDEIDRAGF", "", charged=True), abs=1e-3)


def test_finalized_rows_match_db_schema():
    s = _staging()
    out = bf.finalize(s)
    assert list(out.columns) == [c for c in bf.DB_COLUMNS if c in out.columns]
    for col in ["ID", "Sequence", "cNPDB ID", "Family", "OS", "Monoisotopic Mass"]:
        assert col in out.columns
