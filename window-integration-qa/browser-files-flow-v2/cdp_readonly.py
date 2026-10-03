"""Private inherited CDP pipe. Only exact frozen read-only expressions accepted."""
import json,os,select,time
DOM_QUERY="""JSON.stringify((()=>{const d=document.getElementById('draft');const r=d.getBoundingClientRect();return {url:location.href,title:document.title,value:d.value,selection:[d.selectionStart,d.selectionEnd],active:document.activeElement.id,rect:[r.x,r.y,r.width,r.height],inner:[innerWidth,innerHeight],outer:[outerWidth,outerHeight],screen:[screenX,screenY],ratio:devicePixelRatio,clicks:window.qaClicks,events:window.qaEvents};})())"""
ALLOWED={
 'Browser.getVersion':lambda p:not p,
 'Target.getTargets':lambda p:not p,
 'Target.attachToTarget':lambda p:set(p)=={'targetId','flatten'} and isinstance(p['targetId'],str) and p['flatten'] is True,
 'Runtime.evaluate':lambda p:p=={'expression':DOM_QUERY,'returnByValue':True},
 'Browser.close':lambda p:not p,
}
class TargetNotReady(Exception):pass
class DOMNotReady(Exception):pass
class ReadOnlyPipe:
 def __init__(self,write_fd,read_fd):self.write=write_fd;self.read=read_fd;self.sequence=0;self.buffer=b'';self.events=[];self.acks=[]
 def request(self,method,params=None,session=None,timeout=8):
  params=params or {}
  if method not in ALLOWED or not ALLOWED[method](params):raise RuntimeError('Refused CDP mutation or unfrozen query:'+method)
  if method=='Runtime.evaluate' and not session:raise RuntimeError('DOM query requires exact attached page session')
  self.sequence+=1;row={'id':self.sequence,'method':method,'params':params}
  if session:row['sessionId']=session
  payload=json.dumps(row,separators=(',',':')).encode()+b'\0'
  while payload:
   written=os.write(self.write,payload);payload=payload[written:]
  deadline=time.monotonic()+timeout
  while time.monotonic()<deadline:
   if b'\0' not in self.buffer:
    ready=select.select([self.read],[],[],max(0,deadline-time.monotonic()))[0]
    if not ready:break
    data=os.read(self.read,65536)
    if not data:raise EOFError('CDP pipe closed before reply')
    self.buffer+=data
    if len(self.buffer)>4*1024*1024:raise RuntimeError('CDP frame exceeds bounded buffer')
    continue
   raw,self.buffer=self.buffer.split(b'\0',1)
   if not raw:continue
   reply=json.loads(raw)
   if reply.get('id')!=row['id']:
    if 'id' in reply:raise RuntimeError('Unexpected CDP reply identity')
    self.events.append(reply)
    if len(self.events)>2048:raise RuntimeError('CDP event bound reached')
    continue
   if reply.get('sessionId')!=session and (session or 'sessionId' in reply):raise RuntimeError('CDP session mismatch')
   if 'error' in reply:raise RuntimeError('CDP error:'+str(reply['error']))
   self.acks.append({'method':method,'id':row['id'],'sessionId':session});return reply.get('result',{})
  raise TimeoutError('No bounded actual CDP reply:'+method)
 def attach(self,url):
  rows=self.request('Target.getTargets')['targetInfos']
  matching=[r for r in rows if r['type']=='page' and r['url']==url]
  if not matching:raise TargetNotReady('Exact local page not ready')
  if len(matching)!=1:raise RuntimeError('Need one exact owned local page target')
  target=matching[0];session=self.request('Target.attachToTarget',{'targetId':target['targetId'],'flatten':True})['sessionId'];return target,session
 def dom(self,session):
  result=self.request('Runtime.evaluate',{'expression':DOM_QUERY,'returnByValue':True},session)
  if 'exceptionDetails' in result:raise DOMNotReady('Read-only DOM query threw')
  return json.loads(result['result']['value'])
 def close_fds(self):
  for fd in (self.write,self.read):
   try:os.close(fd)
   except OSError:pass
