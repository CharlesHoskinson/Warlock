"""Freeze source, exact native tuple and accepted serial authority/projection evidence."""
import datetime,hashlib,json,resource,shutil,stat,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def latest(pattern):
 files=sorted((ROOT/'qa').glob(pattern));assert files,pattern;return files[-1]
build_path=latest('build-*/report.json');build=json.loads(build_path.read_text());assert build['passed']
for relative,digest in build['inputs'].items():assert sha(ROOT/relative)==digest,relative
for file,digest in build['dependencies'].items():assert sha(Path(file))==digest,file
assert sha(Path(build['binary']))==build['binarySHA256']
assert sha(Path(build['core']['path']))==build['core']['sha256']
core_path=ROOT/'build-1791053548003608844/report.json';core=json.loads(core_path.read_text());assert core['passed'] and core['binary']==build['core']['path'] and core['binarySHA256']==build['core']['sha256']
assert sha(ROOT/'candidate/src/render/Renderer.cpp')==core['sourceSHA256']
for path,digest in core['dependencies'].items():assert sha(Path(path))==digest,path
native_path=latest('native-*/report.json');native=json.loads(native_path.read_text());assert native['passed'] and native['cleanupPassed']
assert native['buildReportSHA256']==sha(build_path) and Path(native['buildReport'])==build_path
for relative,digest in native['currentInputs'].items():assert sha(ROOT/relative)==digest,relative
assert native['checks'] and all(row['passed'] for row in native['checks'])
elm=json.loads((build_path.parent/'elm-report.json').read_text());conformance=json.loads((build_path.parent/'conformance-report.json').read_text())
actual_elm=json.loads((native_path.parent/'elm-report.json').read_text());assert elm['passed'] and conformance['passed'] and actual_elm['passed']
# Compiler matches the frozen owning-pair tool, observed again before release of this packet.
owner_report=json.loads((REPO/'implementation/maximized-stack-v1/plugin-build-v1/pair-build-report.json').read_text())
compiler=Path(shutil.which('g++')).resolve();assert sha(compiler)==owner_report['compiler_sha256']
compiler_version=subprocess.run([str(compiler),'--version'],capture_output=True,text=True,check=True).stdout
assert compiler_version==owner_report['compiler_version']
archive=ROOT/'qa/native-evidence';archive.mkdir(exist_ok=True)
for receipt in sorted((ROOT/'qa').glob('native-*/report.json')):
 record=json.loads(receipt.read_text());output=Path(record['output']);target=archive/output.name
 if output.exists():
  if not target.exists():shutil.copytree(output,target,symlinks=True)
 else:
  assert not record['passed'] and record.get('privateHost') is None, 'Missing launched native evidence'
  (receipt.parent/'no-native-launch.json').write_text(json.dumps({'scope':'Failed preflight before a private session; no external native output existed','sourceReportSHA256':sha(receipt)},indent=2)+'\n')
manifest={'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'scope':'Native read-only authority/session identity and bounded window projection with compiled Elm replay; no GPU, effect, complete scene-policy or full release acceptance','buildReport':str(build_path.relative_to(ROOT)),'nativeReport':str(native_path.relative_to(ROOT)),'protocolVersion':3,'nativePair':{'core':build['core'],'plugin':{'path':build['binary'],'sha256':build['binarySHA256']},'owningCompilerDependencyCount':len(build['dependencies']),'owningVersionHeaderSHA256':build['core']['versionHeaderSHA256']},'compilerObservedAtFreeze':{'path':str(compiler),'sha256':sha(compiler),'version':compiler_version},'checks':{'nativeCases':len(native['checks']),'appliedElmReplayCases':elm['testCount'],'counterChecks':elm['counterSuccessorChecks']+elm['counterComparisonChecks'],'quintNamedTests':12,'quintInvariantSamples':1000,'quintMaxSteps':40,'actualITFReplayTraces':conformance['traceCount'],'actualITFReplayTransitions':conformance['stepCount'],'actualNativeElmReplayTransitions':actual_elm['transitions']},'completedRequirements':[]}
manifest['rendererBuildReportSHA256']=sha(core_path)
manifest['rendererDependenciesRechecked']=len(core['dependencies'])
manifest['productSceneAcceptance']=False
manifest['files']={str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p.name!='slice-manifest.json'}
manifest['symlinks']={str(p.relative_to(ROOT)):str(p.readlink()) for p in sorted(ROOT.rglob('*')) if p.is_symlink()}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items() if k not in ['files','symlinks']},indent=2))
