"""Actual owned helper process CPU fault tests; fixture frames are NOT native admission."""
from pathlib import Path
from types import SimpleNamespace
import hashlib,importlib.util,json,os,resource,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'qa'/('lifecycle-'+str(time.time_ns()));out.mkdir()
spec=importlib.util.spec_from_file_location('owned_pointer',ROOT/'qa/pointer.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
original_verify=helper.verify_peer
helper.verify_peer=lambda *args:{'cpuFixturePeer':True,'nativeAdmission':False}
original=SimpleNamespace(process=lambda pid:{'pid':pid,'startTime':Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]})
session=SimpleNamespace(guard=lambda:None,host=SimpleNamespace(env={},runtime=out,processes=[]))
host=SimpleNamespace(original=original)
checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
cases={
'normal':('print(json.dumps({"ready":True,"scope":"parent-notify-only"}),flush=True)\nfor i,c in enumerate(commands,1):print(json.dumps({"sequence":i,"accepted":True,"scope":"parent-notify-only"}),flush=True)',True),
'readyInteger':('print(\'{"ready":1,"scope":"parent-notify-only"}\',flush=True)\nfor i,c in enumerate(commands,1):print(json.dumps({"sequence":i,"accepted":True,"scope":"parent-notify-only"}),flush=True)',False),
'acceptedInteger':('print(json.dumps({"ready":True,"scope":"parent-notify-only"}),flush=True)\nfor i,c in enumerate(commands,1):print(json.dumps({"sequence":i,"accepted":1,"scope":"parent-notify-only"}),flush=True)',False),
'floatSequence':('print(json.dumps({"ready":True,"scope":"parent-notify-only"}),flush=True)\nfor i,c in enumerate(commands,1):print(json.dumps({"sequence":float(i),"accepted":True,"scope":"parent-notify-only"}),flush=True)',False),
'duplicateKey':('print(\'{"ready":false,"ready":true,"scope":"parent-notify-only"}\',flush=True)\nfor i,c in enumerate(commands,1):print(json.dumps({"sequence":i,"accepted":True,"scope":"parent-notify-only"}),flush=True)',False),
'nonfinite':('print(\'{"ready":NaN,"scope":"parent-notify-only"}\',flush=True)',False),
'partial':('sys.stdout.write(\'{"ready":true\');sys.stdout.flush()',False),
'nonzero':('print("partial-before-exit",flush=True);sys.stderr.write("owned failure\\n");sys.exit(6)',False),
'stdoutBound':('print("x"*5000,flush=True)',False),
'stderrBound':('sys.stderr.write("x"*5000);print(json.dumps({"ready":True,"scope":"parent-notify-only"}),flush=True)\nfor i,c in enumerate(commands,1):print(json.dumps({"sequence":i,"accepted":True,"scope":"parent-notify-only"}),flush=True)',False),
'hang':('print(json.dumps({"ready":True,"scope":"parent-notify-only"}),flush=True);time.sleep(10)',False),
}
for name,(body,valid) in cases.items():
 fixture=out/(name+'.py')
 # Child commands are bounded and local. They open no compositor/socket.
 fixture.write_text('#!/usr/bin/python3\nimport sys,json,time\ncommands=[line.strip() for line in sys.stdin if line.strip()!="quit"]\n'+body+'\n');fixture.chmod(0o700)
 evidence=out/name
 started=time.monotonic();record=None
 try:record=helper.send(session,host,{},None,fixture,['press 272','release 272'],time.monotonic()+(.15 if name=='hang' else 3),evidence_dir=evidence);accepted=True
 except (ValueError,Exception):accepted=False
 check(name+':acceptance',accepted is valid)
 paths=list(evidence.glob('attempt-*/record.json'));check(name+':persistedRecord',len(paths)==1)
 captured=json.loads(paths[0].read_text());check(name+':registeredOwnedProcess',captured['registered'] is True and type(captured['process']['pid']) is int)
 check(name+':stdoutRetained',Path(captured['stdout']).is_file());check(name+':stderrRetained',Path(captured['stderr']).is_file())
 check(name+':exitRecorded',type(captured['exitCode']) is int)
 if not valid:
  check(name+':failureNotAccepted',captured['probeAccepted'] is False and bool(captured['error']))
  check(name+':explicitReleaseAttemptRetained',type(captured.get('releaseAttempt')) is dict and 'explicitReleaseAdmission' in captured['releaseAttempt'])
 if name=='hang':
  check('hang:boundedWaitAndCleanup',time.monotonic()-started<1.5)
  check('hang:timeoutAndFallbackSeparate',captured['timeout'] is True and 'NOT confirmed' in captured['destructorReleaseFallback'] and captured['releaseAttempt']['scope'].startswith('release-only'))
check('allOwnedProcessesTerminal',all(p.poll() is not None for p,row in session.host.processes))
# Decoder direct boundary controls supplement actual-process fault cases.
for name,raw in [('boolsequence',b'{"ready":true,"scope":"parent-notify-only"}\n{"sequence":true,"accepted":true,"scope":"parent-notify-only"}\n'),('extra',b'{"ready":true,"scope":"parent-notify-only","extra":0}\n'),('negative',b'{"ready":true,"scope":"parent-notify-only"}\n{"sequence":-1,"accepted":true,"scope":"parent-notify-only"}\n')]:
 try:helper.receipts(raw,1);refused=False
 except ValueError:refused=True
 check(name+':strictRejected',refused)
report={'passed':True,'checks':checks,'scope':'CPU actual helper subprocess lifecycle only; synthetic receipt bytes; no native admission or input evidence','nativeAdmission':False,'inputs':{str(ROOT/'qa/pointer.py'):hashlib.sha256((ROOT/'qa/pointer.py').read_bytes()).hexdigest(),str(Path(__file__)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},'processes':[{'pid':r['pid'],'exitCode':p.returncode} for p,r in session.host.processes]}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks),'report':str(out/'report.json')}))
