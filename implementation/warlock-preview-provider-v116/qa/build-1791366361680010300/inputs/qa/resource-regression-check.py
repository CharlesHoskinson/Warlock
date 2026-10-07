"""Current original capture/issuer/resource regressions on stable GUI106 source."""
import hashlib,json,pathlib,resource,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('resource-regression-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['capture-resource-model-check.py','capture-intent-model-check-v3.py','imported-controlled-c-check-v3.py','capture-resource-fd-check.py']
report={'passed':False,'inputs':{str(p.relative_to(root)):sha(p) for p in (root/'native').glob('*') if p.is_file()},'runnerInputs':{n:sha(root/'qa'/n) for n in names},'reports':{},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 for name in names:
  p=subprocess.run(['/usr/bin/python3','-B',str(root/'qa'/name)],capture_output=True,text=True,timeout=1200)
  (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
  report['commands'].append({'runner':name,'exitCode':p.returncode});print(name,p.returncode,flush=True)
  assert p.returncode==0,(name,p.stderr,p.stdout[-2500:])
  result=json.loads(p.stdout.splitlines()[-1]);path=pathlib.Path(result['report']);data=json.loads(path.read_text())
  assert result['passed'] and data['passed'];report['reports'][name]={'path':str(path),'sha256':sha(path)}
 assert all(sha(root/rel)==v for rel,v in report['inputs'].items()) and all(sha(root/'qa'/n)==v for n,v in report['runnerInputs'].items())
 report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2000]}),flush=True);sys.exit(not report['passed'])
