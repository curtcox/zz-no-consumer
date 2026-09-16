"""Offline regression fixtures for timeindex.py; no live writes.

Run inside ``timeindex.py check``. Every ``When`` form present in
``research/timeline.md`` on 15 September 2026 is exercised so a new phrasing
fails loudly instead of dropping a row.
"""

from datetime import datetime

import timeindex


def run():
    cases = [
        ("20 Apr 07:59", "2026-04-20T07:59:00Z", "2026-04-20T08:00:00Z", "minute", False),
        ("7 May", "2026-05-07T00:00:00Z", "2026-05-08T00:00:00Z", "day", False),
        ("12–13 May", "2026-05-12T00:00:00Z", "2026-05-14T00:00:00Z", "days", False),
        ("4–17 Jun", "2026-06-04T00:00:00Z", "2026-06-18T00:00:00Z", "days", False),
        ("Late 4 Jul", "2026-07-04T18:00:00Z", "2026-07-05T00:00:00Z", "part-of-day", True),
        ("5–6 Jul", "2026-07-05T00:00:00Z", "2026-07-07T00:00:00Z", "days", False),
        ("8 Jul 16:01", "2026-07-08T16:01:00Z", "2026-07-08T16:02:00Z", "minute", False),
        ("9 Jul +1h", "2026-07-09T00:00:00Z", "2026-07-09T01:00:00Z", "part-of-day", True),
        ("9 Jul 08:30–20:16", "2026-07-09T08:30:00Z", "2026-07-09T20:16:00Z", "minute", False),
        ("9 Jul morning", "2026-07-09T06:00:00Z", "2026-07-09T12:00:00Z", "part-of-day", True),
        ("11 Jul evening", "2026-07-11T18:00:00Z", "2026-07-12T00:00:00Z", "part-of-day", True),
        ("11 Jul ~05–15", "2026-07-11T05:00:00Z", "2026-07-11T15:00:00Z", "hour", True),
        ("12 Jul ~01:30", "2026-07-12T01:30:00Z", "2026-07-12T01:31:00Z", "minute", True),
        ("13 Jul 07:00–08:00", "2026-07-13T07:00:00Z", "2026-07-13T08:00:00Z", "minute", False),
        ("28–30 Aug", "2026-08-28T00:00:00Z", "2026-08-31T00:00:00Z", "days", False),
    ]
    for text, start, end, precision, approximate in cases:
        when = timeindex.parse_when(text)
        assert when is not None, f"unparsed: {text!r}"
        assert timeindex.iso(when.start) == start, (text, when.start)
        assert timeindex.iso(when.end) == end, (text, when.end)
        assert when.precision == precision, (text, when.precision)
        assert when.approximate == approximate, (text, when.approximate)
    for bad in ("soon", "mid-July", "", "32 Jan"):
        assert timeindex.parse_when(bad) is None, bad

    spans = [
        ("2026", ("2026-01-01T00:00:00Z", "2027-01-01T00:00:00Z")),
        ("2026-05", ("2026-05-01T00:00:00Z", "2026-06-01T00:00:00Z")),
        ("2026-05-11", ("2026-05-11T00:00:00Z", "2026-05-12T00:00:00Z")),
        ("2026-05-11T08:30Z", ("2026-05-11T08:30:00Z", "2026-05-11T08:31:00Z")),
        ("2026-05-11..2026-05-13", ("2026-05-11T00:00:00Z", "2026-05-14T00:00:00Z")),
        ("2026-05-11/2026-05-12", ("2026-05-11T00:00:00Z", "2026-05-13T00:00:00Z")),
        ("2026-05-11T08:00Z..2026-05-11T09:00Z",
         ("2026-05-11T08:00:00Z", "2026-05-11T09:01:00Z")),
    ]
    for spec, (start, end) in spans:
        parsed = timeindex.parse_span(spec)
        assert timeindex.iso(parsed[0]) == start, (spec, parsed)
        assert timeindex.iso(parsed[1]) == end, (spec, parsed)
    for bad in ("", "May 11", "2026-13-40", "yesterday"):
        try:
            timeindex.parse_span(bad)
        except ValueError:
            continue
        raise AssertionError(f"accepted span {bad!r}")

    # Overlap: a day-precision event on the 11th meets a same-day query and a
    # multi-day one, but not the 12th.
    event = {"start": "2026-05-11T00:00:00Z", "end": "2026-05-12T00:00:00Z"}
    index = {"events": [event], "depictions": [], "sources": {},
             "corpus_days": {"2026-05-11": {"events": 2, "saves": 1, "deletes": 1,
                                            "reverts": 0, "probes": 0,
                                            "revisions": 3, "pages_created": 1,
                                            "pages_last_active": 0,
                                            "pages_touched": 4, "labels": 2}}}
    result = timeindex.query(index, "2026-05-11")
    assert result["events"] == [event]
    assert result["corpus"]["totals"]["events"] == 2
    assert not timeindex.query(index, "2026-05-12")["events"]
    assert timeindex.query(index, "2026-05-10..2026-05-12")["events"] == [event]
