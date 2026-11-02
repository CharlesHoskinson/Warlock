#!/usr/bin/env python3
"""Bounded CPU Graphify index. Lexical associations require source verification."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
import sys
import tempfile

from graphify.build import build_from_json
from graphify.paths import load_node_link_graph
from graphify.serve import _query_graph_text
from networkx.readwrite import json_graph

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path.home() / '.local/share/warlock-graph/graphify-out'
GRAPH = CACHE / 'graph.json'
REGISTER = 'docs/elm-roadmap/requirements.json'
STATE = 'docs/warlock-build-loop/v2/STATE.json'
EXCLUDED = {'elm-stuff', 'dist-newstyle', 'build', 'node_modules', '.git', 'vendor'}
DECL = re.compile(r'^(?:(?:port\s+)?module\s+([A-Z][\w.]*)|(?:type\s+(?:alias\s+)?|data\s+|newtype\s+|class\s+)([A-Z][\w\']*)|([a-z][\w\']*)\s*(?:::|:|=))')
IMPORT = re.compile(r'^\s*import\s+(?:qualified\s+)?([A-Z][\w.]*)')
QNT_DECL = re.compile(r'^\s*(?:(module)\s+([A-Za-z_][\w]*)|(?:(?:pure|nondet)\s+)?(?:type|var|const|val|def|action|run|temporal|assume)\s+([A-Za-z_][\w]*))\b')
QNT_IMPORT = re.compile(r'^\s*import\s+([A-Za-z_][\w]*(?:\.(?:[A-Za-z_][\w]*|\*))?)(?:\s+from\s+"([^"\n]+)")?')
TOKEN = re.compile(r"\b[A-Za-z][A-Za-z0-9_']*\b")

def sha(data): return hashlib.sha256(data).hexdigest()
def files():
    base = ROOT / 'implementation/warlock'
    return sorted(p.relative_to(ROOT).as_posix() for p in base.rglob('*')
                  if p.is_file() and p.suffix in {'.elm', '.hs', '.hsc', '.qnt'} and not EXCLUDED.intersection(p.parts))
def active_record(state_bytes):
    record = json.loads(state_bytes)['activeContributorRecord']
    if not isinstance(record, str) or not record.startswith('.warlock-contributor/') or '..' in Path(record).parts:
        raise RuntimeError('Invalid active contributor record')
    return record

def read_inputs():
    # Select the record from the same STATE bytes included in this snapshot.
    # A concurrent switch is caught by update's second complete snapshot.
    state_bytes = (ROOT / STATE).read_bytes()
    record = active_record(state_bytes)
    data = {p: (ROOT/p).read_bytes() for p in files() + [REGISTER, record]}
    data[STATE] = state_bytes
    return data
def loc(path, line): return {'source_file': path, 'source_location': f'L{line}'}
def node(nid, label, path, line, kind, **extra):
    return dict(id=nid, label=label, file_type='document' if kind in {'requirement','scenario','evidence'} else 'code', kind=kind, **loc(path,line), **extra)
def edge(a,b,relation,path,line):
    return dict(source=a,target=b,relation=relation,confidence='EXTRACTED',weight=1.0, **loc(path,line))
def line_for(text, key, value):
    pat = '"' + key + '": ' + json.dumps(value,ensure_ascii=False)
    at = text.find(pat)
    return text.count('\n',0,at)+1 if at >= 0 else 1

def update():
    data=read_inputs(); hashes={p:sha(b) for p,b in data.items()}; nodes=[]; edges=[]; modules={}; parsed={}; qnt_imports=[]
    # Extract precisely the source names and bytes already hashed above; a
    # second directory walk could silently omit a transiently removed file.
    for path in sorted(p for p in data if p.startswith('implementation/warlock/')):
        content=data[path].decode('utf-8', errors='replace'); lines=content.splitlines(); fid='file:'+path
        nodes.append(node(fid,path,path,1,'file')); decls={}; imports=[]
        for i,line in enumerate(lines,1):
            if path.endswith('.qnt'):
                m=QNT_DECL.match(line)
                if m:
                    name=m.group(2) or m.group(3); kind='module' if m.group(1) else 'declaration'
                    nid=f'decl:{path}:{i}:{name}'
                    nodes.append(node(nid,name,path,i,kind)); edges.append(edge(fid,nid,'lexical_declares',path,i))
                m=QNT_IMPORT.match(line)
                if m:
                    label='import '+m.group(1)+((' from "'+m.group(2)+'"') if m.group(2) else '')
                    nid=f'import:{path}:{i}'
                    nodes.append(node(nid,label,path,i,'import')); edges.append(edge(fid,nid,'lexical_import_text',path,i))
                    if m.group(2): qnt_imports.append((path,i,nid,m.group(2)))
                continue
            m=DECL.match(line)
            if m:
                name=next(x for x in m.groups() if x); kind='module' if m.group(1) else 'declaration'
                # A signature and definition may share a name: keep first source location.
                if name not in decls:
                    nid=f'decl:{path}:{i}:{name}'; decls[name]=nid
                    nodes.append(node(nid,name,path,i,kind)); edges.append(edge(fid,nid,'lexical_declares',path,i))
                    if kind=='module': modules.setdefault(name,[]).append(nid)
            m=IMPORT.match(line)
            if m: imports.append((m.group(1),i))
        parsed[path]=(lines,decls,imports)
    for path,i,nid,reference in qnt_imports:
        candidate=posixpath.normpath(posixpath.join(posixpath.dirname(path), reference))
        if not candidate.endswith('.qnt'): candidate += '.qnt'
        if candidate in parsed:
            edges.append(edge(nid,'file:'+candidate,'lexical_import_path_candidate',path,i))
    for path,(lines,decls,imports) in parsed.items():
        fid='file:'+path
        for name,i in imports:
            if len(modules.get(name,[]))==1:
                edges.append(edge(fid,modules[name][0],'lexical_import',path,i))
        # Source text occurrence, not a resolved call or dependency. One edge per name/file.
        found=set()
        for i,line in enumerate(lines,1):
            if line.lstrip().startswith(('--','{-','import ','module ')): continue
            for token in set(TOKEN.findall(line)) & decls.keys():
                if token not in found:
                    found.add(token)
                    oid=f'occurrence:{path}:{i}:{token}'
                    nodes.append(node(oid,token+' occurrence',path,i,'occurrence'))
                    edges.append(edge(fid,oid,'lexical_contains',path,i))
                    edges.append(edge(oid,decls[token],'lexical_name_occurs',path,i))
    register=data[REGISTER].decode(); reg=json.loads(register); requirements=reg['requirements']
    if len(requirements)!=242 or sum(len(r['scenarios']) for r in requirements)!=417: raise ValueError('original register count changed; refusing update')
    evidence=set()
    for req in requirements:
        rid='requirement:'+req['id']; ln=line_for(register,'id',req['id'])
        nodes.append(node(rid,req['id']+' '+req['capability'],REGISTER,ln,'requirement',text=req['ears']))
        for scenario in req['scenarios']:
            sid='scenario:'+req['id']+':'+scenario['name']; sl=line_for(register,'name',scenario['name'])
            nodes.append(node(sid,scenario['name'],REGISTER,sl,'scenario',text=' '.join(scenario.get(k,'') for k in ('given','when','then'))))
            edges.append(edge(rid,sid,'register_scenario',REGISTER,sl))
        for field in ('source','legacyEvidence'):
            value=req.get(field,''); candidate=ROOT/value
            if value and candidate.is_file() and not candidate.is_symlink():
                eid='evidence:'+value
                if eid not in evidence:
                    evidence.add(eid); nodes.append(node(eid,value,value,1,'evidence'))
                edges.append(edge(rid,eid,'register_'+field,REGISTER,ln))
    active=active_record(data[STATE])
    record_text=data[active].decode(); record=json.loads(record_text); slice_=record['slice']
    for rid in slice_['requirements']:
        for path in slice_['paths']:
            if path in parsed:
                at=record_text.find(json.dumps(path)); line=record_text.count('\n',0,at)+1 if at >= 0 else 1
                edges.append(edge('requirement:'+rid,'file:'+path,'recorded_slice_path',active,line))
    g=build_from_json({'nodes':nodes,'edges':edges},directed=True,root=ROOT,dedup=False)
    g.graph.update({'input_sha256':hashes,'extractor_sha256':sha(Path(__file__).read_bytes()),'scope':'active implementation Elm/Haskell/Quint and original register; lexical associations only', 'retrieval':'CPU keyword; no embeddings', 'counts':{'requirements':242,'scenarios':417}})
    out=json_graph.node_link_data(g,edges='links'); encoded=(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n').encode()
    # Detect concurrent edits before publishing; the old graph remains intact on failure.
    if {p:sha(b) for p,b in read_inputs().items()} != hashes: raise RuntimeError('inputs changed during update; graph not published')
    CACHE.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.graph-',dir=CACHE)
    try:
        with os.fdopen(fd,'wb') as f: f.write(encoded); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,GRAPH)
        d=os.open(CACHE,os.O_DIRECTORY); os.fsync(d); os.close(d)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    print(f'Published {GRAPH}: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges; sha256 {sha(encoded)}')

def load():
    raw=GRAPH.read_bytes(); obj=json.loads(raw); expected=obj['graph']['input_sha256']; actual={p:sha(b) for p,b in read_inputs().items()}
    changed=sorted(p for p in set(expected)|set(actual) if expected.get(p)!=actual.get(p))
    if obj['graph'].get('extractor_sha256') != sha(Path(__file__).read_bytes()): changed.append('tools/warlock_ctx.py')
    if changed: print(f'STALE: {len(changed)} changed inputs: '+', '.join(changed[:10]),file=sys.stderr)
    return raw,obj,load_node_link_graph(obj),changed

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--budget',type=int,default=1500)
    sub=ap.add_subparsers(dest='cmd',required=True)
    for cmd in ('q','query','explain','impact'):
        query=sub.add_parser(cmd)
        query.add_argument('--budget',type=int,default=argparse.SUPPRESS)
        query.add_argument('term')
    semantic=sub.add_parser('hq', help='delegate semantic retrieval to warlock-gpu')
    semantic.add_argument('--budget',type=int,default=argparse.SUPPRESS)
    semantic.add_argument('--device', choices=('cuda','cpu'), default='cuda')
    semantic.add_argument('term')
    for cmd in ('update','eval','stats'): sub.add_parser(cmd)
    s=sub.add_parser('show'); s.add_argument('location')
    a=ap.parse_args()
    if a.cmd=='hq':
        # The wrapper owns the offline environment, model checks and locking.
        # Preserve its exit status and errors; never silently fall back to q.
        wrapper=ROOT/'tools/warlock-gpu'
        os.execv(str(wrapper), [str(wrapper), '--device', a.device,
                                '--budget', str(a.budget), 'hq', a.term])
    if a.cmd=='update': update(); return
    if a.cmd=='show':
        path,sep,line=a.location.rpartition(':'); p=(ROOT/path).resolve()
        if not sep or not line.isdigit() or not p.is_relative_to(ROOT/'implementation/warlock'): raise ValueError('show requires implementation/warlock/path:line')
        lines=p.read_text().splitlines(); n=int(line)
        for i in range(max(1,n-10),min(len(lines),n+10)+1): print(f'{i}: {lines[i-1]}')
        return
    raw,obj,g,stale=load()
    print('Lexical index; verify source. CPU keyword retrieval. '+('STALE' if stale else 'Current inputs.'))
    if a.cmd in ('stats','eval'):
        kinds={}
        for _,n in g.nodes(data=True): kinds[n.get('kind','unknown')]=kinds.get(n.get('kind','unknown'),0)+1
        print(json.dumps({'sha256':sha(raw),'nodes':g.number_of_nodes(),'edges':g.number_of_edges(),'kinds':kinds,'stale':stale},indent=2))
        if a.cmd=='eval' and (stale or kinds.get('requirement')!=242 or kinds.get('scenario')!=417): sys.exit(1)
        return
    if a.cmd in ('q','query'):
        print(_query_graph_text(g.to_undirected(),a.term,depth=2,token_budget=max(100,min(a.budget,4000)),graph_path=str(GRAPH))); return
    term=a.term.lower(); matches=[(nid,n) for nid,n in g.nodes(data=True) if term in n.get('label','').lower() or term==nid.lower()]
    print(f'{len(matches)} matching nodes; showing at most 15 and 15 direct associations each')
    for nid,n in matches[:15]:
        print(f"\n{n.get('label')} [{n.get('kind')}] {n.get('source_file')}:{n.get('source_location')}")
        if n.get('text'): print(n['text'])
        links=list(g.in_edges(nid,data=True))+list(g.out_edges(nid,data=True))
        links.sort(key=lambda item: (item[2].get('relation') != 'register_scenario', item[2].get('relation','')))
        for src,dst,e in links[:15]:
            other=src if dst==nid else dst; nd=g.nodes[other]
            print(f"  {e.get('relation')} -> {nd.get('label')} ({e.get('source_file')}:{e.get('source_location')})")
    if not matches: sys.exit(1)

if __name__=='__main__':
    try: main()
    except (OSError,ValueError,RuntimeError,KeyError) as exc: print(f'warlock-ctx: {exc}',file=sys.stderr); sys.exit(1)
