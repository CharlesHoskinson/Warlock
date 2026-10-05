"""Protected actual optimized Elm decoder and original native observation."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
OUT=ROOT/'qa'/('check-'+str(time.time_ns()));OUT.mkdir()
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope}
try:
 provider=REPO/'implementation/warlock-preview-provider-v7'
 build=provider/'qa/build-1791238777317896722/report.json';built=json.loads(build.read_text());assert built['passed']
 native=REPO/'implementation/warlock-client-provider-native-v1/qa/native-1791239211683329896/report.json'
 observed=json.loads(native.read_text());assert observed['passed'] and observed['cleanupPassed'] and all(x['exitCode']==0 for x in observed['ownedExitCodes'])
 worker=build.parent/'inputs/assets/native-source-replay.js';assert sha(worker)==built['compiledAssetPackage']['files'][worker.name]
 inputs={str(p):sha(p) for p in [build,native,worker,ROOT/'SPEC.md',ROOT/'qa/check.js',pathlib.Path(__file__)]}
 for rel,digest in built['inputs'].items():
  if rel.startswith('src/') or rel=='elm.json':
   assert sha(provider/rel)==digest;inputs[str(provider/rel)]=digest
 shutil.copy2(worker,OUT/'native-source-replay.js');shutil.copy2(ROOT/'qa/check.js',OUT/'check.js')
 (OUT/'client-scope.json').write_text(json.dumps(observed['providerReport']['clientScope'],indent=2)+'\n')
 cmd=['node',str(OUT/'check.js'),str(OUT/'native-source-replay.js'),str(OUT/'client-scope.json')]
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=30);(OUT/'checks.stdout').write_text(p.stdout);(OUT/'checks.stderr').write_text(p.stderr)
 r.update(argv=cmd,exitCode=p.returncode,inputs=inputs);assert p.returncode==0 and not p.stderr,p.stderr
 result=json.loads(p.stdout);assert result['passed'] and len(result['checks'])>=200;r['checks']=result['checks'];r['projectionScope']=result['scope']
 assert all(sha(path)==digest for path,digest in inputs.items());r['passed']=True
except Exception as error:r['error']=repr(error)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'checks':len(r.get('checks',[])),'error':r.get('error')}));raise SystemExit(not r['passed'])
