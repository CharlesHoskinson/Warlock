import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir()
shutil.copy2(ROOT/'spec/hit.qnt',OUT/'hit.qnt');shutil.copy2(__file__,OUT/'model.py')
names=['listenerOrderRepairedTest','noIdleDuringDispatchTest','latestLayoutCoalescesTest','supersedingMotionFencesTaskTest','parentFocusLossFencesTaskTest','deviceRetirementFencesTaskTest','ownerReplacementFencesTaskTest','shutdownFencesTaskTest','delayedCommitRepairsEmptyFocusTest','supersededCommitDoesNotQueueTest']
r={'passed':False,'nativeAcceptance':False,'scope':'Sampled serialized bus/idle ordering abstraction; models separate layout/surface generations and excludes coordinates, native transport and rendering','commands':[]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,args,expected=0):
 cmd=[shutil.which('quint'),*args];p=subprocess.run(cmd,cwd=OUT,capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 r['commands'].append({'command':cmd,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True);assert p.returncode==expected,p.stderr or p.stdout
try:
 run('typecheck',['typecheck','hit.qnt'])
 run('named',['test','hit.qnt','--backend=typescript','--match=^('+'|'.join(names)+')$','--max-samples=1','--seed=55001','--out-itf=named-{test}-{seq}.itf.json'])
 assert len(list(OUT.glob('named-*.itf.json')))==len(names)
 run('invariants',['run','hit.qnt','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=55002'])
 source=(OUT/'hit.qnt').read_text()
 mutants=[('during-bus','s.queued and not(s.inBus)','s.queued','noIdleDuringDispatchTest'),
          ('superseded','s.live and s.anchor and s.parentFocus','s.live and s.parentFocus','supersedingMotionFencesTaskTest'),
          ('focus-loss','s.anchor and s.parentFocus and s.deviceAlive','s.anchor and s.deviceAlive','parentFocusLossFencesTaskTest'),
          ('owner-reused','s.deviceAlive and s.owner==s.queuedOwner','s.deviceAlive','ownerReplacementFencesTaskTest'),
          ('missing-commit-refresh','s.queued or (s.live and s.anchor)','s.queued','delayedCommitRepairsEmptyFocusTest')]
 for index,(name,before,after,test) in enumerate(mutants):
  assert source.count(before)==1
  (OUT/(name+'.qnt')).write_text(source.replace(before,after))
  run(name+'-typecheck',['typecheck',name+'.qnt'])
  run(name+'-rejected',['test',name+'.qnt','--backend=typescript','--match=^'+test+'$','--max-samples=1','--seed='+str(55100+index)],expected=1)
 r.update(passed=True,namedScenarios=names,invariantSamples=1000,maxSteps=40,mutantsRejected=len(mutants),sourceSHA256=sha(ROOT/'spec/hit.qnt'))
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
