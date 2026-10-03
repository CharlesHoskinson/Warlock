"""Mechanical selection only after root's actual frozen V28 packet exists."""
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat

QA=Path('/home/hoskinson/window-integration-qa')
BASE=QA/'family-preparation-thumbnail-v12'
B=QA/'family-preparation-thumbnail-v14'
DESIGN=Path(__file__).resolve().parent
SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-focus-transaction-v28')
MANIFEST=SERVICE/'manifest-restore-focus-transaction-v28.json'
BASE_SHA='27816ce53607b0217d41974ecf2f88f91390053a916b310d106a5c851fe87d4b'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(path,row):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())

def main():
    if B.exists():raise ValueError('fresh B14 derivative required')
    if sha(BASE/'frozen-inputs.json')!=BASE_SHA:raise ValueError('frozen B12 changed')
    if not MANIFEST.is_file() or MANIFEST.is_symlink():raise ValueError('actual root-frozen V28 manifest required')
    actual_sha=sha(MANIFEST)
    if actual_sha!='30303eb8b2dac6f3407155d5619e2a828e134b410ce70c141488ed2493e94eb3':raise ValueError('exact root frozen V28 digest required')
    specpath=QA/'restore-focus-v28-proof-source-v1/freeze_restore_focus.py'
    import importlib.util
    spec=importlib.util.spec_from_file_location('v28_pairing_verify',specpath);frozen=importlib.util.module_from_spec(spec);spec.loader.exec_module(frozen)
    packet=json.loads(MANIFEST.read_text());frozen.verify(packet)
    if packet.get('sourceReadySHA256')!='42244ab87cc002e8e60eb5f26f4f505c47ca93a40554b8c0d48fe576a7824d95':raise ValueError('root selected different V28 source-ready epoch')
    def ignored(directory,names):
        return [name for name in names if name=='__pycache__' or name.startswith('attempt-') or Path(directory)==BASE and name=='frozen-inputs.json']
    shutil.copytree(BASE,B,symlinks=True,ignore=ignored)
    source_map={};patch=[]
    for name in ('module_binding.py','native_faults.py'):
        old=(BASE/name).read_text();new=old
        if name=='module_binding.py':
            for a,z in (
                ("SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-planning-v27')","SERVICE=Path('"+str(SERVICE)+"')"),
                ("MANIFEST=SERVICE/'manifest-restore-planning-v27.json'","MANIFEST=SERVICE/'manifest-restore-focus-transaction-v28.json'"),
                ("MANIFEST_SHA256='54857ba311e2862e37037195283cf98b6fba8bb286cb33d32e92685671304e40'","MANIFEST_SHA256='"+actual_sha+"'")):
                if new.count(a)!=1:raise ValueError('exact old service selector absent')
                new=new.replace(a,z)
        else:
            a="if SERVICE.name!='service-restore-planning-v27':";z="if SERVICE.name!='service-restore-focus-transaction-v28':"
            if new.count(a)!=1:raise ValueError('exact old fault admission absent')
            new=new.replace(a,z)
        ast.parse(new);(B/name).write_text(new);(B/name).chmod(stat.S_IMODE((BASE/name).stat().st_mode))
        source_map[name]={'originalSHA256':sha(BASE/name),'proposedSHA256':sha(B/name),'mode':stat.S_IMODE((BASE/name).stat().st_mode)}
        patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=name,tofile=name))
    (DESIGN/'intended-v14.patch').write_text(''.join(patch))
    save(DESIGN/'intended-source-map.json',source_map)
    save(DESIGN/'application.json',{'result':'pass','selectedManifest':str(MANIFEST),'selectedManifestSHA256':actual_sha,'selectedRootReadySHA256':packet['sourceReadySHA256'],'baseline':str(BASE),'baselineManifestSHA256':BASE_SHA,'candidate':str(B),'changedCollectorSources':list(source_map),'nativeTupleUnchanged':True,'nativeAccepted':False})
    print(json.dumps({'result':'pass','candidate':str(B),'selectedManifestSHA256':actual_sha,'sourceChanges':list(source_map)}))

if __name__=='__main__':main()
