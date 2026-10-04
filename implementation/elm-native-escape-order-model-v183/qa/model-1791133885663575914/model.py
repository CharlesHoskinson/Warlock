import hashlib,json,re,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir()
shutil.copy2(ROOT/'spec/recovery.qnt',OUT/'recovery.qnt');shutil.copy2(__file__,OUT/'model.py')
source=(OUT/'recovery.qnt').read_text();names=re.findall(r'^\s*run (\w+)\s*=',source,re.MULTILINE);assert len(names)==24
r={'passed':False,'nativeAcceptance':False,'scope':'Terminal-order346 extended with current native Escape intent independent of DOM lag, strict stale callbacks, one actual release and unchanged scope/deadline; no C/GTK/native refinement claim','commands':[]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,args,expected=0):
 cmd=[shutil.which('quint'),*args];p=subprocess.run(cmd,cwd=OUT,capture_output=True,timeout=180);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True);assert p.returncode==expected,(p.stderr+p.stdout).decode(errors='replace')[-3000:]
try:
 run('typecheck',['typecheck','recovery.qnt'])
 run('named',['test','recovery.qnt','--backend=typescript','--match=^('+'|'.join(names)+')$','--max-samples=1','--seed=79001','--out-itf=named-{test}-{seq}.itf.json']);assert len(list(OUT.glob('named-*.itf.json')))==len(names)
 run('invariants',['run','recovery.qnt','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=79002'])
 mutants=[('native-requires-dom', "action nativeEscape=s'=if(s.available and s.popup", "action nativeEscape=s'=if(s.available and s.domCurrent and s.popup", 'nativeEscapeBeforeDOMAckTest'), ('native-does-not-consume', '{...s,available:false,pending:true} else s', '{...s,available:true,pending:true} else s', 'nativeEscapeBeforeDOMAckTest'), ('native-closes-on-press', '{...s,available:false,pending:true} else s', '{...s,available:false,pending:false,popup:false,closed:s.closed+1,qualified:s.qualified+1} else s', 'nativeEscapeBeforeDOMAckTest'), ('stale-web-admitted', 's.available and s.domCurrent and s.popup', 's.available and s.popup', 'staleDOMCallbackStillRefusedTest'), ('render-ack-renews-deadline', "action renderAck=s'={...s,domCurrent:true}", "action renderAck=s'={...s,domCurrent:true,expired:false}", 'nativeEscapeDeadlineNeverRenewedTest'), ('native-expired-approval', "action nativeEscape=s'=if(s.available and s.popup and s.valid and not(s.expired)", "action nativeEscape=s'=if(s.available and s.popup and s.valid", 'nativeEscapeExpiredPressRefusedTest')]
 for name,before,after,test in mutants:
  assert source.count(before)==1,(name,source.count(before));mutated=source.replace(before,after);(OUT/(name+'.qnt')).write_text(mutated)
  run(name+'-typecheck',['typecheck',name+'.qnt']);run(name+'-rejected',['test',name+'.qnt','--backend=typescript','--match=^'+test+'$','--max-samples=1','--seed=79101'],1)
 r.update(passed=True,namedScenarios=names,invariantSamples=1000,maxSteps=40,mutantsRejected=len(mutants),sourceSHA256=sha(ROOT/'spec/recovery.qnt'))
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
