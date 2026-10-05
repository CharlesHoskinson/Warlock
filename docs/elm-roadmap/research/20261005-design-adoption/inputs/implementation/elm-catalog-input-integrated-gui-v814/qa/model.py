import hashlib,json,pathlib,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('model-'+str(time.time_ns()));out.mkdir();checks=[]
source=root/'spec/catalog.qnt';held=out/'catalog.qnt';held.write_bytes(source.read_bytes())
def run(name,args,expected=True):
 p=subprocess.run(args,capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 checks.append({'name':name,'args':args,'exitCode':p.returncode});assert (p.returncode==0)==expected,p.stdout+p.stderr
 if not expected:assert 'QNT508' in p.stdout+p.stderr and 'Assertion failed' in p.stdout+p.stderr,p.stdout+p.stderr
try:
 run('type',['quint','typecheck',str(held)])
 run('scenarios',['quint','test',str(held),'--main=catalog','--match=Test$','--max-samples=1','--seed=77801'])
 run('safety',['quint','run',str(held),'--main=catalog','--invariant=safety','--max-samples=1000','--max-steps=30','--seed=77802'])
 mutations=[('ignore-current-request','and expected.contains(descriptor.request)','and true','delayedNegativeAfterReopenTest'),('trust-unproven-negative','and nativeUnsent.contains(descriptor)','and true','unprovenNegativeTest'),('ignore-exact-wire','registered.contains(descriptor) and','true and','foreignWireNegativeTest'),('dismiss-newer-popup','matches and descriptor.lease==lease','matches','newerPopupLeaseTest')]
 for name,old,new,witness in mutations:
  text=held.read_text();assert text.count(old)==1;mutant=out/(name+'.qnt');mutant.write_text(text.replace(old,new))
  run(name+'-type',['quint','typecheck',str(mutant)])
  run(name+'-counterexample',['quint','test',str(mutant),'--main=catalog','--match='+witness,'--max-samples=1','--seed=77803'],False)
 assert source.read_bytes()==held.read_bytes()
 report={'passed':True,'checks':checks,'sourceSHA256':hashlib.sha256(held.read_bytes()).hexdigest(),'nativeAcceptance':False,'scope':'Finite exact catalog slot/descriptor proposal: authenticated wire and original never-enqueued proof abstract; no native liveness/deadline/GUI or storage proof transfer'}
except Exception as error:report={'passed':False,'checks':checks,'error':repr(error),'nativeAcceptance':False}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json');sys.exit(not report['passed'])
