"""Actual current broker closed-profile acquisition and inert runner import; no GUI."""
import ast,hashlib,importlib.util,json,os,pathlib,resource,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('acquisition-test-'+str(time.time_ns()));OUT.mkdir(mode=0o700);(OUT/'inputs').mkdir();report={'passed':False,'nativeAcceptance':False,'checks':[]}
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
r=load('closed_relay',ROOT/'relay/qa/relay.py')
def file(path,packet):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as stream:json.dump(packet,stream)
def check(name,value):assert value,name;report['checks'].append({'name':name,'passed':True})
def reject(packet):
 try:r.command_for(packet,ROOT.parents[1])
 except (r.RelayFailure,ValueError,OSError):return True
 return False
try:
 for p in [ROOT/'relay/qa/relay.py',ROOT/'receipt/qa/wrapper.py',ROOT/'qa/native.py',pathlib.Path(__file__)]:
  (OUT/'inputs'/p.name).write_bytes(p.read_bytes())
 private=OUT/'private';private.mkdir(mode=0o700);authority=OUT/'authority.json';file(authority,{'runtime':str(private),'instance':'closed123'})
 packet={'profile':'broker','authorityConfig':str(authority),'controlDirectory':str(private),'runtime':str(private),'instance':'closed123'}
 command=r.command_for(packet,ROOT.parents[1]);check('actual exact521 captured broker command no override',command==['/usr/bin/python3','-B',str(ROOT.parent/'elm-stable-surface-publication-v521/qa/build-1791138800386580258/inputs/adapter/daemon.py'),str(authority)])
 for name,changed in [('arbitrary-profile',dict(packet,profile='shell')),('command-injection',dict(packet,command=['sh','-c','anything'])),('wrong-runtime',dict(packet,runtime='/tmp')),('wrong-instance',dict(packet,instance='other')),('receipt-field-on-broker',dict(packet,receiptConfig=str(authority)))]:check('reject-'+name,reject(changed))
 receipt=OUT/'receipt.json';file(receipt,{'authorityConfig':str(authority),'controlDirectory':str(private),'incarnation':'1','effectOperation':'restore-geometry','selectorOrdinal':2});closed={'profile':'receipt','receiptConfig':str(receipt),'controlDirectory':str(private),'runtime':str(private),'instance':'closed123'}
 check('closed receipt entrypoint not arbitrary command',r.command_for(closed,ROOT.parents[1])==['/usr/bin/python3','-B',str(ROOT/'receipt/qa/broker-entrypoint.py'),str(receipt)])
 # Import defines root-only run but does not call host/session/display constructors.
 import subprocess
 from unittest.mock import patch
 with patch.object(subprocess,'Popen',side_effect=AssertionError('inert import started process')):
  module=load('root_only_full_gtk_runner',ROOT/'qa/native.py');check('actual full runner import starts no process',callable(module.run))
 report['passed']=True
except BaseException as error:report['error']=repr(error)
report['inputs']={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'relay/qa/relay.py',ROOT/'receipt/qa/wrapper.py',ROOT/'qa/native.py',pathlib.Path(__file__)]};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(OUT/'report.json'),'passed':report['passed'],'checks':len(report['checks']),'error':report.get('error')}));raise SystemExit(0 if report['passed'] else 1)
