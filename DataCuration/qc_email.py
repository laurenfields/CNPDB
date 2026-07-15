# -*- coding: utf-8 -*-
"""Run QC on the database and produce an email body for the accuracy alert.

Used by the ``db-accuracy`` workflow after Jacey pushes an updated database.
Writes the flagged-issues CSV, writes a plain-text email body to ``--body-out``,
and prints the number of issues to stdout (so the workflow can decide whether to
send). Finding issues never blocks the database update -- it only notifies.
"""
from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DataCuration import cnpdb_qc as qc  # noqa: E402


def build_body(issues: pd.DataFrame, db_len: int) -> str:
    n = len(issues)
    if n == 0:
        return "The updated cNPDB database passed QC with no flagged issues."
    lines = [
        f"The updated cNPDB database has {n} flagged QC issue(s) across "
        f"{db_len} entries.",
        "These do NOT block the database update, but should be checked.",
        "",
        "By severity:",
    ]
    lines += [f"  {sev}: {c}" for sev, c in issues["severity"].value_counts().items()]
    lines += ["", "By category:"]
    lines += [f"  {cat}: {c}" for cat, c in issues["category"].value_counts().items()]
    lines += ["", "The full itemized list is committed to "
              "DataCuration/outputs/qc_flagged_issues.csv"]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="QC the DB and emit an email body.")
    ap.add_argument("--db", default=qc.DEFAULT_DB)
    ap.add_argument("--out", default=os.path.join(qc.OUTPUTS_DIR, "qc_flagged_issues.csv"))
    ap.add_argument("--body-out", default=None)
    args = ap.parse_args(argv)

    db = qc.load_database(args.db)
    issues = qc.run_all(db)
    if args.out:
        issues.to_csv(args.out, index=False)
    body = build_body(issues, len(db))
    if args.body_out:
        with open(args.body_out, "w", encoding="utf-8") as fh:
            fh.write(body)
    # Stdout is the issue count, for the workflow's send condition.
    print(len(issues))
    return len(issues)


if __name__ == "__main__":
    main()
