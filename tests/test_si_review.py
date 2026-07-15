"""Unit tests for DataCuration.si_review (pure queue logic; no network)."""
import pandas as pd
import pytest

from DataCuration import si_review as sr


def _empty():
    return pd.DataFrame(columns=sr.COLUMNS)


def test_upsert_adds_new_paper():
    q = sr.upsert(_empty(), {"doi": "10.1/x", "title": "T", "reason": "paywalled"})
    assert len(q) == 1
    assert q.iloc[0]["doi"] == "10.1/x"
    assert q.iloc[0]["status"] == "pending"        # defaulted


def test_upsert_normalizes_doi():
    q = sr.upsert(_empty(), {"doi": "https://doi.org/10.1/X"})
    assert q.iloc[0]["doi"] == "10.1/x"


def test_upsert_is_idempotent_and_preserves_edits():
    q = sr.upsert(_empty(), {"doi": "10.1/x", "status": "pending"})
    q = sr.set_status(q, "10.1/x", "done", note="pulled")
    # Re-scanning the same DOI must NOT reset it to pending or wipe the note.
    q2 = sr.upsert(q, {"doi": "10.1/X", "status": "pending"})
    assert len(q2) == 1
    assert q2.iloc[0]["status"] == "done"
    assert q2.iloc[0]["notes"] == "pulled"


def test_upsert_skips_paper_without_doi():
    q = sr.upsert(_empty(), {"doi": "", "title": "no doi"})
    assert len(q) == 0


def test_set_status_validates():
    q = sr.upsert(_empty(), {"doi": "10.1/x"})
    with pytest.raises(ValueError):
        sr.set_status(q, "10.1/x", "bogus")
    with pytest.raises(KeyError):
        sr.set_status(q, "10.9/missing", "done")


def test_pending_excludes_done_and_dropped():
    q = _empty()
    for doi, status in [("10.1/a", "pending"), ("10.1/b", "done"),
                        ("10.1/c", "in_progress"), ("10.1/d", "dropped")]:
        q = sr.upsert(q, {"doi": doi, "status": status})
    assert set(sr.pending(q)["doi"]) == {"10.1/a", "10.1/c"}


@pytest.mark.parametrize("status,expected", [
    ({}, True),                                             # unknown -> review
    ({"open_access": False, "in_epmc": False}, True),       # paywalled
    ({"open_access": True, "in_epmc": False}, True),        # OA flag but not fetchable
    ({"open_access": True, "in_epmc": True}, False),        # fully fetchable -> skip
])
def test_needs_manual_si(status, expected):
    assert sr.needs_manual_si(status) is expected


def test_scan_shortlist_queues_only_blocked(monkeypatch):
    def fake_status(doi, session=None):
        return {"10.1/open": {"open_access": True, "in_epmc": True},
                "10.1/closed": {"open_access": False, "in_epmc": False}}.get(
                    sr.normalize_doi(doi), {})
    monkeypatch.setattr(sr, "access_status", fake_status)

    shortlist = pd.DataFrame({
        "doi": ["10.1/open", "10.1/closed", ""],
        "title": ["open paper", "paywalled paper", "no doi"],
    })
    q = sr.scan_shortlist(shortlist, _empty(), date_added="2026-07-14")
    assert list(q["doi"]) == ["10.1/closed"]               # open one skipped, blank skipped
    assert q.iloc[0]["reason"] == "paywalled"
    assert q.iloc[0]["is_open_access"] == "N"


def test_scan_is_incremental(monkeypatch):
    monkeypatch.setattr(sr, "access_status", lambda doi, session=None: {})
    shortlist = pd.DataFrame({"doi": ["10.1/a"], "title": ["t"]})
    q = sr.scan_shortlist(shortlist, _empty(), "2026-07-14")
    q = sr.set_status(q, "10.1/a", "done")
    q2 = sr.scan_shortlist(shortlist, q, "2026-08-01")     # next month
    assert len(q2) == 1 and q2.iloc[0]["status"] == "done"  # not re-opened


def test_load_queue_roundtrip(tmp_path):
    path = str(tmp_path / "queue.csv")
    q = sr.upsert(_empty(), {"doi": "10.1/x", "title": "T", "reason": "captcha"})
    sr.save_queue(q, path)
    reloaded = sr.load_queue(path)
    assert list(reloaded.columns) == sr.COLUMNS
    assert reloaded.iloc[0]["doi"] == "10.1/x"
