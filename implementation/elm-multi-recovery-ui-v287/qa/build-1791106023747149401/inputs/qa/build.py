"""Compile real Elm entrypoints and execute inherited/new controller replays."""
import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('build-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
files=[*sorted((ROOT/'src').glob('*.elm')),ROOT/'elm.json',*sorted((ROOT/'qa').glob('*.cjs')),*sorted((ROOT/'qa').glob('*.json')),Path(__file__)]
inputs={};commands=[]
for p in files:
 dest=INPUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'scope':'Actual optimized Main/Popup and shared-controller compiled Elm replay; no integrated native host acceptance','inputs':inputs,'commands':commands}
def run(name,args):
 p=subprocess.run(args,cwd=INPUT,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);commands.append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stdout+p.stderr
try:
 for entry in ['Main','Popup','MenuSurfaceReplay']:
  run(entry,['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/'+entry+'.elm','--optimize','--output='+str(OUT/(entry+'.js'))])
 for suite in ['menu','geometry','refresh','recovery']:
  args=['node','qa/'+suite+'.cjs',str(OUT/'MenuSurfaceReplay.js'),'qa/fixtures.json']
  if suite!='menu':args.append('qa/geometry-fixtures.json')
  args.append(str(OUT/(suite+'-checks.json')));run(suite,args);report[suite+'Checks']=json.loads((OUT/(suite+'-checks.json')).read_text())['checks']
 for name,digest in inputs.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
