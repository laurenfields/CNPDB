"""Unit tests for DataCuration.lit_mining pure helpers (no network)."""
import pandas as pd

from DataCuration import lit_mining as lm


def test_normalize_doi_variants():
    assert lm.normalize_doi("https://doi.org/10.1021/ABC") == "10.1021/abc"
    assert lm.normalize_doi("doi:10.1/X") == "10.1/x"
    assert lm.normalize_doi("  10.1/Y  ") == "10.1/y"
    assert lm.normalize_doi(None) == ""


def test_known_dois_splits_multi_value_cells():
    df = pd.DataFrame({"DOI": ["10.1/x; 10.2/y", "10.3/z", None, "nan"]})
    assert lm.known_dois(df) == {"10.1/x", "10.2/y", "10.3/z"}


def test_known_dois_missing_column():
    assert lm.known_dois(pd.DataFrame({"other": [1]})) == set()


def test_filter_new_papers_excludes_seen_and_dedupes_batch():
    hits = [
        {"doi": "10.1/x", "pmid": "1"},   # seen
        {"doi": "10.1/X", "pmid": "2"},   # same DOI (case) -> dropped as seen
        {"doi": "10.2/new", "pmid": "3"},  # new
        {"doi": "10.2/new", "pmid": "4"},  # dup of the new one within batch
        {"doi": "", "pmid": "99"},         # no doi -> keyed by pmid, kept
    ]
    new = lm.filter_new_papers(hits, seen={"10.1/x"})
    pmids = [h["pmid"] for h in new]
    assert pmids == ["3", "99"]


def test_filter_new_papers_all_seen():
    hits = [{"doi": "10.1/x", "pmid": "1"}]
    assert lm.filter_new_papers(hits, {"10.1/x"}) == []
