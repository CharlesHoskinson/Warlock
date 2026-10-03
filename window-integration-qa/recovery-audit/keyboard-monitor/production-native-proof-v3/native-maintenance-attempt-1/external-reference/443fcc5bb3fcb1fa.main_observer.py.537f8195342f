"""Original-session observations only. No dispatch, input or restoration API."""
import base64,hashlib,json,os,socket,stat,subprocess
from pathlib import Path
import lifecycle_preservation as p
def sha(blob):return hashlib.sha256(blob).hexdigest() if blob is not None else None
class MainObserver:
 @staticmethod
 def focus_identity(value):return {k:value.get(k) for k in ('address','stableId','pid')} if isinstance(value,dict) else value
 def __init__(self,env):
  self.env=dict(env);self.home=Path(self.env['HOME']);self.signature=self.env['HYPRLAND_INSTANCE_SIGNATURE']
  if self.home!=Path('/home/hoskinson') or self.env['XDG_RUNTIME_DIR']!=str(Path('/run/user')/str(os.getuid())):raise RuntimeError('observer must use original main environment')
 def command(self,*args):return subprocess.check_output(list(map(str,args)),env=self.env,stderr=subprocess.PIPE,timeout=8)
 def ctl(self,verb,*args):
  if (verb,args) not in [('clients',()),('activewindow',()),('cursorpos',()),('monitors',()),('devices',()),('configerrors',()),('plugin',('list',))]:raise RuntimeError('observer permits getters only')
  flags=[] if verb in ('configerrors','plugin') else ['-j']
  return self.command('/usr/bin/hyprctl','-i',self.signature,*flags,verb,*args).decode().strip()
 def data(self,verb):return json.loads(self.ctl(verb))
 def files(self):
  app=self.home/'.local/share/omarchy-files'
  instances=json.loads(self.command('qs','-p',app,'list','-j'));assert len(instances)==1
  def ipc(name):return json.loads(self.command('qs','-p',app,'ipc','call','files',name))
  public,ui,migration=ipc('state'),ipc('uiState'),ipc('migrationStatus');pid=instances[0]['pid']
  assert migration['ready'] and migration['pid']==pid and migration['instance']==instances[0]['id']
  return dict(pid=pid,instance=instances[0]['id'],processStart=Path('/proc/'+str(pid)+'/stat').read_text().rsplit(')',1)[1].split()[19],visible=ui['visible'],publicSHA256=sha(json.dumps(public,sort_keys=True).encode()),uiSHA256=sha(json.dumps(ui,sort_keys=True).encode()))
 def accessibility(self):
  path=Path(self.env['XDG_RUNTIME_DIR'])/'at-spi/bus_0';row=path.lstat()
  assert row.st_uid==os.getuid() and stat.S_ISSOCK(row.st_mode)
  with socket.socket(socket.AF_UNIX) as connection:
   connection.settimeout(.3);connection.connect(str(path))
  return dict(device=row.st_dev,inode=row.st_ino,connects=True)
 def reader(self):
  self.command('gdbus','call','--session','--dest','org.freedesktop.DBus','--object-path','/org/freedesktop/DBus','--method','org.freedesktop.DBus.GetNameOwner','org.a11y.Bus')
  return self.command('gdbus','call','--session','--dest','org.a11y.Bus','--object-path','/org/a11y/bus','--method','org.freedesktop.DBus.Properties.Get','org.a11y.Status','ScreenReaderEnabled').decode().strip()
 def clipboard(self):
  # Hash observed selection; never send/store its content in logs.
  result=subprocess.run(['wl-paste','--list-types'],env=self.env,capture_output=True,timeout=5)
  if result.returncode:return dict(types=[],unavailable=result.returncode)
  types=result.stdout.decode().splitlines();rows={}
  for kind in types:
   value=subprocess.run(['wl-paste','--no-newline','--type',kind],env=self.env,capture_output=True,timeout=5)
   rows[kind]=dict(exitCode=value.returncode,bytes=len(value.stdout),sha256=sha(value.stdout))
  return dict(types=types,content=rows)
 def capture(self):
  clients=self.data('clients');keyboard_fields=('address','name','layout','variant','options','capsLock','numLock','main')
  catalogs={str(self.home/'.config/omarchy'/name):None for name in p.CATALOG_NAMES}
  for name in catalogs:
   path=Path(name);blob=path.read_bytes() if path.exists() else None
   catalogs[name]=dict(base64=base64.b64encode(blob).decode() if blob is not None else None,sha256=sha(blob))
  focus=self.data('activewindow')
  return dict(clients=p.project_clients(clients),focus=focus,focusTitleSHA256=sha(str(focus.get('title','')).encode()),cursor=self.data('cursorpos'),outputs=p.project_outputs(self.data('monitors')),a11y=self.accessibility(),reader=self.reader(),files=self.files(),plugins=self.ctl('plugin','list'),keyboards=[{k:r.get(k) for k in keyboard_fields} for r in self.data('devices')['keyboards']],catalogs=catalogs,clipboard=self.clipboard(),configErrors=self.ctl('configerrors'))
 @staticmethod
 def compare(before,after):
  fields=('clients','focus','cursor','outputs','a11y','reader','files','plugins','keyboards','catalogs','clipboard','configErrors')
  checks={name:before[name]==after[name] for name in fields}
  checks['focus']=MainObserver.focus_identity(before['focus'])==MainObserver.focus_identity(after['focus'])
  checks['originalFilesExactProcessAndCapturedVisibility']=checks['files']
  checks['canonicalFullClientSet']=set((w['address'],w['pid'],w['stableId']) for w in before['clients'])==set((w['address'],w['pid'],w['stableId']) for w in after['clients'])
  checks['readerRemainsFalse']='false' in before['reader'] and before['reader']==after['reader']
  return checks
