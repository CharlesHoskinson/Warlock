"""Bind new host/compiler/native/graphics evidence; keep all failed attempts."""
import datetime,hashlib,json,resource,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
build_path=sorted((ROOT/'qa').glob('build-*/report.json'))[-1];build=json.loads(build_path.read_text());assert build['passed']
for relative,digest in build['inputs'].items():
 if not relative.startswith('qa/'):assert sha(ROOT/relative)==digest,relative
assert sha(build_path.parent/'elm-host')==build['binarySHA256']
native_path=sorted((ROOT/'qa').glob('native-*/report.json'))[-1];native=json.loads(native_path.read_text());assert native['passed'] and native['cleanupPassed']
assert native['buildReportSHA256']==sha(build_path)
for relative,digest in native['inputs'].items():assert sha(ROOT/relative)==digest,relative
assert native['eventDrivenUnmapRemap']['passed'] and native['eventDrivenUnmapRemap']['oldIncarnation']!=native['eventDrivenUnmapRemap']['newIncarnation']
assert native['normalHostAndBackendExit'] and native['canvasPresentedPassed'] and native['webglReadbackPassed'] and native['hardwareGraphicsAvailableObserved']
assert not native['webgpuExposed']
authority=REPO/'implementation/elm-authority-v3'
for module in ['Observer.elm','Observation.elm','UInt64.elm']:assert sha(ROOT/'src'/module)==sha(authority/'frontend/src'/module),module
assert sha(ROOT/'adapter/endpoint.py')==sha(authority/'adapter/endpoint.py')
archive=ROOT/'qa/native-evidence';archive.mkdir(exist_ok=True)
for path in sorted((ROOT/'qa').glob('native-*/report.json')):
 report=json.loads(path.read_text());output=Path(report['output'])
 if output.exists() and not (archive/output.name).exists():shutil.copytree(output,archive/output.name,symlinks=True)
manifest={'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'scope':'Event-driven native-to-Elm DOM and isolated Intel/Mesa hardware graphics availability; all full implementation/release gates remain open','buildReport':str(build_path.relative_to(ROOT)),'nativeReport':str(native_path.relative_to(ROOT)),'authorityProof':'implementation/elm-authority-v3/qa/slice-manifest.json','authorityProofSHA256':sha(authority/'qa/slice-manifest.json'),'observed':{'eventDrivenUnmapRemap':native['eventDrivenUnmapRemap'],'normalHostAndBackendExit':True,'webglReadbackPassed':True,'canvasPresentedPassed':True,'hardwareGraphicsAvailableObserved':True,'webgpuExposed':False,'nativeGraphicsInfo':native['nativeGraphicsInfo']},'completedRequirements':[]}
manifest['files']={str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p.name!='slice-manifest.json'}
manifest['symlinks']={str(p.relative_to(ROOT)):str(p.readlink()) for p in sorted(ROOT.rglob('*')) if p.is_symlink()}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items() if k not in ['files','symlinks']},indent=2))
