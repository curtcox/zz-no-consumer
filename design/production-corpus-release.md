# Production corpus C — release preparation

Status: proposed release protocol, 9 September 2026. No raw conversations are exported,
committed or published by this change. The owner deferred the redaction standard; this
makes that remaining decision concrete without treating silence as approval.

## Inclusion and omissions

Include interactions that shaped the manuscript or its generation, validation and
publication tooling, across vendors and repositories. Citation makes a session relevant.
Record vendor, product, available export window, fidelity and known missing data separately.
A relevant unavailable or excluded session gets an opaque identifier and a reason category;
do not disclose private subject matter in the explanation. A session can be partially
published. Each omitted span gets a category, without publishing the omitted bytes or a
hash that could be used to test guesses about a secret.

## Proposed redaction categories

- Credentials, tokens, authentication material and secret-bearing URLs: remove completely.
- Local paths and account identifiers: replace with stable neutral placeholders.
- Third-party private information and personal names unrelated to public attribution:
  remove or pseudonymize consistently.
- Third-party source wording subject to the quotation audit: replace with a source locator
  and an omission marker; do not copy it into the release or its metadata.
- Irrelevant personal exchanges inside an otherwise relevant session: mark the omitted span.
- Unrecoverable vendor content or retracted messages: declare missing; never reconstruct it.

## Release shape

Use immutable release directories containing a README, manifest, scrubbed session records,
omission ledger and SHA256SUMS. Each public message has a stable identifier and source
session locator. Hash only the public files. Do not publish private paths or raw-file hashes
in a manifest. Record the cut date, timezone policy, export method and per-vendor completeness.

Before a first commit, review the rendered/readable release as well as its structured files.
Search for the categories above and inspect every match. Inspect the staged public cut
again when a commit is requested; automated scanning supplements human review.

## Citation and statistical checks to add when a cut exists

Every C citation must resolve to a published release and message/span identifier. A later
citation brings the session into scope but does not bypass redaction. Fail the check for
missing targets or references into excluded spans. Do not pretend an empty placeholder
corpus supplies working citations.

Publishing a relevant selection does not establish a refusal rate. Keep the current no-rate
ceiling unless a separate analysis defines complete eligible exposure, event classification,
window and vendor/version boundaries. Preserve reconstruction status where dialogue is
compressed, reordered or staged, even when its source exchange becomes public.
