---
id: PR-16
kind: profession
profession: Data protection officer
field: law-and-policy
title: Nobody in this book asks whether personal data was involved
pages: [045, 051, 091]
conjecture: marked
reading: >-
  Page 045 has production worker files and secrets become readable and page 051 reaches private
  repositories. A data protection officer would stop the story there and ask a question it never
  asks: whose personal data was in reach, and when did the notification clock start?
---

## What the practitioner would say

The distinction that governs everything here is between a security incident and a personal-data
breach. Access to production worker files and private repositories is at least a candidate for
the second, because repositories routinely contain contributor identities, email addresses, and
access tokens tied to named people. Once that candidacy exists, an assessment is mandatory and
time-bound: under the European regime, notification to a supervisory authority without undue
delay and within 72 hours of becoming aware, unless the risk to individuals is unlikely — and
"becoming aware" is a term of art that is argued about precisely because it decides whether the
clock started at the 27 June alert, the 4 July outage, or later.

The book's timeline puts a first victim-side public disclosure in mid-July. Public disclosure
and regulatory notification are different obligations with different deadlines and different
audiences, and a reader is given no way to tell which happened when, or whether any individual
was ever told that data of theirs was in scope.

## What the book gets wrong or omits

The affected parties in this story are institutions. Users appear nowhere. That is a strange
absence in a book so careful about who can know what, because the population with the least
information and the least agency here is the set of people whose repositories, tokens, and
identities sat inside the estate two companies were reconstructing after the fact. Page 091's
containment montage lists revoked credentials and rebuilt systems; it does not list a
notification, because the record the book works from does not contain one.

> **Conjecture.** Whether personal data as the regulations define it was accessed is not
> established by any public source, and this entry does not assert that it was. The objection
> is that the question is unasked, and that a data protection officer would have been obliged
> to ask it on day one.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Statute | [GDPR Article 33, notification of a personal data breach to the supervisory authority](https://gdpr-info.eu/art-33-gdpr/) | 2016 | The 72-hour clock, the awareness trigger, and the content a notification must carry. |
| Statute | [GDPR Article 34, communication to the data subject](https://gdpr-info.eu/art-34-gdpr/) | 2016 | When affected individuals themselves must be told, and the high-risk threshold that decides it. |
| Victim-side account | [Hugging Face security incident disclosure](https://huggingface.co/blog/security-incident-july-2026) | 16 Jul 2026 | The public disclosure, its date, and its characterisation of what was reached. |
| Incident record | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | The access to worker files, secrets, and private repositories that a breach assessment would start from. |
| Conjecture | This entry's framing of a notifiable-breach assessment | 2026 | No public source states whether personal data was in scope or whether any authority was notified. |
