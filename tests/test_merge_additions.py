"""Unit tests for DataCuration.merge_additions -- the only tool that writes the DB."""
import pandas as pd
import pytest

from DataCuration import merge_additions as ma
from utils import peptide_properties as pp


@pytest.fixture
def db():
    return pd.DataFrame([{
        "ID": ">cNP|0001", "Sequence": "YSFGL", "Active Sequence": "YSFGLamide",
        "cNPDB ID": 1, "Family": "RYamide", "OS": "HoA", "Tissue": "PO",
        "Existence": "MSMS", "PTM": "Amidation",
        "Monoisotopic Mass": pp.monoisotopic_mass("YSFGL", "Amidation"),
    }])


def _addition(seq="APERNFLRF", cid=2, ptm="Amidation", **over):
    try:
        mass = pp.monoisotopic_mass(seq, ptm)
    except ValueError:
        mass = 0.0  # deliberately-invalid sequences have no computable mass
    row = {
        "ID": f">cNP|{cid:04d}", "Sequence": seq, "Active Sequence": seq + "amide",
        "cNPDB ID": cid, "Family": "RFamide", "OS": "Lva", "Tissue": "PO",
        "Existence": "MSMS", "PTM": ptm, "Monoisotopic Mass": mass,
    }
    row.update(over)
    return pd.DataFrame([row])


def test_valid_addition_passes(db):
    assert ma.validate(_addition(), db) == []


def test_rejects_duplicate_sequence(db):
    bad = _addition(seq="YSFGL", cid=2, ptm="Amidation")
    problems = ma.validate(bad, db)
    assert any("already in the database" in p for p in problems)


def test_rejects_id_collision(db):
    problems = ma.validate(_addition(cid=1), db)
    assert any("collides" in p for p in problems)


def test_rejects_duplicate_within_additions(db):
    two = pd.concat([_addition(cid=2), _addition(cid=3)], ignore_index=True)
    problems = ma.validate(two, db)
    assert any("duplicated within the additions" in p for p in problems)


def test_rejects_inline_modification(db):
    problems = ma.validate(_addition(seq="QVF(d)DQ"), db)
    assert any("inline annotation" in p for p in problems)


def test_rejects_nonstandard_residue(db):
    problems = ma.validate(_addition(seq="APERXFLRF",
                                     **{"Monoisotopic Mass": 1.0}), db)
    assert any("non-standard" in p for p in problems)


@pytest.mark.parametrize("field", ["Family", "OS", "Existence"])
def test_rejects_blank_required_field(db, field):
    problems = ma.validate(_addition(**{field: ""}), db)
    assert any(field in p and "blank" in p for p in problems)


def test_rejects_field_still_marked_verify(db):
    problems = ma.validate(_addition(Existence="VERIFY"), db)
    assert any("VERIFY" in p for p in problems)


def test_rejects_mass_inconsistent_with_ptm(db):
    # The convention: mass == [M+H]+ of sequence + declared PTMs. Here the row
    # claims amidation but carries the UNMODIFIED mass -- exactly the error class
    # the QC pass found. It must be refused.
    unmodified = pp.monoisotopic_mass("APERNFLRF", "")
    problems = ma.validate(_addition(**{"Monoisotopic Mass": unmodified}), db)
    assert any("disagrees with sequence+PTM" in p for p in problems)


def test_accepts_mass_when_ptm_applied(db):
    # Same peptide, mass correctly includes the amidation shift -> passes.
    assert ma.validate(_addition(ptm="Amidation"), db) == []


def test_accepts_sulfation_when_applied(db):
    seq = "DYDDSDVE"
    add = _addition(seq=seq, cid=5, ptm="Sulfation",
                    **{"Monoisotopic Mass": pp.monoisotopic_mass(seq, "Sulfation")})
    assert ma.validate(add, db) == []


def test_merge_concatenates_and_sorts_by_id(db):
    merged = ma.merge(db, _addition(cid=2))
    assert len(merged) == 2
    assert list(merged["cNPDB ID"]) == [1, 2]


def test_write_fasta_roundtrip(db, tmp_path):
    path = tmp_path / "out.fasta"
    ma.write_fasta(db, str(path))
    text = path.read_text(encoding="utf-8")
    assert text == ">cNP|0001\nYSFGL\n"
