# -*- coding: utf-8 -*-
"""Maintain the standing "papers to check" reminder list and its email body.

The monthly literature scan surfaces crustacean-neuropeptide papers a curator
should look at. This module keeps a persistent list of those papers and, each
month:

* **adds** newly shortlisted papers that aren't already listed, and
* **drops** any paper whose DOI now appears in the database -- i.e. it has been
  incorporated, so it no longer needs chasing.

The remaining papers are formatted into a plain-text email body. A paper stays on
the list (and in every monthly email) until its DOI shows up in the database.

Incorporation is detected by **DOI match** against the database's ``DOI`` column,
so it only works if the source DOI is recorded when sequences are added.

CLI (run by the monthly workflow)::

    python -m DataCuration.notify_papers reconcile \
        --shortlist DataCuration/outputs/shortlist_2026-08-01.csv \
        --list DataCuration/outputs/papers_to_check.csv \
        --body-out email_body.txt
"""
from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DataCuration.cnpdb_qc import DEFAULT_DB, OUTPUTS_DIR, load_database  # noqa: E402
from DataCuration.lit_mining import known_dois, normalize_doi  # noqa: E402

COLUMNS = ["doi", "title", "first_flagged"]
DEFAULT_LIST = os.path.join(OUTPUTS_DIR, "papers_to_check.csv")


def load_list(path: str = DEFAULT_LIST) -> pd.DataFrame:
    if path and os.path.exists(path):
        df = pd.read_csv(path, dtype=str).fillna("")
        for c in COLUMNS:
            if c not in df.columns:
                df[c] = ""
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)


def reconcile(pending: pd.DataFrame, shortlist: pd.DataFrame,
              incorporated: set[str], today: str) -> pd.DataFrame:
    """Return the updated pending list.

    * Rows whose DOI is in ``incorporated`` are dropped (they're in the DB now).
    * Shortlist papers with a DOI not already pending and not incorporated are
      appended, stamped with ``today`` as ``first_flagged``.
    """
    kept = []
    seen: set[str] = set()
    for _, r in pending.iterrows():
        nd = normalize_doi(r.get("doi", ""))
        if not nd or nd in incorporated or nd in seen:
            continue
        seen.add(nd)
        kept.append({"doi": r.get("doi", ""), "title": r.get("title", ""),
                     "first_flagged": r.get("first_flagged", "") or today})

    if not shortlist.empty and "doi" in shortlist.columns:
        for _, r in shortlist.iterrows():
            nd = normalize_doi(r.get("doi", ""))
            if not nd or nd in incorporated or nd in seen:
                continue
            seen.add(nd)
            kept.append({"doi": r.get("doi", ""),
                         "title": str(r.get("title", "")),
                         "first_flagged": today})

    return pd.DataFrame(kept, columns=COLUMNS)


def format_email_body(pending: pd.DataFrame) -> str:
    """Plain-text email body listing the papers still to check. '' if none."""
    if pending.empty:
        return ""
    lines = [
        f"{len(pending)} crustacean-neuropeptide paper(s) are waiting to be "
        f"checked for new sequences.",
        "",
        "A paper drops off this list automatically once its DOI appears in the "
        "database.",
        "",
    ]
    for _, r in pending.iterrows():
        title = str(r.get("title", "")).strip() or "(no title)"
        lines.append(f"- {title}")
        lines.append(f"    DOI: {r.get('doi', '')}    (flagged {r.get('first_flagged', '')})")
    lines.append("")
    lines.append("Source: monthly cNPDB literature scan.")
    return "\n".join(lines)


def _today() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Reconcile the papers-to-check list.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("reconcile", help="update the list and emit an email body")
    r.add_argument("--shortlist", default=None,
                   help="this month's shortlist CSV (optional; adds new papers)")
    r.add_argument("--db", default=DEFAULT_DB)
    r.add_argument("--list", default=DEFAULT_LIST, dest="list_path")
    r.add_argument("--body-out", default=None,
                   help="write the email body here (empty file if nothing to send)")
    r.add_argument("--date", default=None, help="first_flagged stamp (default: today)")

    args = ap.parse_args(argv)
    today = args.date or _today()

    pending = load_list(args.list_path)
    shortlist = (pd.read_csv(args.shortlist) if args.shortlist and os.path.exists(args.shortlist)
                 else pd.DataFrame(columns=["doi", "title"]))
    incorporated = known_dois(load_database(args.db))

    before = len(pending)
    updated = reconcile(pending, shortlist, incorporated, today)
    updated.to_csv(args.list_path, index=False)

    body = format_email_body(updated)
    if args.body_out:
        with open(args.body_out, "w", encoding="utf-8") as fh:
            fh.write(body)

    print(f"papers-to-check: {before} -> {len(updated)} "
          f"(shortlist rows: {len(shortlist)}; DOIs already in DB: {len(incorporated)})")
    return updated


if __name__ == "__main__":
    main()
