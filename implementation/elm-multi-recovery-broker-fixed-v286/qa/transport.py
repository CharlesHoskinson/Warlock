"""Synthetic native transport for actual daemon stdio/filesystem execution.

Process/socket authentication and native geometry mutation are not simulated as
accepted. Real endpoint decoders and Journal writes remain production code.
"""
import copy,json,os,socket,sys,errno
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'adapter'))
import daemon
from geometry_endpoint import GeometryEndpoint
from recovery_journal import Journal
B={'lifetime':'71','session':'2','frontend':'3'}
CAPS={'observe':True,'effects':True,'effectProtocol':2,'operations':['maximize','restore-geometry'],'placementCapacity':256,'canonicalScene':False}
class Transport(GeometryEndpoint):
 def __init__(self,runtime,instance,mode='Committed',**unused):
  self.bound=None;self.pid=os.getpid();self.instance=instance;self.runtime=Path(runtime);self.mode=mode
 def verify_process(self):pass
 def request(self,payload):
  kind=payload['kind']
  if kind=='hello':return {'protocolVersion':3,'kind':'attached','binding':copy.deepcopy(B),'compositor':{'pid':self.pid,'instance':self.instance,'coreHash':'synthetic'},'capabilities':{'observe':True,'effects':True,'minimizedState':True,'effectProtocol':1,'operations':['minimize','restore','activate'],'canonicalScene':False,'taskbarProjectionProtocol':1,'effectInvalidationProtocol':1}}
  if kind=='geometry-attach':return {'protocolVersion':3,'kind':'geometry-attached','geometryProtocol':1,'binding':copy.deepcopy(B),'requestId':payload['requestId'],'capabilities':copy.deepcopy(CAPS)}
  if kind=='window-effect':
   path=Journal.namespace_path(self.runtime,self.instance,B['lifetime'])/'ledger-v4.json'
   pending=json.loads(path.read_text())['latest']
   assert pending=={'schema':2,'effectProtocol':payload['effectProtocol'],'binding':B,'intent':payload['intent'],'status':'Pending'}
   with (self.runtime/'submitted.jsonl').open('a') as stream:stream.write(json.dumps({'request':payload,'durableBeforeSubmit':pending})+'\n')
   if self.mode=='transport-failure':raise daemon.Refused('Synthetic transport interrupted')
   status=self.mode if self.mode in ['Committed','Refused','Unknown'] else 'Committed'
   response={'protocolVersion':3,'kind':'effect-outcome','effectProtocol':payload['effectProtocol'],'binding':copy.deepcopy(B),'intent':copy.deepcopy(payload['intent']),'status':status,'reason':'fixture','revision':'13','outputGeneration':'14'}
   if self.mode=='wrong-receipt':response['intent']['request']='99'
   if self.mode=='settlement-read-failure':path.chmod(0o644)
   return response
  raise AssertionError(kind)
def events(client):
 a,b=socket.socketpair();held.append(b);return a
held=[];daemon.Endpoint=Transport;daemon.event_socket=events
class Catalog:
 def __init__(self,*args):pass
 def handle(self,request):raise AssertionError('Catalog outside this fixture')
daemon.CatalogTransport=Catalog
# Actual errno stimuli are injected only at fsync; other paths use real files.
mode=json.loads(Path(sys.argv[1]).read_text())['mode']
if mode in ['full-before-submit','directory-fsync-failure']:
 real=daemon.os.fsync
 def fsync(fd):
  import stat
  if mode=='full-before-submit' or stat.S_ISDIR(os.fstat(fd).st_mode):
   raise OSError(errno.ENOSPC if mode=='full-before-submit' else errno.EIO,'QA fsync stimulus')
  return real(fd)
 # Journal migration is pre-provisioned by the fixture, so this targets begin.
 daemon.os.fsync=fsync
try:raise SystemExit(daemon.run())
finally:
 for s in held:s.close()
