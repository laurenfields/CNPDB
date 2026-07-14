# 2025–2026 Literature Screen & Completeness Results

Scope: **Crustacea only.** Non-crustacean peptides encountered in these papers
(Drosophila/Locusta/Bombyx ETHs, vasopressin/oxytocin, CAP2B, SCPB) are excluded,
as are synthetic lab analogs (Carcinus Y5-ETH, A1-ETH).

## How the shortlist was produced
Raw Europe PMC scan (316 papers since 2025) → `lit_mining.classify_relevance()`
→ **21 crustacean-neuropeptide keepers → 12 discovery shortlist** → full-text screen.
Machine-readable: `lit_scan/shortlist_crustacean_discovery.csv`,
`lit_scan/candidates_2026_screened.csv`.

## Verdicts

| DOI | Species | New mature sequences? |
|-----|---------|----------------------|
| 10.1021/acschemneuro.6c00123 | *C. borealis*, *C. sapidus* | **YES** — highest yield. Novel AST-B/AST-C, ILP B-chain-like, **first natalisins in *C. borealis*** |
| 10.1021/acsomega.6c00679 | *H. americanus*, *C. sapidus* | **YES** — 6 novel de novo peptides (hemolymph) |
| 10.1016/j.ygcen.2025.114777 | ***Erimacrus isenbeckii*** | **YES** — 1 new mature CHH (**NEW SPECIES**) |
| 10.1016/j.ygcen.2025.114855 | ***Thenus australiensis*** | **SI-only** — 58 precursors (**NEW SPECIES**) |
| 10.64898/2026.03.07.710231 | *H. americanus* | No new seqs; large re-detected mature set + PTM forms |
| 10.1021/jasms.6c00017 | *C. borealis* | No new seqs — novel **PTM states** on known backbones |
| 10.1186/s12915-026-02603-w | *C. maenas* | No (receptor deorphaning); Cam-ETH + carcipyrokinins only |
| 10.1007/s10126-025-10505-1 | *P. monodon* | **DROP** — transcript/expression only |
| 10.3390/ijms26104612 | *L. vannamei* | **DROP** — gene-level only |
| 10.3390/ani15040540 | *P. vannamei* | **DROP** — transcriptomic DEG only |

## Result: 57 candidate sequences screened → **38 genuinely new**, 19 already present

Full table with provenance: `lit_scan/candidates_2026_screened.csv`. Highlights:

- **6 de novo from *C. sapidus* hemolymph** (10.1021/acsomega.6c00679): WLAHKGVW, WLAHRGVW (AST-B); WLKRY, YNDVALVVQDRY, RFLPPAFQRY, ADLAHKQQAVNRSRY (RYamide).
- **First natalisins in *C. borealis*** (10.1021/acschemneuro.6c00123): QEVSPGEAGGSEGHSGAAAPWVGQRHA, GAGHGGTTFWVAR, SGWESNPSLW, DGHGPFWAAR, SGADNTFWVAR, QDGTTPTGPYWIAR, GDEDSVFWAAR, EDETHSFWIAR, PERDPFWVSR, ETDPRGPFWAAR.
- **Eclosion-hormone series in *C. sapidus***: MYTDYFNGGLCGDFCLQTE + N-extended forms.
- **ILP B-chain-like**: LCGWRLANELNRVCKGVYNMPTVSTNALFYLKGRA.

### ⚠ Do NOT add `AGWSSLWGAWamide`
The main text of 10.1021/acschemneuro.6c00123 claims this as a first report, but the
paper's own SI lists only `AGWSSLQGAW`, and **`AGWSSLQGAW` is already in cNPDB**. The
`LW` variant is almost certainly a **typo**. Confirm with the authors before entering.

## Two new species (would take cNPDB from 29 → 31)
1. ***Thenus australiensis*** (Australian slipper lobster) — 58 predicted neuropeptide
   precursors across ~50 families, SI `mmc3.xlsx`. **Precursors only** — mature peptides
   must be derived by in-silico cleavage at KR/GKR sites. Evidence level = `Predicted`.
2. ***Erimacrus isenbeckii*** (horsehair crab) — mature **EiCHHa** (72 aa, pyroGlu N-term,
   C-terminally amidated), sinus gland, Edman + MALDI + cDNA.

Both need new `OS` abbreviations and Glossary entries.

## Still needs manual SI extraction
| Paper | SI | Contents |
|-------|-----|---------|
| Thenus (10.1016/j.ygcen.2025.114855) | `mmc3.xlsx` | 58 precursors — **must-do**, blocked by CAPTCHA for automated fetch |
| ChemNeuro (10.1021/acschemneuro.6c00123) | `si_003/si_004.xlsx` | 147+136 predicted-mature; 20,109 predicted-all |
| HILIC lobster (10.1101/2025.06.26.661634) | Table S1 | ~50 first-reported *H. americanus* peptides (carried over from the earlier screen) |

## Scope decision still needed: AMPs / housekeeping-derived peptides
Two independent screens have now surfaced the same question, so it needs a one-time ruling.

**From 10.1021/acsomega.6c00679 (SI Table S1)** — ~20 predicted **antimicrobial peptides**:
*C. sapidus* RLLYR series; *H. americanus* FWGMLK / FWGRLAKGVL series.

**From 10.64898/2026.05.04.721987 (hybrid sequencing, Fields et al.)** — histone-2A–derived
AMPs and housekeeping fragments, all confirmed absent from cNPDB:

| Sequence | Note | Species |
|----------|------|---------|
| AGLQFPVGR | histone-2A–derived AMP (HDAP) | *C. sapidus* |
| SSRAGLQFPVGR | HDAP, N-extended | *C. sapidus* |
| AGLQFPVAR | HDAP isoform | *C. sapidus* |
| SYGANFSWNKR | ETC-related | *C. sapidus* |
| TLEAKLLR | predicted AMP + neuropeptide, uncharacterized | *C. sapidus* |
| RVAPEEHP, LSKQEYD | actin fragments (housekeeping) | *C. borealis* |
| ALKAMAK | eIF5A-1 fragment (housekeeping) | *C. borealis* |

All are crustacean but **not classical neuropeptides**. Include only if cNPDB's scope admits
endogenous bioactive / AMP peptides. If the answer is no, these drop out permanently and the
question stops recurring in each screen.

---

# OS / tissue completeness — full-database sweep

`python -m DataCuration.os_tissue_completeness` over all 1516 entries →
**134 peptides carry a candidate gap** (`os_tissue_gaps_full.csv`):

- **95** name a species in the literature that the `OS` column omits.
- **76** name a tissue the `Tissue` column omits.

Most-frequently missing species: *Ocypode* (29), *C. borealis* (28), *Procambarus clarkii*
(19), *H. americanus* (17), *C. sapidus* (11), *L. vannamei* (11).
Most-frequently missing tissues: eyestalk (28), hemolymph (19), CNS (19).

**These are screening candidates, not facts** — a species named in a paper that mentions a
peptide is not proof the peptide occurs there. Each row cites its supporting paper
(`supporting` column) for confirmation. The NeuroPep cross-check
(`COVERAGE_AUDIT.md`, 216 gaps) is the higher-confidence source for the 8 species it covers;
this sweep generalizes to the other species and to **tissue**, which NeuroPep does not carry.
