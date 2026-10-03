"""Fresh pre-implementation contract/model evidence, preserving earlier packets."""
import datetime,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];PLAN=REPO/'docs/elm-roadmap'
OUT=ROOT/'qa'/('final-pass-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S'));OUT.mkdir()
rows=[]
def run(name,cmd,cwd=REPO):
 p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 rows.append(dict(name=name,command=list(map(str,cmd)),exitCode=p.returncode));print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(name+' failed: '+p.stderr[-1500:]+p.stdout[-1500:])
 return p.stdout
result=dict(scope='Current contract format and unchanged architecture model checks; no native implementation acceptance',passed=False)
try:
 for name,file in [('plan','validate_plan.py'),('cycles','validate_sprints.py')]:
  source=(PLAN/'tools'/file).read_text().replace("ROOT=Path(__file__).resolve().parents[1]",'ROOT=Path('+repr(str(PLAN))+')').replace("root=Path(__file__).resolve().parents[1]",'root=Path('+repr(str(PLAN))+')')
  if name=='plan':source=source.replace("ROOT/'validation.json'",'Path('+repr(str(OUT/'plan-validation.json'))+')')
  else:
   source=source.replace('Path(__file__),', 'root/"tools/validate_sprints.py",')
   source=source.replace("root/'delivery/validation.json'",'Path('+repr(str(OUT/'cycle-validation.json'))+')')
  script=OUT/(name+'-validator.py');script.write_text(source);run(name,['/usr/bin/python3','-B',str(script)])
 run('quint-version',['quint','--version'])
 scene=PLAN/'prototypes/quint/scene_tests.qnt';names=re.findall(r'run (\w+) =',scene.read_text())
 run('scene-tests',['quint','test',str(scene),'--main=scene_tests','--match=^('+'|'.join(names)+')$','--max-samples=1','--seed=610203'])
 run('scene-invariants',['quint','run',str(scene.parent/'scene_model.qnt'),'--main=scene','--invariants','noExcludedPaint','noExcludedInput','focusSafe','proxyInert','leaseValid','proxyValid','--max-samples=1000','--max-steps=40','--seed=610204'])
 bridge=PLAN/'prototypes/quint/bridge/bridge.qnt'
 run('bridge-tests',['quint','test',str(bridge),'--match=Test$','--max-samples=1','--seed=610205'])
 run('bridge-invariants',['quint','run',str(bridge),'--invariant=safety','--max-samples=2000','--max-steps=40','--seed=610206'])
 result['passed']=True
except Exception as e:result['error']=str(e)
result['commands']=rows
result['inputSHA256']={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [PLAN/'requirements.json',PLAN/'ARCHITECTURE.md',PLAN/'SPRINTS.md',PLAN/'delivery/execution-policy-amendment.json',PLAN/'prototypes/quint/scene_model.qnt',PLAN/'prototypes/quint/scene_tests.qnt',PLAN/'prototypes/quint/bridge/bridge.qnt']}
(OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=result['passed'],output=str(OUT),error=result.get('error'))));raise SystemExit(not result['passed'])
