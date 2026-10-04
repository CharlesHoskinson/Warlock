"""Injected scope/path failure tests; not native peer authentication acceptance."""
import hashlib,json,resource,sys,time
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('transport-'+str(time.time_ns()));OUT.mkdir()
sys.path.insert(0,str(ROOT/'adapter'));from catalog_transport import CatalogTransport
import catalog_transport as module
from endpoint import Refused
class Client:
 bound={'lifetime':'1','session':'2','frontend':'3'}
 calls=[];bad=None
 def verify_process(self):
  self.calls.append('process')
  if self.bad=='process':raise Refused('Retired process')
 def verify_paths(self):
  self.calls.append('paths')
  if self.bad=='paths':raise Refused('Replaced path')
client=Client();roots={'dataHome':'/tmp/owned-data','dataDirs':[],'cacheDir':'/tmp/owned-cache'};transport=CatalogTransport(client,roots)
snapshot={'catalogProtocol':1,'lifetime':'7','generation':'1','entries':[]};checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def refused(name,request):
 try:transport.handle(request)
 except (Refused,ValueError):check(name,True)
 else:raise AssertionError(name)
request={'protocolVersion':3,'kind':'catalog-request','binding':dict(client.bound),'requestId':'1'}
report={'passed':False,'scope':'Injected catalog transport component failures; actual native peers/GUI separate','checks':checks}
try:
 with patch.object(transport.authority,'snapshot',return_value=snapshot) as read:
  frame=transport.handle(request);check('bound catalog response correlation',frame=={**request,'kind':'application-catalog','snapshot':snapshot});check('process and path checked before and after',client.calls==['process','paths','process','paths'])
  for name,mutation in [('old binding',{'binding':{**client.bound,'frontend':'2'}}),('boolean protocol',{'protocolVersion':True}),('unknown protocol',{'protocolVersion':4}),('unknown field',{'exec':'unsafe'}),('zero request',{'requestId':'0'}),('numeric request',{'requestId':1}),('unknown route',{'kind':'launch-shell'})]:refused(name,{**request,**mutation})
  check('invalid envelopes never access catalog',read.call_count==1)
  for failure in ['process','paths']:
   client.bad=failure;refused('retired '+failure+' prevents catalog',request)
  client.bad=None;check('native scope failures never access catalog',read.call_count==1)
  with patch.object(module,'MAX_OUTPUT',16):
   transport.authority.available=True;answer=transport.handle(request);check('full envelope capacity refuses whole snapshot',answer['snapshot'] is None and not transport.authority.available)
 launch={'protocolVersion':3,'kind':'application-launch','binding':dict(client.bound),'intent':{'request':'1','lifetime':'7','generation':'1','entry':'fixture'}}
 with patch.object(transport.authority,'launch',return_value={'status':'Submitted'}) as submit:
  refused('retired binding prevents native submission',{**launch,'binding':{**client.bound,'session':'1'}})
  check('no submission before binding validation',submit.call_count==0)
  answer=transport.handle(launch);check('bound native outcome wrapped without readiness claim',answer=={'protocolVersion':3,'kind':'application-launch-outcome','binding':client.bound,'outcome':{'status':'Submitted'}})
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['inputs']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),*sorted((ROOT/'adapter').glob('*.py'))]}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
