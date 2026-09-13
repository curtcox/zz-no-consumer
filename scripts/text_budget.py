#!/usr/bin/env python3
"""Read-only lettering census and editorial budget comparisons. Standard library only."""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import statistics
import sys
from collections import Counter

import crossref
import panels
import reader_view


METHOD = (
    "Words use panels.py's lettering extractor and token rule (letters/digits, internal "
    "apostrophes; hyphenated words split). Directions, titles and source apparatus are excluded. "
    "The default page ceiling is 400 words, with a separate 100-word panel ceiling in design/lettering.md "
    "and design/page-grammar.md, not a target or a measured layout capacity. "
    "Page-level lettering is counted once and reserved first. Panel allowances are capped "
    "at 100 words, including the repeated banner; the page ceiling also applies independently. "
    "Grouped runs retain one combined row; their words are never assigned to individual cells. "
    "Four element slots apply to each script image slot, including a grouped run. "
    "Repeated banner words are reported separately as an estimate across image slots. "
    "Unused words do not establish that a scene needs more text. Use letterpress.py audit for fit."
)


def word_count(text: str) -> int:
    return sum(len(panels.WORD.findall(line)) for line in panels.visible_text(text))


def metrics(used: int, budget: float) -> dict:
    return dict(words=used, budget_words=budget,
                utilization_pct=100 * used / budget if budget else None,
                remaining_words=max(0, budget - used),
                over_words=max(0, used - budget))


def band(row: dict) -> str:
    if row['words'] == 0:
        return 'zero words'
    pct = row['utilization_pct']
    if pct is None or pct > 100:
        return 'over 100%'
    if pct < 25:
        return 'under 25%'
    if pct < 50:
        return '25–<50%'
    if pct < 75:
        return '50–<75%'
    return '75–100%'


def measure(script: panels.PageScript, chapter: str, title: str, allowance: int) -> dict:
    if not script.count:
        raise ValueError(f'{script.id}: no declared panels')
    rows, types = [], Counter()
    body = script.text.split('\n---\n', 1)[1] if script.text.startswith('---\n') else script.text
    heads = list(panels.SECTION_HEADING.finditer(body))
    banners = 0
    banner_elements = 0
    for i, head in enumerate(heads):
        section = body[head.start():heads[i + 1].start() if i + 1 < len(heads) else len(body)]
        heading = section.splitlines()[0]
        if heading == panels.BANNER_HEADING:
            banners += word_count(section)
            banner_elements += len(panels.visible_text(section))
            continue
        match = panels.PANEL_HEADING.match(heading)
        group = panels.GROUPED_HEADING.match(heading)
        if not match and not group:
            continue
        first = int((match or group).group(1))
        last = int(group.group(2)) if group else first
        elements = 0
        for label, field in reader_view.fields_of(section):
            if reader_view.lettered_label(label):
                elements += 1
                kind = ('dialogue' if 'dialogue' in label.lower() else
                        label.split('—')[0].split('(')[0].strip().lower())
                types[kind] += word_count(field)
        words = word_count(section)
        rows.append(dict(level='panel', id=f'{script.id}-{first:02d}' +
                         (f'–{last:02d}' if group else ''), page=script.id,
                         chapter=chapter, title=title, declared_panels=last - first + 1,
                         image_slots=1, elements=elements,
                         slot_budget=panels.SLOTS_PER_PANEL,
                         words=words, grouped=bool(group),
                         text=' / '.join(panels.visible_text(section))))
    if sum(row['declared_panels'] for row in rows) != script.count:
        raise ValueError(f'{script.id}: panel headings do not reconcile')
    if sum(row['words'] for row in rows) + banners != script.words:
        raise ValueError(f'{script.id}: lettering outside recognized panels/banner; run reader_view.py check')
    if sum(types.values()) != sum(row['words'] for row in rows):
        raise ValueError(f'{script.id}: lettering outside recognized fields; run reader_view.py check')
    available = max(0, allowance - banners)
    for row in rows:
        row.update(metrics(row['words'], min(available, max(0, panels.MAX_PANEL_WORDS - banners))))
        row['band'] = band(row)
        row['elements_with_banner'] = row['elements'] + banner_elements
    types['persistent banner'] += banners
    result = dict(level='page', id=script.id, page=script.id, chapter=chapter, title=title,
                  declared_panels=script.count, image_slots=len(rows),
                  banner_words=banners, panel_budget_words=available,
                  # Reserve the full banner even when it alone exceeds the allowance.
                  banner_over_words=max(0, banners - allowance),
                  repeated_banner_words=banners * len(rows),
                  words_with_repeated_banners=script.words + banners * (len(rows) - 1),
                  elements=sum(row['elements_with_banner'] for row in rows),
                  slot_budget=panels.SLOTS_PER_PANEL * len(rows),
                  panels=rows, words_by_type=dict(types))
    result.update(metrics(script.words, allowance))
    result['band'] = band(result)
    return result


def aggregate(rows: list[dict], level: str, identity: str, title: str = '') -> dict:
    result = dict(level=level, id=identity, title=title, pages=len(rows))
    for key in ('declared_panels', 'image_slots', 'banner_words', 'repeated_banner_words',
                'words_with_repeated_banners', 'elements', 'slot_budget'):
        result[key] = sum(row[key] for row in rows)
    result.update(metrics(sum(row['words'] for row in rows), sum(row['budget_words'] for row in rows)))
    # Net remaining hides a dense page offset by a sparse one: report both.
    result['unused_on_under_budget_pages'] = sum(row['remaining_words'] for row in rows)
    result['excess_on_over_budget_pages'] = sum(row['over_words'] for row in rows)
    return result


def distribution(rows: list[dict]) -> dict:
    words = sorted(row['words'] for row in rows)
    return dict(count=len(words), minimum=words[0] if words else None,
                median=statistics.median(words) if words else None,
                mean=statistics.mean(words) if words else None,
                p90=words[math.ceil(.9 * len(words)) - 1] if words else None,
                maximum=words[-1] if words else None,
                utilization_bands=dict(Counter(row['band'] for row in rows)))


def make_report(pages: list[dict], allowance: int) -> dict:
    all_panels = [panel for page in pages for panel in page['panels']]
    chapters = [aggregate([p for p in pages if p['chapter'] == chapter], 'chapter', chapter)
                for chapter in dict.fromkeys(p['chapter'] for p in pages)]
    types = Counter()
    for page in pages:
        types.update(page['words_by_type'])
    return dict(schema_version=1, methodology=METHOD, page_budget_words=allowance,
                scope=dict(first_page=pages[0]['id'], last_page=pages[-1]['id'], pages=len(pages)),
                overall=aggregate(pages, 'overall', 'selected'), chapters=chapters,
                pages=pages, panels=all_panels, words_by_type=dict(types),
                distributions=dict(pages=distribution(pages), panel_runs=distribution(all_panels)))


def select(scripts: dict, chapters: list, page_spec: str | None, chapter_id: str | None) -> list:
    numbers = sorted(scripts)
    if page_spec:
        match = re.fullmatch(r'(\d{1,3})(?:-(\d{1,3}))?', page_spec)
        if not match:
            raise ValueError('--pages must be NNN or NNN-NNN')
        first, last = int(match[1]), int(match[2] or match[1])
        if first > last:
            raise ValueError('--pages range is reversed')
        missing = sorted(set(range(first, last + 1)) - set(numbers))
        if missing:
            raise ValueError(f'unknown pages: {missing}')
        numbers = [n for n in numbers if first <= n <= last]
    if chapter_id and chapter_id not in {c.id for c in chapters}:
        raise ValueError(f'unknown chapter: {chapter_id}')
    selected = []
    for number in numbers:
        owners = [c for c in chapters if c.first_page <= number <= c.last_page]
        if len(owners) != 1:
            raise ValueError(f'{number:03d}: expected one chapter, found {len(owners)}')
        if chapter_id is None or owners[0].id == chapter_id:
            selected.append((scripts[number], owners[0]))
    if not selected:
        raise ValueError('selection contains no pages')
    return selected


def ordered(rows: list[dict], sort: str, limit: int | None) -> list[dict]:
    if sort != 'reading':
        key = {'used': 'words', 'usage': 'utilization_pct', 'remaining': 'remaining_words'}[sort]
        def order_key(row):
            value = row[key] if row[key] is not None else float('inf')
            return (-value if sort == 'remaining' else value, row['id'])
        rows = sorted(rows, key=order_key)
    return rows[:limit] if limit else rows


def fmt(value) -> str:
    if value is None:
        return 'n/a'
    return f'{value:,.1f}' if isinstance(value, float) else str(value)


def table(rows: list[dict], show_text: bool = False) -> str:
    lines = ['ID             Words    Budget   Used %      Left    Excess   Elements/slots  Title']
    for row in rows:
        elements = row.get('elements_with_banner', row['elements'])
        lines.append(f"{row['id']:<14} {row['words']:>5} {fmt(row['budget_words']):>9} "
                     f"{fmt(row['utilization_pct']):>8} {fmt(row['remaining_words']):>9} "
                     f"{fmt(row['over_words']):>9} {elements:>5}/{row['slot_budget']:<5}  {row.get('title', '')}")
        if show_text and row.get('text'):
            lines.append('  ' + row['text'])
    return '\n'.join(lines)


def text_report(report: dict, args) -> str:
    out = ['LETTERING BUDGET — selected scope', report['methodology'], '',
           table([report['overall']]),
           f"{report['overall']['pages']} pages; {report['overall']['declared_panels']} declared panels; "
           f"{report['overall']['image_slots']} image slots.",
           f"Unused on under-budget pages: {fmt(report['overall']['unused_on_under_budget_pages'])}; "
           f"excess on over-budget pages: {fmt(report['overall']['excess_on_over_budget_pages'])}.",
           f"Banner words counted once per page: {report['overall']['banner_words']}; "
           f"total with banners repeated per image slot: {report['overall']['words_with_repeated_banners']}.",
           '', 'CHAPTERS', table(report['chapters']), '', 'WORD DISTRIBUTIONS']
    for level, dist in report['distributions'].items():
        out.append(f"{level}: " + '; '.join(f'{k}={fmt(v)}' for k, v in dist.items() if k != 'utilization_bands'))
        out.append('  ' + '; '.join(f'{k}: {v}' for k, v in dist['utilization_bands'].items()))
    out += ['', 'WORDS BY LETTERING TYPE', '; '.join(f'{k}: {v}' for k, v in report['words_by_type'].items())]
    out += ['', 'SPARSEST PAGES (lowest percentage)', table(ordered(report['pages'], 'usage', args.limit or 10)),
            '', 'FULLEST PAGES', table(sorted(report['pages'], key=lambda r: (-r['utilization_pct'], r['id']))[:args.limit or 10])]
    for level in ('pages', 'panels'):
        if args.level in (level, 'all'):
            out += ['', level.upper(), table(ordered(report[level], args.sort, args.limit), args.show_text)]
    return '\n'.join(out) + '\n'


def tsv_report(report: dict, args) -> str:
    columns = ['level', 'id', 'page', 'chapter', 'title', 'words', 'budget_words',
               'utilization_pct', 'remaining_words', 'over_words', 'declared_panels',
               'image_slots', 'elements', 'elements_with_banner', 'slot_budget',
               'banner_words', 'repeated_banner_words', 'words_with_repeated_banners',
               'pages', 'panel_budget_words', 'banner_over_words',
               'unused_on_under_budget_pages', 'excess_on_over_budget_pages', 'band', 'grouped']
    if args.show_text:
        columns.append('text')
    levels = ['chapters', 'pages', 'panels'] if args.level == 'all' else [args.level]
    rows = [report['overall']] if args.level in ('summary', 'all') else []
    for level in levels:
        if level in report and isinstance(report[level], list):
            rows.extend(ordered(report[level], args.sort, args.limit))
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore', delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def check() -> int:
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    fixture = '''---
page: 1
---
## Persistent banner
`INVENTED SCENE`
## Panel 1
**Frame:** ignored words here
**Caption:**
> Don’t stop. Try again now.
**References:** none
## Panel 2
**Frame:** silent picture
## Page notes
ignored apparatus
'''
    page = measure(panels.split_page(1, fixture), 'test', 'Fixture', 10)
    require(page['words'] == 7 and page['banner_words'] == 2, 'banner/word count')
    require([r['budget_words'] for r in page['panels']] == [8, 8], 'reserved banner allocation')
    require(page['panels'][0]['over_words'] == 0 and page['panels'][1]['band'] == 'zero words', 'local overage and silence')
    require(page['words_with_repeated_banners'] == 9, 'repeated banner estimate')
    grouped = measure(panels.split_page(2, '## Panels 1–9\n**Caption:**\n> NINE DIFFERENT LANES\n'), 'test', 'Group', 180)
    require(len(grouped['panels']) == 1 and grouped['declared_panels'] == 9 and grouped['words'] == 3, 'group not multiplied')
    require(grouped['panels'][0]['budget_words'] == 100, 'group allocation')
    over = measure(panels.split_page(3, fixture), 'test', 'Over', 1)
    require(over['panels'][0]['utilization_pct'] is None and over['over_words'] == 6, 'banner exhausts budget')
    report = make_report([page, grouped, over], 10)
    require(report['overall']['words'] == 17 and report['overall']['excess_on_over_budget_pages'] == 6, 'aggregate retains overages')
    require(sum(report['words_by_type'].values()) == 17, 'type reconciliation')
    require(distribution([])['median'] is None, 'empty distribution')
    require(json.loads(json.dumps(report))['overall']['words'] == 17, 'JSON roundtrip')
    args = argparse.Namespace(level='panels', sort='usage', limit=1, show_text=True)
    exported = list(csv.DictReader(io.StringIO(tsv_report(report, args)), delimiter='\t'))
    require(len(exported) == 1 and exported[0]['words'] == '0', 'TSV sorted/limited detail')
    require(report['overall']['words'] == 17, 'detail limit leaves totals intact')
    require('LETTERING BUDGET' in text_report(report, args), 'human-readable report')
    for row in report['panels']:
        row['text'] = 'A tab\tand a "quote"\nnext line'
    args.limit = None
    exported = list(csv.DictReader(io.StringIO(tsv_report(report, args)), delimiter='\t'))
    require(exported[0]['text'] == report['panels'][0]['text'], 'TSV quoting roundtrip')
    chapter = crossref.Chapter('test', 'Test', 1, 3)
    require(len(select({1: None, 2: None, 3: None}, [chapter], '002-003', 'test')) == 2, 'range selection')
    for spec in ('003-001', '000', 'abc'):
        try:
            select({1: None}, [chapter], spec, None)
        except ValueError:
            pass
        else:
            raise ValueError(f'accepted invalid selection {spec}')
    scripts = panels.read_scripts()
    selected = select(scripts, crossref.read_chapters(), None, None)
    actual = [measure(script, c.id, '', panels.DENSE_PAGE_WORDS) for script, c in selected]
    require(sum(p['words'] for p in actual) == sum(s.words for s in scripts.values()), 'repository census parity')
    for p in actual:
        require(all(r['budget_words'] <= panels.MAX_PANEL_WORDS for r in p['panels']), 'independent panel ceilings')
    require(not panels.word_limit_errors(scripts), 'repository word ceilings')
    print(f'Text budget check passed: offline fixtures and {len(actual)} pages reconcile with panels.py.')
    return 0


def positive(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError('must be positive')
    return number


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('check', help='offline regression fixtures and current census reconciliation')
    report = commands.add_parser('report', help='read-only budget report; JSON always contains the complete selection')
    report.add_argument('--pages', help='NNN or inclusive NNN-NNN')
    report.add_argument('--chapter', help='chapter ID, e.g. prologue, 01, epilogue')
    report.add_argument('--page-budget', type=positive, default=panels.DENSE_PAGE_WORDS, help='what-if allowance (default: 400); does not change policy')
    report.add_argument('--format', choices=['text', 'json', 'tsv'], default='text')
    report.add_argument('--level', choices=['summary', 'chapters', 'pages', 'panels', 'all'], default='summary', help='text detail / TSV rows; JSON always includes all levels')
    report.add_argument('--sort', choices=['reading', 'used', 'usage', 'remaining'], default='reading', help='detail ordering: ascending words/percentage, descending remaining')
    report.add_argument('--limit', type=positive, help='limit detail/ranking rows only; totals and JSON retain the full selection')
    report.add_argument('--show-text', action='store_true', help='include lettering in text/TSV panel detail (JSON always includes it)')
    args = parser.parse_args(argv)
    try:
        if args.command == 'check':
            return check()
        selected = select(panels.read_scripts(), crossref.read_chapters(), args.pages, args.chapter)
        measured = []
        for script, chapter in selected:
            title = re.search(r'^title:\s*(.+)$', crossref.front_matter(script.text), re.MULTILINE)
            measured.append(measure(script, chapter.id, title[1].strip('"') if title else '', args.page_budget))
        data = make_report(measured, args.page_budget)
        titles = {c.id: c.title for c in crossref.read_chapters()}
        for row in data['chapters']:
            row['title'] = titles[row['id']]
        output = (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n' if args.format == 'json'
                  else tsv_report(data, args) if args.format == 'tsv' else text_report(data, args))
        print(output, end='')
        return 0
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    sys.exit(main())
