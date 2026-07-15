"""Integrity tests that run against the *shipping* cNPDB database.

These lock in the current state of the released database:

* Hard invariants (unique IDs, no duplicate sequences, every property
  recomputes, parquet mirrors xlsx, FASTA count matches) must always hold.
* Known data-quality issues are pinned to a documented baseline so a future
  curation edit that *introduces new* problems fails, while fixing existing
  ones is always allowed (counts may only go down).

Update KNOWN_ISSUE_BASELINE downward as the team resolves flagged entries.
"""
import os

import pytest

from DataCuration import cnpdb_qc as qc

# Baseline captured from Assets/20260418_cNPDB.xlsx (1516 entries).
# See DataCuration/qc_flagged_issues.csv for the itemized list.
KNOWN_ISSUE_BASELINE = {
    "mass_discrepancy": 130,
    "missing_OS": 115,
    "inline_modification_in_Sequence": 3,
    "missing_DOI": 2,
}

# Categories that must never occur in a healthy release.
HARD_ZERO_CATEGORIES = [
    "duplicate",
    "nonstandard_residue",
    "length_mismatch",
    "property_mismatch",
    "property_error",
    "instability_text",
    "missing_required",
]


@pytest.fixture(scope="module")
def issues(db):
    return qc.run_all(db)


def _count(issues, category):
    return int((issues["category"] == category).sum())


def test_expected_row_count(db):
    # Current release size; bump intentionally when the DB grows.
    assert len(db) == 1516


def test_cnpdb_ids_unique_and_contiguous(db):
    ids = db["cNPDB ID"]
    assert ids.is_unique
    assert set(ids) == set(range(int(ids.min()), int(ids.max()) + 1))


@pytest.mark.parametrize("category", HARD_ZERO_CATEGORIES)
def test_no_hard_errors(issues, category):
    offenders = issues[issues["category"] == category]
    assert offenders.empty, f"{category}: {offenders['detail'].tolist()[:5]}"


@pytest.mark.parametrize("category,baseline", sorted(KNOWN_ISSUE_BASELINE.items()))
def test_known_issues_do_not_regress(issues, category, baseline):
    current = _count(issues, category)
    assert current <= baseline, (
        f"{category} rose from baseline {baseline} to {current} -- a curation "
        f"edit introduced new problems."
    )


def test_all_properties_recompute_exactly(db):
    # The strongest guarantee: every stored physicochemical value matches a
    # fresh BioPython recomputation within tolerance.
    assert qc.check_properties(db) == []


def test_parquet_mirrors_xlsx(db, db_parquet):
    assert list(db.columns) == list(db_parquet.columns)
    assert len(db) == len(db_parquet)
    for col in ["Sequence", "cNPDB ID", "Active Sequence", "Family", "Monoisotopic Mass"]:
        a = db[col].astype(str).reset_index(drop=True)
        b = db_parquet[col].astype(str).reset_index(drop=True)
        assert (a == b).all(), f"parquet/xlsx differ in column {col!r}"


def test_fasta_header_count_matches_rows(db, repo_root):
    fasta = os.path.join(repo_root, "20260418_cNPDB_Full_Database.fasta")
    if not os.path.exists(fasta):
        pytest.skip("FASTA not present")
    with open(fasta, encoding="utf-8", errors="replace") as fh:
        n_headers = sum(1 for line in fh if line.startswith(">"))
    assert n_headers == len(db)
