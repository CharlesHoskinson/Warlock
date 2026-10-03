#!/usr/bin/env python3
"""Read-only dependencies plus fresh Qt manifest; execute only once final adapter reviewed."""
from pathlib import Path
import hashlib,json,os
B=Path(__file__).resolve().parent;Q=B.parent
files={};links={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(p,expected=None):
 p=Path(p);actual=sha(p)
 if expected is not None and actual!=expected:raise RuntimeError('Source mismatch '+str(p))
 if str(p) in files and files[str(p)]!=actual:raise RuntimeError('Conflicting hash '+str(p))
 files[str(p)]=actual
# Preserve V6 failed precondition and actual independent geometry attribution.
for relative in ('frozen-inputs.json','attempt-1/report.json','attempt-1/qt/report.json','attempt-1/qt/events.jsonl','attempt-1/root-completion.json','attempt-1/root-geometry-attribution.json'):
 add(Q/'qt-modal-private-v6'/relative)
# Preserve V5 failure and all causal source/evidence, without reclassifying acceptance.
add(Q/'qt-modal-private-v5/frozen-inputs.json')
add(Q/'qt-modal-private-v5/attempt-1/report.json')
add(Q/'qt-modal-private-v5/attempt-1/qt/report.json')
add(Q/'qt-modal-private-v5/attempt-1/qt/events.jsonl')
add(Q/'qt-modal-private-v5/attempt-1/host/privateBus.log')
for path in (Q/'qt-v5-failure-audit').iterdir():
 if path.is_file():add(path)
# Actual native probe compile dependencies, including system headers.
probe=json.loads((B/'native-probe/build-final-report.json').read_text())
for row in probe['sourceDependencies']:add(row['path'],row['sha256'])
# Actual public Qt observation fixture compile dependencies.
for deps in (B/'build-v7').rglob('*.o.d'):
 for path in deps.read_text().replace('\\\n',' ').split(':',1)[1].split():
  candidate=Path(path)
  if candidate.is_file():add(candidate)

# Preserve the V4 CLI failure and its actual unchanged readiness/mapping proof.
add(Q/'qt-modal-private-v4/frozen-inputs.json')
add(Q/'qt-modal-private-v4/attempt-1/report.json')
add(Q/'qt-modal-private-v4/attempt-1/host/host-evidence.json')
# Retain actual primary presentation/failure provenance without changing its result.
raster=Q/'family-raster-oracle-v3/attempt-private-1';add(raster/'report.json')
for path in (raster/'private-session/runtime-archive/hypr').glob('*/hyprland.log'):add(path)
add(Q/'raster-v3-ipc-attribution/report.json')
# Accepted packet carries actual production plugin/helper/pointer/Qt dependencies.
old=Q/'qt-modal-compat-v2/frozen-inputs.json';add(old)
for row in json.loads(old.read_text())['files']:add(row['path'],row['sha256'])
host=Q/'private-weston-host-v2';manifest=host/'host-stage-report.json';add(manifest);packet=json.loads(manifest.read_text())
for path,value in packet['files'].items():add(host/path,value)
for path,value in packet['externalDependencies'].items():add(path,value)
for path,value in packet['symlinks'].items():links[str(host/path)]=value
adapter=Q/'private-weston-aq-host-v4/frozen-inputs.json';add(adapter)
for path,value in json.loads(adapter.read_text())['inputs'].items():add(path,value)
aq=Q/'aquamarine-nested-lifecycle-v1/frozen-inputs.json';add(aq);packet=json.loads(aq.read_text())
for path,value in packet['inputs'].items():add(path,value)
links.update(packet['symlinks'])
for path,target in links.items():
 if not Path(path).is_symlink() or os.readlink(path)!=target:raise RuntimeError('Link mismatch '+path)
for path in B.rglob('*'):
 if path.is_file() and '__pycache__' not in path.parts and not any(part.startswith('attempt-') for part in path.parts) and path.name!='frozen-inputs.json':add(path)
report={'scope':'private Qt same-QApplication WindowModal; no main input/restoration','files':[{'path':p,'sha256':s} for p,s in sorted(files.items())],'symlinks':[{'path':p,'target':s} for p,s in sorted(links.items())],'command':['python3',str(Q/'qa_run.py'),'--','python3',str(B/'run_native.py'),'--attempt',str(B/'attempt-1')],'nativeExecution':False,'qtFeatureGates':19,'hostGates':10,'offlineTests':25,'hostOfflineTests':23,'physicalHardwareProved':False,'mainGUIWrites':False,'mainRestorationWrites':False,'aqManifestSHA256':sha(aq),'adapterManifestSHA256':sha(adapter),'old203ManifestSHA256':sha(old)}
path=B/'frozen-inputs.json';assert not path.exists();path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'files':len(files),'links':len(links),'manifestSHA256':sha(path)}))
