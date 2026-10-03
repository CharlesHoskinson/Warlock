from pathlib import Path
import hashlib,json,os
B=Path(__file__).resolve().parent;Q=B.parent
inputs={};links={}
def add(path,expected=None):
 p=Path(path);value=hashlib.sha256(p.read_bytes()).hexdigest()
 if expected is not None and value!=expected:raise RuntimeError('changed input: '+str(p))
 inputs[str(p)]=value
v4=Q/'private-weston-aq-host-v4/frozen-inputs.json';add(v4)
for path,value in json.loads(v4.read_text())['inputs'].items():add(path,value)
loader=Q/'qt-modal-private-x11-v2/xcb-loader-closure.json';add(loader);row=json.loads(loader.read_text())
for path,value in row['files'].items():add(path,value)
links.update(row['symlinks'])
for path,target in links.items():
 if not Path(path).is_symlink() or str(Path(path).readlink())!=target:raise RuntimeError('changed link: '+path)
build=json.loads((B/'helper-build-report.json').read_text())
for path,value in build['sourceDependencies'].items():add(path,value)
for path in B.iterdir():
 if path.is_file() and path.name!='frozen-inputs.json':add(path)
report={'inputs':dict(sorted(inputs.items())),'symlinks':dict(sorted(links.items())),'nativeServerLaunched':False,'nativeAcceptance':False,'offlineTests':21,'baseV4Unchanged':True,'scope':'explicit X11 campaign only, real owned auth pending actual setup proof','sourceURL':'https://raw.githubusercontent.com/hyprwm/Hyprland/v0.56.2/src/xwayland/Server.cpp'}
p=B/'frozen-inputs.json';assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'files':len(inputs),'links':len(links),'manifestSHA256':hashlib.sha256(p.read_bytes()).hexdigest()}))
