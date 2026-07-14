"""Unit tests for DataCuration.os_tissue_completeness (pure detection; no network)."""
import pandas as pd
import pytest

from DataCuration import os_tissue_completeness as otc


def test_detect_species_scientific_name():
    assert "Cbo" in otc.detect_species("Neuropeptides in Cancer borealis hemolymph")
    assert "HoA" in otc.detect_species("the lobster Homarus americanus brain")


def test_detect_species_common_name():
    assert "Csap" in otc.detect_species("profiling in the blue crab")
    assert "Lva" in otc.detect_species("Pacific white shrimp aquaculture")


def test_detect_species_multiple():
    found = otc.detect_species("Cancer borealis and Carcinus maenas were compared")
    assert found == {"Cbo", "Cmae"}


def test_detect_species_none():
    assert otc.detect_species("Drosophila melanogaster neuropeptides") == set()


def test_detect_species_is_case_insensitive():
    assert "Cbo" in otc.detect_species("CANCER BOREALIS")


def test_detect_tissues():
    assert otc.detect_tissues("dissected the pericardial organ") == {"PO"}
    assert otc.detect_tissues("sinus gland and eyestalk extracts") == {"SG", "ES"}
    assert "STG" in otc.detect_tissues("the stomatogastric ganglion network")
    assert "hemolymph" in otc.detect_tissues("circulating haemolymph titres")


def test_detect_tissues_none():
    assert otc.detect_tissues("no tissue named here") == set()


@pytest.mark.parametrize("cell,expected", [
    ("Cbo;Cmae", {"Cbo", "Cmae"}),
    ("Cbo, Cmae / HoA", {"Cbo", "Cmae", "HoA"}),
    ("nan", set()),
    (None, set()),
    ("", set()),
])
def test_split_tokens(cell, expected):
    assert otc.split_tokens(cell) == expected


def test_check_peptide_diffs_against_current(monkeypatch):
    # Stub the network: one paper mentioning Cancer borealis + pericardial organ.
    def fake_search(query, **kwargs):
        return [{"title": "Peptide X in Cancer borealis pericardial organ",
                 "journal": "J", "doi": "10.1/x", "pmid": "1"}]
    monkeypatch.setattr(otc, "europepmc_search", fake_search)

    res = otc.check_peptide("APERNFLRF", current_os={"HoA"}, current_tissue={"Br"})
    assert res["lit_species"] == "Cbo"
    assert res["missing_OS"] == "Cbo"        # Cbo found in lit, absent from OS
    assert res["missing_Tissue"] == "PO"
    assert res["supporting"] == "10.1/x"


def test_check_peptide_reports_no_gap_when_already_recorded(monkeypatch):
    def fake_search(query, **kwargs):
        return [{"title": "Peptide in Cancer borealis brain", "journal": "",
                 "doi": "10.1/x", "pmid": "1"}]
    monkeypatch.setattr(otc, "europepmc_search", fake_search)

    res = otc.check_peptide("APERNFLRF", current_os={"Cbo"}, current_tissue={"Br"})
    assert res["missing_OS"] == ""
    assert res["missing_Tissue"] == ""


def test_run_skips_short_peptides(monkeypatch, capsys):
    monkeypatch.setattr(otc, "europepmc_search", lambda *a, **k: [])
    db = pd.DataFrame([
        {"cNPDB ID": 1, "Sequence": "YSFGL", "OS": "Cbo", "Tissue": "Br", "Family": "F"},
        {"cNPDB ID": 2, "Sequence": "APERNFLRF", "OS": "Cbo", "Tissue": "Br", "Family": "F"},
    ])
    otc.run(db, sleep=0)
    out = capsys.readouterr().out
    assert "skipped 1" in out          # the 5-mer is skipped as uninformative


def test_run_returns_only_rows_with_gaps(monkeypatch):
    def fake_search(query, **kwargs):
        return [{"title": "found in blue crab sinus gland", "journal": "",
                 "doi": "10.1/y", "pmid": "2"}]
    monkeypatch.setattr(otc, "europepmc_search", fake_search)
    db = pd.DataFrame([
        {"cNPDB ID": 1, "Sequence": "APERNFLRF", "OS": "HoA", "Tissue": "Br", "Family": "F"},
        {"cNPDB ID": 2, "Sequence": "GYSNKDFVRF", "OS": "Csap", "Tissue": "SG", "Family": "F"},
    ])
    out = otc.run(db, sleep=0)
    # Row 1 has gaps (Csap/SG missing); row 2 already records both -> excluded.
    assert list(out["cNPDB ID"]) == [1]
    assert out.iloc[0]["missing_OS"] == "Csap"
