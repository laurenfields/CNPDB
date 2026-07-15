# -*- coding: utf-8 -*-
"""Coverage audit: find sequences/species the original curation may have missed.

Cross-references cNPDB against the NeuroPep species files in
``DataCuration/NeuroPepDatabases/`` (the source used during initial curation) to
surface two kinds of gap:

* ``overlooked``  -- a NeuroPep sequence that is **not in cNPDB at all**.
* ``os_gap``      -- a sequence that **is** in cNPDB but whose ``OS`` column is
  missing the species NeuroPep assigns it to (species under-representation).
  Split into ``os_blank`` (cNPDB has no OS at all) and ``os_partial``
  (OS populated but this species absent).

These are *candidates for human review*, not automatic edits: NeuroPep includes
predicted/transcriptomic assignments that empirical cNPDB may intentionally
exclude. NeuroPep files carry no tissue column, so this audit covers species
(OS) completeness only; tissue completeness needs per-paper mining.

Usage::

    python -m DataCuration.coverage_audit
    python -m DataCuration.coverage_audit --outdir DataCuration
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DataCuration.cnpdb_qc import DEFAULT_DB, OUTPUTS_DIR, load_database  # noqa: E402
from utils.peptide_properties import STANDARD_AA  # noqa: E402
from utils.sequence_utils import strip_inline_modifications  # noqa: E402

NEUROPEP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "NeuroPepDatabases")

# NeuroPep file stem (species) -> cNPDB OS abbreviation.
SPECIES_TO_OS = {
    "Callinectes_sapidus": "Csap",
    "Cancer_borealis": "Cbo",
    "Carcinus_maenas": "Cmae",
    "Homarus_americanus": "HoA",
    "Litopenaeus_vannamei": "Lva",
    "Ocypode_ceratophthalma": "Oce",
    "Orconectes_limosus": "Olim",
    "Procambarus_clarkii": "Pcla",
}


def bare(seq: str) -> str:
    return strip_inline_modifications(seq).upper().strip()


def os_tokens(cell) -> set[str]:
    return {t.strip() for t in re.split(r"[;,/]", str(cell))
            if t.strip() and t.strip().lower() != "nan"}


def build_db_index(df: pd.DataFrame) -> dict[str, set[str]]:
    """Map bare sequence -> set of OS abbreviations recorded in cNPDB."""
    index: dict[str, set[str]] = {}
    for _, r in df.iterrows():
        index.setdefault(bare(r["Sequence"]), set()).update(os_tokens(r.get("OS")))
    return index


def classify(seq: str, os_abbr: str | None, db_index: dict[str, set[str]]) -> str | None:
    """Return the gap category for one NeuroPep (sequence, species), or None."""
    if set(seq) - STANDARD_AA:
        return None  # skip non-standard / precursor annotations
    if seq not in db_index:
        return "overlooked"
    if os_abbr and os_abbr not in db_index[seq]:
        return "os_blank" if not db_index[seq] else "os_partial"
    return None


def audit(df: pd.DataFrame, neuropep_dir: str = NEUROPEP_DIR) -> dict[str, pd.DataFrame]:
    db_index = build_db_index(df)
    rows = {"overlooked": [], "os_gap": []}
    for path in sorted(glob.glob(os.path.join(neuropep_dir, "*.txt"))):
        species = os.path.splitext(os.path.basename(path))[0]
        os_abbr = SPECIES_TO_OS.get(species)
        npdf = pd.read_csv(path, sep="\t")
        for _, r in npdf.iterrows():
            seq = bare(r["Sequence"])
            cat = classify(seq, os_abbr, db_index)
            if cat is None:
                continue
            rec = {"Sequence": seq, "Species": species, "OS_abbr": os_abbr,
                   "Family": r.get("Family", ""), "Name": r.get("Name", ""),
                   "PMID": r.get("PMID", "")}
            if cat == "overlooked":
                rows["overlooked"].append(rec)
            else:
                rec["gap_type"] = cat
                rec["cNPDB_OS"] = ";".join(sorted(db_index[seq]))
                rows["os_gap"].append(rec)
    return {
        "overlooked": pd.DataFrame(rows["overlooked"]).drop_duplicates(["Sequence", "OS_abbr"]),
        "os_gap": pd.DataFrame(rows["os_gap"]).drop_duplicates(["Sequence", "OS_abbr"]),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="cNPDB coverage audit vs NeuroPep.")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--neuropep-dir", default=NEUROPEP_DIR)
    ap.add_argument("--outdir", default=OUTPUTS_DIR, help="write CSVs here")
    args = ap.parse_args(argv)

    df = load_database(args.db)
    result = audit(df, args.neuropep_dir)
    over, gap = result["overlooked"], result["os_gap"]

    print(f"Overlooked (in NeuroPep, absent from cNPDB): {len(over)}")
    if not over.empty:
        print(over.groupby("Species").size().to_string())
    print(f"\nOS gaps (in cNPDB, species missing from OS): {len(gap)}")
    if not gap.empty:
        print(gap.groupby(["gap_type"]).size().to_string())
        print(gap.groupby("Species").size().to_string())
    if args.outdir:
        over.to_csv(os.path.join(args.outdir, "audit_overlooked_neuropep.csv"), index=False)
        gap.to_csv(os.path.join(args.outdir, "audit_os_underrepresented.csv"), index=False)
        print(f"\nWrote audit CSVs to {args.outdir}")
    return result


if __name__ == "__main__":
    main()
