# cNPDB Coverage Audit — did the original curation miss older sequences?

**Method:** cross-reference cNPDB against the 8 NeuroPep species files in
`NeuroPepDatabases/` (the source curated during the initial build). Reproduce with
`python -m DataCuration.coverage_audit --outdir DataCuration`.
**Caveat:** NeuroPep includes predicted/transcriptomic assignments that empirical
cNPDB may intentionally exclude, so these are **review candidates, not auto-adds**.
NeuroPep files have no tissue column — this covers species (`OS`) completeness only.

## Finding 1 — 59 sequences in NeuroPep are absent from cNPDB (overlooked)
Full list: `audit_overlooked_neuropep.csv`. By species:

| Species | Overlooked |
|---------|-----------:|
| *Litopenaeus vannamei* | 25 |
| *Ocypode ceratophthalma* | 18 |
| *Homarus americanus* | 6 |
| *Orconectes limosus* | 5 |
| *Carcinus maenas* | 4 |
| *Callinectes sapidus* | 1 |

These are pre-2025 (PMIDs 2008–2012), so they were available at build time and
missed — heaviest for *L. vannamei* (a large orcokinin/FMRFamide block from
PMID 19852991) and *O. ceratophthalma*. **Highest-value backfill.**

## Finding 2 — 216 species-annotation gaps (OS under-representation)
Full list: `audit_os_underrepresented.csv`. A sequence is in cNPDB, but NeuroPep
records it in a species the `OS` column omits.

| gap type | count | meaning |
|----------|------:|---------|
| `os_partial` | 193 | `OS` is populated but missing this species → **append** the species |
| `os_blank` | 23 | `OS` is empty → **fill** it (overlaps the 115 missing-OS QC entries) |

By species that would be added: *Ocypode* 89, *Homarus* 39, *Cancer borealis* 22,
*Callinectes* 20, *Litopenaeus* 19, *Carcinus* 12, *Procambarus* 12, *Orconectes* 3.

Example: `QLNFSPGW` (RPCH) is listed for HoA;Spar in cNPDB but NeuroPep also
records it in *Cancer borealis* — a highly conserved decapod peptide whose species
list is incomplete.

## Recommended next steps
1. Backfill the 59 overlooked sequences (verify each against its PMID first).
2. Merge the 23 `os_blank` fixes into the 115 missing-`OS` cleanup from the QC pass.
3. Review the 193 `os_partial` additions — bulk-review by family is efficient
   (orcokinins and FMRFamides dominate).
4. This audit only reaches species covered by a NeuroPep file. For the other ~21
   cNPDB species and for **tissue** completeness, the per-peptide literature check
   (planned extension to `lit_mining`) is still needed.
