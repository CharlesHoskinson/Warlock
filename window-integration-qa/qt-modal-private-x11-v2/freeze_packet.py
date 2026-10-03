#!/usr/bin/env python3
"""Immutable X11 union; preserves accepted Wayland proof and all prior sources."""
from pathlib import Path
import hashlib,json,os
B=Path(__file__).resolve().parent;Q=B.parent
files={};links={}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def add(path,expected=None):
 p=Path(path);value=sha(p)
 if expected is not None and value!=expected:raise RuntimeError('changed input: '+str(p))
 if str(p) in files and files[str(p)]!=value:raise RuntimeError('conflicting frozen input')
 files[str(p)]=value
v9=Q/'qt-modal-private-v9/frozen-inputs.json';add(v9);old=json.loads(v9.read_text())
for row in old['files']:add(row['path'],row['sha256'])
for row in old['symlinks']:links[row['path']]=row['target']
for relative in ('attempt-1/report.json','attempt-1/root-completion.json','attempt-1/root-motion-completion.json'):add(Q/'qt-modal-private-v9'/relative)
for relative in ('frozen-inputs.json','attempt-1/report.json','attempt-1/host/host-evidence.json'):
 add(Q/'qt-modal-private-x11-v1'/relative)
add(Q/'private-weston-x11-host-v1/frozen-inputs.json')
add(Q/'x11-v1-attribution/report.json')
xhost=Q/'private-weston-x11-host-v2/frozen-inputs.json';add(xhost);packet=json.loads(xhost.read_text())
for path,value in packet['inputs'].items():add(path,value)
links.update(packet['symlinks'])
for path,target in links.items():
 if not Path(path).is_symlink() or str(Path(path).readlink())!=target:raise RuntimeError('changed link: '+path)
for path in B.rglob('*'):
 if path.is_file() and '__pycache__' not in path.parts and not any(part.startswith('attempt-') for part in path.parts) and path.name!='frozen-inputs.json':add(path)
report={'files':[{'path':p,'sha256':v} for p,v in sorted(files.items())],'symlinks':[{'path':p,'target':v} for p,v in sorted(links.items())],'command':['python3',str(Q/'qa_run.py'),'--','python3',str(B/'run_native.py'),'--attempt',str(B/'attempt-1')],'nativeExecution':False,'nativeAcceptance':False,'qtFeatureGates':19,'hostGates':10,'x11ProtocolGates':1,'offlineTests':38,'x11HostOfflineTests':21,'physicalHardwareProved':False,'mainGUIWrites':False,'mainRestorationWrites':False,'acceptedWaylandReportSHA256':sha(Q/'qt-modal-private-v9/attempt-1/report.json'),'acceptedWaylandManifestSHA256':sha(v9),'x11AdapterManifestSHA256':sha(xhost),'scope':'Explicit private same-process X11 Qt WindowModal; exact owned authority, no main display fallback, no production deployment'}
p=B/'frozen-inputs.json';assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'files':len(files),'links':len(links),'manifestSHA256':sha(p)}))
