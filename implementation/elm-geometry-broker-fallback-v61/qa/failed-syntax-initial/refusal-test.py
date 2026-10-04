"""Authenticated typed native refusal and conservative legacy compatibility."""
import copy,hashlib,importlib.util,json,os,resource,shutil,socket,struct,sys,tempfile,threading,time,traceback
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('refusal-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=[*sorted((ROOT/'adapter').glob('*.py')),*sorted((ROOT/'qa').glob('*.py')),ROOT/'parent-inputs.json',ROOT/'SCOPE.md',ROOT/'source-lineage.json']
inputs={str(p.relative_to(ROOT)):sha(p) for p in files}
for p in files:
 d=OUT/'inputs'/p.relative_to(ROOT);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
sys.path.insert(0,str(OUT/'inputs/adapter'))
import endpoint as base
import daemon
from geometry_endpoint import GeometryEndpoint
checks=[]
def check(name,fn):
 fn();checks.append({'name':name,'passed':True})
def eq(a,b):assert a==b,(a,b)
def fails(fn,typed=False):
 try:fn()
 except base.Refused as e:
  eq(isinstance(e,base.ValidatedNativeRefusal),typed);return e
 raise AssertionError('unsafe response accepted')
B={'lifetime':'7','session':'8','frontend':'9'}
REQUEST={'protocolVersion':3,'kind':'geometry-attach','geometryProtocol':1,'binding':B,'requestId':'1'}
REFUSAL={'protocolVersion':3,'kind':'refused','reason':'request-schema'}
def transport(response=REFUSAL,raw=None,peer=False,path=False,process=False,connect=0,send=0,receive=(0,0),parse_cost=0):
 clock=[0.];calls=[]
 class Stream:
  index=0
  def __enter__(self):return self
  def __exit__(self,*a):return False
  def settimeout(self,v):assert 0<v<=2
  def connect(self,p):clock[0]+=connect
  def getsockopt(self,*a):return struct.pack('3i',os.getpid()+int(peer),os.getuid(),os.getgid())
  def sendall(self,data):calls.append(data);clock[0]+=send
  def shutdown(self,*a):pass
  def recv(self,n):
   i=self.index;self.index+=1;clock[0]+=receive[i];return (raw if raw is not None else json.dumps(response).encode()) if i==0 else b''
 obj=GeometryEndpoint.__new__(GeometryEndpoint);obj.bound=copy.deepcopy(B);obj.geometry_binding=None;obj.geometry_capabilities=None;obj.pid=os.getpid();obj.path=Path('/cpu/socket')
 count=[0]
 def paths():count[0]+=1;return (1,2,3+int(path and count[0]>1))
 def verify():
  if process:raise base.Refused('Native process identity changed')
 obj.verify_paths=paths;obj.verify_process=verify
 loads=json.loads
 def parse(*a,**kw):result=loads(*a,**kw);clock[0]+=parse_cost;return result
 with patch.object(base.socket,'socket',lambda *a:Stream()),patch.object(base.time,'monotonic',lambda:clock[0]),patch.object(base.json,'loads',parse):
  # Exercise actual broker -> geometry attach -> authenticated request parser.
  emitted=[];old=daemon.send;daemon.send=lambda f:emitted.append(f)
  try:return daemon.handle_request(obj,None,copy.deepcopy(REQUEST))
  finally:
   daemon.send=old
   assert not emitted,'refusal invented a capability or outcome'
report={'passed':False,'checks':checks,'inputs':inputs,'qaScope':scope,'nativeAcceptance':False,'fallbackImplemented':False,'scope':'Actual handler and endpoint with synthetic authenticated transport; actual V8 generic request-schema is ambiguous and remains disconnected. No unsupported fallback or native menu acceptance.'}
try:
 check('exact authenticated old-native generic refusal is typed but remains fatal',lambda:eq(fails(transport,True).reason,'request-schema'))
 for reason in ['binding-mismatch','wrong-thread','unverified-peer','unsupported-operation','unsupported-request']:
  check('no reason invents geometry unavailable '+reason,lambda r=reason:eq(fails(lambda:transport({**REFUSAL,'reason':r}),True).reason,r))
 for name,change in [('extra',{'extra':1}),('wrongversion',{'protocolVersion':True}),('reasonobject',{'reason':{}}),('empty',{'reason':''}),('long',{'reason':'x'*257}),('control',{'reason':'bad\n'}),('C1',{'reason':'bad\u0085'}),('surrogate',{'reason':'\ud800'})]:
  check('malformed refusal '+name,lambda c=change:fails(lambda:transport({**REFUSAL,**c})))
 check('missing reason is ordinary schema failure',lambda:fails(lambda:transport({'protocolVersion':3,'kind':'refused'})))
 check('duplicate reason cannot become typed',lambda:fails(lambda:transport(raw=b'{"protocolVersion":3,"kind":"refused","reason":"request-schema","reason":"unsupported-request"}'))))
 for name,kwargs in [('wrongpeer',{'peer':True}),('socketreplacement',{'path':True}),('processchanged',{'process':True}),('lateEOF',{'receive':(2,1)}),('connectsendbudget',{'connect':1.6,'send':1.6}),('lateparse',{'receive':(1,1),'parse_cost':1.1})]:
  check('authentication deadline before classification '+name,lambda k=kwargs:fails(lambda:transport(**k)))
 check('bounded Unicode reason 256 UTF16 units valid',lambda:eq(fails(lambda:transport({**REFUSAL,'reason':'x'*254+'😀'}),True).reason,'x'*254+'😀'))
 # Real AF_UNIX peer plus /proc start/executable verification, no compositor.
 def owned_socket():
  with tempfile.TemporaryDirectory(prefix='refusal-cpu-') as tmp:
   runtime=Path(tmp).resolve();runtime.chmod(0o700);directory=runtime/'hypr'/'CPU_FIXTURE';directory.mkdir(parents=True,mode=0o700);directory.parent.chmod(0o700)
   with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as server:
    server.bind(str(directory/'.socket.sock'));server.listen(1);server.settimeout(3);errors=[]
    def serve():
     try:
      with server.accept()[0] as c:
       c.settimeout(2);raw=bytearray()
       while True:
        part=c.recv(4096)
        if not part:break
        raw.extend(part)
       eq(json.loads(raw[len(b'j/elm_observe '):]),REQUEST);c.sendall(json.dumps(REFUSAL).encode())
     except Exception as e:errors.append(repr(e))
    thread=threading.Thread(target=serve);thread.start()
    obj=GeometryEndpoint(str(runtime),'CPU_FIXTURE',os.getpid(),base.start_time(os.getpid()),sha('/proc/self/exe'));obj.bound=copy.deepcopy(B)
    eq(fails(lambda:obj.geometry_attach('1'),True).reason,'request-schema');thread.join(3);assert not thread.is_alive() and not errors,errors
 check('real owned Unix socket verified process and exact request refusal',owned_socket)
 for row in json.loads((ROOT/'parent-inputs.json').read_text()):eq(sha(ROOT.parents[1]/row['source']),row['sha256'])
 check('held V56 and actual old-native source unchanged',lambda:None)
 for rel,digest in inputs.items():eq(sha(ROOT/rel),digest)
 report['passed']=True
except Exception as e:report.update(passed=False,error=repr(e),traceback=traceback.format_exc())
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks),'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True)
raise SystemExit(not report['passed'])
