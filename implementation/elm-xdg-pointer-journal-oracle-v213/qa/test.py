import copy,hashlib,importlib.util,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('pointer_oracle',s/'oracle.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=[dict(event='pointer-button',ownedSurface=True,pid=123,sequence=11+i,button=272,buttonState=1-i,pointerSerial=99+i,pointerTime=200,local=[16.5,24.25],localFixed=[4224,6208]) for i in range(2)]
checks=[]
def call(rows,**kw):
 params=dict(pid=123,after_sequence=10,button=272,expected_local=[16.5,24.25]);params.update(kw);return m.validate_pair(rows,**params)
assert call(base)['physicalHardwareAccepted'] is False;checks.append('exact fresh fractional surface coordinates')
changes=[('pid',124),('pid',123.0),('sequence',True),('ownedSurface',1),('button',273),('buttonState',0),('localFixed',[4224.0,6208]),('local',[float('nan'),24.25]),('local',[16.5001,24.25]),('pointerSerial',-1),('pointerTime',False),('event','pointer-motion')]
for key,value in changes:
 rows=copy.deepcopy(base);rows[0][key]=value
 try:call(rows)
 except m.Refused:checks.append('reject '+key+' '+repr(value))
 else:raise AssertionError(key)
for name,rows,kw in [('stale',base,{'after_sequence':11}),('reversed',list(reversed(base)),{}),('missing release',base[:1],{}),('surface vs buffer scale',base,{'expected_local':[33,48.5]}),('bool expected point',base,{'expected_local':[True,24.25]}),('huge integer expected point',base,{'expected_local':[10**400,24.25]})]:
 try:call(rows,**kw)
 except m.Refused:checks.append('reject '+name)
 else:raise AssertionError(name)
out=s/'qa'/('test-'+str(time.time_ns()));out.mkdir();d={'passed':True,'checks':checks,'nativeAcceptance':False,'scope':'Synthetic decoder controls; no pointer injection, native recipient or hardware qualification','inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [s/'oracle.py',Path(__file__),s/'REQUIREMENTS.md']}};(out/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'checks':len(checks)}))
