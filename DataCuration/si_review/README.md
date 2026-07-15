# SI-review queue

Papers whose **Supplementary Information needs a manual pull** — because the SI is
paywalled, behind a CAPTCHA, or in a spreadsheet-only format that can't be scraped.
Sequences usually live in the SI, so this is where the automated pipeline hands off
to a human.

## Files
- **`queue.csv`** — the manifest. One row per paper. The monthly literature-mining
  job appends papers whose full text isn't open-access in Europe PMC; you can also
  add papers by hand. **Append-and-update:** a re-scan never overwrites a row, so
  your `status`/`notes` edits are safe.
- **`files/`** — drop the downloaded SI here, ideally in a per-DOI subfolder
  (e.g. `files/10.1021_acschemneuro.6c00123/si_003.xlsx`).

## Columns
`doi, title, species, reason, si_url, is_open_access, date_added, status, notes`
- `reason`: `paywalled` · `captcha` · `spreadsheet_only` · `precursors_only` · `other`
- `status`: `pending` · `in_progress` · `done` · `dropped`

## Workflow
```bash
python -m DataCuration.si_review list                 # what's outstanding
python -m DataCuration.si_review add --doi 10.x/y --title "..." --reason paywalled --url http://...
# ... download the SI into files/, extract the sequences, then:
python -m DataCuration.si_review done --doi 10.x/y --note "extracted 12 seqs -> staging"
```
Extracted sequences flow into the normal path: stage with `backfill`, confirm
`PTM`/`Existence`/`Tissue`, `backfill finalize`, then `merge_additions`.

The monthly job runs `si_review scan --shortlist outputs/shortlist_<date>.csv`
automatically, so blocked papers land here without anyone remembering to file them.
