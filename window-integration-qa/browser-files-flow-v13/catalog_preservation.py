"""Read-only preservation observations for isolated atlas smoke."""
import base64,hashlib,json,os,subprocess,time
from pathlib import Path
CLIENT_FIELDS=('address','pid','stableId','at','size','workspace','pinned','fullscreen','fullscreenClient','grouped','tags','floating','monitor')
OUTPUT_FIELDS=('name','width','height','x','y','scale','transform','reserved','disabled')
CATALOG_NAMES=('virtual-desktops.json','taskbar-settings.json','taskbar-order.json','taskbar-session-order.json')
def digest(data):return hashlib.sha256(data).hexdigest() if data is not None else None
def project_clients(rows):return sorted(({k:r.get(k) for k in CLIENT_FIELDS} for r in rows),key=lambda r:(r['stableId'] or '',r['pid'] or 0,r['address'] or ''))
def project_outputs(rows):return sorted(({k:r.get(k) for k in OUTPUT_FIELDS} for r in rows),key=lambda r:r['name'] or '')
def file_bytes(path):return path.read_bytes() if path.exists() else None
def backup_catalogs(folder,home):
 rows={str(home/'.config/omarchy'/name):file_bytes(home/'.config/omarchy'/name) for name in CATALOG_NAMES}
 destination=folder/'catalog-before.json'
 data=json.dumps({p:{'base64':base64.b64encode(b).decode() if b is not None else None,'sha256':digest(b)} for p,b in rows.items()},indent=2).encode()+b'\n'
 descriptor=os.open(destination,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(descriptor,'wb') as stream:stream.write(data)
 return rows

def settle_catalogs(rows,seconds=4):
 end=time.monotonic()+seconds
 while True:
  actual={p:file_bytes(Path(p)) for p in rows}
  if actual==rows or time.monotonic()>=end:return {p:{'exactBytes':actual[p]==b,'expectedSHA256':digest(b),'actualSHA256':digest(actual[p])} for p,b in rows.items()}
  time.sleep(.08)

def command(*args):return subprocess.check_output(list(map(str,args)),text=True,stderr=subprocess.PIPE,timeout=5).strip()
def reader_status():return command('gdbus','call','--session','--dest','org.a11y.Bus','--object-path','/org/a11y/bus','--method','org.freedesktop.DBus.Properties.Get','org.a11y.Status','ScreenReaderEnabled')
def files_state(home):
 app=home/'.local/share/omarchy-files'
 instances=json.loads(command('qs','-p',app,'list','-j'))
 assert len(instances)==1,'preserve exactly one original Files instance'
 def ipc(method):return json.loads(command('qs','-p',app,'ipc','call','files',method))
 public=ipc('state');ui=ipc('uiState');migration=ipc('migrationStatus')
 assert migration['ready'] and migration['pid']==instances[0]['pid'] and migration['instance']==instances[0]['id'],'Files host is not ready/coherent'
 pid=instances[0]['pid']
 return {'pid':pid,'instance':instances[0]['id'],'processStart':Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[19],'visible':ui['visible'],'publicSHA256':digest(json.dumps(public,sort_keys=True).encode()),'uiSHA256':digest(json.dumps(ui,sort_keys=True).encode())}
