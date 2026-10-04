import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('checks-'+str(time.time_ns()));INPUT=OUT/'inputs';INPUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=[ROOT/'elm.json',*sorted((ROOT/'src').glob('*.elm')),ROOT/'qa/launch.cjs',Path(__file__)]
report={'passed':False,'inputs':{str(p.relative_to(ROOT)):sha(p) for p in paths},'commands':[]}
try:
 for p in paths:
  dest=INPUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 native=ROOT.parent/'elm-catalog-launch-v55/qa/native-1791075707665392131/report.json';receipt=json.loads(native.read_text());assert receipt['passed']
 assert all(sha(native.parents[2]/rel)==digest for rel,digest in receipt['inputs'].items())
 packet=native.parent/'snapshot.json';shutil.copy2(packet,OUT/'native-snapshot.json');shutil.copy2(native,OUT/'native-report.json');report['nativeReport']={'path':str(native),'sha256':sha(native),'snapshotSHA256':sha(packet)}
 commands=[('compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/LaunchReplay.elm','--output='+str(OUT/'launch.js')]),('typed',['node',str(INPUT/'qa/launch.cjs'),str(OUT/'launch.js'),str(OUT/'native-report.json'),str(OUT/'native-snapshot.json'),str(OUT/'typed.json')])]
 for name,command in commands:
  p=subprocess.run(command,cwd=INPUT,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr
 typed=json.loads((OUT/'typed.json').read_text());assert typed['passed'] and typed['checks']==33
 assert all(sha(ROOT/rel)==digest for rel,digest in report['inputs'].items())
 report.update(passed=True,typedChecks=typed['checks'])
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
