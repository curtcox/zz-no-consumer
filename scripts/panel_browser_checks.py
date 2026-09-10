#!/usr/bin/env python3
"""Create a self-contained browser regression page; verify its saved DOM in CI.

python3 scripts/panel_browser_checks.py write --out /tmp/panel-check.html
python3 scripts/panel_browser_checks.py verify --out /tmp/panel-check-result.html
Fixtures use the real local renderer and both real stylesheets. No dependencies.
"""
import argparse
import base64
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def document():
    import local_viewer as local
    import panel_layout
    import viewer_overlays
    session = local.Session()
    # Positioning parity is measured against the published stylesheet, which has no
    # preview overlays; the local-only layers get their own cases below.
    bare = dict(viewer_overlays.DEFAULTS, fog=False, ants=False)
    representatives = {}
    for number, record in session.pages.items():
        representatives.setdefault(record.panel_count, number)
    audit = (local.UI/'panel-audit.js').read_text()
    cases = []
    def add(name, body, css, width, expect=None, legacy=False):
        # Neutral, self-contained images: test actual positioning independently of artwork.
        def image(match):
            key=match.group(1); w,h=panel_layout.target(key)
            svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="100%" height="100%" fill="#53794c"/><text x="20" y="80" font-size="60">{key}</text></svg>'
            return 'src="data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode()+'"'
        # The real page-wide layer, so the fixture proves it neither moves nor hides a panel.
        def overlay(match):
            svg=overlays.setdefault(match.groups(), session.page_overlay(match.group(1), int(match.group(2))))
            return 'src="data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode()+'"'
        body=re.sub(r'src="/panel/(\d{3}-\d{2})\.svg[^"]*"',image,body)
        body=re.sub(r'src="/overlay/([a-z]+)/(\d{3})\.svg"',overlay,body)
        content=f'<!doctype html><meta charset="utf-8"><style>{css}</style>{body}<script>{audit}</script>'
        # Frames are tall enough that ordinary scroll position does not hide test samples.
        cases.append(dict(name=name,document=content,width=width,expect=expect,legacy=legacy))
    overlays={}
    local_css=(local.UI/'app.css').read_text()
    static_css=(ROOT/'site/viewer/viewer.css').read_text()
    for count,number in representatives.items():
        body=session.render_page(number,'art',bare)
        for width in (390,1280):
            add(f'local-{count}-{width}',body,local_css,width)
            add(f'static-{count}-{width}',body.replace('<img style="', '<img class="page-art__panel" style="'),static_css,width)
    # Include the real left/right/spread rendering paths.
    for mode in ('left','right','spread'):
        for width in (390,1280):
            add(f'{mode}-{width}',session.render(mode,2,bare),local_css,width)
    # Preview overlays, including the one page that carries both layers at once.
    for number in sorted({1, *(n for n in session.pages if viewer_overlays.has_page_ants(n))}):
        for width in (390,1280):
            add(f'overlays-{number:03d}-{width}',session.render_page(number,'art',viewer_overlays.DEFAULTS),local_css,width)
    page=session.render_page(1,'art',bare)
    old=re.sub(r' style="[^"]*"','',page).replace(' data-panel-layout="2"','')
    add('old-server-new-css',old,local_css,1280,legacy=True)
    add('old-static-new-css',old.replace('<img ','<img class="page-art__panel" '),static_css,390,legacy=True)
    # Prove the audit catches the original failure, including right-sized but stacked images.
    add('overlap-negative',old,local_css+' .page-art > img {position:absolute!important;left:0;top:0;width:300px!important;height:200px!important}',1280,'panels overlap',True)
    add('missing-negative',re.sub(r'<img [^>]*>','',page,count=1),local_css,1280,'panel count mismatch')
    add('zero-negative',page,local_css+' .page-art > img:first-child {height:0!important}',1280,'invisible panel')
    add('clipped-negative','<div style="height:100px;overflow:hidden">'+page+'</div>',local_css,1280,'panel clipped by ancestor')
    malformed=re.sub(r' style="left:[^"]*"','',page,count=1)
    add('coordinates-negative',malformed,local_css,1280,'missing panel coordinates')
    runner=r'''
    const cases = CASES;
    (async () => {
      const results=[];
      for(const test of cases) {
        const frame=document.createElement('iframe');
        frame.style.cssText=`display:block;border:0;width:${test.width}px;height:2400px`;
        document.body.append(frame);
        await new Promise(resolve=>{frame.onload=resolve;frame.srcdoc=test.document});
        await Promise.all([...frame.contentDocument.images].map(img=>img.decode().catch(()=>{})));
        const errors=await frame.contentWindow.auditPanelFit(frame.contentDocument,{allowLegacy:test.legacy});
        const passed=test.expect ? errors.some(e=>e.problem===test.expect) : errors.length===0;
        results.push({name:test.name,passed,errors});
        frame.remove();
      }
      const report={passed:results.every(r=>r.passed),count:results.length,results};
      document.querySelector('#results').textContent=JSON.stringify(report);
      document.title=report.passed?'PASS: panel browser checks':'FAIL: panel browser checks';
    })().catch(error=>{document.querySelector('#results').textContent=JSON.stringify({passed:false,error:String(error)})});
    '''.replace('CASES',json.dumps(cases).replace('</',r'<\/'))
    return '<!doctype html><meta charset="utf-8"><title>Running panel checks</title><pre id="results">pending</pre><script>'+runner+'</script>'


def verify(path):
    text=path.read_text()
    match=re.search(r'<pre id="results">(.*?)</pre>',text,re.S)
    if not match or match.group(1)=='pending': raise SystemExit('Browser checks did not complete')
    report=json.loads(html.unescape(match.group(1)))
    if not report.get('passed'): raise SystemExit(json.dumps(report,indent=2))
    print(f"Browser panel checks passed: {report['count']} cases")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['write','verify']);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.command=='write':args.out.write_text(document());print(args.out)
    else:verify(args.out)

if __name__=='__main__':main()
