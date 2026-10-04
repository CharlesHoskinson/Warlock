import copy,hashlib,json,pathlib,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('controls-'+str(time.time_ns()));OUT.mkdir();PRIMARY=max((ROOT/'qa').glob('tests-*/report.json')).parent;DRAIN=max((ROOT/'qa').glob('drain-*/report.json')).parent
checks=[];commands=[]
def check(n,b):checks.append({'name':n,'passed':bool(b)});assert b,n
def cmd(n,args,cwd=None):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=180);(OUT/(n+'.log')).write_text(p.stdout+p.stderr);commands.append({'name':n,'command':args,'cwd':str(cwd),'exit':p.returncode});assert p.returncode==0,p.stderr
 return p
base=json.loads((DRAIN/'mixed-announced-events.json').read_text());good=base[-1]['frame'];later=json.loads((DRAIN/'mixed-after-turn1-events.json').read_text())[-1]['frame'];cases={}
for n,change in [('foreign-current',lambda f:f['binding'].update(session='999')),('current-queried',lambda f:f.update(queriedBinding=copy.deepcopy(f['binding']))),('future-grant',lambda f:f.update(grantState='Future')),('foreign-lifetime',lambda f:f['queriedBinding'].update(lifetime='999'))]:
 f=copy.deepcopy(good);change(f);cases[n]=base[:-1]+[{'kind':'native','frame':f}]
cases['duplicate-info-proof']=base+[{'kind':'native','frame':copy.deepcopy(good)}]
cases['new-scope-before-informational-release']=base+[{'kind':'native','frame':copy.deepcopy(later)}]
beforeRelease=json.loads((DRAIN/'mixed-after-turn1-events.json').read_text())
proofStart=next(i for i,e in enumerate(beforeRelease) if e.get('frame',{}).get('kind')=='binding-retirement' and e['frame']['binding']==good['binding'] and e['frame']['requestId']==good['requestId'])
releaseIndex=next(i for i,e in enumerate(beforeRelease) if i>proofStart and e.get('frame',{}).get('kind')=='host-reservation-released')
cases['info-retry']=beforeRelease[:releaseIndex]+[{'kind':'refresh'}]
for n,events in cases.items():
 p=OUT/(n+'-events.json');p.write_text(json.dumps(events,indent=2)+'\n');target=OUT/(n+'-rows.json');cmd(n,['node',str(ROOT/'qa/probe.cjs'),str(PRIMARY/'worker.js'),str(p),str(target)]);rows=json.loads(target.read_text())
 if n=='info-retry':check(n+'-ready-before-fresh-read-pair',[w['kind'] for w in rows[-1]['wires']]==['reconciliation-ready','projection-request','geometry-facts-request'])
 else:check(n+'-cannot-emit-another-ready-read-turn',rows[-1]['wires']==[] and rows[-1]['unresolved']==1)
 check(n+'-keeps-A-released-B-reserved-and-Unknown',len(rows[-1]['history'])==2 and sum(v['released'] for v in rows[-1]['history'])==1 and all(v['status']=='Unknown' for v in rows[-1]['history']))
# Actual compiled source mutations with behavior-level oracles; malformed/noncompiling mutations never count.
mutants=[
 ('released-not-eligible','ReconciliationTracking.elm','let eligible slot = slot.record.binding','let eligible slot = not slot.released && slot.record.binding','mixed-announced',False),
 ('informational-read-ignored','ReconciliationTracking.elm','if slot.proof==Nothing then slot else','if slot.released || slot.proof==Nothing then slot else','mixed-after-turn1',False),
 ('informational-release-not-stored','SurfaceController.elm','then (Model {model|recovery=recovery},[]) else\n                            let cleared','then (current,[]) else\n                            let cleared','mixed-after-turn1',False),
 ('informational-scope-unchecked','ReconciliationTracking.elm','anotherActiveScope || informationalScopeChanged','anotherActiveScope','new-scope-before-informational-release',True),
 ('future-info-proof-admitted','ReconciliationFrame.elm','exactString "Retired"','D.string','future-grant',True),
 ('informational-retry-no-ready','SurfaceController.elm',' ++ (reset.informational |> Maybe.map List.singleton |> Maybe.withDefault [])','','info-retry',False)]
controls=[]
for n,file,old,new,scenario,unexpected in mutants:
 d=OUT/n;shutil.copytree(ROOT/'src',d/'src');shutil.copy2(ROOT/'elm.json',d/'elm.json');shutil.copy2(ROOT/'qa/Probe.elm',d/'src/Probe.elm');p=d/'src'/file;s=p.read_text();count=s.count(old);assert count==(2 if n=='informational-read-ignored' else 1),(n,count);p.write_text(s.replace(old,new))
 if scenario in ['mixed-announced','mixed-after-turn1']:events=json.loads((DRAIN/(scenario+'-events.json')).read_text())
 else:events=cases[scenario]
 (d/'events.json').write_text(json.dumps(events,indent=2)+'\n');cmd(n+'-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Probe.elm','--optimize','--output='+str(d/'worker.js')],d);cmd(n+'-probe',['node',str(ROOT/'qa/probe.cjs'),str(d/'worker.js'),str(d/'events.json'),str(d/'rows.json')]);rows=json.loads((d/'rows.json').read_text());ready=any(w['kind']=='reconciliation-ready' for w in rows[-1]['wires']);detected=ready if unexpected else not ready;check(n+'-compiled-behavioral-control-detected',detected);controls.append({'name':n,'scenario':scenario,'detected':detected,'mutatedSourceSHA256':hashlib.sha256(p.read_bytes()).hexdigest()})
r={'passed':True,'assertions':len(checks),'checks':checks,'compiledControls':controls,'commands':commands,'nativeAcceptance':False,'scope':'Compiled informational-history proof/read/strict-release controls; synthetic protocol trajectories'};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'assertions':len(checks),'compiledControls':len(controls)}))
