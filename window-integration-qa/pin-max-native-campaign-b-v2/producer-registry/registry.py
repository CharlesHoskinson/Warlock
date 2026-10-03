"""Draft exact private QA producer registry. Not a general process launcher."""
from pathlib import Path
import hashlib,json,os,re,stat,time,subprocess

FIXTURE=Path('/home/hoskinson/window-integration-qa/qt-modal-private-v9/build-v7/qt-window-modal-fixture')
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
KEYBOARD=Path('/home/hoskinson/window-behavior-spec/pin-lifetime-v3/keyboard-chords/physical-keyboard')
def require(value,message):
 if value is not True:raise ValueError(message)
def exact(a,b):
 if type(a)is not type(b):return False
 if type(a)is dict:return a.keys()==b.keys()and all(exact(a[k],b[k])for k in a)
 if type(a)is list:return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
 return a==b
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def lifetime(pid):
 require(type(pid)is int and pid>0,'typed producer PID')
 raw=Path('/proc/'+str(pid)+'/stat').read_text();parts=raw.rsplit(')',1)[1].split()
 require(len(parts)>=20 and re.fullmatch(r'[1-9][0-9]*',parts[19])is not None,'one complete process identity read')
 return dict(pid=pid,start=parts[19],pgid=int(parts[2]))

class Registry:
 def __init__(self,session,output,frozen):
  self.session=session;self.output=Path(output);self.frozen=frozen;self.rows=[];self.sealed=False
 def persist(self):
  target=self.output/'producer-registry.json';temporary=self.output/'producer-registry.new'
  require(not target.is_symlink(),'no registry alias')
  with temporary.open('x')as f:
   json.dump(dict(rows=self.rows,sealed=self.sealed),f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
  temporary.chmod(0o600);temporary.replace(target)
  fd=os.open(self.output,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:os.fsync(fd)
  finally:os.close(fd)
 def source(self,path):
  require(not path.is_symlink()and path.is_file(),'literal exact producer source')
  key=str(path);mode=stat.S_IMODE(path.stat().st_mode);digest=sha(path)
  require(type(self.frozen['inputModes'][key])is int and mode==self.frozen['inputModes'][key]and digest==self.frozen['inputs'][key],'selected frozen producer bytes/modes')
  return dict(path=key,sha256=digest,mode=mode)
 def launch(self,case,kind,ordinal,*,route=None,actor_output=None,width=1600,height=1000,output_name=None):
  require(not self.sealed and len(self.rows)<256 and type(case)is str and re.fullmatch(r'B(?:0[1-9]|1[0-2])',case)is not None,'fixed bounded reviewed first-phase B01–B12 case; B13–B24 not executable')
  require(type(ordinal)is int and 1<=ordinal<=64 and kind in {'qt','pointer','key'},'fixed bounded producer role')
  name='pin-'+case.lower()+'-'+kind+'-'+str(ordinal)
  require(not any(r['name']==name for r in self.rows),'no producer retry/replacement')
  if kind=='qt':
   p=Path(actor_output);require(p.parent==self.output/'actors'/case and p.name=='qt-'+str(ordinal)and p.resolve()==p and p.is_dir(),'fixed owned separate actor output')
   argv=[str(FIXTURE),str(p)]
  elif kind=='pointer':
   require(type(width)is int and width==1600 and type(height)is int and height==1000,'known actual private desktop extents')
   argv=[str(POINTER),str(width),str(height)]
  elif kind=='key':
   require(type(route)is str and route=='super-p','original physical chord source')
   argv=[str(KEYBOARD),'--chord',route]
  self.session.guard();source=self.source(Path(argv[0]));env=dict(self.session.env)
  env.pop('DISPLAY',None)
  if kind=='qt':env.update(QT_QPA_PLATFORM='wayland',QT_QPA_PLATFORMTHEME='',QT_STYLE_OVERRIDE='Fusion',QT_NO_XDG_DESKTOP_PORTAL='1')
  if kind=='key':env.update(WINDOW_QA_COMPOSITOR_PID=str(self.session.evidence['compositorPID']),WINDOW_QA_COMPOSITOR_START=self.session.evidence['compositorStart'])
  if kind=='pointer':
   path=self.output/(name+'.log');log=path.open('x');path.chmod(0o600)
   proc=subprocess.Popen(argv,env=env,stdin=subprocess.PIPE,stdout=log,stderr=log,text=True,start_new_session=True)
   registered=lifetime(proc.pid);registered.update(name=name,command=argv,log=str(path));self.session.host.processes.append((proc,registered));self.session.host.logs.append(log)
  else:proc=self.session.host.launch(name,argv,env)
  matching=[row for p,row in self.session.host.processes if p is proc]
  require(len(matching)==1,'original host exact Popen registration')
  registered=matching[0];require(type(registered['pid'])is int and registered['pid']==proc.pid and type(registered['pgid'])is int and registered['pgid']==proc.pid and type(registered['start'])is str and registered['start'].isdigit(),'exact original selected lifetime/group')
  row=dict(name=name,case=case,kind=kind,ordinal=ordinal,argv=argv,source=source,registered=dict(registered),normalTerminal=None,forced=False)
  self.rows.append(row);self.persist();return proc,row
 def terminal(self,proc,row,*,timeout,receipt):
  # Caller must first perform genuine normal protocol termination (Qt quit,
  # pointer EOF/releases, or finite keyboard/capture completion). No signals here.
  require(type(timeout)in {int,float}and not isinstance(timeout,bool)and timeout in {2,4,5,8},'declared unchanged operation deadline')
  require(type(receipt)is dict,'actual typed producer completion receipt')
  if row['kind']=='qt':require(receipt.get('kind')=='qt-quit'and type(receipt.get('commandEpoch'))is int and receipt['commandEpoch']>0 and receipt.get('commandHandled')is True and type(receipt.get('pid'))is int and receipt['pid']==proc.pid,'actual same-epoch Qt quit')
  elif row['kind']=='pointer':require(receipt.get('kind')=='pointer-eof'and receipt.get('allButtonsReleased')is True and receipt.get('stdinClosed')is True,'actual releases and EOF')
  elif row['kind']=='key':require(receipt.get('kind')=='physical-chord'and exact(receipt.get('route'),row['argv'][2])and type(receipt.get('delivery'))is dict and receipt['delivery'].get('observedPressAndRelease')is True and receipt['delivery'].get('sameCapturedOwner')is True,'actual source-bound key delivery')
  self.session.guard();proc.wait(timeout=timeout)
  observation=dict(pid=proc.pid,returncode=proc.returncode,gone=not Path('/proc/'+str(proc.pid)).exists(),receipt=receipt,sourceAfter=self.source(Path(row['argv'][0])))
  row['normalTerminal']=observation;self.persist()
  require(type(proc.returncode)is int and proc.returncode==0 and observation['gone']is True and exact(observation['sourceAfter'],row['source'])and row['forced']is False,'normal exact producer terminal; uncertainty is not accepted')
 def seal_before_host_close(self):
  self.session.guard()
  require(not self.sealed and all(type(r['normalTerminal'])is dict and r['normalTerminal']['returncode']==0 and r['normalTerminal']['gone']is True and r['forced']is False for r in self.rows),'all declared producers genuinely closed before host stop')
  expected=[r['name']for r in self.rows]
  actual=[r['name']for p,r in self.session.host.processes]
  require(actual==['privateBus','weston','hyprland']+expected,'complete registry, no undeclared process or reordered role')
  for p,r in self.session.host.processes[3:]:
   require(type(p.poll())is int and p.returncode==0 and not Path('/proc/'+str(p.pid)).exists(),'current before-stop actual terminal witness')
  self.sealed=True;self.persist();return dict(rows=self.rows,registeredOrder=actual,requiredStopOrder=list(reversed(actual)),clientFirst=True)
