"""Explicit selected Quint scenarios and sampled combined-recovery invariants."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
out=root/'qa'/('model-'+str(time.time_ns()));out.mkdir(mode=0o700);(out/'inputs').mkdir(mode=0o700)
inputs={str(path):sha(path) for path in [root/'spec/combined_recovery.qnt',root/'spec/combined_recovery_tests.qnt',pathlib.Path(__file__)]}
for name in ['combined_recovery.qnt','combined_recovery_tests.qnt']:shutil.copy2(root/'spec'/name,out/'inputs'/name)
names=re.findall(r'^ run ([A-Za-z0-9_]+)=',(out/'inputs/combined_recovery_tests.qnt').read_text(),re.M);assert len(names)==14
report={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewUncertaintyNativeQualified':False,'inputs':inputs,'quint':{'path':str(tool),'sha256':sha(tool)},'commands':[],'scope':'Fourteen explicitly selected acceptance scenarios and200 sampled invariant traces. Independent native strict-close event is an abstract external proof, never inferred from renderer/reader disposal. Window Unknown and preview Unknown remain distinct; fresh native host namespace is not an old grant reset. No native/hardware/full release acceptance.'}
try:
 for name,args in [('typecheck',[str(tool),'typecheck','combined_recovery_tests.qnt']),('selected',[str(tool),'test','combined_recovery_tests.qnt','--main=combined_recovery_tests','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=2040049','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')]),('invariants',[str(tool),'run','combined_recovery.qnt','--main=combined_recovery','--backend=typescript','--init=init','--step=step','--invariant=safety','--max-samples=200','--max-steps=80','--seed=2040049'])]:
  process=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(process.stdout);(out/(name+'.stderr')).write_text(process.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':process.returncode});print(name,process.returncode,flush=True);assert process.returncode==0,process.stdout+process.stderr
 assert len(list(out.glob('named-*.itf.json')))==14 and all(sha(p)==h for p,h in inputs.items());report.update(passed=True,namedScenarios=14,invariantSamples=200)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
