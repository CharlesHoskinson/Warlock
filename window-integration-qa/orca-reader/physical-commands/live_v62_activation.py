#!/usr/bin/env python3
"""Narrow native AT-SPI taskbar activation regression for the v62 motion frontend."""
import json, subprocess, sys, time
from pathlib import Path
QA=Path(__file__).resolve().parent
sys.path.insert(0,str(QA.parent.parent))
from atspi_qa import assistive_session, find, invoke
H=Path.home();SHELL='/usr/share/omarchy/shell';processes=[]
report={'suite':'v62 native AX activation through motion frontend','checks':[]}
def run(*args):return subprocess.check_output([str(a) for a in args],text=True).strip()
def data(name):return json.loads(run('hyprctl',name,'-j'))
def taskbar():return json.loads(run('qs','-p',SHELL,'ipc','call','hoskinson.windows','state'))
def window(p):return next((w for w in data('clients') if w['pid']==p.pid),None)
def wait(fn,label):
 end=time.monotonic()+8
 while time.monotonic()<end:
  v=fn()
  if v:return v
  time.sleep(.1)
 raise AssertionError(label)
def check(name,value,**detail):
 report['checks'].append(dict(name=name,passed=bool(value),**detail));assert value,name
initial=data('activewindow');cursor=data('cursorpos');catalog=H/'.config/omarchy/virtual-desktops.json'
catalog_before=catalog.read_bytes() if catalog.exists() else None
clients_before={(w['address'],w['stableId'],w['pid']) for w in data('clients')}
with assistive_session():
 try:
  manifest=json.loads((H/'.config/omarchy/plugins/hoskinson.windows/manifest.json').read_text())
  assert manifest['entryPoints']['barWidget']=='widget_v62/Windows.qml',manifest
  for label,app in [('one','org.omarchy.readerv62activationqa'),('peer','org.omarchy.readerv62activationpeerqa')]:
   p=subprocess.Popen(['foot','--app-id='+app,'--title=Reader v62 activation '+label,'sleep','180'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);processes.append(p);wait(lambda:window(p),label)
  own,peer=processes;w=window(own);address=w['address'];identity=w['stableId'];geometry=w['at']+w['size']
  group=wait(lambda:next((g for g in taskbar()['taskbarItems'] if address in g['windows']),None),'own single taskbar group')
  assert group['windows']==[address],group
  def appnode():return wait(lambda:find(accessible_id='taskbar-app:'+group['key']),'own app accessibility node')
  run('hyprctl','dispatch',f'hl.dsp.focus({{window="address:{address}"}})');wait(lambda:data('activewindow').get('address')==address,'own focus')
  invoke(appnode());wait(lambda:window(own)['workspace']['name']=='special:win-minimized','AX activate minimizes active own window')
  check('AX app press minimizes exact active identity through activate',window(own)['stableId']==identity)
  wait(lambda:'minimized' in appnode().get_description().lower(),'minimized snapshot/accessibility description')
  check('minimized app remains semantically exposed',True)
  invoke(appnode());wait(lambda:window(own)['workspace']['name']!='special:win-minimized' and data('activewindow').get('address')==address,'AX activate restores own window')
  check('AX app press restores minimized exact identity and focus',window(own)['stableId']==identity)
  wait(lambda:window(own)['at']+window(own)['size']==geometry,'restore original geometry')
  check('AX restore preserves original native geometry',True,geometry=geometry)
  run('hyprctl','dispatch',f'hl.dsp.focus({{window="address:{window(peer)["address"]}"}})');wait(lambda:data('activewindow').get('address')==window(peer)['address'],'peer focus')
  invoke(appnode());wait(lambda:data('activewindow').get('address')==address,'AX inactive app focus')
  check('AX inactive app press raises exact window without minimizing',window(own)['workspace']['name']!='special:win-minimized')
  check('native user identities preserved',clients_before<={(w['address'],w['stableId'],w['pid']) for w in data('clients')})
  check('desktop catalog byte-for-byte preserved',(catalog.read_bytes() if catalog.exists() else None)==catalog_before)
  report['result']='pass'
 except Exception as e:report.update(result='fail',error=repr(e))
 finally:
  run('qs','-p',SHELL,'ipc','call','hoskinson.windows','dismiss')
  for p in processes:
   if p.poll() is None:p.terminate();p.wait(timeout=3)
  if initial.get('address'):run('hyprctl','dispatch',f'hl.dsp.focus({{window="address:{initial["address"]}"}})')
  run('hyprctl','dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
  (QA/'v62-activation-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2));assert report['result']=='pass'
