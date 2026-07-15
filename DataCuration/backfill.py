# -*- coding: utf-8 -*-
"""Build a reviewable staging table for sequences missing from cNPDB.

Takes the overlooked-sequence list produced by ``coverage_audit`` and turns it
into rows matching the cNPDB schema: mapped family, resolved DOI/title, computed
physicochemical properties, and the next free cNPDB IDs.

**This deliberately does not write into the shipping database.** Three fields
cannot be known from the NeuroPep export alone and must be confirmed against the
source paper:

* ``PTM``       -- most crustacean neuropeptides are C-terminally amidated, which
  shifts the monoisotopic mass by -0.984 Da. Guessing here would reintroduce the
  exact class of mass error the QC pass found, so the staging file reports the
  unmodified mass **and** the amidated mass and flags the row.
* ``Existence`` -- evidence level (Predicted / MS / MSMS / Denovo).
* ``Tissue``    -- not present in the NeuroPep export.

Workflow::

    python -m DataCuration.backfill --out DataCuration/staging_additions.xlsx
    # curator fills PTM / Existence / Tissue in the xlsx, then:
    python -m DataCuration.backfill finalize --staging DataCuration/staging_additions.xlsx

``finalize`` recomputes the monoisotopic mass from the confirmed PTM and emits
schema-clean rows ready to append.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import pandas as pd
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DataCuration.cnpdb_qc import DEFAULT_DB, OUTPUTS_DIR, STAGING_DIR, load_database  # noqa: E402
from utils import peptide_properties as pp  # noqa: E402

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

DB_COLUMNS = [
    "ID", "Sequence", "Active Sequence", "cNPDB ID", "Family", "OS", "Tissue",
    "Existence", "Monoisotopic Mass", "Length", "GRAVY", "% Hydrophobic Residue",
    "PTM", "Instability Index", "Instability Index Value", "Isoelectric Point (pI)",
    "Net Charge (pH 7.0)", "Boman Index", "Aliphatic Index", "MSI Tissue 1",
    "MSI Tissue 2", "MSI Tissue 3", "DOI", "Source", "Title", "Topic",
    "Instrument", "Technique",
]

# NeuroPep family -> cNPDB family vocabulary.
FAMILY_MAP = {
    "arthropod chh/mih/gih/vih hormone": "CHH",
    "orcokinin": "Orcokinin",
    "pyrokinin": "Pyrokinin",
    "fmrfamide related peptide": "RFamide",
    "allatostatin": "Allatostatin-A_type",
    "arthropod pdh": "PDH",
    "tachykinin": "Tachykinin",
    "npy": "NPF",
}
# Families whose members are, as a rule, C-terminally amidated. Used only to
# HINT the curator -- never to set the mass.
TYPICALLY_AMIDATED = {
    "RFamide", "RYamide", "Allatostatin-A_type", "Allatostatin-B_type", "PDH",
    "Pyrokinin", "Tachykinin", "RPCH", "SIFamide", "CCAP", "Leucokinin",
    "Kinins", "sNPF", "NPF", "HIGSLYRamide", "GSEFLamide", "Corazonin",
}


def map_family(neuropep_family, name="") -> str:
    """Map a NeuroPep family (refined by the peptide Name) to cNPDB vocabulary."""
    fam = str(neuropep_family).strip().lower()
    nm = str(name).strip().lower()
    if fam in ("", "nan", "none"):
        return "Others"
    # Allatostatin subtypes are distinguished by the Name field.
    if fam == "allatostatin":
        if "b" in nm.split() or "type b" in nm or nm.endswith(" b"):
            return "Allatostatin-B_type"
        if "c" in nm.split() or "type c" in nm or nm.endswith(" c"):
            return "Allatostatin-C_type"
        return "Allatostatin-A_type"
    # CHH superfamily: MIH / MOIH / GIH split out by Name where stated.
    if fam.startswith("arthropod chh"):
        if "molt-inhibiting" in nm or "molt inhibiting" in nm or nm.startswith("mih"):
            return "MIH"
        if "mandibular organ" in nm or nm.startswith("moih"):
            return "MOIH"
        return "CHH"
    return FAMILY_MAP.get(fam, "Others")


def likely_amidated(cnpdb_family: str) -> bool:
    return cnpdb_family in TYPICALLY_AMIDATED


def resolve_pmid(pmid, session: requests.Session | None = None) -> dict:
    """Look up DOI + title for a PMID via Europe PMC. Returns {} on failure."""
    pmid = str(pmid).split(".")[0].strip()
    if not pmid or pmid.lower() == "nan":
        return {}
    session = session or requests.Session()
    try:
        r = session.get(EPMC, params={"query": f"EXT_ID:{pmid} AND SRC:MED",
                                      "format": "json", "resultType": "core"}, timeout=30)
        r.raise_for_status()
        hits = r.json().get("resultList", {}).get("result", [])
        if hits:
            h = hits[0]
            return {"DOI": h.get("doi", ""), "Title": h.get("title", "")}
    except Exception:
        pass
    return {}


def make_id_header(cnpdb_id, family, os_abbr, existence, mz, tissue, seq) -> str:
    """Build the cNPDB FASTA/ID header.

    Matches the shipping convention: multi-value OS/Tissue are joined with ``_``
    (not ``;``), and ``Seq=`` carries the **active** sequence (with PTM suffix),
    e.g. ``>cNP|0003 Family=... OS=Cbo_Cpro ... Tissue=PO_PO Seq=YSFGLamide``.
    """
    def _join(v):
        return str(v).replace(";", "_").replace(",", "_").strip() if v else "VERIFY"
    return (f">cNP|{int(cnpdb_id):04d} Family={family} OS={_join(os_abbr)} "
            f"Existence={existence or 'VERIFY'} mz={mz} "
            f"Tissue={_join(tissue)} Seq={seq}")


def build_staging(overlooked: pd.DataFrame, db: pd.DataFrame,
                  resolve: bool = True, session=None) -> pd.DataFrame:
    """Build schema-shaped staging rows for the overlooked sequences."""
    next_id = int(db["cNPDB ID"].max()) + 1
    rows = []
    cache: dict[str, dict] = {}
    for _, r in overlooked.sort_values(["Species", "Sequence"]).iterrows():
        seq = str(r["Sequence"]).upper()
        family = map_family(r.get("Family"), r.get("Name"))
        props = pp.calculate_properties(seq)
        mass_unmod = pp.monoisotopic_mass(seq, "", charged=True)
        mass_amid = pp.monoisotopic_mass(seq, "Amidation", charged=True)
        amid_hint = likely_amidated(family)

        meta = {}
        if resolve:
            key = str(r.get("PMID"))
            if key not in cache:
                cache[key] = resolve_pmid(key, session)
                time.sleep(0.25)
            meta = cache[key]

        row = {c: "" for c in DB_COLUMNS}
        row.update({
            "Sequence": seq,
            "Active Sequence": seq,          # VERIFY: add 'amide' etc. once PTM confirmed
            "cNPDB ID": next_id,
            "Family": family,
            "OS": r.get("OS_abbr", ""),
            "Tissue": "",                    # VERIFY
            "Existence": "",                 # VERIFY
            "Monoisotopic Mass": round(mass_unmod, 5),   # VERIFY if amidated
            "Length": props["Length"],
            "GRAVY": props["GRAVY Score"],
            "% Hydrophobic Residue": props["% Hydrophobic Residue"],
            "PTM": "",                       # VERIFY
            "Instability Index": props["Instability Index"].replace("stable", "Stable")
                                                            .replace("unStable", "Unstable"),
            "Instability Index Value": float(props["Instability Index"].split()[0]),
            "Isoelectric Point (pI)": props["Isoelectric Point (pI)"],
            "Net Charge (pH 7.0)": props["Net Charge (pH 7.0)"],
            "Boman Index": props["Boman Index"],
            "Aliphatic Index": props["Aliphatic Index"],
            "DOI": meta.get("DOI", ""),
            "Source": "NeuroPep",
            "Title": meta.get("Title", ""),
        })
        row["ID"] = make_id_header(next_id, family, row["OS"], "", row["Monoisotopic Mass"],
                                   "", seq)
        # Review-only columns (dropped by finalize).
        row["_neuropep_family"] = r.get("Family")
        row["_neuropep_name"] = r.get("Name")
        row["_PMID"] = r.get("PMID")
        row["_likely_amidated"] = amid_hint
        row["_mass_if_amidated"] = round(mass_amid, 5)
        row["_VERIFY"] = "PTM(amidation?); Existence; Tissue" + \
                         ("; mass shown is UNMODIFIED but family is usually amidated"
                          if amid_hint else "")
        rows.append(row)
        next_id += 1
    return pd.DataFrame(rows)


def finalize(staging: pd.DataFrame) -> pd.DataFrame:
    """Recompute mass from the curator-confirmed PTM and drop review columns."""
    out = staging.copy()
    for i, r in out.iterrows():
        seq = str(r["Sequence"]).upper()
        ptm = str(r.get("PTM", "") or "")
        mass = pp.monoisotopic_mass(seq, ptm, charged=True)
        out.at[i, "Monoisotopic Mass"] = round(mass, 5)
        active = seq + ("amide" if "amidation" in ptm.lower() else "")
        out.at[i, "Active Sequence"] = active
        out.at[i, "ID"] = make_id_header(r["cNPDB ID"], r["Family"], r["OS"],
                                         r.get("Existence", ""), round(mass, 5),
                                         r.get("Tissue", ""), active)
    return out[[c for c in DB_COLUMNS if c in out.columns]]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage/finalize cNPDB additions.")
    sub = ap.add_subparsers(dest="mode")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--overlooked",
                    default=os.path.join(OUTPUTS_DIR, "audit_overlooked_neuropep.csv"))
    ap.add_argument("--out", default=os.path.join(STAGING_DIR, "staging_additions.xlsx"))
    ap.add_argument("--no-resolve", action="store_true", help="skip PMID->DOI lookup")

    f = sub.add_parser("finalize", help="recompute mass from confirmed PTM")
    f.add_argument("--staging", default=os.path.join(STAGING_DIR, "staging_additions.xlsx"))
    f.add_argument("--out", default=os.path.join(STAGING_DIR, "finalized_additions.xlsx"))

    args = ap.parse_args(argv)

    if args.mode == "finalize":
        st = pd.read_excel(args.staging)
        out = finalize(st)
        out.to_excel(args.out, index=False)
        print(f"Finalized {len(out)} rows -> {args.out}")
        return out

    db = load_database(args.db)
    over = pd.read_csv(args.overlooked)
    staging = build_staging(over, db, resolve=not args.no_resolve)
    staging.to_excel(args.out, index=False)
    print(f"Staged {len(staging)} additions (cNPDB IDs "
          f"{staging['cNPDB ID'].min()}-{staging['cNPDB ID'].max()}) -> {args.out}")
    print(f"  DOIs resolved: {(staging['DOI'].astype(str).str.len() > 0).sum()}/{len(staging)}")
    print(f"  flagged likely-amidated (mass needs confirming): "
          f"{int(staging['_likely_amidated'].sum())}")
    print("\nBy family:")
    print(staging["Family"].value_counts().to_string())
    return staging


if __name__ == "__main__":
    main()
