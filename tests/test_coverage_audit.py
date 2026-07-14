"""Unit tests for DataCuration.coverage_audit."""
import pandas as pd
import pytest

from DataCuration import coverage_audit as ca


def test_bare_strips_inline_mods_and_uppercases():
    assert ca.bare("qvf(d)dq") == "QVFDQ"


def test_os_tokens_splits_and_drops_nan():
    assert ca.os_tokens("Cbo;Cmae") == {"Cbo", "Cmae"}
    assert ca.os_tokens("nan") == set()
    assert ca.os_tokens("Csap, HoA / Spar") == {"Csap", "HoA", "Spar"}


def test_build_db_index_maps_sequence_to_os():
    df = pd.DataFrame({"Sequence": ["YSFGL", "AAAA"], "OS": ["Cbo;Cmae", None]})
    idx = ca.build_db_index(df)
    assert idx["YSFGL"] == {"Cbo", "Cmae"}
    assert idx["AAAA"] == set()


@pytest.fixture
def db_index():
    return {
        "YSFGL": {"Cbo", "Cmae"},   # populated
        "AAAA": set(),               # in DB but no OS
    }


def test_classify_overlooked(db_index):
    assert ca.classify("NEWSEQ", "HoA", db_index) == "overlooked"


def test_classify_os_partial(db_index):
    # YSFGL is in DB for Cbo/Cmae; NeuroPep says HoA -> partial gap.
    assert ca.classify("YSFGL", "HoA", db_index) == "os_partial"


def test_classify_os_blank(db_index):
    # AAAA is in DB but has no OS at all -> blank gap.
    assert ca.classify("AAAA", "HoA", db_index) == "os_blank"


def test_classify_no_gap_when_species_present(db_index):
    assert ca.classify("YSFGL", "Cbo", db_index) is None


def test_classify_skips_nonstandard(db_index):
    assert ca.classify("YSFGL(precursor)", "HoA", db_index) is None
    assert ca.classify("SEQXZ", "HoA", db_index) is None


def test_audit_end_to_end(tmp_path):
    # Minimal DB: KKKK present (HoA only); YSFGL present (no OS).
    df = pd.DataFrame({
        "Sequence": ["KKKK", "YSFGL"],
        "OS": ["HoA", None],
    })
    npdir = tmp_path / "NeuroPepDatabases"
    npdir.mkdir()
    (npdir / "Cancer_borealis.txt").write_text(
        "ID\tSequence\tLength\tOrganism\tFamily\tName\tPMID\n"
        "NP1\tKKKK\t4\tCancer borealis\tFamA\tpepA\t111\n"   # in DB but missing Cbo -> os_partial
        "NP2\tYSFGL\t5\tCancer borealis\tFamB\tpepB\t222\n"  # in DB, OS blank -> os_blank
        "NP3\tWWWW\t4\tCancer borealis\tFamC\tpepC\t333\n",  # not in DB -> overlooked
        encoding="utf-8",
    )
    result = ca.audit(df, str(npdir))
    assert set(result["overlooked"]["Sequence"]) == {"WWWW"}
    gap = result["os_gap"].set_index("Sequence")["gap_type"].to_dict()
    assert gap == {"KKKK": "os_partial", "YSFGL": "os_blank"}
