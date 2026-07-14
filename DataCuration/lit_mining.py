# -*- coding: utf-8 -*-
"""Literature-mining pipeline to keep cNPDB current.

Two complementary modes:

* ``discover`` -- find *recent* crustacean neuropeptide papers (by topic/species
  keywords over a date window) whose DOI is **not** already cited in the
  database. This is the mode meant to be scheduled (e.g. monthly) so a curator
  gets a short digest of papers to screen for new sequences.

* ``references`` -- the original behaviour: for every peptide already in the
  database, query PubMed + Europe PMC for the exact sequence to collect
  supporting references. Useful when back-filling citations.

Network calls are isolated in thin functions; the parsing/filtering helpers are
pure so they can be unit-tested without hitting the network. Set an NCBI API key
via the ``NCBI_API_KEY`` environment variable to raise the PubMed rate limit.

Examples::

    python -m DataCuration.lit_mining discover --since 2025-01-01 --out new_papers.csv
    python -m DataCuration.lit_mining references --db Assets/20260418_cNPDB.xlsx --out refs.csv
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DataCuration.cnpdb_qc import DEFAULT_DB, load_database  # noqa: E402

EPMC_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
NCBI_EMAIL = os.environ.get("NCBI_EMAIL", "lafields2@wisc.edu")
NCBI_API_KEY = os.environ.get("NCBI_API_KEY")

# Topic query used by ``discover``. Combines neuropeptide vocabulary with the
# crustacean clade so we cast wide but stay on-topic.
DISCOVER_QUERY = (
    '(neuropeptide OR neuropeptidome OR peptidome OR "peptide hormone" OR allatostatin '
    'OR RFamide OR orcokinin OR "crustacean cardioactive peptide" OR "crustacean hyperglycemic hormone") '
    'AND (crustacean OR decapod OR crab OR lobster OR crayfish OR shrimp OR Crustacea)'
)


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested)
# ---------------------------------------------------------------------------
def normalize_doi(doi: str) -> str:
    """Lower-case and strip a DOI to a comparable bare form."""
    if doi is None:
        return ""
    d = str(doi).strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if d.startswith(prefix):
            d = d[len(prefix):]
    return d.strip()


def known_dois(df: pd.DataFrame) -> set[str]:
    """Set of normalized DOIs already present in the database's DOI column.

    Cells may contain multiple DOIs separated by ``;`` or whitespace.
    """
    out: set[str] = set()
    if "DOI" not in df.columns:
        return out
    for cell in df["DOI"].dropna().astype(str):
        for token in cell.replace(",", ";").split(";"):
            nd = normalize_doi(token)
            if nd and nd not in ("nan", "none"):
                out.add(nd)
    return out


def load_seen_dois(path: str) -> set[str]:
    """Read a persisted seen-DOI list (one per line; ``#`` comments ignored)."""
    if not path or not os.path.exists(path):
        return set()
    out = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                out.add(normalize_doi(line))
    return {d for d in out if d}


def append_seen_dois(path: str, dois) -> None:
    """Append new DOIs to the persisted seen-list, keeping it sorted & unique."""
    combined = load_seen_dois(path) | {normalize_doi(d) for d in dois if normalize_doi(d)}
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("# DOIs already surfaced by lit_mining discover; do not edit by hand.\n")
        for d in sorted(combined):
            fh.write(d + "\n")


def filter_new_papers(hits: list[dict], seen: set[str]) -> list[dict]:
    """Return hits whose DOI is not in ``seen`` (deduped within the batch too)."""
    new, batch = [], set()
    for h in hits:
        nd = normalize_doi(h.get("doi", ""))
        key = nd or f"pmid:{h.get('pmid', '')}"
        if not key or key in seen or key in batch:
            continue
        batch.add(key)
        new.append(h)
    return new


# ---------------------------------------------------------------------------
# Network functions
# ---------------------------------------------------------------------------
def europepmc_search(query: str, page_size: int = 100, max_pages: int = 5,
                     session: requests.Session | None = None) -> list[dict]:
    """Query Europe PMC and return normalized hit dicts.

    Uses cursorMark pagination. Each hit -> {title, doi, pmid, journal, year, source_query}.
    """
    session = session or requests.Session()
    results, cursor = [], "*"
    for _ in range(max_pages):
        params = {"query": query, "format": "json", "pageSize": page_size,
                  "cursorMark": cursor, "resultType": "core"}
        resp = session.get(EPMC_BASE, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        for r in data.get("resultList", {}).get("result", []):
            results.append({
                "title": r.get("title", ""),
                "doi": r.get("doi", ""),
                "pmid": r.get("pmid", ""),
                "journal": r.get("journalTitle", ""),
                "year": r.get("pubYear", ""),
                "authors": r.get("authorString", ""),
                "source_query": query,
            })
        next_cursor = data.get("nextCursorMark")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
        time.sleep(0.3)
    return results


def discover_recent_papers(df: pd.DataFrame, since: str, until: str | None = None,
                           query: str = DISCOVER_QUERY,
                           session: requests.Session | None = None,
                           extra_seen: set[str] | None = None) -> pd.DataFrame:
    """Find recent on-topic papers not already cited in the database.

    ``since``/``until`` are ISO dates (YYYY-MM-DD). ``extra_seen`` is a set of
    already-surfaced DOIs (e.g. from a persisted seen-list) to exclude on top of
    the DOIs already in the database -- this is what makes a scheduled monthly
    run show only *newly appeared* papers. Returns a DataFrame of candidate
    papers for a curator to screen for new sequences.
    """
    date_clause = f'(FIRST_PDATE:[{since} TO {until or "3000-12-31"}])'
    full_query = f"{query} AND {date_clause}"
    hits = europepmc_search(full_query, session=session)
    seen = known_dois(df) | (extra_seen or set())
    new = filter_new_papers(hits, seen)
    cols = ["title", "authors", "journal", "year", "doi", "pmid", "source_query"]
    return pd.DataFrame(new, columns=cols).sort_values("year", ascending=False)


def references_for_sequences(sequences, session: requests.Session | None = None,
                             sleep: float = 0.4) -> pd.DataFrame:
    """For each peptide sequence, collect Europe PMC references mentioning it.

    A lightweight, robust rewrite of the original per-peptide search. PubMed
    E-utilities can be layered in via Biopython if desired; Europe PMC alone
    covers PubMed + PMC + preprints and needs no API key.
    """
    session = session or requests.Session()
    records = []
    for seq in sequences:
        try:
            hits = europepmc_search(f'"{seq}"', page_size=50, max_pages=1, session=session)
            for h in hits:
                records.append({"Peptide": seq, "DOI": h["doi"], "PMID": h["pmid"],
                                "Title": h["title"], "Source": "Europe PMC"})
        except Exception as exc:  # pragma: no cover - network defensive
            records.append({"Peptide": seq, "DOI": "", "PMID": "",
                            "Title": f"ERROR: {exc}", "Source": "error"})
        time.sleep(sleep)
    return pd.DataFrame(records, columns=["Peptide", "DOI", "PMID", "Title", "Source"])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="cNPDB literature mining.")
    sub = ap.add_subparsers(dest="mode", required=True)

    d = sub.add_parser("discover", help="find recent papers not yet cited in the DB")
    d.add_argument("--since", required=True, help="ISO date, e.g. 2025-01-01")
    d.add_argument("--until", default=None, help="ISO date (default: open-ended)")
    d.add_argument("--db", default=DEFAULT_DB)
    d.add_argument("--out", default="new_papers.csv")
    d.add_argument("--seen", default=None,
                   help="path to a persisted seen-DOI list; excludes already-surfaced "
                        "papers so each run shows only what is new")
    d.add_argument("--update-seen", action="store_true",
                   help="append this run's DOIs to the --seen file")

    r = sub.add_parser("references", help="collect references for existing peptides")
    r.add_argument("--db", default=DEFAULT_DB)
    r.add_argument("--out", default="peptide_references.csv")
    r.add_argument("--limit", type=int, default=None, help="only first N peptides (testing)")

    args = ap.parse_args(argv)
    df = load_database(args.db)

    if args.mode == "discover":
        extra_seen = load_seen_dois(args.seen) if args.seen else set()
        out = discover_recent_papers(df, since=args.since, until=args.until, extra_seen=extra_seen)
        out.to_csv(args.out, index=False)
        print(f"Found {len(out)} candidate new papers since {args.since} "
              f"(excluding {len(extra_seen)} already-seen) -> {args.out}")
        if args.seen and args.update_seen:
            append_seen_dois(args.seen, out["doi"].tolist())
            print(f"Updated seen-list -> {args.seen}")
    else:
        seqs = df["Sequence"].dropna().astype(str).tolist()
        if args.limit:
            seqs = seqs[:args.limit]
        out = references_for_sequences(seqs)
        out.to_csv(args.out, index=False)
        print(f"Collected {len(out)} reference rows for {len(seqs)} peptides -> {args.out}")
    return out


if __name__ == "__main__":
    main()
