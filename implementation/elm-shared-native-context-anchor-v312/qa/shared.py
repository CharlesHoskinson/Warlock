import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('outputs-'+str(time.time_ns()));INPUT=OUT/'inputs';INPUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=[ROOT/'elm.json',*sorted((ROOT/'src').glob('*.elm')),ROOT/'qa/outputs.cjs',ROOT/'qa/shared-recovery.cjs',ROOT/'qa/shared-menu.cjs',ROOT/'qa/shared-fixtures.json',ROOT/'qa/shared-geometry-fixtures.json',Path(__file__)]
report={'passed':False,'scope':'Compiled actual shared Elm controller/output scoping and typed recovery; no native GUI run','inputs':{str(p.relative_to(ROOT)):sha(p) for p in paths},'commands':[]}
try:
 for p in paths:
  dest=INPUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 commands=[('main',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Main.elm','--optimize','--output='+str(OUT/'main.js')]),('bar',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Bar.elm','--optimize','--output='+str(OUT/'bar.js')]),('replay',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/OutputReplay.elm','--output='+str(OUT/'output.js')]),('shared-replay',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/SharedRecoveryReplay.elm','--output='+str(OUT/'shared.js')]),('recovery',['node',str(INPUT/'qa/shared-recovery.cjs'),str(OUT/'shared.js'),str(INPUT/'qa/shared-fixtures.json'),str(INPUT/'qa/shared-geometry-fixtures.json'),str(OUT/'recovery.json')]),('shared-menu',['node',str(INPUT/'qa/shared-menu.cjs'),str(OUT/'shared.js'),str(INPUT/'qa/shared-fixtures.json'),str(INPUT/'qa/shared-geometry-fixtures.json'),str(OUT/'menu.json')]),('typed',['node',str(INPUT/'qa/outputs.cjs'),str(OUT/'output.js'),str(OUT/'typed.json')])]
 for name,command in commands:
  p=subprocess.run(command,cwd=INPUT,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr
 typed=json.loads((OUT/'typed.json').read_text());assert typed['passed'] and typed['checks']==37
 recovery=json.loads((OUT/'recovery.json').read_text());assert recovery['passed'] and recovery['checks']==49
 menu=json.loads((OUT/'menu.json').read_text());assert menu['passed'] and menu['checks']==13
 report['sharedMenuChecks']=menu['checks']
 report['recoveryChecks']=recovery['checks']
 assert all(sha(ROOT/rel)==digest for rel,digest in report['inputs'].items())
 report.update(passed=True,typedChecks=typed['checks'])
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
