#!/usr/bin/env python3
"""Location background palette and conservative storyboard fill; standard library only.

plan is read-only; apply creates missing versioned components and fills only scenes
without setting artwork. Existing components, foregrounds and intentional blanks stay.
"""
from __future__ import annotations
import argparse
import html
import re
from pathlib import Path

import panels
import storyboards
import svg_components

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'location-background-'
# Margin motifs are authored setting cues, never records, counts, paths or claims.
# Synonymous source IDs have different views of a setting, not different real sites.
MOTIFS = {
 'agent-board-composite': ('Open shared-board margin', 'M4 17H96M4 83H96M9 22V35H16M9 43V56H16M9 64V77H16M84 22H91V35M84 43H91V56M84 64H91V77'),
 'analysis-agent-tree': ('Branching analysis margin', 'M50 4V9M50 9H16V16M50 9H84V16M16 16H6V24M16 16H26V20M84 16H74V20M84 16H94V24M6 78V92H94V78'),
 'artifactory-cache': ('Indented package-cache shelves', 'M5 10H95M8 19V83M8 24H17M8 42H22M8 62H17M8 80H22M82 22H94V33H82ZM82 48H94V59H82ZM5 92H95'),
 'composite-accountability-forum': ('Paper-built four-bay forum', 'M4 5L26 9L49 5L73 9L96 5V95H4ZM4 5L16 22H84L96 5M16 22V78H84V22M16 78L4 95M84 78L96 95M24 12V19M42 10V19M60 10V19M78 12V19'),
 'composite-lab-room': ('Broken conference envelope', 'M4 8H35M40 8H71M76 8H96V92H4V8M4 8L18 24H82L96 8M18 24V76H82V24M18 76L4 92M82 76L96 92M33 15H67'),
 'creator-production-tooling': ('Terminal gutter and diff rails', 'M4 10H96V90H4ZM4 19H96M9 14H13M17 14H21M9 27L14 31L9 35M17 35H23M7 73H16M11 69V77M84 78H93M28 85H72'),
 'curt-home-office': ('Domestic window and receding floor', 'M4 8L18 22H82L96 8M4 8V94H96V8M18 22V74H82V22M18 74L4 94M82 74L96 94M7 29H15V58H7ZM11 29V58M7 43H15M85 31H94M85 42H94M86 31V25M91 31V23'),
 'customer-hosted-modal-workload': ('Nested customer island, upper view', 'M3 5H97V95H3ZM8 10H92V90H8ZM16 17H84M16 17V27M84 17V27M16 83H84M16 73V83M84 73V83M25 6H41M59 94H75'),
 'documentary-evidence-field': ('Folded evidence sheet', 'M8 4H80L94 18V96H8ZM80 4V18H94M13 23V80M17 23V80M24 89H80M24 93H61'),
 'evaluation-container': ('Isolated task boundary', 'M5 7H95V93H5ZM10 12H30M70 12H90M10 88H30M70 88H90M10 28V72M90 28V72'),
 'evaluation-container-53927': ('Short-budget lane enclosure', 'M5 8H95V92H5ZM10 14H90M10 86H90M7 25H14M7 37H14M7 49H14M7 61H14M7 73H14M78 14V19H89V14'),
 'evaluation-containers': ('Parallel isolated lane edges', 'M4 8H29M36 8H63M70 8H96M4 92H29M36 92H63M70 92H96M4 8V92M96 8V92M29 8V17M36 8V17M63 8V17M70 8V17M29 83V92M36 83V92M63 83V92M70 83V92'),
 'evaluation-transcript-archive': ('Transcript spool and sequence margin', 'M12 6H91V94H12ZM7 6V94M17 14H28M17 23H24M17 32H28M17 41H24M17 50H28M17 59H24M17 68H28M17 77H24M17 86H28M82 10V90'),
 'evidence-dossier': ('Tabbed case folder', 'M5 17V8H30L37 17H95V93H5ZM10 22H90M10 87H90M7 30H17M7 40H17M7 50H17M77 9H91V14H77Z'),
 'external-network': ('Disconnected exterior segments', 'M4 20H20V7M36 7H53M72 7H91V24M4 43H13M4 64H13M8 83H23V94M41 94H57M77 94H94V76M88 42H96M88 59H96'),
 'hugging-face-infrastructure': ('Platform service terrace', 'M5 12H95V88H5ZM9 18H28M38 18H62M72 18H91M10 82H30V91M40 82H60V91M70 82H90V91M8 30V69M92 30V69'),
 'huggingface-clusters': ('Separate cluster perimeter cells', 'M4 5H28V17H4ZM38 5H62V17H38ZM72 5H96V17H72ZM4 83H28V95H4ZM38 83H62V95H38ZM72 83H96V95H72ZM7 27V73M93 27V73'),
 'huggingface-dataset-processor': ('Worker enclosure and layered dataset edge', 'M7 7H93V93H7ZM11 16H89M11 84H89M9 29H19V40H9ZM9 45H19V56H9ZM9 61H19V72H9ZM83 24V75M88 24V75'),
 'huggingface-infrastructure': ('Stepped infrastructure surround', 'M4 26V12H30V6H70V12H96V26M4 74V88H30V94H70V88H96V74M9 32V68M91 32V68M16 17H32M68 17H84'),
 'huggingface-production-node': ('Production chassis rim', 'M4 10H96V90H4ZM9 16H91V84H9ZM5 27H15M5 35H15M5 65H15M5 73H15M85 27H95M85 35H95M85 65H95M85 73H95'),
 'huggingface-security-stack': ('Layered telemetry bands', 'M6 9H94V18H6ZM9 23V77M91 23V77M6 82H94V91H6ZM17 10V17M34 10V17M51 10V17M68 10V17M85 10V17M18 84H30M40 84H53M65 84H82'),
 'institutional-composite': ('Unbranded institutional colonnade', 'M4 17L50 5L96 17M8 22H92M12 27V76M19 27V76M81 27V76M88 27V76M7 81H93M4 89H96M24 94H76'),
 'jfrog-security-workspace': ('Patch-workbench rim', 'M5 10H95V78H5ZM10 17H90M11 26H19V34H11ZM11 40H19V48H11ZM81 27H89M81 42H89M50 79V87M29 87H71M5 95H95'),
 'metr-review-workspace': ('Evidence wall and bounded review floor', 'M4 7H96V94H4ZM12 19H88V73H12ZM12 19L4 7M88 19L96 7M12 73L4 94M88 73L96 94M18 10V16M26 10V16M34 10V16M42 10V16M50 10V16M58 10V16M66 10V16M74 10V16M82 10V16'),
 'modal-customer-workload': ('Customer island inside intact host', 'M3 4H97V96H3ZM8 9H92V91H8ZM16 21V16H84V21M16 79V84H84V79M4 30H8M4 70H8M92 30H96M92 70H96'),
 'openai-artifactory': ('Administrative repository surround', 'M5 14H95V91H5ZM5 14V6H29V14M12 20V82M12 26H23M12 47H23M12 68H23M77 7H94M81 11H94M80 25H90V37H80ZM80 62H90V74H80Z'),
 'openai-artifactory-cache': ('Archive-side cache shelves', 'M5 8H95V92H5ZM11 15V84M11 22H21M11 40H26M11 58H21M11 76H26M82 16V84M87 16V84M30 10H67M30 89H67'),
 'openai-cloud-worker': ('Cloud-hosted worker chassis', 'M5 24V16H20M80 16H95V24M5 76V91H95V76M11 30V70M89 30V70M26 15Q26 7 36 8Q39 1 49 5Q60 1 65 9Q76 7 76 15M20 84H80'),
 'openai-cybergym-evaluation': ('Challenge and grader boundary tabs', 'M5 8H95V92H5ZM10 14H39M61 14H90M10 86H39M61 86H90M7 26H16V42H7ZM84 58H93V74H84ZM44 9V16M50 9V16M56 9V16'),
 'openai-incident-response': ('Escalation docket surround', 'M7 5H93V95H7ZM7 18H93M14 9H28M36 9H50M58 9H72M14 26H22V37H14ZM14 48H22V59H14ZM14 70H22V81H14ZM31 88H85'),
 'openai-provided-evidence-store': ('Sealed source-store corners', 'M6 6H94V94H6ZM6 6L18 18M94 6L82 18M6 94L18 82M94 94L82 82M21 10H79M21 90H79M10 25V75M90 25V75M14 36H20M14 58H20'),
 'openai-research-environment': ('Research rack-room shell', 'M3 9H97V95H3ZM3 9L21 23H79L97 9M21 23V73H79V23M21 73L3 95M79 73L97 95M8 31H16M8 39H16M8 47H16M84 31H92M84 39H92M84 47H92'),
 'openai-research-infrastructure': ('Multi-service research backbone', 'M5 8H95M5 92H95M6 18H17V34H6ZM6 42H17V58H6ZM6 66H17V82H6ZM83 18H94V34H83ZM83 42H94V58H83ZM83 66H94V82H83ZM27 13H73M27 87H73'),
 'openai-training-program': ('Training-batch trays', 'M6 7H94V20H6ZM6 80H94V93H6ZM13 8V19M27 8V19M41 8V19M55 8V19M69 8V19M83 8V19M10 29V71M90 29V71M21 86H44M55 86H79'),
 'public-announcement-ledger': ('Dated announcement folio', 'M8 9H92V94H8ZM8 23H92M19 5V16M40 5V16M61 5V16M82 5V16M13 31H22M13 47H22M13 63H22M13 79H22M32 88H84'),
 'public-internet': ('Open unjoined network margin', 'M4 6H24M37 6H63M76 6H96M4 6V24M96 6V24M4 76V94H24M37 94H63M76 94H96V76M7 39L13 45L7 51M93 49L87 55L93 61'),
 'public-record': ('Open public document leaves', 'M50 13Q28 3 7 11V89Q28 81 50 91Q72 81 93 89V11Q72 3 50 13M50 13V20M50 84V91M12 18L19 16M12 26L19 24M81 16L88 18M81 24L88 26'),
 'public-web': ('Browser page with open outer margin', 'M5 12H95V91H5ZM5 23H95M11 17H15M20 17H24M31 17H82M10 30V80M90 30V80M25 86H75'),
 'public-wiki-dse': ('Community wiki sidebar and page tabs', 'M5 9H95V92H5ZM5 23H95M10 15H29M38 15H57M67 15H85M19 23V92M9 34H15M9 43H15M9 52H15M9 69H15M25 85H89'),
 'reconstructed-security-operations-center': ('Tiled telemetry wall and paging recess', 'M4 8H96V94H4ZM13 21H87V74H13ZM4 8L13 21M96 8L87 21M13 74L4 94M87 74L96 94M20 10H36V17H20ZM43 10H59V17H43ZM66 10H82V17H66ZM7 37H11V57H7Z'),
 'regulatory-office': ('Compulsory-process docket, no invented office', 'M10 7H90V93H10ZM16 14H84M16 86H84M13 25H24M13 40H24M13 55H24M13 70H24M75 18V77M80 18V77'),
 'report-comparison-space': ('Two independent source gutters', 'M5 7H44M56 7H95M5 7V93H44M56 93H95V7M44 7V17M56 7V17M44 83V93M56 83V93M11 17H31M69 17H89M11 83H31M69 83H89'),
 'security-operations-center': ('Long telemetry wall and fluorescent ceiling', 'M4 9H96V94H4ZM15 24H85V74H15ZM4 9L15 24M96 9L85 24M15 74L4 94M85 74L96 94M25 14H43M57 14H75M18 79H82'),
 'separate-evaluation-run': ('Offset independent task lane', 'M12 5H95V88H12ZM5 12V95H88M18 11H37M70 11H89M18 82H37M70 82H89M17 25V66M90 25V66'),
 'systems-view': ('Unconnected system quadrants', 'M5 24V6H28M72 6H95V24M5 76V94H28M72 94H95V76M12 18V12H30M70 12H88V18M12 82V88H30M70 88H88V82'),
 'training-configuration': ('Flat specification register', 'M5 8H95V92H5ZM5 22H95M18 22V92M9 31H14M9 47H14M9 63H14M9 79H14M26 14H49M59 14H84M26 85H84'),
 'unidentified-evaluation-container': ('Anonymous enclosure with empty header', 'M7 6H93V94H7ZM16 12H84V19H16ZM12 30V70M88 30V70M16 87H32M68 87H84M8 77L15 84M85 84L92 77'),
 'unnamed-future-evaluation': ('Unfamiliar clipped-corner surface', 'M18 5H82L95 18V82L82 95H18L5 82V18ZM22 11H78M22 89H78M11 24V36M11 64V76M89 24V36M89 64V76M7 18H18V7M82 93V82H93'),
 'institutional-montage': ('Separate institutional strips', 'M5 7H26M30 12H48M52 7H70M74 12H95M5 7V93H26M30 88H48M52 93H70M74 88H95V12M30 12V20M52 7V20M74 12V20'),
 'continuation-montage': ('Unequal open-ended continuation rails', 'M5 8H95M5 20H24M5 8V92M95 8V78M13 87H31M38 92H57M65 83H82M89 88H96M24 15V23M45 12V20M68 15V23M86 12V20'),
}


def svg(location):
    title, path = MOTIFS[location]
    # Restrained ink; clear center, no text, arrows, people, credentials or logos.
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">\n'
            f'<title>{html.escape(title)}</title>\n'
            '<g fill="none" stroke="currentColor" stroke-width="0.8" '
            'stroke-linejoin="round" stroke-linecap="round" opacity="0.34">'
            f'<path d="{path}"/></g>\n</svg>\n')


def locations(body):
    match = re.search(r'^\*\*Location:\*\*(.*?)(?=^\*\*|^## |\Z)', body, re.M | re.S)
    if not match:
        raise ValueError('Panel has no location field')
    return re.findall(r'`([^`]+)`', match[1])


def sources():
    result = {}
    all_locations = set()
    for page in panels.read_scripts().values():
        metadata = re.search(r'^locations:\n((?:  - [^\n]+\n)+)', page.text, re.M)
        all_locations.update(re.findall(r'  - (.+)', metadata[1]))
        sections = [(f'{page.id}-{s.index:02d}', s.body) for s in page.sections]
        if page.grouped:
            sections = [(f'{page.id}-01', page.text.split('## Panels ', 1)[1])]
        for key, body in sections:
            result[key] = locations(body)
            all_locations.update(result[key])
    return result, all_locations


def existing_background(scene, catalog):
    # Solid-color blank/silent panels and borderless ending frames are authored
    # backgrounds. A palette undercoat on an ordinary scene is not a setting.
    if not scene['nodes'] or scene.get('border') == 'none' or scene.get('shot') == 'blank':
        return 'intentional blank or borderless field'
    if any(catalog[n['asset']]['category'] == 'locations' for n in scene['nodes']):
        return 'existing location artwork'
    return None


def background_nodes(key, scene, ids):
    def node(loc, box):
        return dict(asset=PREFIX+loc, box=box, color='steel')
    if key in ('006-01', '007-01'):
        cells = [n['box'] for n in scene['nodes'] if n['asset'] == 'outline-box']
        assert len(cells) == 9
        result = [node(ids[0], b) for b in cells]
        # The nine lanes occupy the left field; the shared cache is the existing
        # right-side resource field. Never lay a backdrop across cell gutters.
        if len(ids) > 1:
            result.append(node(ids[1], [0.59, 0.03, 0.37, 0.91]))
        return result
    n = len(ids)
    cols = min(n, 3)
    rows = (n+cols-1)//cols
    gutter = 0.025
    width = (0.96-gutter*(cols-1))/cols
    height = (0.96-gutter*(rows-1))/rows
    return [node(loc, [round(0.02+(i%cols)*(width+gutter),6),
                        round(0.02+(i//cols)*(height+gutter),6),
                        round(width,6), round(height,6)]) for i,loc in enumerate(ids)]


def plan():
    library = svg_components.Library()
    catalog = library.load()['components']
    data = storyboards.load()
    by_panel, all_locations = sources()
    unknown = all_locations-set(MOTIFS)
    if unknown:
        raise ValueError('Design background motifs for: '+', '.join(sorted(unknown)))
    missing = sorted(loc for loc in all_locations if PREFIX+loc not in catalog)
    additions = {}
    skipped = {}
    for key, scene in data['scenes'].items():
        reason = existing_background(scene, catalog)
        if reason:
            skipped[key] = reason
        else:
            additions[key] = background_nodes(key, scene, by_panel[key])
    return library, data, missing, additions, skipped


def apply():
    library, data, missing, additions, skipped = plan()
    for loc in missing:
        title, _ = MOTIFS[loc]
        library.add(PREFIX+loc, svg(loc), 'Initial quiet location background; open center and distinctive margin geometry.',
                    create=dict(category='locations', name=f'Background — {loc}',
                                description=f'{title}. Reusable background for {loc}; project-authored setting cues, not documentary architecture. Keep actors, states and lettering separate.'))
    for key, nodes in additions.items():
        data['scenes'][key]['nodes'] = nodes + data['scenes'][key]['nodes']
    if additions:
        storyboards.DATA.write_text(storyboards.encoded(data))
    print(f'Created {len(missing)} backgrounds; filled {len(additions)} storyboards; preserved {len(skipped)} existing backgrounds.')


def check():
    library, data, missing, additions, _ = plan()
    errors = library.errors()
    if missing: errors.append('Missing palette backgrounds: '+', '.join(missing))
    if additions: errors.append('Missing scene backgrounds: '+', '.join(additions))
    by_panel, all_locations = sources()
    catalog = library.load()['components']
    fragments = [re.sub(r'<title>.*?</title>', '', library.resolve(PREFIX+loc))
                 for loc in sorted(all_locations) if PREFIX+loc in catalog]
    if len(set(fragments)) != len(fragments): errors.append('Duplicate background geometry')
    for key, scene in data['scenes'].items():
        actual = {n['asset'][len(PREFIX):] for n in scene['nodes'] if n['asset'].startswith(PREFIX)}
        if actual and actual != set(by_panel[key]): errors.append(f'{key}: background/location drift')
    if errors: raise ValueError('\n'.join(errors))
    print(f'Location backgrounds checked: {len(all_locations)} unique palette entries; all {len(data["scenes"])} scenes have a setting or intentional blank background.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan','apply','check'])
    args = parser.parse_args()
    if args.command == 'apply': apply()
    elif args.command == 'check': check()
    else:
        _, _, missing, additions, skipped = plan()
        print(f'{len(missing)} palette additions; {len(additions)} scenes to fill; {len(skipped)} backgrounds preserved.')
        for k, reason in skipped.items(): print(k, reason)

if __name__ == '__main__':
    main()
