#!/usr/bin/env python3
"""Qt events delivered only inside isolated offscreen Quickshell; no compositor input."""
from pathlib import Path
import json,os,subprocess,time,sys
B=Path(__file__).resolve().parent
report={'scope':'Actual copied QML and Qt event routing on offscreen QQuickWindow; no native physical input or reader claim','checks':[]}
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',HOME=str(B/'home'),FILES_STATE=str(B/'state'),FILES_DRYRUN='1',FILES_OPEN='home',XDG_CACHE_HOME=str(B/'cache'))
env.pop('WAYLAND_DISPLAY',None);env.pop('DISPLAY',None);env['DBUS_SESSION_BUS_ADDRESS']='unix:path='+str(B/'no-shared-session-bus')
env['QT_QPA_PLATFORMTHEME']='';env['QT_STYLE_OVERRIDE']='Fusion'
log=(B/'offscreen-keys.log').open('w'); p=None
def check(name,value):
 report['checks'].append({'name':name,'passed':bool(value)});assert value,name
try:
 p=subprocess.Popen(['qs','-p',str(B/'app')],env=env,stdout=log,stderr=log)
 def ipc(name,*args):return subprocess.check_output(['qs','ipc','--pid',str(p.pid),'call','files-keyboard-qa',name,*map(str,args)],text=True,timeout=6).strip()
 def wait(fn):
  end=time.monotonic()+5
  while time.monotonic()<end:
   try:
    if fn():return
   except subprocess.CalledProcessError:pass
   time.sleep(.05)
  raise AssertionError('fixture not ready')
 wait(lambda:json.loads(ipc('state'))['view']=='home')
 def state():return json.loads(ipc('state'))
 def ui():return json.loads(ipc('uiState'))
 def key(k,mods=0):check('Qt event delivered '+str(k),ipc('key',k,mods)=='true');time.sleep(.12)
 check('Installed V7 real QML/native V6 instantiate',p.poll() is None)
 check('named toolbar Home can focus',ipc('focus','Home')=='true')
 key(16777217);check('Tab skips disabled Back/Forward/Up/View/Sort/Details on Home',ipc('locus')=='Btn.root')
 ipc('open',str(B/'isolated-home/fixture'));wait(lambda:state()['entries']==4)
 check('View button can focus',ipc('focus','Show list')=='true')
 key(16777220);check('Return activates existing View callback',state()['mode']=='list')
 check('Sort can focus',ipc('focus','Sort')=='true');key(16777220)
 check('Sort opens existing menu',ui()['menu']['visible'])
 key(16777216);check('menu Escape closes',not ui()['menu']['visible'])
 check('toolbar focus retained for shortcut test',ipc('focus','Sort')=='true')
 key(70,0x04000000);check('Ctrl F bubbles to existing command handler',ipc('locus')=='Explorer.filterInput')
 key(16777216);check('filter Escape restores main focus',ipc('locus')=='Explorer.keys')
 ipc('act','prompt','');check('existing NewFolder prompt owns text focus',ipc('locus')=='Prompt.input')
 key(16777217);check('prompt Tab input to Cancel',ipc('locus')=='Prompt.cancelBtn')
 key(16777217);check('prompt Tab Cancel to accept',ipc('locus')=='Prompt.acceptBtn')
 key(16777217);check('prompt Tab traps accept to input',ipc('locus')=='Prompt.input')
 key(16777218,0x02000000);check('prompt Backtab traps input to accept',ipc('locus')=='Prompt.acceptBtn')
 key(16777216);check('prompt Escape cancels without operation',not ui()['prompt']['visible'] and state()['entries']==4)
 ipc('resize',330,320);wait(lambda:ui()['windowWidth']==330 and ui()['windowHeight']==320)
 check('330x320 actual Qt window instantiated',ui()['windowWidth']==330 and ui()['windowHeight']==320)
 ipc('act','view','list');ipc('focus','Explorer.keys');key(16777237)
 check('list arrow owns real accessible row focus',ipc('locus')=='FileArea.row' and state()['cur']==0)
 key(16777237);check('list next arrow moves focus and selection',ipc('locus')=='FileArea.row' and state()['cur']==1)
 key(16777301);check('Menu key opens current file context menu',ui()['menu']['visible'])
 key(16777237);check('menu Down focuses actual row',ipc('locus')=='ContextMenu.menuRow')
 key(16777216);check('menu closes to original file commands',not ui()['menu']['visible'])
 ipc('act','view','grid');ipc('focus','Explorer.keys');key(16777237)
 check('grid arrow owns real accessible cell focus',ipc('locus')=='FileArea.cl' and state()['cur']==2)
 key(66,0x04000000);check('Ctrl B focuses compact sidebar collection',ipc('locus')=='Explorer.cr' and ui()['sidebarRequested'])
 key(16777217);check('sidebar Tab reaches next collection',ipc('locus')=='Explorer.cr')
 key(16777216);check('sidebar Escape closes and returns command focus',not ui()['sidebarRequested'] and ipc('locus')=='Explorer.keys')
 key(66,0x04000000);ipc('focus','Tree.row');key(16777237)
 check('tree Down keeps real row focus',ipc('locus')=='Tree.row')
 key(16777216);check('tree Escape closes compact sidebar',not ui()['sidebarRequested'])
 ipc('open','home');wait(lambda:state()['view']=='home')
 check('Home filter can receive real focus',ipc('focus','Dashboard.filterChip')=='true')
 key(16777217);check('Home filter Tab reaches another chip',ipc('locus')=='Dashboard.filterChip')
 check('Home collection card has real focus',ipc('focus','Dashboard.cc')=='true')
 key(16777220);check('Home collection Return uses existing navigation',state()['view']=='folder' and state()['coll']=='recent')
except Exception as e:report['error']=repr(e)
finally:
 if p and p.poll() is None:
  try:ipc('toggle');time.sleep(.1)
  except Exception:pass
  p.terminate()
  try:p.wait(timeout=8)
  except subprocess.TimeoutExpired:report['cleanupError']='normal teardown timed out'
 log.close();report['exitCode']=p.poll() if p else None
 report['result']='pass' if not report.get('error') and not report.get('cleanupError') and all(c['passed'] for c in report['checks']) else 'fail'
 (B/'offscreen-keys-report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'result':report['result'],'checks':len(report['checks']),'error':report.get('error')},indent=2))
sys.exit(report['result']!='pass')
