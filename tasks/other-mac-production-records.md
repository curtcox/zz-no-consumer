# Prompt: collect production records from the other Mac

Written 13 September 2026 for Curt to give to Claude on the second Mac. It supports
[the three-stream restructure](three-stream-restructure.md), whose collaboration movement
must be established from this repository's history on **both** Macs and GitHub. The first
Mac's inventory already exists; this Mac's does not.

---

You are collecting evidence, not writing the book. Curt, Codex and Claude are characters
in the graphic novel's second movement, and what they did has to come from preserved
records. Your job is to find this project's session histories on this Mac, catalog them
without exposing their contents, and package them so Curt can carry them to the other Mac
by hand. Someone else selects, reads and writes from them later.

## Read first

- `AGENTS.md` — especially the git-lock rules. Every read-only git call carries
  `--no-optional-locks`.
- `editions/three-stream/README.md` — the working edition and its evidence rules.
- `scripts/collaboration_records.py` — the inventory tool you will run. It records
  locators and hashes only; it never exports message bodies.

If this checkout does not contain `scripts/collaboration_records.py`, stop and tell Curt
the checkout needs updating. Do not pull, fetch or change branches yourself.

## Ground rules

- **Change nothing tracked.** No edits to tracked files, no commits, no branches, no
  stashes, no pushes. Everything you write goes under the ignored `256t/` directory.
- **Do not print message bodies** into the conversation, a summary, or any file other than
  the byte-for-byte transcript copies in the bundle. Report paths, line numbers,
  timestamps, roles, models, counts and hashes.
- **Do not modify, move or clean up** any history file under `~/.codex`, `~/.claude`,
  `~/.cursor` or anywhere else. Copy; never rewrite.
- **Never copy credentials.** Exclude `~/.codex/auth.json`, keychains, `.env` files, and
  any config holding tokens. Transcripts themselves may contain secrets in tool output;
  that is why the bundle stays private and travels by hand.
- **Do not assign meaning.** An inventory row is a candidate locator, not a finding about
  who did what. The tool's `user` role can be injected context or tool results rather
  than Curt, and a subagent's messages are not a separate collaborator. Leave
  `selection: unreviewed` alone.
- Standard-library Python only, per the repository rules. One-off inspection code stays
  in the conversation or a scratch directory outside the repository.

## Steps

### 1. Identify the machine and its clock

Record in `256t/editions/other-mac/machine.json`: the label `other-mac`,
`scutil --get ComputerName`, macOS version (`sw_vers`), the local time zone, the output
of `date -u`, and the clock offset from `sntp -t 5 time.apple.com` if it runs. Timestamps
from the two Macs will be interleaved, so a skewed clock matters.

### 2. Find every checkout and its unpublished history

Find all local checkouts of `curtcox/zz-no-consumer` (the directory may have another name).
For each, record its path, `git --no-optional-locks worktree list`, current branch and
`HEAD`, and commits that exist locally but on no remote:
`git --no-optional-locks log --branches --not --remotes --format='%H %aI %cI %an %s'`.
Also list local branch names and `git --no-optional-locks stash list`. Unpushed work is
production history that GitHub cannot show. Do not push it.

### 3. Find the session histories

Report which of these exist, with file counts and earliest/latest modification dates:
`~/.codex/sessions`, `~/.codex/archived_sessions`, `~/.claude/projects`, `~/.cursor/projects`,
and any other coding-agent history directory you find (for example Devin or another
agent's local store). Report presence only for tools other than Codex and Claude; the
inventory tool understands Codex and Claude transcript formats alone.

Then list the distinct working directories recorded inside Codex and Claude transcripts
whose path contains `zz-no-consumer` or the name of any checkout found in step 2, with a
count of files for each. The inventory tool matches a transcript only when a recorded
working directory's **final path component** equals `--project`. Worktree paths such as
`.claude/worktrees/<name>` or a differently named checkout will not match
`zz-no-consumer`; note every basename you will need.

### 4. Run the inventory

For each distinct project basename from step 3 (usually just `zz-no-consumer`):

```sh
python3 scripts/collaboration_records.py ~/.codex/sessions ~/.codex/archived_sessions ~/.claude/projects \
  --machine other-mac --project zz-no-consumer \
  --out 256t/editions/other-mac/messages-zz-no-consumer.json
```

Replace the basename in both `--project` and the output name for each additional one.
Omit a directory argument that does not exist. Do not edit the tool; if it fails or
misclassifies a format, record what happened and stop that directory.

### 5. Look for the project before the repository existed

The repository's first commit is 1 September 2026. Search Codex, Claude and Cursor
transcripts **modified on or before 3 September 2026, in any working directory**, for
these case-insensitive terms: `zz-no-consumer`, `graphic novel`, `Hugging Face`,
`HuggingFace`, `Artifactory`, `METR`, `GemStuffer`, `Collusion Wiki`. Record only path,
line number, record timestamp, role and the matched term in `256t/editions/other-mac/early-mentions.json`. Earlier planning in another
directory would be missed by the project filter, and it could bear on when the book began.

### 6. Summarize

Write `256t/editions/other-mac/summary.json` with, for each inventory file: record counts
by actor, role and model; counts per UTC day; earliest and latest UTC timestamps; the
number of distinct transcript files; and every limitation you hit. Include the step 2
unpushed-commit findings and the step 5 match count.

### 7. Bundle for transfer

Create `256t/editions/other-mac/sources/` and copy into it, byte for byte, every
transcript file named by an inventory row or an early-mention row, preserving the path
below the home directory (for example `sources/.claude/projects/<dir>/<file>.jsonl`).
Write `256t/editions/other-mac/SHA256SUMS` covering every file in the bundle, and confirm
each copied transcript's hash equals the `file_sha256` in its inventory rows. Your own
running session's transcript keeps growing, so its hash will differ: rerun the inventory
immediately before copying, and record any file that still changed as a limitation. Then:

```sh
tar -cf 256t/editions/other-mac-bundle-$(date -u +%Y%m%dT%H%MZ).tar -C 256t/editions other-mac
shasum -a 256 256t/editions/other-mac-bundle-*.tar
```

The tar is private. Do not upload it, commit it, attach it to an issue or send it through
any service. Curt moves it to the first Mac by hand.

### 8. Report to Curt

Tell Curt the tar path, its size and SHA-256; the summary counts; the unpushed commits and
branches; any history directories for other agents; the early-mention count; and every
limitation or surprise. Do not select records, quote messages, draft beats or recommend
manuscript changes.

---

## On the first Mac, after transfer

```sh
python3 scripts/production_history.py verify-bundle 256t/editions/other-mac-bundle-….tar --extract
python3 scripts/production_history.py attribute
```

The first command checks member paths, `SHA256SUMS` and transcript hashes before extracting
into `256t/editions/other-mac/`; the second folds the bundled transcripts into commit
attribution. Treat the `other-mac` inventory exactly as
`256t/editions/current-mac-messages.json` is treated:
select records individually, preserve each selected record by its hash, and keep product
and actor identities as the records give them. Commit metadata alone does not identify an
authoring agent; see the restructure plan.
