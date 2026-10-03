#!/usr/bin/env python3
"""Root-coordinated Wayland virtual-keyboard Qt keys plus real silent Orca; isolated copied Files."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,signal,socket,subprocess,sys,time
import preservation
from freeze_guard import verify_manifest, prepare_attempt
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from atspi_qa import assistive_session
import gi
from gi.repository import Gio,GLib
B=Path(__file__).resolve().parent;H=Path.home();READER=B.parents[2]/'orca-reader'
parser=argparse.ArgumentParser();parser.add_argument('--attempt',required=True,type=Path);args=parser.parse_args()
verify_manifest(B/'frozen-inputs.json')
O=prepare_attempt(B,args.attempt)
bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
report={'scope':'Isolated copied Files on native Wayland; Wayland virtual-keyboard Qt keyboard plus actual Orca focus/navigation/press actions; silent speech log','checks':[],'failures':[],'physicalHardwareProved':False,'inputSource':'wtype Wayland virtual-keyboard protocol, routed through the compositor to the copied Qt window'}
app=reader=None;app_log=(O/'native.log').open('w');reader_log=(O/'reader.log').open('w')
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
def a11y_socket():
 path=Path(os.environ['XDG_RUNTIME_DIR'])/'at-spi/bus_0';st=path.stat();connection=socket.socket(socket.AF_UNIX);connection.settimeout(.3)
 try:connection.connect(str(path));connects=True
 except OSError:connects=False
 finally:connection.close()
 return {'dev':st.st_dev,'inode':st.st_ino,'connects':connects}
def keyboard_state():
 fields=('address','name','layout','variant','options','capsLock','numLock','main')
 return sorted([{k:d.get(k) for k in fields} for d in data('devices')['keyboards']],key=lambda d:(d['name'] or '',d['address'] or ''))
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
 fields=preservation.CLIENT_FIELDS+('class','title')
 return sorted([{k:w.get(k) for k in fields} for w in values],key=lambda w:w['address'])
private=O/'private-preservation';private.mkdir(mode=0o700)
(private/'original-clients.json').write_text(json.dumps(canonical_clients(initial),indent=2));(private/'original-clients.json').chmod(0o600)
(private/'original-ui.json').write_text(original_ui);(private/'original-ui.json').chmod(0o600)
original_start=Path('/proc/667402/stat').read_text().rsplit(')',1)[1].split()[19]
catalogs={}
for name in ['virtual-desktops.json','taskbar-settings.json','taskbar-order.json','taskbar-session-order.json']:
 path=H/'.config/omarchy'/name;raw=path.read_bytes() if path.exists() else None;catalogs[name]=(raw,path.stat().st_mode&0o777 if raw is not None else None)
 if raw is not None:(private/name).write_bytes(raw);(private/name).chmod(0o600)
flags=[run('gsettings' ,'get',s,k) for s,k in [('org.gnome.desktop.a11y.applications','screen-reader-enabled'),('org.gnome.desktop.interface','toolkit-accessibility')]]
socket_before=a11y_socket();reader_enabled=preservation.reader_status()
outputs_before=preservation.project_outputs(data('monitors'));plugins_before=run('hyprctl','plugin','list');keyboards_before=keyboard_state()
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
 ipc('open',O/'home/fixture');wait(lambda:json.loads(ipc('state'))['entries']==4,'sandbox folder');ipc('act','view','list')
def home():
 key('Escape');ipc('open','home');wait(lambda:json.loads(ipc('state'))['view']=='home','Home');time.sleep(.25)
def sandbox_path(target,kind):
 value=Path(target['logicalIdentity'].removeprefix(kind+':'));root=(O/'home').resolve();assert value==root or root in value.parents;return value
try:
 with assistive_session():
  env=dict(os.environ,HOME=str(O/'home'),FILES_STATE=str(O/'state'),FILES_DRYRUN='0',PATH=str(B/'bin')+os.pathsep+os.environ['PATH'],FILES_QA_OPEN_LOG=str(O/'opener.jsonl'),FILES_OPEN='home',XDG_CACHE_HOME=str(O/'isolated-cache'))
  env.pop('QT_QPA_PLATFORM',None)
  app=subprocess.Popen(['qs','-p',str(B/'qa-app')],env=env,stdout=app_log,stderr=app_log,start_new_session=True)
  w=wait(lambda:next((w for w in data('clients') if w['pid']==app.pid and w['title']=='Files Responsive QA'),None),'native fixture maps')
  identity=(w['address'],w['stableId'],w['pid']);report['fixtureIdentity']=identity
  run('hyprctl','dispatch',f'hl.dsp.window.resize({{x=330,y=320,window="address:{w["address"]}"}})')
  wait(lambda:own()['size']==[330,320],'native minimum')
  run('hyprctl','dispatch',f'hl.dsp.focus({{window="address:{w["address"]}"}})')
  check('native minimum330x320',own()['size']==[330,320])
  (O/'utterances.jsonl').write_text('')
  renv=dict(os.environ,ORCA_QA_UTTERANCES=str(O/'utterances.jsonl'),ORCA_QA_LEGACY_GRAB_FIX='1',ORCA_QA_NATIVE_WAYLAND_MODIFIERS='1',GDK_BACKEND='wayland',GSETTINGS_BACKEND='memory',PYTHONPATH=str(READER)+':'+str(READER/'prefix/usr/lib/python3.14/site-packages'),LD_LIBRARY_PATH=str(READER/'prefix/usr/lib')+':'+os.environ.get('LD_LIBRARY_PATH',''),GI_TYPELIB_PATH=str(READER/'prefix/usr/lib/girepository-1.0')+':'+os.environ.get('GI_TYPELIB_PATH',''),XDG_DATA_HOME=str(O/'reader-profile/data'),XDG_CONFIG_HOME=str(O/'reader-profile/config'),XDG_CACHE_HOME=str(O/'reader-profile/cache'),XDG_DATA_DIRS=str(READER/'prefix/usr/share')+':/usr/local/share:/usr/share')
  renv.pop('DISPLAY',None)
  reader=subprocess.Popen(['python',str(READER/'prefix/usr/bin/orca'),'--speech-system','silent_factory','--debug-file',str(O/'reader.debug')],env=renv,stdout=reader_log,stderr=reader_log,start_new_session=True)
  wait(state,'actual Orca native loop',15)
  check('real Orca native Wayland loop ready',reader.poll() is None)
  ipc('focus','Home');check('Orca recognizes actual named Home button',reader_focus('Home')['focus']['role']=='button')
  key('Tab');check('virtual-keyboard Tab produces actual Orca button focus',(state().get('focus') or {}).get('role')=='button',readerState=state())
  ipc('open',str(O/'home/fixture'));wait(lambda:json.loads(ipc('state'))['entries']==4,'fixture folder')
  ipc('focus','Show list');reader_focus('Show list');key('Return');check('virtual-keyboard Return activates existing View',json.loads(ipc('state'))['mode']=='list')
  ipc('focus','Explorer.keys');key('Down');check('virtual-keyboard arrow moves real file row reader focus',reader_focus('subfolder')['focus']['role']=='list item')
  key('Down');check('virtual-keyboard next file arrow retains named reader focus',reader_focus('alpha-long-file-name-to-test-eliding.txt')['focus']['role']=='list item')
  key('F2');check('virtual-keyboard F2 opens named text prompt',reader_focus('Rename','text')['focus']['role']=='text')
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
  key('Tab');check('virtual-keyboard Home filter Tab announces next name',reader_focus('Documents')['focus']['role']=='button')
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
   log=O/'opener.jsonl'
   return log.exists() and any(json.loads(line)['path']==str(path) and json.loads(line)['sha256']==sha(path) for line in log.read_text().splitlines())
  wait(opened,'captured real opener dispatch');check('Home actual reader recent file captured opener reads real file',opened())
  home();wait(lambda:json.loads(ipc('focusInfo','Treemap.t')).get('valid'),'actual storage scan',15)
  target=perform('Treemap.t');check('Home actual reader storage directory',json.loads(ipc('state'))['cwd']==str(sandbox_path(target,'storage')))
  folder();ipc('focus','Explorer.keys');key('Down');key('i',('ctrl',));perform('Close details')
  check('actual reader closes compact details overlay',not json.loads(ipc('uiState'))['detailOverlayRequested'])
  folder();ipc('focus','Explorer.keys');key('Down');key('Menu');perform('ContextMenu.menuRow')
  check('actual reader file menu Open uses captured sandbox directory',json.loads(ipc('state'))['cwd']==str(O/'home/fixture/subfolder'))
  folder();ipc('focus','Explorer.keys');key('Down');key('Down');key('F2');reader_focus('Rename','text')
  source=O/'home/fixture/alpha-long-file-name-to-test-eliding.txt';beforeHash=sha(source)
  key('a',('ctrl',));run('wtype','reader-renamed.txt');time.sleep(.25)
  check('actual Orca text query sees edited sandbox name',(state().get('focus') or {}).get('text')=='reader-renamed.txt',readerState=state())
  check('actual Orca WhereAmI reads edited native input',dbus('WhereAmIPresenter','ExecuteCommand',GLib.Variant('(sb)',('WhereAmIBasic',True))))
  time.sleep(.25);perform('Prompt.acceptBtn')
  renamed=O/'home/fixture/reader-renamed.txt';wait(lambda:renamed.exists() and not source.exists(),'real sandbox rename')
  check('actual reader prompt accept runs unchanged real rename preserving bytes',sha(renamed)==beforeHash)
  report['openerBoundary']='The existing xdg-open invocation is captured by a sandbox-only executable that reads the actual target and records its hash; no default-association GUI launch claim.'
  speech=[json.loads(s) for s in (O/'utterances.jsonl').read_text().splitlines() if s]
  check('actual reader silently presents edited native input',any(s.get('kind')=='speech' and 'reader-renamed.txt' in str(s.get('text','')) for s in speech))
  check('real reader generated silent utterances',any(s['kind']=='speech' and s['text'] for s in speech),utteranceCount=len(speech))
except Exception as e:report['error']=repr(e)
finally:
 report['fixtureCleanup']=[]
 for label,process in [('reader',reader),('copiedFiles',app)]:
  if process is None:continue
  item={'name':label,'pid':process.pid,'ownNewSession':True,'forcedKill':False}
  try:
   if process.poll() is None:
    if label=='copiedFiles':
     try:ipc('shutdown')
     except Exception as error:item['hideError']=repr(error)
    os.killpg(process.pid,signal.SIGTERM)
    try:process.wait(timeout=8)
    except subprocess.TimeoutExpired:
     item['forcedKill']=True;os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=4)
   item['exitCode']=process.poll();item['exited']=process.poll() is not None
  except Exception as error:item['error']=repr(error);item['exited']=process.poll() is not None
  report['fixtureCleanup'].append(item)
 p=report['preservation']={}
 def retain(name,fn):
  try:p[name]=bool(fn())
  except Exception as error:p[name]=False;report.setdefault('preservationErrors',{})[name]=repr(error)
 try:existing={w['address']:w for w in data('clients')}
 except Exception as error:report.setdefault('preservationErrors',{})['line5']=repr(error)
 retain('originalCanonicalClients',lambda: canonical_clients(list(existing.values()))==canonical_clients(initial))
 try:
  if focus.get('address') in existing and existing[focus['address']].get('stableId')==focus.get('stableId'):run('hyprctl','dispatch',f'hl.dsp.focus({{window="address:{focus["address"]}"}})')
 except Exception as error:report.setdefault('preservationErrors',{})['line8']=repr(error)
 try:run('hyprctl','dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})');time.sleep(.2)
 except Exception as error:report.setdefault('preservationErrors',{})['line10']=repr(error)
 retain('originalFocus',lambda: data('activewindow').get('stableId')==focus.get('stableId'))
 retain('originalCursor',lambda: data('cursorpos')==cursor)
 retain('originalLayers',lambda: data('layers')==layers)
 try:report['catalogImmediatelyAfterCleanup']={name:{'exactBytes':preservation.file_bytes(H/'.config/omarchy'/name)==raw,'expectedSHA256':preservation.digest(raw),'actualSHA256':preservation.digest(preservation.file_bytes(H/'.config/omarchy'/name))} for name,(raw,_) in catalogs.items()}
 except Exception as error:report.setdefault('preservationErrors',{})['line15']=repr(error)
 try:report['catalogNaturalSettling']=preservation.settle_catalogs({str(H/'.config/omarchy'/name):raw for name,(raw,_) in catalogs.items()},seconds=4)
 except Exception as error:report.setdefault('preservationErrors',{})['line17']=repr(error)
 retain('allFourCatalogBytes',lambda: all(c['exactBytes'] for c in report['catalogNaturalSettling'].values()))
 retain('originalFullUiState',lambda: json.loads(run('qs','-p',H/'.local/share/omarchy-files','ipc','call','files','uiState'))==json.loads(original_ui))
 retain('sharedReaderProfileBytes',lambda: sha(shared_profile)==shared_profile_sha)
 retain('originalProcessStart',lambda: Path('/proc/667402/stat').read_text().rsplit(')',1)[1].split()[19]==original_start)
 retain('clipboardAndPrimaryRawAndMimeHashes',lambda: [clips(),clips(True)]==clip)
 retain('catalogBytes',lambda: sha(catalog)==catsha)
 retain('dashboardBytes',lambda: sha(dashboard)==dashsha)
 retain('originalExplorerPublicState',lambda: hashlib.sha256(run('qs','-p',H/'.local/share/omarchy-files','ipc','call','files','state').encode()).hexdigest()==oldpublic)
 retain('originalExplorerPID',lambda: Path('/proc/667402').exists())
 retain('originalExplorerHidden',lambda: not any(w['pid']==667402 for w in existing.values()))
 retain('a11yFlags',lambda: flags==[run('gsettings','get',s,k) for s,k in [('org.gnome.desktop.a11y.applications','screen-reader-enabled'),('org.gnome.desktop.interface','toolkit-accessibility')]])
 retain('a11ySocketConnectivity',lambda: socket_before==a11y_socket() and socket_before['connects'])
 retain('readerEnabledProperty',lambda: preservation.reader_status()==reader_enabled)
 retain('originalOutputs',lambda: preservation.project_outputs(data('monitors'))==outputs_before)
 retain('originalPlugins',lambda: run('hyprctl','plugin','list')==plugins_before)
 retain('originalKeyboardStates',lambda: keyboard_state()==keyboards_before)
 retain('frozenDependencies',lambda: verify_manifest(B/'frozen-inputs.json',raise_on_failure=False) and verify_manifest(O/'executed-inputs.json',raise_on_failure=False))
 retain('fixturesNormalShutdown',lambda: all(item.get('exited') and not item.get('error') and not item['forcedKill'] and item.get('exitCode') not in [-6,-11] for item in report['fixtureCleanup']))
 retain('fixturesExited',lambda: all(process.poll() is not None for process in (app,reader) if process is not None))
 retain('responsiveManifestBytes',lambda: sha(B.parents[2]/'files-responsive/source-hashes.json')==original_state)
 report['result']='pass' if not report.get('error') and not report.get('preservationErrors') and not report['failures'] and all(p.values()) else 'fail'
 app_log.close();reader_log.close();(O/'native-reader-report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'result':report['result'],'checks':len(report['checks']),'error':report.get('error'),'preservation':p},indent=2))
sys.exit(report['result']!='pass')
