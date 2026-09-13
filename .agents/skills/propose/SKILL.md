---
name: propose
description: Write a proposal in proposals/ instead of acting, when a change needs Curt's approval or other agents' opinions; or add an opinion to an existing proposal.
argument-hint: "<the change, or an existing proposal file to comment on>"
---

# Propose instead of acting

Follow `proposals/README.md`. In short:

1. **Check for an existing proposal** covering the same change:
   `grep -il '<keyword>' proposals/2*.md`. If one exists, add an opinion instead of a new file.
2. **New proposal:** copy `proposals/TEMPLATE.md` to `proposals/YYYY-MM-DD-short-slug.md`
   (today's date). Set `proposed_by` to your product and model, e.g. `Devin (model)`, and
   `blocking: true` only if work is waiting. Fill in every section briefly; link files,
   commits and tool output as evidence instead of pasting them.
3. **Opinion on an existing proposal:** append under `## Opinions` a new entry
   `### Your name (product/model), YYYY-MM-DD — support | oppose | amend | question`
   with your reasoning. Never edit someone else's entry.
4. **Do not carry out the proposed change.** Read-only investigation is fine.
5. **Never record a decision on Curt's behalf** unless he gave it in this session; then
   quote his words and the date under `## Decision` and update `status`, `decided`,
   `decided_by`.
6. Tell Curt the file path and the decision requested, in one or two sentences.

Do not commit unless Curt asks; if he does, use the `commit` skill.
