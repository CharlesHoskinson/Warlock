"""Retain wrong historical build entry-point attempt without modifying evidence."""
import hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v141/qa/build-1791400298601984305/report.json';d=json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not d['passed'] and d['commands'][-1]['name']=='host-build' and d['commands'][-1]['exitCode']==1
log=p.parent/'host-build.stderr';assert 'undefined reference' in log.read_text() and 'warlock_policy_driver_new' in log.read_text()
out=pathlib.Path(__file__).with_name('gui141-old-build-entry-failure.json');assert not out.exists()
out.write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','failedScope':'f8ab1731bffb4df9b057335dc2274947','report':str(p),'reportSHA256':sha(p),'linkerStderr':str(log),'linkerStderrSHA256':sha(log),'failure':'Historical qa/build.py lacks controlled policy/visual/router linker objects; changed C compilation passed.','correction':'Invoke unchanged inherited qa/build-controlled-host.py full119 entry point. No source/oracle/deadline changes.','nativeLaunchedFromFailedBuild':False,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
print(out)
