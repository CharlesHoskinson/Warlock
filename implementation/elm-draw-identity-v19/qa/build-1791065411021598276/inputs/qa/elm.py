"""Compile typed diagnostic trace decoder and replay actual native packets."""
import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('elm-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
for name in ['src','elm.json']: 
 p=ROOT/name
 if p.is_dir():shutil.copytree(p,INPUT/name)
 else:shutil.copy2(p,INPUT/name)
shutil.copy2(ROOT/'qa/elm.cjs',INPUT/'elm.cjs')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'elm.json',ROOT/'qa/elm.cjs',*sorted((ROOT/'src').glob('*.elm'))]},'commands':[]}
native_path=sorted((ROOT/'qa').glob('native-*/report.json'))[-1];native=json.loads(native_path.read_text());assert native['passed'] and not native.get('error')
try:
 for name,command in [('compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Replay.elm','--output='+str(OUT/'replay.js')]),('checks',['node',str(INPUT/'elm.cjs'),str(OUT/'replay.js'),str(native_path),str(OUT/'checks.json')])]:
  p=subprocess.run(command,cwd=INPUT,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr
 checks=json.loads((OUT/'checks.json').read_text());assert checks['passed'];report.update(passed=True,nativeReportSHA256=sha(native_path),**{k:v for k,v in checks.items() if k!='passed'})
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
