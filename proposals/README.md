# Proposals: approval and opinions before acting

This directory holds changes that someone — Curt, Codex, Claude, Devin, Cursor, or any
other agent working here — wants approved, or wants more opinions on, **before** doing
them. A proposal is a question with a recommendation attached, not a record of work done.

## When to write one

Write a proposal instead of acting when a change:

- edits files the working edition freezes (see `editions/three-stream/baseline.json`),
  the story contract, an invariant in `AGENTS.md`, or a tool's ownership of identities;
- changes CI, deletes or renumbers material, or rewrites history;
- contradicts or reinterprets a task plan or an owner decision;
- chooses between editorial options the owner has not settled;
- continues a disagreement between agents, or between an agent and a plan.

Small, reversible, in-scope work does not need one. When unsure, write a short one; it
costs less than undoing a change.

## How

1. Copy [`TEMPLATE.md`](TEMPLATE.md) to `YYYY-MM-DD-short-slug.md`, dated the day it is
   opened. Fill in the front matter and the sections; keep it short and link evidence
   rather than pasting it.
2. Name yourself in `proposed_by` with product and model when known (`Codex (gpt-6-astra)`,
   `Claude (claude-opus-5)`). Commit metadata does not identify authors here, so the file
   has to.
3. Do not start the proposed work. Read-only investigation and throwaway prototypes outside
   the tracked tree are fine.

## Opinions

Anyone may add an opinion under **Opinions**. Append a new `###` entry headed with who you
are and the date; state a position (`support`, `oppose`, `amend`, or `question`) and why.
Never edit or delete someone else's entry. Change your own position with a new, dated entry.

## Decisions

**Only Curt decides.** He may write the decision himself, or tell an agent in chat; the
agent then records it under **Decision**, quoting Curt's words and the date, and sets
`status`, `decided` and `decided_by: Curt`. An approval covers the stated scope only; a
materially different change needs a new proposal or an amended, re-approved one.

Status values: `open`, `approved`, `declined`, `withdrawn` (by its proposer), `superseded`
(link the replacement), `done` (approved and carried out; link the commits or files).

Decided proposals stay here. They are the record of why the repository is the way it is.

Agent support: `AGENTS.md` (read by Codex, Claude, Cursor and Devin) points here, as does
`.cursor/rules/working-with-curt.mdc`; Devin and other skill-aware agents can also use
`.agents/skills/propose/`.

## Finding open proposals

```sh
grep -l '^status: open' proposals/2*.md
```

Quotation and evidence rules still apply inside proposals: quote sources with their
registrations or 256t pointers, and never paste private transcript or export contents.
