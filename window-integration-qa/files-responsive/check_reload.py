#!/usr/bin/env python3
"""Actual same-PID QML reload, default offscreen. Native requires root GUI slot."""
import json,os,subprocess,time,hashlib,signal,shutil,tempfile,sys
from pathlib import Path
B=Path(__file__).resolve().parent;report={'checks':[],'failures':[]};native='--native' in sys.argv
report['platform']='main-Wayland' if native else 'offscreen'
def run(*a):return subprocess.check_output(list(map(str,a)),text=True,timeout=10).strip()
def wait(fn,label):
 end=time.monotonic()+8
 while time.monotonic()<end:
  try:x=fn()
  except Exception:x=None
  if x:return x
  time.sleep(.08)
 raise AssertionError(label)
native_clients_before=json.loads(run('hyprctl','clients','-j')) if native else []
native_layers_before=json.loads(run('hyprctl','layers','-j')) if native else {}
def check(name,value,**detail):
 report['checks'].append(dict(name=name,passed=bool(value),**detail));assert value,name
 if not value:report['failures'].append(name)
with tempfile.TemporaryDirectory(prefix='files-reload-',dir=B) as d:
 root=Path(d);app=root/'app';shutil.copytree(Path.home()/'.local/share/omarchy-files',app)
 def host(stage):
  text=(stage/'shell.qml').read_text();a=text.index('  Widget {');b=text.index('  Explorer {',a);text=text[:a]+text[b:]
  text=text.replace('target: "files"','target: "files-reload-qa"').replace('if (which === "widget") widget.grab(path); else explorer.grab(path)','explorer.grab(path)')
  if 'function migrationStatus()' not in text:text=text.replace('    function state(): string { return explorer.state() }','    function state(): string { return explorer.state() }\n    function migrationStatus(): string { return JSON.stringify({pid:Quickshell.processId,instance:Quickshell.instanceId}) }')
  text=text.replace('    function state(): string { return explorer.state() }','    function state(): string { return explorer.state() }\n    function qaResize(w: string, h: string): void { explorer.visible=false; Qt.callLater(function(){explorer.implicitWidth=Number(w);explorer.implicitHeight=Number(h)}) }\n    function qaSidebar(): void { explorer.sidebarRequested=true }')
  return text
 (app/'shell.qml').write_text(host(app));p=app/'explorer/Explorer.qml';p.write_text(p.read_text().replace('title: "Files"','title: "Files Reload QA"'))
 env=dict(os.environ,HOME=str(B/'isolated-home'),FILES_STATE=str(root/'state'),FILES_DRYRUN='1',FILES_OPEN='home',XDG_CACHE_HOME=str(root/'cache'))
 if not native:env.update(QT_QPA_PLATFORM='offscreen',QT_QPA_PLATFORMTHEME='basic',QT_STYLE_OVERRIDE='Fusion',QT_QUICK_BACKEND='software',DISPLAY='',WAYLAND_DISPLAY='')
 process=None;log=(B/('reload-native.log' if native else 'reload-offscreen.log')).open('w')
 try:
  process=subprocess.Popen(['qs','-p',str(app)],env=env,stdout=log,stderr=log)
  def ipc(fn,*a):return run('qs','ipc','--pid',process.pid,'call','files-reload-qa',fn,*a)
  wait(lambda:json.loads(ipc('state')),'old copied IPC')
  ipc('act','go',str(B/'isolated-home/fixture'));wait(lambda:json.loads(ipc('state'))['entries']==4,'fixture directory loaded')
  ipc('act','go','home');ipc('toggle');before=json.loads(ipc('state'));meta=json.loads(ipc('migrationStatus'))
  check('legacy copied app has nontrivial Home history',before['view']=='home' and len(before['hist'])==3 and before['hIdx']==2)
  migration={'targetPid':process.pid,'targetInstance':meta['instance'],'legacyState':before,'visible':False,'promptInfo':ipc('act','promptinfo',''),'windowWidth':1320,'windowHeight':800}
  # Freeze only our copied process while atomic source writes coalesce.
  os.kill(process.pid,signal.SIGSTOP)
  try:
   m=app/'ui-migration.json';m.write_text(json.dumps(migration));m.chmod(0o600)
   for f in (B/'app').rglob('*.qml'):
    rel=f.relative_to(B/'app');text=host(B/'app') if rel==Path('shell.qml') else f.read_text()
    if rel==Path('explorer/Explorer.qml'):text=text.replace('title: "Files"','title: "Files Reload QA"')
    tmp=(app/rel).with_suffix('.qml.new');tmp.write_text(text);os.replace(tmp,app/rel)
  finally:os.kill(process.pid,signal.SIGCONT)
  wait(lambda:json.loads(ipc('migrationStatus')).get('ready'),'migration ready');time.sleep(.3)
  after=json.loads(ipc('state'));ui=json.loads(ipc('uiState'));loaded=json.loads(ipc('migrationStatus'))['initialization']
  check('snapshot is imported before backing window can map',loaded['resumed'] and loaded['visible'] is False and loaded['backingVisible'] is False and loaded['historyLength']==3 and loaded['historyIndex']==2)
  check('actual legacy reload retains exact same PID',json.loads(ipc('migrationStatus'))['pid']==process.pid and process.poll() is None)
  check('legacy history and public state unchanged',after==before)
  check('FILES_OPEN home cannot resurrect hidden migrated explorer',ui['visible'] is False)
  if native:
   clients=json.loads(run('hyprctl','clients','-j'));check('legacy reload leaves no mapped copied client',not any(w['pid']==process.pid for w in clients))
   check('hidden source reload creates no popup client',{(w['address'],w['pid'],w.get('stableId')) for w in clients}=={(w['address'],w['pid'],w.get('stableId')) for w in native_clients_before})
   check('hidden source reload creates no popup layer',json.loads(run('hyprctl','layers','-j'))==native_layers_before)
  # Guarded migration file is no longer needed; later cold instances cannot match it.
  (app/'ui-migration.json').unlink()
  ipc('qaResize','330','320');time.sleep(.2)
  ipc('act','go',str(B/'isolated-home/fixture'));wait(lambda:json.loads(ipc('state'))['entries']==4,'folder before persistent reload')
  ipc('act','select','alpha-long-file-name-to-test-eliding.txt');ipc('act','copy','');ipc('act','hidden','');ipc('act','sort','size');ipc('act','view','list');ipc('act','zoom','280');ipc('act','kind','image')
  ipc('act','detail','on');ipc('qaSidebar');ipc('act','prompt','');time.sleep(.2);before2=json.loads(ipc('state'));u1=json.loads(ipc('uiState'))
  check('future snapshot carries absolute clipboard and selection',u1['clip']['paths']==[str(B/'isolated-home/fixture/alpha-long-file-name-to-test-eliding.txt')] and list(u1['sel'])==u1['clip']['paths'])
  check('narrow future snapshot retains requested overlays',u1['windowWidth']==330 and u1['sidebarRequested'] and u1['detailOverlayRequested'])
  check('future snapshot includes pending prompt and dashboard filter',u1['prompt']['visible'] and u1['prompt']['mode']=='mkdir' and u1['dashboardKind']=='image')
  with (app/'shell.qml').open('a') as f:f.write('\n// persistence reload fixture\n')
  wait(lambda:'Reloading configuration' in (B/('reload-native.log' if native else 'reload-offscreen.log')).read_text(),'source watcher reload');time.sleep(.8)
  u2=json.loads(ipc('uiState'));after2=json.loads(ipc('state'))
  check('future persistent reload preserves same PID',process.poll() is None and json.loads(ipc('migrationStatus'))['pid']==process.pid)
  check('future persistent reload preserves public UI history/selection/clipboard/preferences',after2==before2)
  check('future persistent reload retains absolute clipboard and selection',u2['clip']==u1['clip'] and u2['sel']==u1['sel'])
  check('future persistent reload keeps prompt payload/text/selection',u2['prompt']==u1['prompt'])
  check('narrow future reload preserves geometry and requested overlays',u2['windowWidth']==330 and u2['windowHeight']==320 and u2['sidebarRequested'] and u2['detailOverlayRequested'])
  check('future persistent reload retains dashboard filter and hidden state',u2['dashboardKind']==u1['dashboardKind'] and not u2['visible'])
  check('successful source reload has no configuration error','ERROR:' not in (B/('reload-native.log' if native else 'reload-offscreen.log')).read_text())
  if native:
   check('future hidden reload creates no popup client',{(w['address'],w['pid'],w.get('stableId')) for w in json.loads(run('hyprctl','clients','-j'))}=={(w['address'],w['pid'],w.get('stableId')) for w in native_clients_before})
   check('future hidden reload creates no popup layer',json.loads(run('hyprctl','layers','-j'))==native_layers_before)
 except Exception as e:report['error']=repr(e)
 finally:
  if process and process.poll() is None:
   try:
    u=json.loads(ipc('uiState'))
    if u['visible']:ipc('toggle');time.sleep(.2)
   except Exception:pass
   process.terminate()
   try:process.wait(timeout=8)
   except subprocess.TimeoutExpired:report['cleanupError']='normal copied-process termination timed out'
  report['exitCode']=process.poll() if process else None;log.close()
  report['result']='pass' if not report.get('error') and not report.get('cleanupError') and all(x['passed'] for x in report['checks']) else 'fail'
  (B/('reload-native-report.json' if native else 'reload-offscreen-report.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
sys.exit(report['result']!='pass')
