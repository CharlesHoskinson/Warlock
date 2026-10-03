"""Compile actual shell and replay typed activation and original recovery tests."""
import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('elm-'+str(time.time_ns()));INPUT=OUT/'inputs';INPUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
paths=[ROOT/'elm.json',*sorted((ROOT/'src').glob('*.elm')),*[ROOT/'qa'/n for n in ['replay.cjs','shell.cjs','activation.cjs','elm.py']]]
report={'passed':False,'inputs':{str(p.relative_to(ROOT)):sha(p) for p in paths},'commands':[],'scope':'Compiled Elm controls and pure replay only; native GUI separate'}
try:
 for p in paths:
  dest=INPUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 commands=[('main',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Main.elm','--output='+str(OUT/'main.js')]),('replay',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Replay.elm','--output='+str(OUT/'replay.js')]),('shell',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/ShellReplay.elm','--output='+str(OUT/'shell.js')]),('original-effects',['node',str(INPUT/'qa/replay.cjs'),str(OUT/'replay.js'),str(OUT/'original-effects.json')]),('original-shell',['node',str(INPUT/'qa/shell.cjs'),str(OUT/'shell.js'),str(OUT/'original-shell.json')]),('activation',['node',str(INPUT/'qa/activation.cjs'),str(OUT/'replay.js'),str(OUT/'activation.json')])]
 for name,command in commands:
  p=subprocess.run(command,cwd=INPUT,capture_output=True,text=True,timeout=180)
  (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr
 results={name:json.loads((OUT/(name+'.json')).read_text()) for name in ['original-effects','original-shell','activation']}
 assert all(r['passed'] for r in results.values())
 assert results['original-effects']['checks']==20 and results['original-shell']['checks']==27 and results['activation']['checks']==17
 assert all(sha(ROOT/rel)==digest for rel,digest in report['inputs'].items())
 report.update(passed=True,checks={name:r['checks'] for name,r in results.items()},artifacts={p.name:sha(p) for p in OUT.glob('*.json')})
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
