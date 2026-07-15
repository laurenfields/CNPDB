# cNPDB automated monitoring — handoff

Lightweight automated monitoring on the cNPDB repository, so the database and
site keep an eye on themselves. It rides on the GitHub Actions already in the
repo and **does not change how anyone updates the database or the site** — it
only adds automatic email alerts on top. Nothing new to install or host.

For provider/setup specifics, see [`README.md`](README.md). This file is the
plain-English overview for maintainers and the PI.

## What you get — three automatic emails

| Email | When it sends | What it means |
|-------|---------------|---------------|
| **Papers to check** | Monthly (1st, ~08:00 UTC) | A list of new crustacean-neuropeptide papers worth reviewing for new sequences. A paper drops off automatically once its DOI is in the database. |
| **Database accuracy check** | When the database is pushed | A quality-control summary (wrong masses, missing species, etc.). **Never blocks the update** — the new database goes live regardless; this is a heads-up. |
| **Test-failure alert** | Any change to the repo | Sent only if the automated test suite breaks, with a link to the details — so nobody has to watch the Actions tab. |

## Which database it monitors

The live database the site actually serves:

- **`Assets/20260418_cNPDB.parquet`** — the file the Streamlit app loads
  (`pages/1_NP_Database_Search.py`, `pages/2_Tools.py`)
- **`Assets/20260418_cNPDB.xlsx`** — the source spreadsheet (1516 entries)

The `20260418` is just the original build date — it is simply *the* current
database. If it's ever renamed to a new dated file, three places must be updated
together or they'll silently drift apart:

1. the two `read_parquet("Assets/20260418_cNPDB.parquet")` lines in `pages/`
2. `DEFAULT_DB` in `DataCuration/cnpdb_qc.py`
3. the trigger `paths:` in `.github/workflows/db-accuracy.yml`

## What it's connected to (for longevity)

- Runs entirely on **GitHub Actions** in the lab repo — no external server,
  nothing to pay for or keep alive.
- Emails are sent from a **dedicated Gmail account** (e.g.
  `lingjun.li.notifications@gmail.com`) using an app password stored as
  repository secrets. That account exists only to send these alerts.
- The recipient list is a plain repo file — [`recipients.txt`](recipients.txt),
  one address per line. Edit and commit to change who gets emails. No code.

## What's needed from maintainers

- **Repository secrets** `MAIL_USERNAME` / `MAIL_PASSWORD` must be set on the repo
  (Settings → Secrets and variables → Actions). Until they are, the workflows
  still run fine — the email step just skips silently.
- **Keep the bot Gmail account recoverable by the lab**, not one person: save its
  2-Step-Verification backup codes somewhere the lab retains, and ideally use a
  lab phone number for recovery.
- **Record the DOI when adding sequences.** That's how a paper drops off the
  monthly "to check" list. Sequences added without a DOI keep the paper on the list.
- **Org action policy:** if the org restricts third-party Actions, an admin must
  allow `dawidd6/action-send-mail@v3` (plus the standard `actions/*`).

## How to run any workflow manually (e.g. to test)

1. Go to the repository's **Actions** tab on GitHub.
2. Pick a workflow from the left sidebar — **db-accuracy** is the quickest test.
3. Click **Run workflow** → choose the **main** branch → **Run workflow**.
4. It finishes in under a minute; the corresponding email is sent.

They also run automatically: monthly for the papers list, and on every database
update / repo change for the other two.

## The workflows, at a glance

| Workflow file | Purpose | Trigger |
|---------------|---------|---------|
| `.github/workflows/lit-mining.yml` | Monthly paper scan + "papers to check" email | schedule (monthly) + manual |
| `.github/workflows/db-accuracy.yml` | QC on the database + accuracy email | push to `Assets/20260418_cNPDB.*` + manual |
| `.github/workflows/tests.yml` | Run tests; email on failure | any push / PR + manual |
| `.github/workflows/curation-refresh.yml` | (pre-existing) regenerate QC/coverage output files | DB or tool change |
| `.github/actions/notify-email/` | Shared "send an email" step used by all three | — |

## What no automatic check can catch

The accuracy check finds mechanical problems (wrong mass, missing species, a
modification left inside a sequence). It **cannot** tell whether a sequence is the
*correct* one for its paper — only a human reading the paper can. Treat the emails
as prompts for review, not guarantees.
