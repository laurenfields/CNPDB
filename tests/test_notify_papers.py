# -*- coding: utf-8 -*-
"""Tests for the papers-to-check reminder reconciliation."""
import pandas as pd

from DataCuration import notify_papers as np


def _pending(*rows):
    return pd.DataFrame(list(rows), columns=np.COLUMNS)


def test_new_shortlist_paper_is_added():
    pending = _pending()
    shortlist = pd.DataFrame([{"doi": "10.1/aaa", "title": "Paper A"}])
    out = np.reconcile(pending, shortlist, incorporated=set(), today="2026-08-01")
    assert list(out["doi"]) == ["10.1/aaa"]
    assert out.iloc[0]["first_flagged"] == "2026-08-01"


def test_incorporated_paper_is_dropped():
    pending = _pending({"doi": "10.1/aaa", "title": "A", "first_flagged": "2026-07-01"})
    out = np.reconcile(pending, pd.DataFrame(columns=["doi", "title"]),
                       incorporated={"10.1/aaa"}, today="2026-08-01")
    assert out.empty


def test_paper_keeps_original_flag_date_across_months():
    pending = _pending({"doi": "10.1/aaa", "title": "A", "first_flagged": "2026-06-01"})
    # Same paper reappears on the shortlist; must not reset its flag date.
    shortlist = pd.DataFrame([{"doi": "10.1/AAA", "title": "A"}])  # different case
    out = np.reconcile(pending, shortlist, incorporated=set(), today="2026-08-01")
    assert len(out) == 1
    assert out.iloc[0]["first_flagged"] == "2026-06-01"


def test_duplicate_shortlist_dois_added_once():
    shortlist = pd.DataFrame([{"doi": "10.1/aaa", "title": "A"},
                              {"doi": "10.1/aaa", "title": "A dup"}])
    out = np.reconcile(_pending(), shortlist, incorporated=set(), today="2026-08-01")
    assert len(out) == 1


def test_blank_doi_is_ignored():
    shortlist = pd.DataFrame([{"doi": "", "title": "no doi"}])
    out = np.reconcile(_pending(), shortlist, incorporated=set(), today="2026-08-01")
    assert out.empty


def test_body_empty_when_nothing_pending():
    assert np.format_email_body(_pending()) == ""


def test_body_lists_pending_papers():
    pending = _pending({"doi": "10.1/aaa", "title": "Cool peptides", "first_flagged": "2026-07-01"})
    body = np.format_email_body(pending)
    assert "Cool peptides" in body
    assert "10.1/aaa" in body
    assert "1 crustacean-neuropeptide paper" in body


def test_mix_add_and_drop_in_one_pass():
    pending = _pending(
        {"doi": "10.1/old", "title": "Old", "first_flagged": "2026-05-01"},   # will drop
        {"doi": "10.1/stay", "title": "Stay", "first_flagged": "2026-06-01"},  # stays
    )
    shortlist = pd.DataFrame([{"doi": "10.1/new", "title": "New"}])            # adds
    out = np.reconcile(pending, shortlist, incorporated={"10.1/old"}, today="2026-08-01")
    assert set(out["doi"]) == {"10.1/stay", "10.1/new"}
