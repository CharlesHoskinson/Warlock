#!/usr/bin/env python3
"""Root-coordinated physical Qt keys plus real silent Orca; isolated copied Files."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from atspi_qa import assistive_session
import gi
from gi.repository import Gio,GLib
B=Path(__file__).resolve().parent;H=Path.home();READER=B.parent/'orca-reader'
bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
report={'scope':'Isolated copied Files on native Wayland; physical Qt keyboard plus actual Orca focus/navigation/press actions; silent speech log','checks':[],'failures':[]}
app=reader=None;app_log=(B/'native.log').open('w');reader_log=(B/'reader.log').open('w')
def run(*a):return subprocess.check_output(list(map(str,a)),text=True,timeout=8).strip()
def data(n):return json.loads(run('hyprctl',n,'-j'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
def clips(primary=False):
 opts=['--primary'] if primary else [];out=[]
 for mode in ('--no-newline','--list-types'):
  r=subprocess.run(['wl-paste',*opts,mode],capture_output=True,timeout=4);out.append((r.returncode,hashlib.sha256(r.stdout).hexdigest()))
 return out
def blocked():return [s for m in data('layers').values() for ss in m.get('levels',{}).values() for s in ss if s.get('alpha',1)>0 and ('sudo-askpass' in s.get('namespace','') or 'hyprlock' in s.get('namespace',''))]
assert not blocked(),'foreign input grab'
initial=data('clients');focus=data('activewindow');cursor=data('cursorpos');layers=data('layers');clip=[clips(),clips(True)]
catalog=H/'.config/omarchy/virtual-desktops.json';dashboard=H/'.local/state/omarchy-files/dashboard.json';catsha=sha(catalog);dashsha=sha(dashboard)
original_state=sha(B.parent/'files-responsive/source-hashes.json')
oldpublic=hashlib.sha256(run('qs','-p',H/'.local/share/omarchy-files','ipc','call','files','state').encode()).hexdigest()
flags=[run('gsettings','get',s,k) for s,k in [('org.gnome.desktop.a11y.applications','screen-reader-enabled'),('org.gnome.desktop.interface','toolkit-accessibility')]]
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
try:
 with assistive_session():
  env=dict(os.environ,HOME=str(B/'isolated-home'),FILES_STATE=str(B/'isolated-state'),FILES_DRYRUN='1',FILES_OPEN='home',XDG_CACHE_HOME=str(B/'isolated-cache'))
  env.pop('QT_QPA_PLATFORM',None)
  app=subprocess.Popen(['qs','-p',str(B/'qa-app')],env=env,stdout=app_log,stderr=app_log)
  w=wait(lambda:next((w for w in data('clients') if w['pid']==app.pid and w['title']=='Files Responsive QA'),None),'native fixture maps')
  identity=(w['address'],w['stableId'],w['pid']);report['fixtureIdentity']=identity
  run('hyprctl','dispatch',f'hl.dsp.window.resize({{x=330,y=320,window="address:{w["address"]}"}})')
  wait(lambda:own()['size']==[330,320],'native minimum')
  run('hyprctl','dispatch',f'hl.dsp.focus({{window="address:{w["address"]}"}})')
  check('native minimum330x320',own()['size']==[330,320])
  (B/'utterances.jsonl').write_text('')
  renv=dict(os.environ,ORCA_QA_UTTERANCES=str(B/'utterances.jsonl'))
  reader=subprocess.Popen([str(READER/'run-orca-native-wayland'),'--debug-file',str(B/'reader.debug')],env=renv,stdout=reader_log,stderr=reader_log)
  wait(state,'actual Orca native loop',15)
  check('real Orca native Wayland loop ready',reader.poll() is None)
  ipc('focus','Home');check('Orca recognizes actual named Home button',reader_focus('Home')['focus']['role']=='button')
  key('Tab');check('physical Tab produces actual Orca button focus',(state().get('focus') or {}).get('role')=='button',readerState=state())
  ipc('open',str(B/'isolated-home/fixture'));wait(lambda:json.loads(ipc('state'))['entries']==4,'fixture folder')
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
 p['originalClientsGeometries']=len(existing)==len(initial) and all(w['address'] in existing and all(existing[w['address']].get(k)==w.get(k) for k in ('pid','stableId','workspace','at','size','pinned','fullscreen')) for w in initial)
 if focus.get('address') in existing and existing[focus['address']].get('stableId')==focus.get('stableId'):run('hyprctl','dispatch',f'hl.dsp.focus({{window="address:{focus["address"]}"}})')
 run('hyprctl','dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})');time.sleep(.2)
 p['originalFocus']=data('activewindow').get('stableId')==focus.get('stableId');p['originalCursor']=data('cursorpos')==cursor;p['originalLayers']=data('layers')==layers
 p['clipboardAndPrimaryRawAndMimeHashes']=[clips(),clips(True)]==clip;p['catalogBytes']=sha(catalog)==catsha;p['dashboardBytes']=sha(dashboard)==dashsha
 p['originalExplorerPublicState']=hashlib.sha256(run('qs','-p',H/'.local/share/omarchy-files','ipc','call','files','state').encode()).hexdigest()==oldpublic
 p['originalExplorerPID']=Path('/proc/667402').exists();p['originalExplorerHidden']=not any(w['pid']==667402 for w in existing.values())
 p['a11yFlags']=flags==[run('gsettings','get',s,k) for s,k in [('org.gnome.desktop.a11y.applications','screen-reader-enabled'),('org.gnome.desktop.interface','toolkit-accessibility')]]
 p['a11ySocketInode']=socketstat is None or (socket.exists() and socket.stat().st_ino==socketstat.st_ino)
 p['responsiveManifestBytes']=sha(B.parent/'files-responsive/source-hashes.json')==original_state
 report['result']='pass' if not report.get('error') and not report['failures'] and all(p.values()) else 'fail'
 app_log.close();reader_log.close();(B/'native-reader-report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'result':report['result'],'checks':len(report['checks']),'error':report.get('error'),'preservation':p},indent=2))
sys.exit(report['result']!='pass')
