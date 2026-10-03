"""Read-only main-desktop observations; never repair catalogs or user state."""
from pathlib import Path
import hashlib,json,os,socket,subprocess,time
import catalog_preservation as shared
HOME=Path.home()
FIELDS=shared.CLIENT_FIELDS+('mapped','hidden','visible','acceptsInput','class','initialClass','initialTitle','xwayland','pinFullscreened','fullscreenHandler','allowedOverFullscreen','swallowing','inhibitingIdle','xdgTag','xdgDescription','contentType','tearingHint')
def run(*args):return subprocess.check_output(list(map(str,args)),text=True,stderr=subprocess.PIPE,timeout=8).strip()
def data(name):return json.loads(run('hyprctl',name,'-j'))
def digest(path):return shared.digest(path.read_bytes()) if path.exists() else None
def start(pid):return Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[19]
def private_json(path,value):path.write_text(json.dumps(value,indent=2)+'\n');path.chmod(0o600)
def stable_clients(rows):return sorted([{k:r.get(k) for k in FIELDS} for r in rows],key=lambda r:r['address'])
def clipboard(primary=False):
 options=['--primary'] if primary else [];types=subprocess.run(['wl-paste',*options,'--list-types'],capture_output=True,timeout=4);out=[(types.returncode,shared.digest(types.stdout))]
 for mime in sorted(types.stdout.decode().splitlines()):
  r=subprocess.run(['wl-paste',*options,'--type',mime],capture_output=True,timeout=4);out.append((shared.digest(mime.encode()),r.returncode,len(r.stdout),shared.digest(r.stdout)))
 return out

def accessibility():
 path=Path(os.environ['XDG_RUNTIME_DIR'])/'at-spi/bus_0';st=path.stat()
 with socket.socket(socket.AF_UNIX) as connection:connection.settimeout(.5);connection.connect(str(path))
 return {'socket':[st.st_dev,st.st_ino], 'connects':True,'readerEnabled':shared.reader_status(),'flags':[run('gsettings','get',s,k) for s,k in [('org.gnome.desktop.a11y.applications','screen-reader-enabled'),('org.gnome.desktop.interface','toolkit-accessibility')]]}
def keyboards():
 fields=('address','name','layout','variant','options','capsLock','numLock','main')
 return sorted([{k:r.get(k) for k in fields} for r in data('devices')['keyboards']],key=lambda r:(r['name'] or '',r['address'] or ''))
def files():
 live=HOME/'.local/share/omarchy-files';instances=json.loads(run('qs','-p',live,'list','-j'))
 assert len(instances)<=1,'Read-only baseline requires zero or one actual live Files instance'
 if not instances:return {'running':False,'pid':None,'start':None,'instance':None,'public':None,'ui':None,'migration':None}
 instance=instances[0];pid=instance['pid'];state=json.loads(run('qs','ipc','--pid',pid,'call','files','state'));ui=json.loads(run('qs','ipc','--pid',pid,'call','files','uiState'));ready=json.loads(run('qs','ipc','--pid',pid,'call','files','migrationStatus'))
 assert ready['ready'] and ready['instance']==instance['id'] and ready['pid']==pid,'Actual Files instance is not ready/coherent'
 return {'running':True,'pid':pid,'start':start(pid),'instance':instance['id'],'public':state,'ui':ui,'migration':ready}

def capture(folder):
 folder.mkdir(mode=0o700);clients=data('clients');private_json(folder/'clients-raw.json',clients);original=files();private_json(folder/'files-state.json',original)
 return {'clients':stable_clients(clients),'titles':{r['address']:shared.digest(r.get('title','').encode()) for r in clients},'focus':{k:data('activewindow').get(k) for k in ('address','stableId','pid')},'cursor':data('cursorpos'),'layers':data('layers'),'clipboard':[clipboard(),clipboard(True)],'a11y':accessibility(),'outputs':shared.project_outputs(data('monitors')),'plugins':run('hyprctl','plugin','list'),'keyboards':keyboards(),'catalog':shared.backup_catalogs(folder,HOME),'dashboard':shared.file_bytes(HOME/'.local/state/omarchy-files/dashboard.json'),'files':original}

def compare(before,folder,allow_empty_focus_addition=False):
 folder.mkdir(mode=0o700);clients=data('clients');private_json(folder/'clients-raw.json',clients);actual=files();private_json(folder/'files-state.json',actual)
 catalog=shared.settle_catalogs(before['catalog'],seconds=4);private_json(folder/'catalog-comparison.json',catalog)
 active=data('activewindow');checks={'allStableClientFields':stable_clients(clients)==before['clients'],'originalFocus':{k:active.get(k) for k in ('address','stableId','pid')}==before['focus'],'originalCursor':data('cursorpos')==before['cursor'],'originalLayers':data('layers')==before['layers'],'typedClipboardAndPrimary': [clipboard(),clipboard(True)]==before['clipboard'],'a11ySocketFlagsAndReaderEnabled':accessibility()==before['a11y'],'outputs':shared.project_outputs(data('monitors'))==before['outputs'],'plugins':run('hyprctl','plugin','list')==before['plugins'],'keyboardStates':keyboards()==before['keyboards'],'fourCatalogNaturalBytes':all(r['exactBytes'] for r in catalog.values()),'dashboardBytes':shared.file_bytes(HOME/'.local/state/omarchy-files/dashboard.json')==before['dashboard'],'originalFilesProcess':all(actual[k]==before['files'][k] for k in ('running','pid','start','instance')),'originalFilesPublicState':actual['public']==before['files']['public'],'originalFilesFullUi':actual['ui']==before['files']['ui'],'originalFilesVisibility':(actual['ui'] or {}).get('visible')==(before['files']['ui'] or {}).get('visible')}
 if allow_empty_focus_addition:
  old=before['files']['ui'];new=dict(actual['ui']);added='focusIdentity' not in old
  valid=(new.pop('focusIdentity',None)=='') if added else True
  checks.pop('originalFilesFullUi')
  checks['originalFilesFullUiWithEmptyAddedFocusIdentity']=valid and new==old if added else actual['ui']==old
 return checks,{'currentTitleHashesBefore':before['titles'],'currentTitleHashesAfter':{r['address']:shared.digest(r.get('title','').encode()) for r in clients},'catalogNaturalComparison':catalog,'stableFields':list(FIELDS)}
