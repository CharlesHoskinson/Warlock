"""Mechanical selection only after root's actual frozen V27 packet exists."""
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat

QA=Path('/home/hoskinson/window-integration-qa')
BASE=QA/'family-preparation-thumbnail-v11'
B=QA/'family-preparation-thumbnail-v12'
DESIGN=Path(__file__).resolve().parent
SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-planning-v27')
MANIFEST=SERVICE/'manifest-restore-planning-v27.json'
BASE_SHA='53f6ddde08633dc3bfab3cbadfde2997695bf189b095382e2805cd1e8441a3c9'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(path,row):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())

def main():
    if B.exists():raise ValueError('fresh B12 derivative required')
    if sha(BASE/'frozen-inputs.json')!=BASE_SHA:raise ValueError('frozen B11 changed')
    if not MANIFEST.is_file() or MANIFEST.is_symlink():raise ValueError('actual root-frozen V27 manifest required')
    actual_sha=sha(MANIFEST)
    specpath=QA/'restore-planning-v27-proof-source-v1/freeze_restore_planning.py'
    import importlib.util
    spec=importlib.util.spec_from_file_location('v27_pairing_verify',specpath);frozen=importlib.util.module_from_spec(spec);spec.loader.exec_module(frozen)
    packet=json.loads(MANIFEST.read_text());frozen.verify(packet)
    if packet.get('sourceReadySHA256')!='e2ae883d241edf4c8c38cc00185bf07f0310d766de366100b797e70ff279747a':raise ValueError('root selected different V27 source-ready epoch')
    shutil.copytree(BASE,B,symlinks=True,ignore=shutil.ignore_patterns('__pycache__','attempt-*','frozen-inputs.json'))
    source_map={};patch=[]
    for name in ('module_binding.py','native_faults.py'):
        old=(BASE/name).read_text();new=old
        if name=='module_binding.py':
            for a,z in (
                ("SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-housekeeping-admission-v26')","SERVICE=Path('"+str(SERVICE)+"')"),
                ("MANIFEST=SERVICE/'manifest-housekeeping-admission-v26.json'","MANIFEST=SERVICE/'manifest-restore-planning-v27.json'"),
                ("MANIFEST_SHA256='e98809f3cee21c3fc8a0447c98c76915cc3083df2ac1090f1531c7fa3b25a1b2'","MANIFEST_SHA256='"+actual_sha+"'")):
                if new.count(a)!=1:raise ValueError('exact old service selector absent')
                new=new.replace(a,z)
        else:
            a="if SERVICE.name!='service-housekeeping-admission-v26':";z="if SERVICE.name!='service-restore-planning-v27':"
            if new.count(a)!=1:raise ValueError('exact old fault admission absent')
            new=new.replace(a,z)
        ast.parse(new);(B/name).write_text(new);(B/name).chmod(stat.S_IMODE((BASE/name).stat().st_mode))
        source_map[name]={'originalSHA256':sha(BASE/name),'proposedSHA256':sha(B/name),'mode':stat.S_IMODE((BASE/name).stat().st_mode)}
        patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=name,tofile=name))
    (DESIGN/'intended-v12.patch').write_text(''.join(patch))
    save(DESIGN/'intended-source-map.json',source_map)
    save(DESIGN/'application.json',{'result':'pass','selectedManifest':str(MANIFEST),'selectedManifestSHA256':actual_sha,'selectedRootReadySHA256':packet['sourceReadySHA256'],'baseline':str(BASE),'baselineManifestSHA256':BASE_SHA,'candidate':str(B),'changedCollectorSources':list(source_map),'nativeTupleUnchanged':True,'nativeAccepted':False})
    print(json.dumps({'result':'pass','candidate':str(B),'selectedManifestSHA256':actual_sha,'sourceChanges':list(source_map)}))

if __name__=='__main__':main()
