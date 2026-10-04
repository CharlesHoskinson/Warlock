import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V33=ROOT.parent/'elm-taskbar-projection-v33'
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('replay-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((V33/'qa/slice-manifest.json').read_text())
for rel,digest in manifest['files'].items():assert sha(V33/rel)==digest,rel
compiled=V33/'qa/taskbar-1791071664426703686/taskbar.js'
inputs={str(p):sha(p) for p in [compiled,Path(__file__),ROOT/'qa/replay.cjs']}
shutil.copy2(ROOT/'qa/replay.cjs',OUT/'replay.cjs')
report={'passed':False,'inputs':inputs,'commands':[],'scope':'Frozen V33 Elm worker on both actual native V34 campaigns'}
try:
 natives=sorted((ROOT/'qa').glob('native-*/report.json'));assert len(natives)==2
 for index,p in enumerate(natives):
  native=json.loads(p.read_text());assert native['passed'] and native['cleanupPassed'];inputs[str(p)]=sha(p)
  dest=OUT/('native-'+str(index)+'.json');shutil.copy2(p,dest)
  cmd=['node',str(OUT/'replay.cjs'),str(compiled),str(dest),str(OUT/('checks-'+str(index)+'.json'))]
  result=subprocess.run(cmd,capture_output=True,text=True,timeout=10);(OUT/('stderr-'+str(index))).write_text(result.stderr);report['commands'].append({'command':cmd,'exitCode':result.returncode});assert result.returncode==0,result.stderr
  check=json.loads((OUT/('checks-'+str(index)+'.json')).read_text());assert check['passed'] and check['checks']==60
 assert all(sha(Path(p))==digest for p,digest in inputs.items())
 report.update(passed=True,checks=120,nativeCampaigns=2,packets=20)
except Exception as error:report['error']=repr(error)
report['artifacts']={p.name:sha(p) for p in OUT.iterdir() if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
