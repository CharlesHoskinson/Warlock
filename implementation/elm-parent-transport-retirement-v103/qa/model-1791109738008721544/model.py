import hashlib,json,re,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir()
shutil.copy2(ROOT/'spec/transport.qnt',OUT/'transport.qnt');shutil.copy2(__file__,OUT/'model.py')
source=(OUT/'transport.qnt').read_text();names=re.findall(r'^\s*run (\w+)\s*=',source,re.MULTILINE);assert len(names)==10
r={'passed':False,'nativeAcceptance':False,'scope':'Bounded parent transport retirement/consumer-idle notification abstraction; actual function replay and native QA separate','commands':[]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,args,expected=0):
 cmd=[shutil.which('quint'),*args];p=subprocess.run(cmd,cwd=OUT,capture_output=True,timeout=180);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True);assert p.returncode==expected,(p.stderr+p.stdout).decode(errors='replace')[-3000:]
try:
 run('typecheck',['typecheck','transport.qnt'])
 run('named',['test','transport.qnt','--backend=typescript','--match=^('+'|'.join(names)+')$','--max-samples=1','--seed=79001','--out-itf=named-{test}-{seq}.itf.json']);assert len(list(OUT.glob('named-*.itf.json')))==len(names)
 run('invariants',['run','transport.qnt','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=79002'])
 mutants=[('devices','pointers:0,keyboards:0','pointers:s.pointers,keyboards:s.keyboards','devicesRetiredTest'),
  ('output','outputs:0,focus:false','outputs:s.outputs,focus:s.focus','outputRetiredTest'),
  ('queue','queued:0,logs:s.logs+1','queued:s.queued,logs:s.logs+1','pendingPublicationDiscardedTest'),
  ('descriptor','fd:false,pointers:0','fd:s.fd,pointers:0','failedDescriptorWithdrawnTest'),
  ('synchronous-notification','queued:0,logs:s.logs+1,notifyQueued:true','queued:0,logs:s.logs+1,notifyQueued:true,notifications:s.notifications+1','deferredDescriptorNotificationTest'),
  ('one-shot','not(s.transport) and not(s.retired)','not(s.transport)','repeatedLossOneShotTest'),
  ('copied-frame','not(s.retired) and s.transport','true','copiedFrameAfterRetirementTest'),
  ('late-enable','if(s.transport and not(s.retired)) {...s,pointers:1','if(true) {...s,pointers:1','lateCapabilityRefusedTest')]
 for name,before,after,test in mutants:
  assert source.count(before)==1,(name,source.count(before));mutated=source.replace(before,after);(OUT/(name+'.qnt')).write_text(mutated)
  run(name+'-typecheck',['typecheck',name+'.qnt']);run(name+'-rejected',['test',name+'.qnt','--backend=typescript','--match=^'+test+'$','--max-samples=1','--seed=79101'],1)
 r.update(passed=True,namedScenarios=names,invariantSamples=1000,maxSteps=40,mutantsRejected=len(mutants),sourceSHA256=sha(ROOT/'spec/transport.qnt'))
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
