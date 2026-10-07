"""Couple explicitly selected native-ticket transport traces to actual JS."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('recovered-pages-model-check-v2-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
names=['assets/recovered-native-preview-control-outbox.js','qa/recovered-pages-replay-v2.js','qa/recovered-pages-model-check-v2.py','spec/recovered_control_pages_v2.qnt','spec/recovered_control_pages_tests_v2.qnt']
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual JS retained native-ticket frontier/receipt prefix, queue occupancy, exact wire retry, ordered data and independent confirmation attempts/results against explicitly selected Quint traces. Native issuance is a synthetic trace input; actual controlled C issuer qualified separately. No WebKit/real compositor activation or effect/physical acceptance.'}
def run(name,args,cwd=None):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout;return p.stdout
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 run('syntax',['node','--check','assets/recovered-native-preview-control-outbox.js'])
 folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'recovered_control_pages_tests_v2.qnt').read_text());assert len(selected)==24
 run('typecheck',[tool,'typecheck','recovered_control_pages_tests_v2.qnt'],folder)
 run('selected',[tool,'test','recovered_control_pages_tests_v2.qnt','--main=recovered_control_pages_tests_v2','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1120061','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],folder)
 assert len(list(out.glob('named-*.itf.json')))==24
 run('samples',[tool,'run','recovered_control_pages_v2.qnt','--main=recovered_control_pages_v2','--backend=typescript','--invariant=safety','--seed=1120062','--max-samples=200','--max-steps=30','--n-traces=12','--out-itf='+str(out/'sample-{seq}.itf.json')],folder)
 traces=[];compared=0
 for path in sorted(out.glob('*.itf.json')):
  e=json.loads(run('replay-'+path.stem,['node','qa/recovered-pages-replay-v2.js','assets/recovered-native-preview-control-outbox.js',str(path)]));assert e['passed'];compared+=e['statesCompared'];traces.append({'trace':path.name,'statesCompared':e['statesCompared']})
 mutants=[]
 for name,old,new,witness,wanted in [
  ('changed-issued-bytes','if(existing.wire!==ticket.wire)return false;','if(false)return false;','changedIssuedBytesRefuse','Ordered exact native transmissions'),
  ('advisory-drains-row','transmit();return true;\n    }','if(ticket.alreadyDelivered){queue.shift();return true;}transmit();return true;\n    }','deliveredAdvisoryCannotDrain','Bounded retained ticket occupancy'),
  ('future-receipt','ordinal!==queue[0].ordinal','ordinal<queue[0].ordinal','futureReceiptCannotRelease','Original delivery prefix'),
  ('forget-dropped-post','try {post(queue[0].wire);return true;} catch(_error) {return false;}','try {post(queue[0].wire);return true;} catch(_error) {queue.shift();return false;}','droppedPostRetainsExactTicket','Bounded retained ticket occupancy'),
  ('forget-dropped-confirmation','try {confirm(confirmationWire);return true;} catch(_error) {return false;}','try {confirm(confirmationWire);return true;} catch(_error) {confirmationWire=null;return false;}','lostConfirmationRetainedAfterQueueEmpty','Independent retained confirmation attempts'),
  ('ignore-capacity','queue.length>=capacity || ordinal!==nativeIssuedThrough+1n','ordinal!==nativeIssuedThrough+1n','backpressureRetainsNativeIssuance','Native ticket retained frontier')]:
  changed=out/name;shutil.copytree(out/'inputs',changed);p=changed/'assets/recovered-native-preview-control-outbox.js';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  run(name+'-syntax',['node','--check','assets/recovered-native-preview-control-outbox.js'],changed)
  trace=next(out.glob('named-'+witness+'-*.itf.json'));p=subprocess.run(['node','qa/recovered-pages-replay-v2.js','assets/recovered-native-preview-control-outbox.js',str(trace)],cwd=changed,capture_output=True,text=True,timeout=180)
  (changed/'replay.stdout').write_text(p.stdout);(changed/'replay.stderr').write_text(p.stderr)
  assert p.returncode==1 and 'AssertionError' in p.stderr and wanted in p.stderr,(name,p.stdout,p.stderr)
  mutants.append({'name':name,'syntaxPassed':True,'witness':witness,'namedObservableMismatch':True})
 assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
 report.update(passed=True,namedScenarios=24,invariantSamples=200,coupledTraces=traces,statesCompared=compared,unsafeActualJSVariantsDetected=6,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1600]}),flush=True);sys.exit(not report['passed'])
