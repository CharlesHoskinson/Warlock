#!/usr/bin/env python3
"""Root-coordinated physical Qt keys plus real silent Orca; isolated copied Files."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from atspi_qa import assistive_session
import gi
from gi.repository import Gio,GLib
B=Path(__file__).resolve().parent;H=Path.home();READER=B.parents[2]/'orca-reader'
bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
report={'scope':'Isolated copied Files on native Wayland; physical Qt keyboard plus actual Orca focus/navigation/press actions; silent speech log','checks':[],'failures':[]}
app=reader=None;app_log=(B/'native.log').open('w');reader_log=(B/'reader.log').open('w')
def run(*a):return subprocess.check_output(list(map(str,a)),text=True,timeout=8).strip()
def data(n):return json.loads(run('hyprctl',n,'-j'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
def clips(primary=False):
 opts=['--primary'] if primary else [];out=[]
 types=subprocess.run(['wl-paste',*opts,'--list-types'],capture_output=True,timeout=4)
 out.append((types.returncode,hashlib.sha256(types.stdout).hexdigest()))
 for mime in sorted(types.stdout.decode().splitlines()):
  r=subprocess.run(['wl-paste',*opts,'--type',mime],capture_output=True,timeout=4)
  out.append((hashlib.sha256(mime.encode()).hexdigest(),r.returncode,len(r.stdout),hashlib.sha256(r.stdout).hexdigest()))
 return out
def blocked():return [s for m in data('layers').values() for ss in m.get('levels',{}).values() for s in ss if s.get('alpha',1)>0 and ('sudo-askpass' in s.get('namespace','') or 'hyprlock' in s.get('namespace',''))]
assert not bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','NameHasOwner',GLib.Variant('(s)',('org.gnome.Orca.Service',)),None,Gio.DBusCallFlags.NONE,5000,None).unpack()[0],'Existing reader owner must remain untouched'
assert not blocked(),'foreign input grab'
initial=data('clients');focus=data('activewindow');cursor=data('cursorpos');layers=data('layers');clip=[clips(),clips(True)]
catalog=H/'.config/omarchy/virtual-desktops.json';dashboard=H/'.local/state/omarchy-files/dashboard.json';catsha=sha(catalog);dashsha=sha(dashboard)
original_state=sha(B.parents[2]/'files-responsive/source-hashes.json')
oldpublic=hashlib.sha256(run('qs','-p',H/'.local/share/omarchy-files','ipc','call','files','state').encode()).hexdigest()
original_ui=run('qs','-p',H/'.local/share/omarchy-files','ipc','call','files','uiState')
assert not json.loads(original_ui)['visible'] and Path('/proc/667402').exists()
shared_profile=READER/'data/orca/orca-customizations.py';shared_profile_sha=sha(shared_profile)
def canonical_clients(values):
 fields=('address','stableId','pid','class','title','workspace','monitor','at','size','pinned','fullscreen','floating')
 return sorted([{k:w.get(k) for k in fields} for w in values],key=lambda w:w['address'])
private=B/'private-preservation';private.mkdir(mode=0o700)
(private/'original-clients.json').write_text(json.dumps(canonical_clients(initial),indent=2));(private/'original-clients.json').chmod(0o600)
(private/'original-ui.json').write_text(original_ui);(private/'original-ui.json').chmod(0o600)
original_start=Path('/proc/667402/stat').read_text().rsplit(')',1)[1].split()[19]
catalogs={}
for name in ['virtual-desktops.json','taskbar-settings.json','taskbar-order.json','taskbar-session-order.json']:
 path=H/'.config/omarchy'/name;raw=path.read_bytes() if path.exists() else None;catalogs[name]=(raw,path.stat().st_mode&0o777 if raw is not None else None)
 if raw is not None:(private/name).write_bytes(raw);(private/name).chmod(0o600)
flags=[run('gsettings' ,'get',s,k) for s,k in [('org.gnome.desktop.a11y.applications','screen-reader-enabled'),('org.gnome.desktop.interface','toolkit-accessibility')]]
socket=Path(os.environ['XDG_RUNTIME_DIR'])/'at-spi/bus_0';socketstat=socket.stat() if socket.exists() else None
def check(name,value,**detail):
 report['checks'].append(dict(name=name,passed=bool(value),**detail))
 if not value:report['failures'].append(name);raise AssertionError(name)
def wait(fn,label,seconds=8):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  try:
   value=fn()
   if value:return value
  except (GLib.Error,subprocess.CalledProcessError):pass
  time.sleep(.1)
 raise AssertionError(label)
def ipc(method,*args):return run('qs','ipc','--pid',app.pid,'call','files-keyboard-qa',method,*args)
def dbus(module,method,args):return bus.call_sync('org.gnome.Orca.Service','/org/gnome/Orca/Service/'+module,'org.gnome.Orca.Module',method,args,None,Gio.DBusCallFlags.NONE,5000,None).unpack()[0]
def state():return json.loads(dbus('QAObservation','ExecuteRuntimeGetter',GLib.Variant('(s)',('State',))))
def command(name):
 check('real Orca command '+name,dbus('ObjectNavigator','ExecuteCommand',GLib.Variant('(sb)',(name,True))));time.sleep(.25)
def own():
 w=next((w for w in data('clients') if w['pid']==app.pid and w['title']=='Files Responsive QA'),None)
 assert w and (w['address'],w['stableId'],w['pid'])==identity,'fixture identity'
 return w
def key(name,mods=()):
 assert not blocked(),'foreign input grab'
 assert data('activewindow').get('stableId')==own()['stableId'],'own native focus'
 args=['wtype']
 for m in mods:args+=['-M',m]
 args+=['-k',name]
 for m in reversed(mods):args+=['-m',m]
 run(*args);time.sleep(.35)
def reader_focus(name,role=None):
 def expected():
  s=state();f=s.get('focus') or {}
  return s if f.get('name')==name and (role is None or f.get('role')==role) else None
 value=wait(expected,'Orca focus '+name)
 report.setdefault('focusTrace',[]).append(value);return value
def info(name):
 value=json.loads(ipc('focusInfo',name));assert value.get('valid') and value.get('name'),(name,value);return value
def perform(name):
 target=info(name);actual=reader_focus(target['name']);identity=(actual['focus'].get('app_bus'),actual['focus'].get('object_path'));assert identity[1],actual
 command('MoveToParent');command('MoveToFirstChild')
 for _ in range(180):
  if ((state().get('navigator') or {}).get('app_bus'),(state().get('navigator') or {}).get('object_path'))==identity:break
  command('MoveToNextSibling')
 check('actual Orca navigator reaches exact '+name,((state().get('navigator') or {}).get('app_bus'),(state().get('navigator') or {}).get('object_path'))==identity)
 command('PerformAction');report.setdefault('actions',[]).append(dict(target=name,observed=target,readerFocus=actual))
 return target
def folder():
 ipc('open',B/'home/fixture');wait(lambda:json.loads(ipc('state'))['entries']==4,'sandbox folder');ipc('act','view','list')
def home():
 key('Escape');ipc('open','home');wait(lambda:json.loads(ipc('state'))['view']=='home','Home');time.sleep(.25)
def sandbox_path(target,kind):
 value=Path(target['logicalIdentity'].removeprefix(kind+':'));root=(B/'home').resolve();assert value==root or root in value.parents;return value
try:
 with assistive_session():
  env=dict(os.environ,HOME=str(B/'home'),FILES_STATE=str(B/'state'),FILES_DRYRUN='0',PATH=str(B/'bin')+os.pathsep+os.environ['PATH'],FILES_QA_OPEN_LOG=str(B/'opener.jsonl'),FILES_OPEN='home',XDG_CACHE_HOME=str(B/'isolated-cache'))
  env.pop('QT_QPA_PLATFORM',None)
  app=subprocess.Popen(['qs','-p',str(B/'qa-app')],env=env,stdout=app_log,stderr=app_log)
  w=wait(lambda:next((w for w in data('clients') if w['pid']==app.pid and w['title']=='Files Responsive QA'),None),'native fixture maps')
  identity=(w['address'],w['stableId'],w['pid']);report['fixtureIdentity']=identity
  run('hyprctl','dispatch',f'hl.dsp.window.resize({{x=330,y=320,window="address:{w["address"]}"}})')
  wait(lambda:own()['size']==[330,320],'native minimum')
  run('hyprctl','dispatch',f'hl.dsp.focus({{window="address:{w["address"]}"}})')
  check('native minimum330x320',own()['size']==[330,320])
  (B/'utterances.jsonl').write_text('')
  renv=dict(os.environ,ORCA_QA_UTTERANCES=str(B/'utterances.jsonl'),ORCA_QA_LEGACY_GRAB_FIX='1',ORCA_QA_NATIVE_WAYLAND_MODIFIERS='1',GDK_BACKEND='wayland',GSETTINGS_BACKEND='memory',PYTHONPATH=str(READER)+':'+str(READER/'prefix/usr/lib/python3.14/site-packages'),LD_LIBRARY_PATH=str(READER/'prefix/usr/lib')+':'+os.environ.get('LD_LIBRARY_PATH',''),GI_TYPELIB_PATH=str(READER/'prefix/usr/lib/girepository-1.0')+':'+os.environ.get('GI_TYPELIB_PATH',''),XDG_DATA_HOME=str(B/'reader-profile/data'),XDG_CONFIG_HOME=str(B/'reader-profile/config'),XDG_CACHE_HOME=str(B/'reader-profile/cache'),XDG_DATA_DIRS=str(READER/'prefix/usr/share')+':/usr/local/share:/usr/share')
  renv.pop('DISPLAY',None)
  reader=subprocess.Popen(['python',str(READER/'prefix/usr/bin/orca'),'--speech-system','silent_factory','--debug-file',str(B/'reader.debug')],env=renv,stdout=reader_log,stderr=reader_log)
  wait(state,'actual Orca native loop',15)
  check('real Orca native Wayland loop ready',reader.poll() is None)
  ipc('focus','Home');check('Orca recognizes actual named Home button',reader_focus('Home')['focus']['role']=='button')
  key('Tab');check('physical Tab produces actual Orca button focus',(state().get('focus') or {}).get('role')=='button',readerState=state())
  ipc('open',str(B/'home/fixture'));wait(lambda:json.loads(ipc('state'))['entries']==4,'fixture folder')
  ipc('focus','Show list');reader_focus('Show list');key('Return');check('physical Return activates existing View',json.loads(ipc('state'))['mode']=='list')
  ipc('focus','Explorer.keys');key('Down');check('physical arrow moves real file row reader focus',reader_focus('subfolder')['focus']['role']=='list item')
  key('Down');check('physical next file arrow retains named reader focus',reader_focus('alpha-long-file-name-to-test-eliding.txt')['focus']['role']=='list item')
  key('F2');check('physical F2 opens named text prompt',reader_focus('Rename','text')['focus']['role']=='text')
  key('Tab');reader_focus('Cancel');key('Tab');reader_focus('Rename','button');key('Tab');check('native prompt Tab traps at text input',reader_focus('Rename','text')['focus']['role']=='text')
  key('Escape');check('native prompt Escape preserves fixture files',not json.loads(ipc('uiState'))['prompt']['visible'])
  ipc('focus','Sort');reader_focus('Sort');command('MoveToParent');command('MoveToFirstChild')
  for _ in range(35):
   if (state().get('navigator') or {}).get('name')=='Sort':break
   command('MoveToNextSibling')
  check('actual Orca ObjectNavigator reaches Sort',(state().get('navigator') or {}).get('name')=='Sort',readerState=state())
  command('PerformAction');check('actual Orca press opens existing Sort menu',json.loads(ipc('uiState'))['menu']['visible'])
  key('Down');check('menu arrow gives real named reader row focus',reader_focus('Name')['focus']['role']=='menu item')
  key('Escape');key('b',('ctrl',));check('compact sidebar reader focus follows collection',reader_focus('Recent activity')['focus']['role']=='button')
  key('Escape');ipc('open','home');ipc('focus','Dashboard.filterChip');check('Home filter has actual button reader role',reader_focus('All')['focus']['role']=='button')
  key('Tab');check('physical Home filter Tab announces next name',reader_focus('Documents')['focus']['role']=='button')
  # Broad cases use real Data scans and unchanged operations in the fixture home.
  folder();ipc('act','view','grid');ipc('focus','Explorer.keys');key('Down');target=perform('FileArea.cl')
  check('gallery actual reader directory press',json.loads(ipc('state'))['cwd']==str(sandbox_path(target,'file')))
  folder();key('b',('ctrl',));target=perform('Tree.chev')
  row=info('Tree.row');check('tree actual reader branch toggle announces changed state',('expanded' in row['description']) != ('Collapse' in target['name']))
  target=perform('Tree.row');check('tree actual reader captured directory navigation',json.loads(ipc('state'))['cwd']==str(sandbox_path(target,'tree')))
  home();target=perform('Dashboard.cc');check('Home actual reader smart collection',json.loads(ipc('state'))['coll']==target['logicalIdentity'].removeprefix('home-collection:'))
  home();target=perform('Dashboard.tile');check('Home actual reader pinned folder',json.loads(ipc('state'))['cwd']==str(sandbox_path(target,'pin')))
  home();target=perform('Dashboard.mt');path=sandbox_path(target,'media')
  check('Home actual reader media reveal',json.loads(ipc('state'))['cwd']==str(path.parent) and path.name in json.loads(ipc('state'))['sel'])
  home();target=perform('Dashboard.rr');path=sandbox_path(target,'recent')
  def opened():
   log=B/'opener.jsonl'
   return log.exists() and any(json.loads(line)['path']==str(path) and json.loads(line)['sha256']==sha(path) for line in log.read_text().splitlines())
  wait(opened,'captured real opener dispatch');check('Home actual reader recent file captured opener reads real file',opened())
  home();wait(lambda:json.loads(ipc('focusInfo','Treemap.t')).get('valid'),'actual storage scan',15)
  target=perform('Treemap.t');check('Home actual reader storage directory',json.loads(ipc('state'))['cwd']==str(sandbox_path(target,'storage')))
  folder();ipc('focus','Explorer.keys');key('Down');key('i',('ctrl',));perform('Close details')
  check('actual reader closes compact details overlay',not json.loads(ipc('uiState'))['detailOverlayRequested'])
  folder();ipc('focus','Explorer.keys');key('Down');key('Menu');perform('ContextMenu.menuRow')
  check('actual reader file menu Open uses captured sandbox directory',json.loads(ipc('state'))['cwd']==str(B/'home/fixture/subfolder'))
  folder();ipc('focus','Explorer.keys');key('Down');key('Down');key('F2');reader_focus('Rename','text')
  source=B/'home/fixture/alpha-long-file-name-to-test-eliding.txt';beforeHash=sha(source)
  key('a',('ctrl',));run('wtype','reader-renamed.txt');time.sleep(.2);perform('Prompt.acceptBtn')
  renamed=B/'home/fixture/reader-renamed.txt';wait(lambda:renamed.exists() and not source.exists(),'real sandbox rename')
  check('actual reader prompt accept runs unchanged real rename preserving bytes',sha(renamed)==beforeHash)
  report['openerBoundary']='The existing xdg-open invocation is captured by a sandbox-only executable that reads the actual target and records its hash; no default-association GUI launch claim.'
  speech=[json.loads(s) for s in (B/'utterances.jsonl').read_text().splitlines() if s]
  check('real reader generated silent utterances',any(s['kind']=='speech' and s['text'] for s in speech),utteranceCount=len(speech))
except Exception as e:report['error']=repr(e)
finally:
 if reader and reader.poll() is None:
  reader.terminate();reader.wait(timeout=8)
 if app and app.poll() is None:
  try:ipc('shutdown')
  except Exception:pass
  app.terminate()
  try:app.wait(timeout=8)
  except subprocess.TimeoutExpired:app.terminate();app.wait(timeout=8)
 existing={w['address']:w for w in data('clients')};p=report['preservation']={}
 p['originalCanonicalClients']=canonical_clients(list(existing.values()))==canonical_clients(initial)
 if focus.get('address') in existing and existing[focus['address']].get('stableId')==focus.get('stableId'):run('hyprctl','dispatch',f'hl.dsp.focus({{window="address:{focus["address"]}"}})')
 run('hyprctl','dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})');time.sleep(.2)
 p['originalFocus']=data('activewindow').get('stableId')==focus.get('stableId');p['originalCursor']=data('cursorpos')==cursor;p['originalLayers']=data('layers')==layers
 # Wait for fixture tracking to retire, then restore exact catalog bytes captured
 # inside the exclusive root-granted slot. Preserve the private backups for recovery.
 time.sleep(1.1)
 for name,(raw,mode) in catalogs.items():
  path=H/'.config/omarchy'/name
  if raw is not None and path.read_bytes()!=raw:
   temp=path.with_name(path.name+'.files-reader-qa-restore');temp.write_bytes(raw);temp.chmod(mode);os.replace(temp,path)
 time.sleep(.4)
 p['allFourCatalogBytes']=all((H/'.config/omarchy'/name).read_bytes()==raw if raw is not None else not (H/'.config/omarchy'/name).exists() for name,(raw,_) in catalogs.items())
 p['originalFullUiState']=json.loads(run('qs','-p',H/'.local/share/omarchy-files','ipc','call','files','uiState'))==json.loads(original_ui)
 p['sharedReaderProfileBytes']=sha(shared_profile)==shared_profile_sha
 p['originalProcessStart']=Path('/proc/667402/stat').read_text().rsplit(')',1)[1].split()[19]==original_start
 p['clipboardAndPrimaryRawAndMimeHashes']=[clips(),clips(True)]==clip;p['catalogBytes']=sha(catalog)==catsha;p['dashboardBytes']=sha(dashboard)==dashsha
 p['originalExplorerPublicState']=hashlib.sha256(run('qs','-p',H/'.local/share/omarchy-files','ipc','call','files','state').encode()).hexdigest()==oldpublic
 p['originalExplorerPID']=Path('/proc/667402').exists();p['originalExplorerHidden']=not any(w['pid']==667402 for w in existing.values())
 p['a11yFlags']=flags==[run('gsettings','get',s,k) for s,k in [('org.gnome.desktop.a11y.applications','screen-reader-enabled'),('org.gnome.desktop.interface','toolkit-accessibility')]]
 p['a11ySocketInode']=socketstat is None or (socket.exists() and socket.stat().st_ino==socketstat.st_ino)
 p['responsiveManifestBytes']=sha(B.parents[2]/'files-responsive/source-hashes.json')==original_state
 report['result']='pass' if not report.get('error') and not report['failures'] and all(p.values()) else 'fail'
 app_log.close();reader_log.close();(B/'native-reader-report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'result':report['result'],'checks':len(report['checks']),'error':report.get('error'),'preservation':p},indent=2))
sys.exit(report['result']!='pass')
