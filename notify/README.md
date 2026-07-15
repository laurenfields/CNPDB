# cNPDB email notifications

Automated emails so nobody has to watch the GitHub Actions tab. Three of them:

| When | Email | Workflow |
|------|-------|----------|
| **Monthly**, after the literature scan | "Papers to check this month" — crustacean-neuropeptide papers not yet in the database. A paper drops off automatically once its DOI is in the DB. | `lit-mining.yml` |
| **When the database is pushed** | "QC found issues to check" — a summary of any accuracy problems. Does **not** block the update. | `db-accuracy.yml` |
| **When the tests fail** on any push | "Unit tests FAILED" — with a link to the run. | `tests.yml` |

All three send to the same list and are otherwise independent.

## Who gets the emails — `recipients.txt`

Edit [`recipients.txt`](recipients.txt): one email address per line. Lines
starting with `#` are ignored. Commit the change — that's all. No code involved.

## One-time setup: let Actions send email (required once)

Nothing sends until this is done. Until then, the workflows still run fine — the
email step just logs "email skipped" and succeeds.

You need a Gmail account to send *from* (a dedicated project account is cleanest)
and a Google **app password** (not the normal password):

1. On the sending Google account, turn on 2-Step Verification.
2. Go to <https://myaccount.google.com/apppasswords> and create an app password
   named e.g. "cNPDB GitHub". Copy the 16-character code.
3. In this repository on GitHub: **Settings → Secrets and variables → Actions →
   New repository secret**, and add two secrets:
   - `MAIL_USERNAME` — the full Gmail address (e.g. `cnpdb.bot@gmail.com`)
   - `MAIL_PASSWORD` — the 16-character app password
4. Add at least one address to `recipients.txt` and commit.

That's it. To test immediately without waiting for a schedule, open the
**Actions** tab, pick **db-accuracy** or **literature-mining**, and click
**Run workflow** (workflow_dispatch).

## Turning it off

Remove the secrets (or empty `recipients.txt`) and emails stop; the workflows
keep working. To stop a whole notification, delete or disable its workflow.

## What each email can and can't tell you

- The **papers-to-check** list depends on the source **DOI** being recorded when
  sequences are added. If a paper's sequences go in without its DOI, it will keep
  appearing on the list.
- The **accuracy** email reports mechanical QC problems (wrong mass, missing
  species, a modification left inside a sequence). It cannot tell whether a
  sequence is the *correct* one for its paper — only a human reading the paper can.
