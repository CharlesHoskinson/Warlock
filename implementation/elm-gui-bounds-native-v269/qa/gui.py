import json,os,socket,struct,subprocess,time
from pathlib import Path
from inspection import Collector
class Gui:
 def __init__(self,session,host,process,log,pointer,physical,scale,check,wait,output):
  self.session=session;self.host=host;self.process=process;self.log=log;self.pointer=pointer;self.physical=physical;self.scale=scale;self.check=check;self.wait=wait;self.output=output;self.collector=Collector(physical[0]//scale)
  self.parent=next(row for _,row in session.host.processes if row['name']=='weston');self.socket=session.host.runtime/'weston-host';self.socket_identity=host.original.socket_identity(self.socket,session.host.runtime)
  with socket.socket(socket.AF_UNIX) as probe:
   probe.settimeout(2);probe.connect(str(self.socket));pid,uid,gid=struct.unpack('3i',probe.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
  check('GUI:verifiedPhysicalParent',pid==self.parent['pid'] and uid==os.getuid() and host.original.same_process(self.parent))
 def text(self):
  raw=self.log.read_bytes()
  if len(raw)>16*1024*1024:raise RuntimeError('GUI journal bound')
  return raw.decode(errors='replace')
 def frames(self,prefix):return [json.loads(line[len(prefix):]) for line in self.text().splitlines() if line.startswith(prefix)]
 def projection(self):return self.collector.read(self.text())
 def coherent(self):
  p=self.projection();return p if p and p['phase']=='Coherent' else None
 def effects(self):return [r for r in self.frames('frontend-request: ') if r['kind']=='window-effect']
 def click(self,item,button,deadline):
  assert item['visible'],'GUI control clipped';x,y=[round(v*self.scale) for v in item['point']];assert 0<x<self.physical[0] and 0<y<self.physical[1]
  self.session.guard();assert self.process.poll() is None and self.host.original.same_process(self.parent) and self.socket_identity==self.host.original.socket_identity(self.socket,self.session.host.runtime)
  remaining=deadline-time.monotonic();assert remaining>0
  p=subprocess.run([str(self.pointer)],input=f'motion {x} {y}\npress {button}\nrelease {button}\nquit\n',text=True,capture_output=True,env=dict(self.session.host.env,ELM_PARENT_INPUT_QA='1'),cwd=self.session.host.runtime,timeout=min(3,remaining));acks=[json.loads(line) for line in p.stdout.splitlines()]
  self.check('GUI:physicalParentClick',p.returncode==0 and len(acks)==4 and acks[0].get('ready') is True and all(r.get('accepted') is True for r in acks[1:]),logicalPoint=item['point'],physicalPoint=[x,y],button=button,acks=acks);assert time.monotonic()<deadline
 def open(self,incarnation,deadline):
  before=self.effects();p=self.wait(lambda:self.coherent() if self.coherent() and len(self.coherent()['groups'])==1 and not self.coherent()['groups'][0]['disabled'] else None,deadline)
  self.click(p['groups'][0],273,deadline)
  menu=self.wait(lambda:self.coherent()['menu'] if self.coherent() and self.coherent()['menu'] else None,deadline)
  self.check('GUI:exactNativeTargetMenu',menu['incarnation']==incarnation and self.effects()==before,menu=menu)
  return menu
 def action(self,menu,label):return next(r for r in menu['actions'] if r['label']==label)
 def close(self,menu,deadline):
  self.click(menu['close'],272,deadline);self.wait(lambda:self.coherent() if self.coherent() and self.coherent()['menu'] is None else None,deadline)
 def apply(self,incarnation,label,operation,deadline):
  menu=self.open(incarnation,deadline);item=self.action(menu,label);self.check('GUI:'+label+':enabled',not item['disabled'] and item['enabled']);before=len(self.effects());lease=self.projection()['lease'];self.click(item,272,deadline)
  issued=self.wait(lambda:self.effects()[-1] if len(self.effects())==before+1 else None,deadline);intent=issued['intent'];self.check('GUI:'+label+':exactIssuedNamespace',issued['effectProtocol']==2 and intent['operation']==operation and intent['incarnation']==incarnation,issued=issued)
  receipt=self.wait(lambda:next((r for r in self.frames('backend-frame: ') if r.get('kind')=='effect-outcome' and r.get('binding')==issued['binding'] and r.get('intent')==intent and r.get('effectProtocol')==2),None),deadline)
  self.check('GUI:'+label+':actualCorrelatedCommit',receipt['status']=='Committed',receipt=receipt)
  self.wait(lambda:self.coherent() if self.coherent() and self.coherent()['menu'] is None and self.coherent()['outstanding']==0 else None,deadline)
  lines=self.text().splitlines();dispatch=next(i for i,l in enumerate(lines) if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])==issued)
  self.check('GUI:'+label+':popupRetiredBeforeEffect',any(i<dispatch and l.startswith('surface-popup-closed: lease='+lease) for i,l in enumerate(lines)))
  self.check('GUI:'+label+':oneIntent',len(self.effects())==before+1)
  return receipt
 def pixels(self,name,native,buffer,native_read,latest_buffer,deadline):
  serial=buffer['ackedSerial'];rgb=[0x28^(serial&63),0x71^((serial>>6)&63),0xc8^((serial>>12)&63)];x,y=native['at'];w,h=native['size'];points=[(round((x+w//2)*self.scale),round((y+h//2)*self.scale)),(round((x+20)*self.scale),round(max(60,y+20)*self.scale)),(round((x+w-21)*self.scale),round((y+h-21)*self.scale))];attempts=[]
  def capture():
   assert native_read() is not None and all(native_read()[k]==native[k] for k in ['address','at','size','fullscreen','fullscreenClient']) and latest_buffer()==buffer,'GUI pixel generation changed'
   p=self.output/(name+'-pixels-'+str(len(attempts))+'.png');remaining=deadline-time.monotonic();assert remaining>0
   result=subprocess.run(['/usr/bin/grim',str(p)],capture_output=True,env=self.session.env,timeout=min(5,remaining));assert result.returncode==0,result.stderr
   png=p.read_bytes();assert png[:8]==bytes.fromhex('89504e470d0a1a0a') and struct.unpack('>II',png[16:24])==tuple(self.physical)
   remaining=deadline-time.monotonic();assert remaining>0;decoded=subprocess.run(['/usr/bin/magick',str(p),'-depth','8','rgb:-'],capture_output=True,timeout=min(5,remaining));assert decoded.returncode==0 and len(decoded.stdout)==self.physical[0]*self.physical[1]*3
   samples=[]
   for px,py in points:
    assert 0<=px<self.physical[0] and 0<=py<self.physical[1];offset=(py*self.physical[0]+px)*3;samples.append(list(decoded.stdout[offset:offset+3]))
   assert all(native_read()[k]==native[k] for k in ['address','at','size','fullscreen','fullscreenClient']) and latest_buffer()==buffer,'GUI pixel generation changed during capture'
   row={'path':str(p),'sha256':self.host.digest(p),'points':points,'samples':samples,'expectedRGB':rgb,'serial':serial};attempts.append(row)
   return row if all(v==rgb for v in samples) else None
  matched=self.wait(capture,deadline);self.check(name+':GUIactualSerialRGBPixels',bool(matched),capture=matched,attempts=attempts)
