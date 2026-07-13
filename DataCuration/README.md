# cNPDB Data Curation & Maintenance

Tools for QC-ing the database and keeping it current with the literature.

## Contents

| File | Purpose |
|------|---------|
| `cnpdb_qc.py` | Quality-control engine (importable checks + CLI). |
| `lit_mining.py` | Literature-mining pipeline (`discover` new papers, `references` back-fill). |
| `QC_REPORT.md` | Human-readable findings from the latest QC run. |
| `qc_flagged_issues.csv` | Itemized, machine-readable QC findings. |
| `candidate_new_sequences_2025-2026.md` | Candidate new sequences from recent literature. |
| `auto_lit_search.py` | Original per-peptide reference search (kept for reference; superseded by `lit_mining.py`). |
| `APIretrieve_ESMfold.py` | Batch ESMFold structure retrieval. |
| `NeuroPepDatabases/` | Downloaded NeuroPep species files used during initial curation. |

## Quality control

```bash
# From the repo root:
python -m DataCuration.cnpdb_qc                     # QC the shipping DB, print summary
python -m DataCuration.cnpdb_qc --out issues.csv    # also write itemized CSV
python -m DataCuration.cnpdb_qc path/to/other.xlsx  # QC a candidate/updated file
```

Every check is a pure function in `cnpdb_qc.py` (`check_mass`, `check_length`,
`check_properties`, `check_duplicates`, …) so it can be reused and is covered by
`tests/test_qc.py`. Property and mass math lives in `utils/peptide_properties.py`
— the **same module the Streamlit Tools page imports**, so the app, the database,
and QC can never drift apart.

## Regular literature mining

`discover` finds recent on-topic papers whose DOI is **not** already cited in the
database, so a curator gets a short screening list each cycle:

```bash
python -m DataCuration.lit_mining discover --since 2025-01-01 --out new_papers.csv
python -m DataCuration.lit_mining discover --since 2026-01-01 --until 2026-06-30 --out h1.csv
```

Back-fill references for existing peptides:

```bash
python -m DataCuration.lit_mining references --limit 50 --out refs.csv   # test on 50
python -m DataCuration.lit_mining references --out refs.csv              # full run
```

Set `NCBI_API_KEY` (and optionally `NCBI_EMAIL`) in the environment to raise the
PubMed rate limit. Europe PMC (used for `discover`) needs no key.

### Suggested cadence
Run `discover --since <last-run-date>` monthly or quarterly, triage the CSV, then
pull the **Supplementary Information** of the promising hits (SI tables are where
most new sequences live and cannot be scraped automatically). See
`candidate_new_sequences_2025-2026.md` for the current backlog.

## Adding new entries — checklist
1. Store **bare residues** in `Sequence`; put every modification in the `PTM` column
   (never inline like `(d)` — see QC P2).
2. Compute `Monoisotopic Mass` **programmatically** from sequence + PTM
   (`utils.peptide_properties.monoisotopic_mass`), not by hand.
3. Fill `OS`, `Family` (from the controlled list), `Existence`, and `DOI`.
4. Run `python -m DataCuration.cnpdb_qc` and `python -m pytest` — both must pass.
5. Regenerate the `.parquet` and FASTA so all three artifacts stay in sync.
```

## Tests
```bash
pip install -r requirements-dev.txt
python -m pytest            # unit tests + database integrity gate
```
