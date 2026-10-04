"""Integrity freeze of bounded CPU qualification and retained native failure."""
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE = REPO/'implementation'
TARGET = ROOT/'qa/diagnostic-manifest.json'
PACKETS = ['elm-window-geometry-authority-v35','elm-geometry-observer-native-v37',
           'elm-geometry-observer-adapter-v38','elm-geometry-observer-native-v39']
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path): return json.loads(Path(path).read_text())
def hash_check(path, digest):
    assert sha(path) == digest, str(path)
    external[str(Path(path).absolute())] = digest

def verify_manifest():
    packet=load(TARGET)
    assert packet['evidenceIntegrityPassed'] and packet['nativeAcceptance'] is False and packet['completedRequirementIds']==[]
    for path,item in packet['files'].items():
        p=REPO/path
        if 'symlink' in item: assert p.is_symlink() and str(p.readlink())==item['symlink'],path
        else: assert p.is_file() and not p.is_symlink() and sha(p)==item['sha256'] and p.stat().st_size==item['size'],path
    for path,digest in packet['externalInputs'].items(): assert sha(path)==digest,path
    print(json.dumps({'passed':True,'nativeAcceptance':False,'manifest':str(TARGET),'files':len(packet['files'])}))

if '--verify' in sys.argv:
    verify_manifest();raise SystemExit(0)
assert not TARGET.exists(), 'Frozen diagnostic manifest is immutable'
external={}
selected=[
('elm-window-geometry-authority-v35/qa/geometry-endpoint-1791099529466724136/report.json',117),
('elm-geometry-observer-adapter-v38/qa/geometry-endpoint-1791100045917134683/report.json',132)]
reports=[]
for rel,count in selected:
    path=BASE/rel;row=load(path)
    assert row['passed'] and row['checkCount']==count and all(check['passed'] for check in row['checks'])
    assert row['nativeAcceptance'] is False and row['effectsImplemented'] is False
    packet=path.parent.parent.parent
    for name,digest in row['inputs'].items():
        hash_check(packet/name,digest);hash_check(path.parent/'inputs'/name,digest)
    reports.append({'path':str(path.relative_to(REPO)),'sha256':sha(path),'passed':True,'checkCount':count})
plugin_path=BASE/'elm-window-geometry-authority-v35/qa/geometry-build-1791099555616078276/report.json'
plugin=load(plugin_path);assert plugin['passed'] and not plugin['missingSymbols'] and plugin['nativeAcceptance'] is False
hash_check(plugin['binary'],plugin['binarySHA256'])
for name,digest in plugin['inputs'].items():
    hash_check(BASE/'elm-window-geometry-authority-v35'/name,digest)
    hash_check(plugin_path.parent/'inputs'/name,digest)
for name,digest in plugin['owningHeaders'].items(): hash_check(plugin_path.parent/'owning-headers'/name,digest)
for section in ['dependencies','linkedLibraries','tools']:
    for name,digest in plugin[section].items(): hash_check(name,digest)
for name,digest in plugin['artifacts'].items(): hash_check(plugin_path.parent/name,digest)
for key in ['parentManifest','parentBuildReport']: hash_check(plugin[key],plugin[key+'SHA256'])
core=plugin['core'];hash_check(core['path'],core['sha256'])
for key in ['buildReport','componentManifest']: hash_check(core[key],core[key+'SHA256'])
# Validate the selected component's entire retained inventory, including ABI
# source headers, rather than hashing only its manifest pointer.
component=load(core['componentManifest']);assert component['passed']
for item in component['files']:
    path=Path(core['inventoryBase'])/item['path']
    if 'symlink' in item:
        assert path.is_symlink() and str(path.readlink())==item['symlink']
    else:
        hash_check(path,item['sha256'])
        assert path.stat().st_size==item['size']
reports.append({'path':str(plugin_path.relative_to(REPO)),'sha256':sha(plugin_path),'passed':True,'nativeAcceptance':False})
native_path=ROOT/'qa/native-1791100141973200584/report.json';native=load(native_path)
assert native['passed'] is False and native['cleanupPassed'] is True
assert native['error']=="AssertionError('ordinary:truthfulUnsupportedGeometryAndConstraints')"
assert [check['name'] for check in native['checks'] if not check['passed']]==['ordinary:truthfulUnsupportedGeometryAndConstraints']
assert native['pluginSHA256']==plugin['binarySHA256'] and native['coreBuild']['sha256']==core['sha256']
for name,digest in native['inputs'].items(): hash_check(name,digest)
for name,digest in native['artifacts'].items(): hash_check(native_path.parent/name,digest)
for descriptor in [native['coreBuild'],native['clientBuild']]:
    for key,value in descriptor.items():
        if key.endswith('SHA256') and key[:-6] in descriptor:
            hash_check(descriptor[key[:-6]],value)
    if 'binary' in descriptor: hash_check(descriptor['binary'],descriptor['sha256'])
    if 'client' in descriptor: hash_check(descriptor['client'],descriptor['clientSHA256'])
    build=load(descriptor['buildReport'])
    for section in ['dependencies','tools','linkedLibraries','retainedPolicyHeaders']:
        for name,digest in build.get(section,{}).items(): hash_check(name,digest)
# Native runner captured the exact core link descriptor; resolve its report,
# dependency and input closure separately rather than treating its pointer as proof.
core_root=Path(native['coreBuild']['binary']).parents[1]
link_descriptor=load(core_root/'link-build-report.json')
hash_check(core_root/'link-build-report.json',sha(core_root/'link-build-report.json'))
hash_check(link_descriptor['report'],link_descriptor['reportSHA256'])
link=load(link_descriptor['report']);assert link['passed'] and link['sha256']==core['sha256']
for section in ['dependencies','tools','inputs']:
    for name,digest in link.get(section,{}).items():hash_check(name,digest)
reports.append({'path':str(native_path.relative_to(REPO)),'sha256':sha(native_path),'passed':False,'cleanupPassed':True,'error':native['error']})
files={}
for packet in PACKETS:
    for path in sorted((BASE/packet).rglob('*')):
        if path==TARGET:continue
        rel=str(path.relative_to(REPO))
        if path.is_symlink():files[rel]={'symlink':str(path.readlink())}
        elif path.is_file():files[rel]={'sha256':sha(path),'size':path.stat().st_size}
manifest={'evidenceIntegrityPassed':True,'createdNs':time.time_ns(),'nativeAcceptance':False,'geometryEffectsImplemented':False,
          'wholeFeatureAccepted':False,'completedRequirementIds':[], 'scope':'Bounded CPU checks/build closure and retained native constraint failure; integrity only',
          'reports':reports,'files':files,'externalInputs':external,
          'remainingGates':['repair unspecified client size-limit defaults in fresh core','rerun full native observer transitions','workarea and output-owner change','geometry effects and menu integration','broader geometry and release acceptance']}
with TARGET.open('x') as stream:stream.write(json.dumps(manifest,indent=2)+'\n')
verify_manifest()
