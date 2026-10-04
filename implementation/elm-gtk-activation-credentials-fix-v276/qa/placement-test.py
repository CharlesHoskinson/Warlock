"""Actual Lua parser + independent exact-target API boundary doubles; no compositor."""
import copy,hashlib,json,resource,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from placement import place
from journal import Refused
ROOT=Path(__file__).resolve().parent;OUT=ROOT/('placement-'+str(time.time_ns()));OUT.mkdir();checks=[];report={'passed':False,'nativeAcceptance':False,'actualLuaWithNativeBoundaryDoubles':True,'checks':checks}
lua='''hl={dsp={window={}}}
local function selected(t) assert(t.window=="address:0x123") end
hl.dsp.window.float=function(t) selected(t);assert(t.action=="enable");return function() return {ok=true} end end
hl.dsp.window.resize=function(t) selected(t);assert(t.x==320 and t.y==180 and t.relative==false);return function() return {ok=true} end end
hl.dsp.window.move=function(t) selected(t);assert(t.x==40 and t.y==70 and t.relative==false);return function() return {ok=true} end end
hl.dispatch=function(d) return d() end
'''
class Session:
 def __init__(self,mode,folder):self.mode=mode;self.folder=folder;self.calls=[];self.native={'address':'0x123','pid':123,'title':'owned-fixture','floating':False,'size':[360,240],'at':[100,100]}
 def data(self,*args):return [copy.deepcopy(self.native)]
 def ctl(self,kind,code):
  assert kind=='eval';self.calls.append(code);index=len(self.calls);result=subprocess.run(['/usr/bin/lua','-e',lua+code+';print("ok")'],capture_output=True,timeout=1);(self.folder/(str(index)+'.stdout')).write_bytes(result.stdout);(self.folder/(str(index)+'.stderr')).write_bytes(result.stderr);assert result.returncode==0
  if self.mode=='refused':return 'refused'
  if self.mode=='stale':self.native['pid']=124
  if '.float(' in code:self.native['floating']=True
  if '.resize(' in code:self.native['size']=[320,180]
  if '.move(' in code:self.native['at']=[40,70]
  return result.stdout.decode()
try:
 for name in ('valid','stale','refused','bool-coordinate','expired'):
  folder=OUT/name;folder.mkdir();session=Session(name,folder);binding={'native':copy.deepcopy(session.native)};refused=False
  try:receipt=place(session,binding,True if name=='bool-coordinate' else 40,70,320,180,time.monotonic()+(-1 if name=='expired' else 2))
  except Refused:refused=True
  assert refused is (name!='valid'),name
  assert len(session.calls)==(3 if name=='valid' else 1 if name in ('stale','refused') else 0),name
  checks.append({'name':name,'passed':True,'commands':session.calls,'refused':refused})
 legacy=subprocess.run(['/usr/bin/lua','-e','return hl.dispatch(setfloating address:0x123)'],capture_output=True,timeout=1);assert legacy.returncode!=0;checks.append({'name':'actual legacy syntax rejected by Lua parser','passed':True,'stderr':legacy.stderr.decode()})
 report['passed']=True
finally:
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'placement.py',Path('/usr/bin/lua'),ROOT.parents[1]/'maximized-stack-v1/native-core-v2/src/config/lua/bindings/LuaBindingsDispatchers.cpp']};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
