#!/usr/bin/env python3
"""Versioned SVG components, independent of storyboards. Standard library only.

    python3 scripts/svg_components.py serve --port 8767
    python3 scripts/svg_components.py check [--built]
    python3 scripts/svg_components.py add COMPONENT --svg FILE --note TEXT
    python3 scripts/svg_components.py choose COMPONENT VERSION
    python3 scripts/svg_components.py export
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import tempfile
import threading
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
UI = Path(__file__).with_name('component_workshop_ui')
CATEGORIES = ('characters', 'objects', 'connections', 'locations')
KEY = re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z')
VERSION = re.compile(r'v[0-9]{3,}\Z')
MAX_SVG = 2_000_000
SVG_NS = 'http://www.w3.org/2000/svg'
TAGS = {'svg','g','path','rect','circle','ellipse','line','polyline','polygon','defs','symbol','use','clipPath','mask','linearGradient','radialGradient','stop','pattern','title','desc','image'}

def encoded(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + '\n'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def svg_body(svg):
    """Validate a self-contained, passive 100-unit component; retain authored bytes."""
    if not isinstance(svg,str) or not svg.strip() or len(svg.encode()) > MAX_SVG:
        raise ValueError('Provide an SVG of at most 2 MB.')
    if re.search(r'<!DOCTYPE|<!ENTITY',svg,re.I):
        raise ValueError('SVG entities and document types are not supported.')
    try:
        root=ET.fromstring(svg)
    except ET.ParseError as error:
        raise ValueError(f'Invalid SVG: {error}') from error
    if root.tag not in ('svg',f'{{{SVG_NS}}}svg'):
        raise ValueError('The file must have an SVG root.')
    try:
        view=[float(n) for n in root.get('viewBox','').replace(',',' ').split()]
    except ValueError:
        view=[]
    if view != [0,0,100,100]:
        raise ValueError('Components use viewBox="0 0 100 100".')
    if set(root.attrib)-{'viewBox','width','height'}:
        raise ValueError('Put presentation attributes on a group inside the SVG root.')
    ids=set();refs=[]
    nodes=list(root.iter())
    if len(nodes)>10000:
        raise ValueError('The SVG has too many elements.')
    for node in nodes:
        tag=node.tag
        if not isinstance(tag,str):continue
        if tag.startswith('{') and not tag.startswith('{'+SVG_NS+'}'):
            raise ValueError('Only SVG elements are supported.')
        tag=tag.split('}')[-1]
        if tag not in TAGS or (tag=='svg' and node is not root):
            raise ValueError(f'Unsupported SVG element: {tag}')
        for raw,value in node.attrib.items():
            attr=raw.split('}')[-1]
            if raw.startswith('{') and raw!='{http://www.w3.org/1999/xlink}href':
                raise ValueError('Unsupported attribute namespace.')
            if attr.lower().startswith('on') or attr in ('style','class'):
                raise ValueError('Use SVG presentation attributes, without scripts or CSS.')
            if attr=='id':
                if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.-]*',value) or value in ids:
                    raise ValueError('Component IDs must be unique XML identifiers.')
                ids.add(value)
            if attr=='href':
                if value.startswith('#'):refs.append(value[1:])
                elif tag=='image' and re.fullmatch(r'data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/=\s]+',value):
                    try:base64.b64decode(value.split(',',1)[1],validate=True)
                    except ValueError as error:raise ValueError('Invalid embedded image.') from error
                else:raise ValueError('External references are not supported; embed raster images or use local IDs.')
            if re.search(r'\burl\s*\(', value, re.I):
                match=re.fullmatch(r'url\(#([A-Za-z_][A-Za-z0-9_.-]*)\)',value)
                if not match:raise ValueError('Only local SVG paint references are supported.')
                refs.append(match[1])
            if 'javascript:' in value.lower():raise ValueError('Active content is not supported.')
    if set(refs)-ids:raise ValueError('An SVG reference names an ID absent from this component.')
    match=re.fullmatch(r'\s*(?:<\?xml[^?]*\?>\s*)?<svg\b[^>]*>(.*)</svg>\s*',svg,re.S)
    if not match:raise ValueError('Use an explicit SVG opening and closing tag.')
    fragment = match[1].strip()
    if 'xmlns:xlink=' not in fragment:
        fragment = re.sub(r'\bxlink:href=', 'href=', fragment)
    return fragment

def scope_ids(fragment,prefix):
    """Avoid collisions when a component with paint/clip IDs appears twice."""
    if not re.search(r'\bid\s*=', fragment):
        return fragment
    root = ET.fromstring('<g>'+fragment+'</g>')
    names = {node.get('id'): prefix+node.get('id') for node in root.iter() if node.get('id')}
    for node in root.iter():
        for attr, value in list(node.attrib.items()):
            if attr == 'id':
                node.set(attr, names[value])
            elif attr.split('}')[-1] == 'href' and value.startswith('#'):
                node.set(attr, '#'+names.get(value[1:], value[1:]))
            elif value.startswith('url(#') and value.endswith(')'):
                node.set(attr, 'url(#'+names.get(value[5:-1], value[5:-1])+')')
    return ''.join(ET.tostring(node, encoding='unicode') for node in root)

class Library:
    def __init__(self,root=ROOT):
        self.root=Path(root)
        self.catalog=self.root/'data/svg-components.json'
        self.compat=self.root/'data/storyboard-assets.json'
        self.files=self.root/'assets/svg-components'
        self.lockfile=self.root/'data/.svg-components.lock'

    def load(self):
        data=json.loads(self.catalog.read_text())
        if data.get('version')!=1:raise ValueError('Unsupported component catalog version.')
        return data

    def revision(self):return sha(self.catalog.read_bytes())

    @contextmanager
    def lock(self):
        try:fd=os.open(self.lockfile,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        except FileExistsError as error:raise ValueError('The component library is busy. Retry after the other operation finishes.') from error
        try:
            os.write(fd,str(os.getpid()).encode());os.close(fd)
            yield
        finally:self.lockfile.unlink()

    def record(self,key,version=None,data=None):
        if not isinstance(key,str) or not KEY.fullmatch(key):raise ValueError('Invalid component ID.')
        data=self.load() if data is None else data
        if key not in data['components']:raise ValueError('Unknown component: '+key)
        component=data['components'][key];version=version or component['default']
        if not isinstance(version,str) or not VERSION.fullmatch(version):raise ValueError('Invalid component version.')
        for row in component['versions']:
            if row['id']==version:return row
        raise ValueError(f'Unknown version: {key}/{version}')

    def path(self,key,version):
        if not KEY.fullmatch(key) or not VERSION.fullmatch(version):raise ValueError('Invalid component path.')
        result=self.files/key/(version+'.svg')
        if not result.resolve().is_relative_to(self.files.resolve()):raise ValueError('Component files must stay inside the library.')
        return result

    def source(self,key,version=None,data=None):
        record=self.record(key,version,data)
        raw=self.path(key,record['id']).read_bytes()
        if sha(raw)!=record['sha256']:raise ValueError(f'{key}/{record["id"]}: saved SVG changed; save a new version instead.')
        return raw.decode()

    def resolve(self,key,version=None,data=None):return svg_body(self.source(key,version,data))

    def compiled(self,data):
        return dict(version=1,about=data['compatibility_about'],assets={k:self.resolve(k,c['default'],data) for k,c in data['components'].items()})

    def _atomic(self,path,text):
        fd,name=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
        try:
            with os.fdopen(fd,'w') as out:out.write(text)
            os.replace(name,path)
        finally:
            if os.path.exists(name):os.unlink(name)

    def _commit(self,data):
        # Catalog is authoritative. If interrupted before the compatibility export,
        # `export` repairs the derived file; no historical SVG is overwritten.
        compiled=self.compiled(data)
        self._atomic(self.catalog,encoded(data))
        self._atomic(self.compat,encoded(compiled))

    def expect(self,revision):
        if revision is not None and revision!=self.revision():
            raise ValueError('The library changed in another window. Reload before saving.')

    def add(self,key,svg,note,*,parent=None,revision=None,create=None):
        svg_body(svg)
        if not isinstance(note,str) or not note.strip():raise ValueError('Describe what changed before saving a version.')
        if not isinstance(key,str) or not KEY.fullmatch(key):raise ValueError('Use a lowercase component ID with hyphens.')
        with self.lock():
            self.expect(revision);data=self.load()
            if create is not None:
                if key in data['components']:raise ValueError('That component ID already exists.')
                if create.get('category') not in CATEGORIES:raise ValueError('Choose a component category.')
                for field in ('name','description'):
                    if not isinstance(create.get(field),str) or not create[field].strip():raise ValueError('Provide a name and a visual purpose.')
                data['components'][key]=dict(name=create['name'].strip(),description=create['description'].strip(),category=create['category'],default='v001',versions=[])
            elif key not in data['components']:raise ValueError('Unknown component.')
            c=data['components'][key]
            if parent is not None:self.record(key,parent,data)
            number=max([int(v['id'][1:]) for v in c['versions']]+[0])+1
            version=f'v{number:03d}';path=self.path(key,version);path.parent.mkdir(parents=True,exist_ok=True)
            raw=(svg.strip()+'\n').encode()
            # Exclusive creation also refuses to overwrite a file orphaned by an
            # interrupted write. Its data must be recovered explicitly.
            with path.open('xb') as out:out.write(raw)
            c['versions'].append(dict(id=version,sha256=sha(raw),note=note.strip(),parent=parent,created=datetime.now(timezone.utc).isoformat(timespec='seconds')))
            self._commit(data)
            return version

    def choose(self,key,version,revision=None):
        with self.lock():
            self.expect(revision);data=self.load();self.record(key,version,data)
            data['components'][key]['default']=version;self._commit(data)

    def export(self):
        with self.lock():self._atomic(self.compat,encoded(self.compiled(self.load())))

    def usage(self):
        path=self.root/'data/storyboards.json'
        scenes=json.loads(path.read_text())['scenes'] if path.exists() else {}
        result={}
        for key,s in scenes.items():
            for node in s['nodes']:
                row=result.setdefault(node['asset'],{'default':set(),'pinned':{}})
                pin=node.get('asset_version')
                if pin:row['pinned'].setdefault(pin,set()).add(key)
                else:row['default'].add(key)
        return {k:dict(default=sorted(v['default']),pinned={p:sorted(keys) for p,keys in v['pinned'].items()}) for k,v in result.items()}

    def snapshot(self,editable=False,token=None):
        data=self.load();usage=self.usage();components=[]
        for key,c in data['components'].items():
            versions=[dict(v,url=f'versions/{key}/{v["id"]}.svg') for v in c['versions']]
            components.append(dict(c,id=key,versions=versions,usage=usage.get(key,dict(default=[],pinned={}))))
        return dict(components=components,revision=self.revision(),editable=editable,token=token,categories=list(CATEGORIES))

    def errors(self):
        errors=[]
        try:
            data=self.load()
            for key,c in data['components'].items():
                if c['category'] not in CATEGORIES or not c['name'] or not c['description']:errors.append(key+': incomplete definition')
                versions=[v['id'] for v in c['versions']]
                if len(set(versions))!=len(versions):errors.append(key+': duplicate versions')
                self.record(key,c['default'],data)
                for version in versions:self.resolve(key,version,data)
            if self.compiled(data)!=json.loads(self.compat.read_text()):errors.append('Default component export is stale; run svg_components.py export.')
            for key,usage in self.usage().items():
                self.record(key,data=data)
                for pin in usage['pinned']:self.record(key,pin,data)
        except (ValueError,KeyError,OSError,TypeError) as error:errors.append(str(error))
        return errors


def gallery(output,library=None):
    library=library or Library();output=Path(output);output.mkdir(parents=True,exist_ok=True)
    for path in UI.iterdir():
        if path.is_file():shutil.copyfile(path,output/path.name)
    (output/'catalog.json').write_text(encoded(library.snapshot()))
    data=library.load()
    for key,c in data['components'].items():
        for v in c['versions']:
            target=output/'versions'/key/(v['id']+'.svg');target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(library.source(key,v['id'],data))


def check_built(output,library=None):
    library=library or Library();output=Path(output)
    assert json.loads((output/'catalog.json').read_text())==library.snapshot(),'Built component catalog is stale.'
    for path in UI.iterdir():
        if path.is_file():assert (output/path.name).read_bytes()==path.read_bytes(),path.name
    for key,c in library.load()['components'].items():
        for v in c['versions']:assert (output/'versions'/key/(v['id']+'.svg')).read_text()==library.source(key,v['id'])


def server(library,port):
    token=secrets.token_urlsafe(32);job={'running':False,'message':'','ok':None};job_lock=threading.Lock()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send(self,status,body,mime='application/json'):
            if isinstance(body,(dict,list)):body=encoded(body).encode()
            if isinstance(body,str):body=body.encode()
            self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'" if mime!='image/svg+xml' else "sandbox; default-src 'none'; img-src data:; style-src 'unsafe-inline'")
            self.end_headers();self.wfile.write(body)
        def trusted_host(self):
            return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}')
        def do_GET(self):
            if not self.trusted_host():return self.send(403,{'error':'Local host required.'})
            path=urlsplit(self.path).path
            try:
                if path=='/catalog.json':return self.send(200,library.snapshot(True,token))
                if path=='/api/build':
                    with job_lock:return self.send(200,dict(job))
                if path in ('/','/index.html','/app.js','/style.css'):
                    name='index.html' if path=='/' else path[1:]
                    return self.send(200,(UI/name).read_bytes(),{'index.html':'text/html; charset=utf-8','app.js':'text/javascript; charset=utf-8','style.css':'text/css; charset=utf-8'}[name])
                match=re.fullmatch(r'/versions/([a-z0-9-]+)/(v[0-9]+)\.svg',path)
                if match:return self.send(200,library.source(*match.groups()),'image/svg+xml')
                return self.send(404,{'error':'Not found.'})
            except (ValueError,OSError) as error:self.send(400,{'error':str(error)})
        def do_POST(self):
            origin=self.headers.get('Origin')
            if not self.trusted_host() or self.headers.get('X-Component-Token')!=token or (origin and origin not in (f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}')):
                return self.send(403,{'error':'Open the local component workshop to make changes.'})
            try:
                if self.headers.get_content_type()!='application/json':raise ValueError('JSON required.')
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=MAX_SVG+100_000:raise ValueError('Request too large or empty.')
                request=json.loads(self.rfile.read(length))
                if not isinstance(request,dict):raise ValueError('Expected an object.')
                if not isinstance(request.get('revision'),str):raise ValueError('Reload the catalog before writing.')
                path=urlsplit(self.path).path
                if path=='/api/version':
                    version=library.add(request['id'],request['svg'],request['note'],parent=request.get('parent'),revision=request['revision'],create=request.get('create'))
                    return self.send(200,dict(version=version,catalog=library.snapshot(True,token)))
                if path=='/api/default':
                    library.choose(request['id'],request['version'],request['revision'])
                    return self.send(200,dict(catalog=library.snapshot(True,token)))
                if path=='/api/rebuild':
                    library.expect(request['revision'])
                    with job_lock:
                        if job['running']:raise ValueError('A rebuild is already running.')
                        job.update(running=True,message='Updating storyboard artwork…',ok=None)
                    def build():
                        try:
                            with library.lock():
                                for script in ('storyboards.py','build-site.py'):
                                    cmd=[__import__('sys').executable,str(library.root/'scripts'/script)]
                                    if script=='storyboards.py':cmd.append('generate')
                                    r=subprocess.run(cmd,cwd=library.root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
                                    if r.returncode:raise ValueError(r.stdout[-4000:])
                            with job_lock:job.update(running=False,message='Storyboards and site rebuilt.',ok=True)
                        except Exception as error:
                            with job_lock:job.update(running=False,message=str(error),ok=False)
                    threading.Thread(target=build,daemon=True).start()
                    return self.send(202,dict(job))
                return self.send(404,{'error':'Not found.'})
            except (ValueError,KeyError,TypeError,OSError) as error:self.send(400,{'error':str(error)})
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)


def check():
    errors=Library().errors()
    if errors:raise ValueError('\n'.join(errors))
    # Fixtures exercise preservation, optimistic concurrency, unsafe SVG rejection,
    # version pinning and the compatibility export without touching production data.
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);(root/'data').mkdir();lib=Library(root)
        lib.catalog.write_text(encoded(dict(version=1,compatibility_about='fixture',components={})))
        svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M0 0L100 100" stroke="currentColor"/></svg>'
        first=lib.add('route',svg,'Initial route',create=dict(name='Route',category='connections',description='A direction.'))
        old=lib.source('route');revision=lib.revision()
        second=lib.add('route',svg.replace('100 100" stroke','80 80" stroke'),'Shorter route',parent=first,revision=revision)
        assert first=='v001' and second=='v002' and lib.source('route')==old
        try:lib.choose('route',second,revision)
        except ValueError:pass
        else:raise AssertionError('Stale writes must fail')
        lib.choose('route',second)
        assert lib.source('route',first)==old and lib.source('route')!=old
        assert not lib.errors(),lib.errors()
        for bad in (svg.replace('<path','<script'),svg.replace('stroke="currentColor"','onload="alert(1)"'),svg.replace('<path d="M0 0L100 100" stroke="currentColor"/>','<image href="https://example.com/x.svg"/>'),svg.replace('0 0 100 100','0 0 500 500')):
            try:svg_body(bad)
            except ValueError:pass
            else:raise AssertionError('Unsafe/invalid SVG accepted')
        fragment='<defs><clipPath id="clip"><rect width="1" height="1"/></clipPath></defs><g clip-path="url(#clip)"/>'
        assert 'url(#one-clip)' in scope_ids(fragment,'one-')
        assert 'id="two-clip"' in scope_ids(fragment,'two-')
        # A scene can use two revisions of one component without conflating their
        # source snapshots, and each instance gets independent SVG paint IDs.
        import storyboards
        clipped = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'+fragment+'</svg>'
        third=lib.add('route',clipped,'Clip fixture',parent=first)
        scene=dict(title='Versions',intent='Independent revisions',background='paper',nodes=[
            dict(asset='route',asset_version=v,box=[0,0,1,1],color='steel')
            for v in (first,second,third,third)])
        rendered=storyboards.render(scene,dict(palette=dict(paper='#fff',steel='#000')),component_library=lib)
        parsed=ET.fromstring(rendered)
        snapshot=json.loads(parsed.find('{'+SVG_NS+'}metadata').text)
        assert set(snapshot['assets'])=={'route@v001','route@v002','route@v003'}
        assert 'M0 0L100 100' in rendered and 'M0 0L80 80' in rendered
        assert 'url(#node-2-clip)' in rendered and 'url(#node-3-clip)' in rendered
        (root/'data/storyboards.json').write_text(encoded(dict(scenes={'001-01':scene})))
        assert lib.usage()['route']['pinned'][first]==['001-01']
        scene['nodes'][0]['asset_version']='v999'
        (root/'data/storyboards.json').write_text(encoded(dict(scenes={'001-01':scene})))
        assert lib.errors(),'Missing pins must fail'
        (root/'data/storyboards.json').unlink()
        out=root/'out';gallery(out,lib);check_built(out,lib)
        lib.path('route',first).write_text('changed')
        assert lib.errors(),'Historical tampering must fail'
    print('SVG components: catalog, immutable versions, defaults, stale-write rejection, SVG safety, ID scoping and static export passed.')


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('serve');s.add_argument('--port',type=int,default=8767)
    s=sub.add_parser('check');s.add_argument('--built',action='store_true')
    s=sub.add_parser('gallery');s.add_argument('--output',type=Path,default=ROOT/'256t/components')
    sub.add_parser('export')
    s=sub.add_parser('add');s.add_argument('component');s.add_argument('--svg',type=Path,required=True);s.add_argument('--note',required=True);s.add_argument('--parent')
    s=sub.add_parser('choose');s.add_argument('component');s.add_argument('version')
    args=p.parse_args();lib=Library()
    try:
        if args.command=='serve':
            errors=lib.errors()
            if errors:raise ValueError('\n'.join(errors))
            httpd=server(lib,args.port);print(f'Component workshop: http://127.0.0.1:{httpd.server_port}/',flush=True)
            try:httpd.serve_forever()
            except KeyboardInterrupt:pass
            finally:httpd.server_close()
        elif args.command=='check':
            check()
            if args.built:check_built(ROOT/'docs/components');print('Built component workshop checked.')
        elif args.command=='gallery':gallery(args.output);print(args.output/'index.html')
        elif args.command=='export':lib.export()
        elif args.command=='add':print(lib.add(args.component,args.svg.read_text(),args.note,parent=args.parent))
        elif args.command=='choose':lib.choose(args.component,args.version)
    except (ValueError,OSError) as error:raise SystemExit(str(error))

if __name__=='__main__':main()
