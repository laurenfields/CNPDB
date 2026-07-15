# -*- coding: utf-8 -*-
"""Merge reviewed additions into the cNPDB database.

**This is the only tool that writes the database.** Everything else in
DataCuration/ is read-only analysis.

It is deliberately paranoid, because a bad merge ships. Before writing anything
it re-validates the incoming rows and **refuses** the merge on any of:

* a sequence already present in the database (duplicate),
* a duplicate or colliding cNPDB ID,
* a non-standard residue, or an inline annotation such as ``(d)`` in ``Sequence``,
* a blank required field (``Sequence``/``Family``/``OS``/``Existence``),
* a ``Monoisotopic Mass`` that disagrees with sequence + declared PTM.

That last check is the point of the agreed convention: **the stored mass is the
[M+H]+ of the sequence plus every declared PTM.** So a row can only merge if its
mass is internally consistent with what it claims to be.

On success it writes a **new dated snapshot** -- the previous database file is
never overwritten -- and regenerates all three artifacts so they cannot drift:

    Assets/<YYYYMMDD>_cNPDB.xlsx
    Assets/<YYYYMMDD>_cNPDB.parquet
    <YYYYMMDD>_cNPDB_Full_Database.fasta

Usage::

    python -m DataCuration.merge_additions --additions DataCuration/staging/finalized_additions.xlsx --dry-run
    python -m DataCuration.merge_additions --additions DataCuration/staging/finalized_additions.xlsx --date 20260801
"""
from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DataCuration import cnpdb_qc as qc  # noqa: E402
from DataCuration.backfill import DB_COLUMNS  # noqa: E402
from utils import peptide_properties as pp  # noqa: E402
from utils import sequence_utils as su  # noqa: E402

REPO_ROOT = qc.REPO_ROOT
MASS_TOL = 0.02  # Da

# Scope ruling (2026-07): cNPDB is a **classical neuropeptide** resource.
# Antimicrobial and housekeeping-derived peptides are out of scope and are
# refused at merge time, so they stop resurfacing in every literature screen.
#
# This is FORWARD-LOOKING only. The shipping database already contains 35 such
# entries (16 Cryptocyanin, 2 Actin, 17 "Others") -- and one of them,
# LTEELANQEELLAK (cNPDB ID 855), is Figure 4D of the manuscript. Whether to
# retire those is a separate call for the team; this guard does not touch them.
NON_NEUROPEPTIDE_FAMILIES = {
    "amp", "hdap", "antimicrobial", "histone", "actin", "eif5a", "eif",
    "housekeeping", "cryptocyanin", "hemocyanin", "tubulin",
}


def is_out_of_scope(family) -> bool:
    """True if a family is antimicrobial/housekeeping rather than a neuropeptide."""
    fam = str(family).strip().lower()
    return any(bad in fam for bad in NON_NEUROPEPTIDE_FAMILIES)


def validate(additions: pd.DataFrame, db: pd.DataFrame) -> list[str]:
    """Return a list of blocking problems. Empty list == safe to merge."""
    problems: list[str] = []

    missing_cols = [c for c in ("Sequence", "cNPDB ID", "Family", "OS", "Existence",
                                "Monoisotopic Mass", "PTM") if c not in additions.columns]
    if missing_cols:
        return [f"additions are missing required column(s): {missing_cols}"]

    db_seqs = {str(s).upper() for s in db["Sequence"]}
    db_ids = set(int(i) for i in db["cNPDB ID"])

    seen_seqs: set[str] = set()
    seen_ids: set[int] = set()

    for _, r in additions.iterrows():
        raw = str(r["Sequence"])
        seq = raw.upper()
        cid = r["cNPDB ID"]
        tag = f"row cNPDB ID={cid} seq={seq[:24]!r}"

        if su.inline_modifications(raw):
            # Blocking on its own, and the mass check below cannot run on a
            # sequence that still carries an inline annotation.
            problems.append(f"{tag}: inline annotation in Sequence -- put it in PTM")
            continue
        bad = su.nonstandard_residues(raw)
        if bad:
            problems.append(f"{tag}: non-standard residue(s) {sorted(bad)}")
            continue

        if seq in db_seqs:
            problems.append(f"{tag}: sequence already in the database")
        if seq in seen_seqs:
            problems.append(f"{tag}: duplicated within the additions file")
        seen_seqs.add(seq)

        try:
            cid_i = int(cid)
        except (TypeError, ValueError):
            problems.append(f"{tag}: cNPDB ID is not an integer")
            continue
        if cid_i in db_ids:
            problems.append(f"{tag}: cNPDB ID {cid_i} collides with an existing entry")
        if cid_i in seen_ids:
            problems.append(f"{tag}: cNPDB ID {cid_i} duplicated within the additions")
        seen_ids.add(cid_i)

        for col in ("Family", "OS", "Existence"):
            v = r.get(col)
            if pd.isna(v) or str(v).strip() in ("", "nan", "VERIFY"):
                problems.append(f"{tag}: {col} is blank or still marked VERIFY")

        if is_out_of_scope(r.get("Family")):
            problems.append(
                f"{tag}: Family={r.get('Family')!r} is out of scope -- cNPDB is a "
                f"classical neuropeptide resource (antimicrobial/housekeeping-derived "
                f"peptides are excluded).")

        # The agreed convention: mass == [M+H]+ of sequence + declared PTMs.
        stored = r.get("Monoisotopic Mass")
        if pd.isna(stored):
            problems.append(f"{tag}: Monoisotopic Mass is blank")
        else:
            theo = pp.monoisotopic_mass(seq, r.get("PTM", "") or "", charged=True)
            if abs(float(stored) - theo) > MASS_TOL:
                problems.append(
                    f"{tag}: mass {float(stored):.4f} disagrees with sequence+PTM "
                    f"({theo:.4f}, delta {abs(float(stored) - theo):.3f} Da). "
                    f"PTM={r.get('PTM')!r} -- rerun `backfill finalize`.")
    return problems


def write_fasta(df: pd.DataFrame, path: str) -> None:
    """FASTA = the ID column as header, bare Sequence as the body."""
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for _, r in df.iterrows():
            fh.write(f"{r['ID']}\n{r['Sequence']}\n")


def merge(db: pd.DataFrame, additions: pd.DataFrame) -> pd.DataFrame:
    add = additions[[c for c in DB_COLUMNS if c in additions.columns]].copy()
    out = pd.concat([db, add], ignore_index=True)
    return out.sort_values("cNPDB ID").reset_index(drop=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Merge reviewed additions into cNPDB.")
    ap.add_argument("--db", default=qc.DEFAULT_DB)
    ap.add_argument("--additions", required=True, help="finalized additions .xlsx/.csv")
    ap.add_argument("--date", default=None, help="snapshot stamp, YYYYMMDD (default: today)")
    ap.add_argument("--dry-run", action="store_true", help="validate only; write nothing")
    args = ap.parse_args(argv)

    db = qc.load_database(args.db)
    additions = (pd.read_csv(args.additions) if args.additions.endswith(".csv")
                 else pd.read_excel(args.additions))
    print(f"Database: {len(db)} entries   Additions: {len(additions)} rows")

    problems = validate(additions, db)
    if problems:
        print(f"\nREFUSING TO MERGE -- {len(problems)} blocking problem(s):")
        for p in problems[:40]:
            print(f"  - {p}")
        if len(problems) > 40:
            print(f"  ... and {len(problems) - 40} more")
        return 1

    print("Validation passed: no duplicates, no ID collisions, all masses consistent "
          "with sequence + declared PTMs.")

    merged = merge(db, additions)

    # The merged database must itself be QC-clean of hard errors.
    issues = qc.run_all(merged)
    hard = issues[issues["severity"] == "high"]
    new_hard = len(hard) - int((qc.run_all(db)["severity"] == "high").sum())
    print(f"Post-merge QC: {len(merged)} entries, {len(hard)} high-severity issues "
          f"({new_hard:+d} vs before)")
    if new_hard > 0:
        print("REFUSING TO MERGE -- the merge would introduce new high-severity QC issues.")
        return 1

    if args.dry_run:
        print("\n--dry-run: nothing written. Merge would produce "
              f"{len(merged)} entries (+{len(additions)}).")
        return 0

    from datetime import datetime
    stamp = args.date or datetime.now().strftime("%Y%m%d")
    xlsx = os.path.join(REPO_ROOT, "Assets", f"{stamp}_cNPDB.xlsx")
    parquet = os.path.join(REPO_ROOT, "Assets", f"{stamp}_cNPDB.parquet")
    fasta = os.path.join(REPO_ROOT, f"{stamp}_cNPDB_Full_Database.fasta")
    for p in (xlsx, parquet, fasta):
        if os.path.exists(p):
            print(f"REFUSING TO MERGE -- {p} already exists; pass a different --date.")
            return 1

    merged.to_excel(xlsx, index=False)
    merged.to_parquet(parquet, index=False)
    write_fasta(merged, fasta)
    print(f"\nWrote {len(merged)} entries to:\n  {xlsx}\n  {parquet}\n  {fasta}")
    print("\nNEXT: point the app at the new snapshot (pages/1_NP_Database_Search.py and "
          "pages/2_Tools.py load the .parquet), update tests/test_database_integrity.py's "
          "expected row count, then run `python -m pytest`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
