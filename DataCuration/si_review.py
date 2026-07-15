# -*- coding: utf-8 -*-
"""SI-review queue: track papers whose supplementary info needs a manual pull.

Sequences usually live in a paper's Supplementary Information, and SI often
cannot be fetched automatically (paywall, CAPTCHA, or spreadsheet-only formats).
This module maintains a persistent queue of such papers so nothing gets lost
between the automated scan and a human's manual extraction.

Home: ``DataCuration/si_review/``
  * ``queue.csv``  -- the manifest (one row per paper)
  * ``files/``     -- drop the downloaded SI here, ideally in a per-DOI subfolder

The queue is **append-and-update**, never rewritten: ``scan`` only adds papers
not already present, so a human's ``status``/``notes`` edits are preserved across
CI runs. Columns::

    doi, title, species, reason, si_url, is_open_access, date_added, status, notes

``reason``  -- why manual: paywalled | captcha | spreadsheet_only | precursors_only | other
``status``  -- pending | in_progress | done | dropped

CLI::

    python -m DataCuration.si_review scan --shortlist DataCuration/outputs/shortlist_<date>.csv
    python -m DataCuration.si_review add --doi 10.x/y --title "..." --reason paywalled --url http://...
    python -m DataCuration.si_review list                 # pending items
    python -m DataCuration.si_review done --doi 10.x/y --note "extracted 12 seqs"
"""
from __future__ import annotations

import argparse
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DataCuration.cnpdb_qc import CURATION_DIR  # noqa: E402
from DataCuration.lit_mining import normalize_doi  # noqa: E402

SI_DIR = os.path.join(CURATION_DIR, "si_review")
QUEUE_CSV = os.path.join(SI_DIR, "queue.csv")
FILES_DIR = os.path.join(SI_DIR, "files")
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

COLUMNS = ["doi", "title", "species", "reason", "si_url", "is_open_access",
           "date_added", "status", "notes"]
VALID_STATUS = {"pending", "in_progress", "done", "dropped"}


# ---------------------------------------------------------------------------
# Pure queue operations (unit-tested)
# ---------------------------------------------------------------------------
def load_queue(path: str = QUEUE_CSV) -> pd.DataFrame:
    if path and os.path.exists(path):
        df = pd.read_csv(path, dtype=str).fillna("")
        for c in COLUMNS:
            if c not in df.columns:
                df[c] = ""
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)


def _key(doi: str) -> str:
    return normalize_doi(doi)


def upsert(queue: pd.DataFrame, entry: dict) -> pd.DataFrame:
    """Add a paper if its DOI is new; otherwise leave the existing row untouched.

    Returns a new DataFrame. Existing human edits (status/notes) are preserved --
    an already-queued DOI is never overwritten by a re-scan.
    """
    entry = {**{c: "" for c in COLUMNS}, **entry}
    entry["doi"] = _key(entry.get("doi", ""))
    if not entry["doi"]:
        return queue  # cannot track a paper with no DOI
    if not entry.get("status"):
        entry["status"] = "pending"
    existing = set(queue["doi"].map(_key))
    if entry["doi"] in existing:
        return queue
    return pd.concat([queue, pd.DataFrame([entry])[COLUMNS]], ignore_index=True)


def set_status(queue: pd.DataFrame, doi: str, status: str, note: str = "") -> pd.DataFrame:
    if status not in VALID_STATUS:
        raise ValueError(f"status must be one of {sorted(VALID_STATUS)}")
    q = queue.copy()
    mask = q["doi"].map(_key) == _key(doi)
    if not mask.any():
        raise KeyError(f"DOI {doi!r} not in queue")
    q.loc[mask, "status"] = status
    if note:
        q.loc[mask, "notes"] = note
    return q


def pending(queue: pd.DataFrame) -> pd.DataFrame:
    return queue[queue["status"].isin(["pending", "in_progress"])]


# ---------------------------------------------------------------------------
# Access status (network)
# ---------------------------------------------------------------------------
def access_status(doi: str, session: requests.Session | None = None) -> dict:
    """Europe PMC access flags for a DOI. Empty dict on lookup failure.

    ``open_access`` True means the full text (and thus SI) is fetchable in EPMC;
    False/absent means a manual pull is likely needed.
    """
    session = session or requests.Session()
    try:
        r = session.get(EPMC, params={"query": f"DOI:{doi}", "format": "json",
                                       "resultType": "core"}, timeout=30)
        r.raise_for_status()
        res = r.json().get("resultList", {}).get("result", [])
        if not res:
            return {}
        h = res[0]
        return {"open_access": h.get("isOpenAccess") == "Y",
                "in_epmc": h.get("inEPMC") == "Y",
                "has_suppl": h.get("hasSuppl") == "Y",
                "pmid": h.get("pmid", "")}
    except Exception:
        return {}


def needs_manual_si(status: dict) -> bool:
    """True when SI cannot be fetched programmatically (paper not OA / not in EPMC).

    Conservative: an unknown status (empty dict) is treated as needing review.
    """
    if not status:
        return True
    return not (status.get("open_access") and status.get("in_epmc"))


# ---------------------------------------------------------------------------
# Scan a shortlist and enqueue the blocked papers
# ---------------------------------------------------------------------------
def scan_shortlist(shortlist: pd.DataFrame, queue: pd.DataFrame,
                   date_added: str, session: requests.Session | None = None) -> pd.DataFrame:
    """Add shortlist papers whose SI likely needs a manual pull to the queue."""
    session = session or requests.Session()
    for _, r in shortlist.iterrows():
        doi = str(r.get("doi", ""))
        if not normalize_doi(doi):
            continue
        st = access_status(doi, session=session)
        if not needs_manual_si(st):
            continue
        queue = upsert(queue, {
            "doi": doi,
            "title": str(r.get("title", "")),
            "species": str(r.get("species", "")),
            "reason": "paywalled" if st and not st.get("open_access") else "other",
            "si_url": "",
            "is_open_access": "Y" if st.get("open_access") else "N",
            "date_added": date_added,
            "status": "pending",
        })
    return queue


def save_queue(queue: pd.DataFrame, path: str = QUEUE_CSV) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    queue.sort_values(["status", "date_added"]).to_csv(path, index=False)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="cNPDB SI-review queue.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="add blocked shortlist papers to the queue")
    s.add_argument("--shortlist", required=True)
    s.add_argument("--date", default=None, help="date_added stamp (default: today)")

    a = sub.add_parser("add", help="manually queue one paper")
    a.add_argument("--doi", required=True)
    a.add_argument("--title", default="")
    a.add_argument("--species", default="")
    a.add_argument("--reason", default="other")
    a.add_argument("--url", default="", dest="si_url")
    a.add_argument("--date", default=None)

    d = sub.add_parser("done", help="mark a queued paper resolved")
    d.add_argument("--doi", required=True)
    d.add_argument("--note", default="")
    d.add_argument("--status", default="done", choices=sorted(VALID_STATUS))

    sub.add_parser("list", help="show pending items")

    args = ap.parse_args(argv)

    def _today():
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")

    queue = load_queue()

    if args.cmd == "scan":
        shortlist = pd.read_csv(args.shortlist)
        before = len(queue)
        queue = scan_shortlist(shortlist, queue, args.date or _today())
        save_queue(queue)
        print(f"Scanned {len(shortlist)} papers; queue {before} -> {len(queue)} "
              f"({len(pending(queue))} pending). -> {QUEUE_CSV}")
    elif args.cmd == "add":
        queue = upsert(queue, {"doi": args.doi, "title": args.title,
                               "species": args.species, "reason": args.reason,
                               "si_url": args.si_url, "date_added": args.date or _today(),
                               "status": "pending"})
        save_queue(queue)
        print(f"Queued {args.doi}. {len(pending(queue))} pending. -> {QUEUE_CSV}")
    elif args.cmd == "done":
        queue = set_status(queue, args.doi, args.status, args.note)
        save_queue(queue)
        print(f"Marked {args.doi} {args.status}.")
    elif args.cmd == "list":
        p = pending(queue)
        if p.empty:
            print("SI-review queue is empty.")
        else:
            print(f"{len(p)} paper(s) awaiting manual SI extraction:\n")
            for _, r in p.iterrows():
                print(f"  [{r['status']:<11}] {r['doi']}  ({r['reason']})")
                print(f"                {str(r['title'])[:76]}")
                if r["si_url"]:
                    print(f"                SI: {r['si_url']}")
    return queue


if __name__ == "__main__":
    main()
