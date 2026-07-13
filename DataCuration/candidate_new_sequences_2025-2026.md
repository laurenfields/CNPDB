# Candidate New Sequences — 2025–2026 Literature Screen

Snapshot date: 2026-07. Method: `lit_mining.py discover` (Europe PMC topic search,
316 recent papers not yet cited in cNPDB) + a manual full-text read of the two
highest-yield preprints. **No sequences were invented** — every sequence below was
read directly from a paper's main text and then checked against the DB.

## Bottom line
- Every *classical* neuropeptide the read papers print in their **main text** is
  **already in cNPDB** (checked against `Sequence` + `Active Sequence`).
- The genuinely-new main-text sequences are **AMP / housekeeping-derived** peptides
  (histone-2A–derived AMPs, actin, eIF5A) from the hybrid-sequencing paper — in
  scope only if cNPDB admits non-classical endogenous bioactive peptides.
- **The real backlog is in Supplementary Information**, above all Table S1 of the
  HILIC lobster paper (~50 first-reported *H. americanus* neuropeptides). SI tables
  must be pulled manually.

## Highest-priority extraction target
**Tran et al., "HILIC-Enabled MS Discovery of Novel Endogenous and Glycosylated
Neuropeptides in the American Lobster," bioRxiv 2025, DOI 10.1101/2025.06.26.661634**
- 154 endogenous neuropeptides from 25 families; **~50 reported for the first time**;
  24 glycosylated neuropeptides; first periviscerokinin (PVK) in any decapod.
- Action: extract **Table S1** (full list) and **Table 1** (glycopeptides). Raw data
  MassIVE `MSV000097908`.

## Other promising recent papers (from `discover`, not yet screened)
| Year | Title (abbrev.) | DOI |
|------|-----------------|-----|
| 2026 | Neuropeptide Diversity Encoded in Newly Sequenced Crustacean Genomes | 10.1021/acschemneuro.6c00123 |
| 2026 | In silico analysis of the slipper lobster (*Thenus australiensis*) neuropeptidome | 10.1016/j.ygcen.2025.114855 |
| 2026 | Global Profiling of Post-Translationally Modified Crustacean Neuropeptides | 10.1021/jasms.6c00017 |
| 2026 | Quantitative Neuropeptidomics Reveals Thermal Acclimation-Induced changes | 10.64898/2026.03.07.710231 |
| 2026 | Mass Spectrometry-Based Peptidomics for Discovery and Profiling (crustacean) | 10.1021/acsomega.6c00679 |
| 2025 | Key Neuropeptides Regulating Molting in *Penaeus vannamei* | PMC11851517 |
| 2025 | DIA-MS label-free quant of *C. borealis*/*C. sapidus* neuropeptidome (copper) | 10.1039/d5cb00082c (paywalled) |

Full list of 316 candidates: `new_papers_since_2025.csv` (many are off-topic —
Drosophila, aquaculture nutrition — the topic query casts wide on purpose).

## Confirmed-new main-text sequences (hybrid-sequencing paper, DOI 10.64898/2026.05.04.721987)
These are **NOT in cNPDB** as of this snapshot. Mostly AMP/housekeeping-derived — confirm scope before adding.

| Sequence | Family / note | Species | Evidence |
|----------|---------------|---------|----------|
| AGLQFPVGR | Histone-2A–derived AMP (HDAP) | *C. sapidus* | de novo + genome |
| SSRAGLQFPVGR | HDAP (N-extended) | *C. sapidus* | de novo + genome |
| AGLQFPVAR | HDAP isoform | *C. sapidus* | de novo |
| SYGANFSWNKR | ETC-related | *C. sapidus* | de novo |
| TLEAKLLR | predicted AMP + neuropeptide (uncharacterized) | *C. sapidus* | de novo |
| RVAPEEHP | actin fragment (housekeeping) | *C. borealis* | de novo |
| LSKQEYD | actin fragment (housekeeping) | *C. borealis* | de novo |
| ALKAMAK | eIF5A-1 fragment (housekeeping) | *C. borealis* | de novo |

## Confirmed main-text sequences that are ALREADY in cNPDB (HILIC lobster paper)
QAFHPWGamide, QDLIPFPRVamide/pQDLIPFPRVamide (PVK), pQTFQYSRGWTNamide (corazonin),
pQITFSRSWVPQamide (ACP), pQLNFSPGWamide (RPCH), VYRKPPFNGSIFamide (SIFamide),
pQDLDHVFLRFamide (myosuppressin), FDAFTTGFGHN / NFDEIDRSGFGFH / VYGPRDIANLY (orcokinins)
— all matched an existing `Sequence` or `Active Sequence`. Their newly-characterized
**glycosylated forms** are still worth adding as PTM variants (see Table 1 of the paper).

## Could not access (need a human/institutional pull)
- RSC Chem Biol 2025 `10.1039/d5cb00082c` (PDF 403; quant paper, low novelty risk).
- SI spreadsheets of the two bioRxiv preprints (readable in a browser but not via automated fetch).
