import hashlib,json,os,pathlib,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
from toolchain import verify
ROOT=pathlib.Path(__file__).resolve().parents[1];PARENT=ROOT.parent/'elm-recovery-delivery-integrated-gui-v640'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
t=verify();version=subprocess.run([str(ROOT/t['compiler']),'--version'],capture_output=True,text=True,env=dict(os.environ,ELM_HOME=str(ROOT/t['elmHome'])),timeout=30);assert version.returncode==0 and version.stdout.strip()=='0.19.2';verify();(ROOT/'qa/elm-version.log').write_text(version.stdout+version.stderr)
buildpath=max((ROOT/'qa').glob('build-*/report.json'));build=json.loads(buildpath.read_text());publicpath=max((ROOT/'qa').glob('tests-*/report.json'));public=json.loads(publicpath.read_text());assert build['passed'] and public['passed'] and len(public['checks'])==51
parentpath=PARENT/'qa/build-1791153819143987946/report.json';parent=json.loads(parentpath.read_text());sources={}
for directory in ['src','native','adapter','assets']:
 expected={str(p.relative_to(PARENT)) for p in (PARENT/directory).rglob('*') if p.is_file()};actual={str(p.relative_to(ROOT)) for p in (ROOT/directory).rglob('*') if p.is_file()};assert actual==expected
 for n in expected:assert sha(ROOT/n)==sha(PARENT/n);sources[n]=sha(ROOT/n)
assert sha(ROOT/'elm.json')==sha(PARENT/'elm.json')
comparisons={}
for n in ['inputs/assets/elm.js','inputs/assets/bar.js','inputs/assets/popup.js']:
 assert sha(buildpath.parent/n)==build['artifacts'][n] and sha(parentpath.parent/n)==parent['artifacts'][n];comparisons[n]={'new':build['artifacts'][n],'parent640':parent['artifacts'][n],'byteIdentical':build['artifacts'][n]==parent['artifacts'][n]}
assert sha(buildpath.parent/'elm-host')==build['binarySHA256'] and sha(parentpath.parent/'elm-host')==parent['binarySHA256'];comparisons['elm-host']={'new':build['binarySHA256'],'parent640':parent['binarySHA256'],'byteIdentical':build['binarySHA256']==parent['binarySHA256']};assert all(r['byteIdentical'] for r in comparisons.values())
postSnapshotLogs=[]
for n,h in build['inputs'].items():
 if n.startswith('qa/') and n.endswith('.log') and sha(ROOT/n)!=h:postSnapshotLogs.append({'path':n,'snapshotSHA256':h,'terminalSHA256':sha(ROOT/n)})
 else:assert sha(ROOT/n)==h,n
 expected=build['artifacts'].get('inputs/'+n,h);assert sha(buildpath.parent/'inputs'/n)==expected
for n,h in public['sourceSHA256'].items():assert sha(ROOT/'src'/n)==h and sha(publicpath.parent/'inputs/src'/n)==h
for group in ['tools','compilerDependencies','linkedLibraries']:
 for p,row in build[group].items():assert sha(pathlib.Path(p))==row['sha256']
assert all(v['beforeAfterVerified'] for v in build['elmToolchainBeforeAfterChecks']) and all(v['beforeAfterVerified'] for v in public['elmToolchainBeforeAfterChecks'])
assert all(r['command'][0]!='npm' for r in build['commands']) and all(r['command'][0]!='npm' for r in public['commands'])
guards=json.loads((ROOT/'qa/guard-fixtures/report.json').read_text());assert guards['passed'] and len(guards['checks'])==8
oldOriginal={p:row for p,row in t['originalCacheFiles'].items()};assert all(sha(pathlib.Path(p))==row['sha256'] for p,row in oldOriginal.items())
r={'passed':True,'compiler':t['compiler'],'compilerSHA256':t['compilerSHA256'],'actualCompilerVersion':version.stdout.strip(),'heldCompilerPackageCacheFiles':len(t['heldFiles']),'dependencyPackages':len(t['elmDependencies']),'buildReport':str(buildpath),'publicReport':str(publicpath),'newPublicAssertions':51,'provenanceGuardFixtures':8,'buildBeforeAfterCommands':len(build['elmToolchainBeforeAfterChecks']),'publicBeforeAfterCommands':len(public['elmToolchainBeforeAfterChecks']),'sameProgramComparisons':comparisons,'postSnapshotUnusedQALogs':postSnapshotLogs,'productionSourceHashes':sources,'nativeAcceptance':False,'fullReleaseAccepted':False,'old640CompilerProvenanceReconstructed':False,'scope':'Fresh explicit pinned compiler/package/cache build and optimized public51; actual runtime programs byteidentical640; no native qualification'};(ROOT/'qa/provenance-report.json').write_text(json.dumps(r,indent=2)+'\n');(ROOT/'qa/current-build.json').write_text(json.dumps({'report':str(buildpath)},indent=2)+'\n');print(json.dumps({'passed':True,'compilerSHA256':t['compilerSHA256'],'byteIdenticalPrograms':len(comparisons),'publicAssertions':51,'guards':8}))
