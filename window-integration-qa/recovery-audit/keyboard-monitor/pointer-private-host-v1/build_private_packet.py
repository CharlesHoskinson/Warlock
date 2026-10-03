#!/usr/bin/env python3
"""Offline packet preparation; writing the final freeze requires root review.

The default only checks actual files and prints counts. It launches no processes,
imports no compositor/client modules and never writes the main session.
"""
import argparse,ast,hashlib,json,os
from pathlib import Path
STAGE=Path(__file__).resolve().parent
QA=Path('/home/hoskinson/window-integration-qa')
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def collect(adapter):
    tree=ast.parse((STAGE/'native_probe_pointer.py').read_text())
    selection=next(node.value for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='HOST_ROOT' for target in node.targets))
    if not isinstance(selection,ast.BinOp) or not isinstance(selection.op,ast.Div) or not isinstance(selection.left,ast.Name) or selection.left.id!='QA_ROOT' or not isinstance(selection.right,ast.Constant):raise RuntimeError('Unknown actual host selection source')
    if QA/selection.right.value!=adapter:raise RuntimeError('Packet adapter does not match actual runner host')
    actual={};links={}
    def add(path,expected=None):
        path=Path(path);value=digest(path)
        if expected is not None and value!=expected:raise RuntimeError('Frozen actual dependency changed: '+str(path))
        key=str(path)
        if key in actual and actual[key]!=value:raise RuntimeError('Conflicting dependency: '+key)
        actual[key]=value
    def link(path,expected):
        path=Path(path)
        if not path.is_symlink() or str(path.readlink())!=expected:raise RuntimeError('Loader link changed: '+str(path))
        if str(path) in links and links[str(path)]!=expected:raise RuntimeError('Conflicting link')
        links[str(path)]=expected
    original=json.loads((STAGE/'v8c-original-manifest.json').read_text())
    for name,value in original['externalDependencies'].items():add(name,value)
    base=QA/'private-weston-host-v2';base_manifest=base/'host-stage-report.json';add(base_manifest)
    row=json.loads(base_manifest.read_text())
    for name,value in row['files'].items():add(base/name,value)
    for name,value in row['externalDependencies'].items():add(name,value)
    for name,value in row['symlinks'].items():link(base/name,value)
    for manifest in (adapter/'frozen-inputs.json',QA/'aquamarine-nested-lifecycle-v1/frozen-inputs.json'):
        add(manifest);row=json.loads(manifest.read_text())
        for name,value in row['inputs'].items():add(name,value)
        for name,value in row.get('symlinks',{}).items():link(name,value)
    # The lifecycle phase executes the actual signed package, unlike the pointer
    # phase's explicit compat copy. Freeze every actual Orca Python source and
    # package library/type library loaded from that immutable private prefix.
    prefix=QA/'orca-reader/prefix'
    for source in (prefix/'usr/lib/python3.14/site-packages/orca').rglob('*.py'):add(source)
    for pattern in ('usr/lib/lib*.so*','usr/lib/girepository-1.0/*.typelib'):
        for source in prefix.glob(pattern):
            if source.is_symlink():link(source,str(source.readlink()))
            add(source)
    for source in ('/usr/bin/foot','/usr/bin/python3','/usr/bin/gdbus','/usr/bin/hyprctl','/usr/bin/wl-paste'):
        path=Path(source)
        if path.is_symlink():link(path,str(path.readlink()))
        add(path)
    native=json.loads((STAGE/'native-dependency-map.json').read_text())
    for name,value in native['files'].items():add(name,value)
    for name,value in native['symlinks'].items():link(name,value)
    local={}
    ignored={'pointer-frozen-stage-report.json','packet-preview.json'}
    for source in sorted(STAGE.rglob('*')):
        relative=source.relative_to(STAGE)
        if any(part=='__pycache__' or part.startswith('native-pointer-attempt-') or part in ('owned-host','external-reference') for part in relative.parts):continue
        if not source.is_file() or source.suffix=='.pyc' or str(relative) in ignored:continue
        if source.is_symlink():raise RuntimeError('Local stage source must be owned regular file: '+str(source))
        if source.stat().st_uid!=os.getuid():raise RuntimeError('Foreign local stage source')
        local[str(relative)]=digest(source)
    return dict(kind='private full pointer/keyboard campaign',frozen=True,nativeLaunched=False,hostAdapter=str(adapter),dependencies=local,externalDependencies=dict(sorted(actual.items())),externalSymlinks=dict(sorted(links.items())))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--host-root',required=True);parser.add_argument('--write-reviewed-freeze',action='store_true');args=parser.parse_args()
    adapter=Path(args.host_root).resolve()
    if adapter.parent!=QA or not adapter.name.startswith('private-weston-aq-host-v'):raise RuntimeError('Host adapter outside reviewed QA root')
    result=collect(adapter)
    if args.write_reviewed_freeze:
        # Call only after root has reviewed source and accepted actual host health.
        path=STAGE/'pointer-frozen-stage-report.json'
        fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(fd,'w') as stream:stream.write(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(path=str(path),sha256=digest(path))))
    else:
        print(json.dumps(dict(frozen=False,nativeLaunched=False,local=len(result['dependencies']),external=len(result['externalDependencies']),loaderLinks=len(result['externalSymlinks']),externalBytes=sum(Path(p).stat().st_size for p in result['externalDependencies']),adapter=str(adapter)),indent=2))
if __name__=='__main__':main()
