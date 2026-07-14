# -*- coding: utf-8 -*-
"""Per-peptide species (OS) and tissue completeness checker.

For each peptide in cNPDB, search the literature for its exact sequence and
detect which crustacean **species** and **tissues** the retrieved papers mention.
Anything mentioned in the literature but absent from that peptide's ``OS`` /
``Tissue`` column is reported as a candidate gap.

Precision caveat -- read before acting on the output
----------------------------------------------------
A species/tissue named in a paper that mentions a peptide is **not proof** that
the peptide was found in that species/tissue: a paper may discuss several
species, or cite a peptide in passing. These are **screening candidates for human
confirmation**, not facts. Two guards are applied:

* peptides shorter than ``MIN_SEQ_LEN`` (default 6) are skipped -- a 5-mer string
  match retrieves too much unrelated literature to be informative;
* the source paper is reported alongside every proposed addition so a curator can
  check it directly.

For the 8 species covered by a NeuroPep export, ``coverage_audit`` gives a
higher-confidence answer; this module generalizes to the other species and to
tissue, which NeuroPep does not carry.

Usage::

    python -m DataCuration.os_tissue_completeness --limit 50 --out gaps.csv
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DataCuration.cnpdb_qc import DEFAULT_DB, OUTPUTS_DIR, load_database  # noqa: E402
from DataCuration.lit_mining import europepmc_search  # noqa: E402

MIN_SEQ_LEN = 6

# cNPDB OS abbreviation -> literature match terms (scientific + common names).
SPECIES_TERMS: dict[str, set[str]] = {
    "Cbo": {"cancer borealis", "jonah crab"},
    "Cirr": {"cancer irroratus", "atlantic rock crab"},
    "Cmae": {"carcinus maenas", "green crab"},
    "Cmag": {"cancer magister", "metacarcinus magister", "dungeness crab"},
    "Cpag": {"cancer pagurus", "edible crab", "brown crab"},
    "Cpro": {"cancer productus", "red rock crab"},
    "Csap": {"callinectes sapidus", "blue crab"},
    "Dpu": {"daphnia pulex", "water flea"},
    "Arm": {"armadillidium", "woodlouse"},
    "Eur": {"eurydice"},
    "HoA": {"homarus americanus", "american lobster"},
    "Lma": {"lithodes maja", "norway king crab"},
    "Lva": {"litopenaeus vannamei", "penaeus vannamei", "pacific white shrimp",
            "whiteleg shrimp"},
    "Mens": {"metapenaeus ensis", "greasyback shrimp"},
    "Mjap": {"marsupenaeus japonicus", "kuruma shrimp", "kuruma prawn"},
    "Mlan": {"macrobrachium lanchesteri"},
    "Mros": {"macrobrachium rosenbergii", "giant river prawn"},
    "Nnor": {"nephrops norvegicus", "norway lobster"},
    "Oce": {"ocypode ceratophthalm", "ghost crab"},
    "Olim": {"orconectes limosus", "spinycheek crayfish"},
    "Paz": {"penaeus aztecus", "brown shrimp"},
    "Pbo": {"pandalus borealis", "northern prawn"},
    "Pbou": {"procambarus bouvieri"},
    "Pcla": {"procambarus clarkii", "red swamp crayfish", "crayfish"},
    "Pint": {"panulirus interruptus", "california spiny lobster"},
    "Pmon": {"penaeus monodon", "giant tiger prawn", "black tiger shrimp"},
    "Ppro": {"pugettia producta", "kelp crab"},
    "Spar": {"scylla paramamosain", "mud crab"},
    "Sser": {"scylla serrata", "giant mud crab"},
    "Sver": {"sagmariasus verreauxi", "rock lobster"},
}

# cNPDB Tissue abbreviation -> literature match terms.
TISSUE_TERMS: dict[str, set[str]] = {
    "Br": {"brain", "supraoesophageal ganglion", "supraesophageal ganglion"},
    "PO": {"pericardial organ"},
    "SG": {"sinus gland"},
    "ES": {"eyestalk", "eye stalk"},
    "CoG": {"commissural ganglion"},
    "STG": {"stomatogastric ganglion"},
    "hemolymph": {"hemolymph", "haemolymph"},
    "VNC": {"ventral nerve cord"},
    "OG": {"oesophageal ganglion", "esophageal ganglion"},
    "TG": {"thoracic ganglion"},
    "CG": {"cardiac ganglion"},
    "CNS": {"central nervous system"},
    "OVR": {"ovary", "ovarian"},
}


def _detect(text: str, vocab: dict[str, set[str]]) -> set[str]:
    low = str(text).lower()
    return {abbr for abbr, terms in vocab.items() if any(t in low for t in terms)}


def detect_species(text: str) -> set[str]:
    """Crustacean species (as cNPDB OS abbreviations) named in a block of text."""
    return _detect(text, SPECIES_TERMS)


def detect_tissues(text: str) -> set[str]:
    """Neural/other tissues (as cNPDB abbreviations) named in a block of text."""
    return _detect(text, TISSUE_TERMS)


def split_tokens(cell) -> set[str]:
    """Parse a cNPDB OS/Tissue cell into a token set."""
    return {t.strip() for t in re.split(r"[;,/]", str(cell))
            if t.strip() and t.strip().lower() not in ("nan", "none")}


def check_peptide(sequence: str, current_os: set[str], current_tissue: set[str],
                  session: requests.Session | None = None,
                  max_pages: int = 1) -> dict:
    """Search the literature for ``sequence`` and diff mentions against cNPDB.

    Returns lit-detected species/tissues, the gaps, and the supporting papers.
    """
    hits = europepmc_search(f'"{sequence}"', page_size=25, max_pages=max_pages,
                            session=session)
    lit_species: set[str] = set()
    lit_tissue: set[str] = set()
    papers = []
    for h in hits:
        text = f"{h.get('title', '')} {h.get('journal', '')}"
        sp, ti = detect_species(text), detect_tissues(text)
        if sp or ti:
            papers.append(h.get("doi") or h.get("pmid") or "")
        lit_species |= sp
        lit_tissue |= ti
    return {
        "Sequence": sequence,
        "cNPDB_OS": ";".join(sorted(current_os)),
        "cNPDB_Tissue": ";".join(sorted(current_tissue)),
        "lit_species": ";".join(sorted(lit_species)),
        "lit_tissue": ";".join(sorted(lit_tissue)),
        "missing_OS": ";".join(sorted(lit_species - current_os)),
        "missing_Tissue": ";".join(sorted(lit_tissue - current_tissue)),
        "n_papers": len(hits),
        "supporting": ";".join(sorted({p for p in papers if p})[:5]),
    }


def run(db: pd.DataFrame, limit: int | None = None, min_len: int = MIN_SEQ_LEN,
        sleep: float = 0.34, session: requests.Session | None = None) -> pd.DataFrame:
    """Check peptides and return only those with a candidate OS/Tissue gap."""
    session = session or requests.Session()
    rows, checked, skipped = [], 0, 0
    for _, r in db.iterrows():
        seq = str(r["Sequence"]).upper()
        if len(seq) < min_len:
            skipped += 1
            continue
        res = check_peptide(seq, split_tokens(r.get("OS")), split_tokens(r.get("Tissue")),
                            session=session)
        res["cNPDB ID"] = r["cNPDB ID"]
        res["Family"] = r.get("Family")
        if res["missing_OS"] or res["missing_Tissue"]:
            rows.append(res)
        checked += 1
        if limit and checked >= limit:
            break
        time.sleep(sleep)
    cols = ["cNPDB ID", "Sequence", "Family", "cNPDB_OS", "missing_OS",
            "cNPDB_Tissue", "missing_Tissue", "lit_species", "lit_tissue",
            "n_papers", "supporting"]
    out = pd.DataFrame(rows, columns=cols)
    print(f"Checked {checked} peptides (skipped {skipped} shorter than {min_len} aa); "
          f"{len(out)} have a candidate gap.")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Per-peptide OS/tissue completeness check.")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--limit", type=int, default=None, help="check only the first N peptides")
    ap.add_argument("--min-len", type=int, default=MIN_SEQ_LEN)
    ap.add_argument("--out", default=os.path.join(OUTPUTS_DIR, "os_tissue_gaps.csv"))
    args = ap.parse_args(argv)

    db = load_database(args.db)
    out = run(db, limit=args.limit, min_len=args.min_len)
    out.to_csv(args.out, index=False)
    print(f"Wrote {len(out)} candidate gaps -> {args.out}")
    return out


if __name__ == "__main__":
    main()
