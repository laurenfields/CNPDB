# cNPDB Data Curation & Maintenance

Tools for QC-ing the database and keeping it current with the literature.

## Contents

| File | Purpose |
|------|---------|
| `cnpdb_qc.py` | Quality-control engine (importable checks + CLI). |
| `lit_mining.py` | Literature-mining pipeline (`discover` new papers, `references` back-fill). |
| `coverage_audit.py` | Cross-check vs NeuroPep for overlooked sequences / missing species. |
| `backfill.py` | Stage missing sequences as reviewable cNPDB rows; `finalize` after PTM confirmation. |
| `os_tissue_completeness.py` | Per-peptide check for species/tissues reported in the literature but absent from `OS`/`Tissue`. |
| `QC_REPORT.md` | Human-readable findings from the latest QC run. |
| `qc_flagged_issues.csv` | Itemized, machine-readable QC findings. |
| `COVERAGE_AUDIT.md` | Overlooked-sequence / OS-completeness findings. |
| `candidate_new_sequences_2025-2026.md` | Candidate new sequences from recent literature. |
| `lit_scan/` | Committed monthly new-paper digests + persistent `seen_dois.txt` (created by CI). |
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

### Incremental / scheduled mining
The monthly GitHub Action (`.github/workflows/lit-mining.yml`) runs `discover`
with a **persistent seen-list** so each run surfaces only papers that are new
since the last scan, and **commits** a dated digest into `DataCuration/lit_scan/`:

```bash
python -m DataCuration.lit_mining discover --since 2025-01-01 \
    --seen DataCuration/lit_scan/seen_dois.txt --update-seen \
    --out DataCuration/lit_scan/new_papers_$(date +%F).csv
```

`--seen` excludes already-surfaced DOIs (on top of DOIs already in the DB);
`--update-seen` appends this run's DOIs so they don't reappear next month.

### Suggested cadence
Let the monthly Action run, triage `lit_scan/new_papers_*.csv`, then pull the
**Supplementary Information** of promising hits (SI tables hold most new sequences
and cannot be scraped automatically). See `candidate_new_sequences_2025-2026.md`.

### Crustacea-only scope filter
cNPDB covers **Crustacea only**. `lit_mining.classify_relevance()` scores a paper
from its title/abstract and keeps it only when it is *both* crustacean *and*
neuropeptide-related; `rank_by_relevance()` sorts a digest best-first. This is what
cuts a raw ~316-paper scan down to a screenable shortlist. A non-crustacean model
organism (Drosophila, mouse, …) only vetoes a paper when **no** crustacean signal is
present, so crustacean-vs-insect comparisons survive.

## Coverage audit (overlooked sequences & species)
```bash
python -m DataCuration.coverage_audit --outdir DataCuration
```
Cross-references cNPDB against the NeuroPep species files to find sequences that
were missed entirely and species missing from the `OS` column. Findings in
`COVERAGE_AUDIT.md` (+ `audit_overlooked_neuropep.csv`, `audit_os_underrepresented.csv`).

## Backfilling missing sequences
```bash
python -m DataCuration.backfill --out DataCuration/staging_additions.xlsx
```
Turns the overlooked list into schema-shaped rows: mapped family, resolved DOI/title,
computed physicochemical properties, next free cNPDB IDs.

**It does not write into the shipping database, by design.** `PTM` (amidation),
`Existence`, and `Tissue` cannot be known from the NeuroPep export, and guessing the
amidation state would reintroduce the exact mass errors the QC pass found. The staging
file therefore carries the **unmodified** mass, an `_mass_if_amidated` alternative, a
`_likely_amidated` hint from the family, and a `_VERIFY` column. Once a curator fills
`PTM`/`Existence`/`Tissue`:

```bash
python -m DataCuration.backfill finalize --staging DataCuration/staging_additions.xlsx
```
recomputes the mass from the confirmed PTM, rebuilds the `Active Sequence` and `ID`
header, and emits schema-clean rows ready to append.

## OS / tissue completeness
```bash
python -m DataCuration.os_tissue_completeness --limit 100 --out gaps.csv
```
For each peptide, searches the literature for its exact sequence and flags crustacean
species/tissues that papers mention but the `OS`/`Tissue` columns omit.

**These are screening candidates, not facts** — a species named in a paper that
mentions a peptide is not proof the peptide occurs there. Every proposed addition
cites its supporting paper so a curator can confirm. Peptides shorter than 6 aa are
skipped (short string matches retrieve too much unrelated literature).

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
