#!/usr/bin/env python3
"""Run only in root-coordinated GUI slot; copied real app, silent reader not involved."""
from pathlib import Path
import subprocess,json,time,os,hashlib,re,sys
H=Path.home();B=Path(__file__).resolve().parent
report={'checks':[],'failures':[],'scope':'Copied real Files QML on main Wayland compositor; own window physical input and actual snap'}
def run(*a,timeout=10):return subprocess.check_output(list(map(str,a)),text=True,timeout=timeout).strip()
def ctl(*a):return run('hyprctl',*a)
def data(name):return json.loads(ctl(name,'-j'))
def wait(fn,label):
 end=time.monotonic()+8
 while time.monotonic()<end:
  x=fn()
  if x:return x
  time.sleep(.08)
 raise AssertionError(label)
def close(a,b):return len(a)==len(b) and all(abs(x-y)<=1 for x,y in zip(a,b))
def check(name,value,**detail):
 report['checks'].append(dict(name=name,passed=bool(value),**detail))
 if not value:report['failures'].append(name)
 assert value,name

def clipboard(primary=False):
 opts=['--primary'] if primary else []
 r=subprocess.run(['wl-paste',*opts,'--no-newline'],capture_output=True,timeout=4)
 types=subprocess.run(['wl-paste',*opts,'--list-types'],capture_output=True,timeout=4)
 return {'exit':r.returncode,'bytes':len(r.stdout),'sha256':hashlib.sha256(r.stdout).hexdigest(),'typesSha256':hashlib.sha256(types.stdout).hexdigest()}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
initial=data('clients');focus=data('activewindow');cursor=data('cursorpos');monitors=data('monitors');devices=data('devices')
clip=[clipboard(),clipboard(True)]
catalog=H/'.config/omarchy/virtual-desktops.json';catalog_before=sha(catalog)
snapstate=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr-snap-groups/state.json';snapbytes=snapstate.read_bytes() if snapstate.exists() else None
userstate=H/'.local/state/omarchy-files/dashboard.json';userstate_before=sha(userstate)
original_state=run('qs','-p',H/'.local/share/omarchy-files','ipc','call','files','state');original_state_hash=hashlib.sha256(original_state.encode()).hexdigest()
flags=[run('gsettings','get',s,k) for s,k in [('org.gnome.desktop.a11y.applications','screen-reader-enabled'),('org.gnome.desktop.interface','toolkit-accessibility')]]
process=None;pointer=None;address=None;identity=None
log=(B/'native.log').open('w')
try:
 env=dict(os.environ,HOME=str(B/'isolated-home'),FILES_STATE=str(B/'isolated-state'),FILES_DRYRUN='1',FILES_OPEN='home',XDG_CACHE_HOME=str(B/'isolated-cache'))
 process=subprocess.Popen(['qs','-p',str(B/'qa-app')],env=env,stdout=log,stderr=log)
 def window():return next((w for w in data('clients') if w['pid']==process.pid and w['title']=='Files Responsive QA'),None)
 w=wait(window,'QA app maps');address=w['address'];identity=(address,w['stableId'],w['pid']);report['fixtureIdentity']=identity
 def own():
  z=window();assert z and (z['address'],z['stableId'],z['pid'])==identity,'fixture identity changed';return z
 def ipc(fn,*a):return run('qs','ipc','--pid',process.pid,'call','files-responsive-qa',fn,*a)
 def probe():return json.loads(ipc('probe'))
 def state():return json.loads(ipc('state'))
 def native_focus():ctl('dispatch',f'hl.dsp.focus({{window="address:{address}"}})');wait(lambda:data('activewindow').get('address')==address,'own focus')
 def arrange(width,height):
  ctl('eval',f'hypr_snap_forget("{address}")')
  ctl('dispatch',f'hl.dsp.window.resize({{x={width},y={height},window="address:{address}"}})')
  ctl('dispatch',f'hl.dsp.window.move({{x=120,y=250,window="address:{address}"}})')
  wait(lambda:close(own()['size'],[width,height]) and [probe()['width'],probe()['height']]==own()['size'],'actual client size');time.sleep(.35);native_focus()
 m=next(m for m in monitors if m['focused']);logicalW=round(m['width']/m['scale']);logicalH=round(m['height']/m['scale'])
 pointer=subprocess.Popen([str(H/'.local/share/hypr-window-controls/qa/virtual-pointer'),str(logicalW),str(logicalH)],stdin=subprocess.PIPE,text=True,stdout=subprocess.DEVNULL,stderr=log)
 def click(x,y):
  w=own();assert 0<=x<w['size'][0] and 0<=y<w['size'][1],(x,y,w['size']);native_focus()
  pointer.stdin.write(f'move {w["at"][0]+x} {w["at"][1]+y}\nsleep 120\nbutton 272 1\nsleep 60\nbutton 272 0\nsleep 160\n');pointer.stdin.flush();time.sleep(.4)
  assert data('activewindow').get('address')==address,'pointer input lost own focus'
 def keys(*a):native_focus();run('wtype',*a);time.sleep(.25)
 def scroll(x,y):
  w=own();pointer.stdin.write(f'move {w["at"][0]+x} {w["at"][1]+y}\nsleep 100\n'+('wheel 120\nsleep 100\n'*8));pointer.stdin.flush();time.sleep(2)
 def shot(label):ipc('shot','explorer',str(B/'native-shots'/f'{label}.png'));time.sleep(.15)
 (B/'native-shots').mkdir(exist_ok=True)
 for width,height in [(330,320),(487,320),(500,320),(533,320),(800,500)]:
  arrange(width,height);ipc('scenario','folder-list');time.sleep(.35);p=probe()
  check(f'actual native client accepts {width}x{height}',close(own()['size'],[width,height]) and not p['negative'],requested=[width,height],size=own()['size'],allowedFractionalScaleRounding=1,pathWidth=p['rects']['path']['w'],filterWidth=p['rects']['filter']['w']);shot(f'{width}x{height}-list')
 arrange(600,400);normal=own()['at']+own()['size'];r=list(map(float,ctl('repl','local r=hl.get_active_monitor().reserved;print(r.top,r.bottom,r.left,r.right)').split()));x=m['x']+r[2]+10;y=m['y']+r[0]+34;ww=logicalW-r[2]-r[3]-20;hh=logicalH-r[0]-r[1]-44
 expected={'left':[x,y,int((ww-10)//2),hh],'top_left':[x,y,int((ww-10)//2),int((hh-34)//2)],'third_left':[x,y,int((ww-20)//3),hh]}
 for zone,rect in expected.items():
  ctl('eval',f'hypr_snap_zone("{zone}","{address}",false)');wait(lambda:close(own()['at']+own()['size'],rect),'snap zone '+zone);time.sleep(.3)
  check('actual '+zone+' snap fits minimum',close(own()['at']+own()['size'],rect) and probe()['width']==own()['size'][0],requestedRect=rect,actualRect=own()['at']+own()['size'],allowedFractionalScaleRounding=1)
  shot('snap-'+zone);ctl('eval',f'hypr_snap_restore("{address}")');wait(lambda:close(own()['at']+own()['size'],normal),'snap restore normal')
  check('actual '+zone+' unsnap restores normal',close(own()['at']+own()['size'],normal))
 arrange(330,320);ipc('scenario','folder-list');time.sleep(.4);p=probe();r=p['rects']
 # New actions stay present and call the existing prompt semantics.
 click(55,r['files']['y']+58);check('physical New Folder opens mkdir prompt',ipc('act','promptinfo','').startswith('mkdir |'));keys('-k','Escape')
 click(130,r['files']['y']+58);check('physical New File opens newfile prompt',ipc('act','promptinfo','').startswith('newfile |'));keys('-k','Escape')
 keys('-M','ctrl','-k','f','-m','ctrl');keys('alpha');check('physical CtrlF filter works at330',state()['filter']=='alpha' and state()['count']==1);keys('-k','Escape');check('physical Escape clears filter',state()['filter']=='')
 keys('-M','ctrl','-k','l','-m','ctrl');keys(str(B/'isolated-home/fixture/subfolder'));keys('-k','Return');check('physical CtrlL navigates compact path',state()['cwd']==str(B/'isolated-home/fixture/subfolder'))
 keys('-M','alt','-k','Left','-m','alt');check('physical AltLeft restores folder history',state()['cwd']==str(B/'isolated-home/fixture'))
 p=probe();t=p['rects']['tools'];click(t['x']+15,t['y']+15);check('physical View button switches grid',state()['mode']=='grid');p=probe();check('physical grid switch keeps filename/meta visible at330x320',p['thumbHeight']+52<=p['named']['FileArea.gridList']['h']+.1);shot('330-grid-name-visible');click(t['x']+15,t['y']+15);check('physical View button restores list',state()['mode']=='list')
 click(t['x']+49,t['y']+15);keys('-k','Down','-k','Down','-k','Down','-k','Down','-k','Return');check('physical Sort menu reaches compact hidden Kind column',state()['sort'].startswith('kind'))
 keys('-M','ctrl','-k','b','-m','ctrl');check('physical CtrlB opens compact sidebar',probe()['rects']['sidebar']['visible']);scroll(150,210);p=probe();check('physical sidebar wheel reaches tree',p['named']['Tree.list']['y']>=128 and p['named']['Tree.list']['y']+p['named']['Tree.list']['h']<=294);shot('330-sidebar-tree');keys('-k','Escape');check('physical Escape dismisses sidebar',not probe()['rects']['sidebar']['visible'])
 click(100,251);check('physical selection preserves full compact file area',state()['sel'] and not probe()['detailVisible'] and probe()['rects']['files']['w']==330)
 keys('-M','ctrl','-k','i','-m','ctrl');check('physical CtrlI opens details overlay',probe()['detailVisible'] and probe()['rects']['files']['w']==330)
 scroll(180,230);p=probe();b=p['named']['Btn.root'];check('physical details wheel reaches Trash action',128<=b['y'] and b['y']+b['h']<=294,button=b);shot('330-details-actions')
 # Rename is the second cell of the row immediately above Trash.
 click(230,b['y']-32-8+16);check('physical compact details Rename preserves prompt payload',ipc('act','promptinfo','').startswith('rename |'));keys('-k','Escape');keys('-k','Escape');check('physical Escape dismisses details',not probe()['detailVisible'])
 keys('-k','Space');check('physical Space opens compact preview',state()['lb']);shot('330-preview');keys('-k','Escape');check('physical Escape closes preview',not state()['lb'])
 check('original explorer remains same hidden process',Path('/proc/667402').exists() and not any(w['pid']==667402 for w in data('clients')))
except Exception as e:
 report['error']=repr(e)
 if address:
  report['lastFixture']=window()
  try:report['lastLayout']=probe()
  except Exception:pass
finally:
 if pointer:
  pointer.stdin.close();pointer.wait(timeout=4)
 if address:
  subprocess.run(['hyprctl','eval',f'hypr_snap_forget("{address}")'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  subprocess.run([str(H/'.local/bin/hypr-snap-groups'),'forget',address],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 if process and process.poll() is None:
  try:run('qs','ipc','--pid',process.pid,'call','files-responsive-qa','toggle');time.sleep(.25)
  except Exception:pass
  process.terminate()
  try:process.wait(timeout=8)
  except subprocess.TimeoutExpired:report['cleanupError']='normal copied-app termination timed out; no SIGKILL used'
 existing=data('clients')
 if snapbytes is None:snapstate.unlink(missing_ok=True)
 else:snapstate.write_bytes(snapbytes)
 old={w['address']:w for w in initial};new={w['address']:w for w in existing}
 originals=all(a in new and all(new[a].get(k)==w.get(k) for k in ('pid','stableId','workspace','at','size','pinned','fullscreen')) for a,w in old.items())
 def finalcheck(name,value):
  report['checks'].append(dict(name=name,passed=bool(value)))
  if not value:report['failures'].append(name)
 finalcheck('original clients and geometries preserved',originals)
 if focus.get('address') in new and new[focus['address']].get('stableId')==focus.get('stableId'):ctl('dispatch',f'hl.dsp.focus({{window="address:{focus["address"]}"}})')
 ctl('dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})');time.sleep(.2)
 finalcheck('original cursor restored',data('cursorpos')==cursor)
 finalcheck('original focus restored',data('activewindow').get('stableId')==focus.get('stableId'))
 finalcheck('original catalog bytes unchanged',sha(catalog)==catalog_before)
 finalcheck('original explorer dashboard bytes unchanged',sha(userstate)==userstate_before)
 finalcheck('original explorer navigation selection history unchanged',hashlib.sha256(run('qs','-p',H/'.local/share/omarchy-files','ipc','call','files','state').encode()).hexdigest()==original_state_hash)
 afterclip=[clipboard(),clipboard(True)];finalcheck('clipboard and primary selection unchanged by raw byte hash and MIME hash',clip==afterclip)
 report['clipboardPreservation']={'method':'wl-paste --no-newline and --list-types, SHA256 comparison in memory; contents never printed/stored','matched':clip==afterclip}
 finalcheck('accessibility flags unchanged',flags==[run('gsettings','get',s,k) for s,k in [('org.gnome.desktop.a11y.applications','screen-reader-enabled'),('org.gnome.desktop.interface','toolkit-accessibility')]])
 beforekeys={k['name']:k for k in devices['keyboards'] if not k['name'].startswith('wtype')};afterkeys={k['name']:k for k in data('devices')['keyboards'] if not k['name'].startswith('wtype')}
 finalcheck('original physical keyboard layouts and locks preserved',all(n in afterkeys and all(afterkeys[n].get(k)==v.get(k) for k in ('active_keymap','numlock','capslock','main','rules','model','layout','variant','options')) for n,v in beforekeys.items() if not n.startswith('fcitx5')))
 finalcheck('copied fixture exits normally',process is None or process.poll()==0 or process.poll()==-15)
 report['exitCode']=process.poll() if process else None
 log.close()
 report['result']='pass' if not report.get('error') and not report.get('cleanupError') and not report['failures'] else 'fail'
 (B/'native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'result':report['result'],'checks':len(report['checks']),'failures':report['failures'],'error':report.get('error'),'exitCode':report['exitCode']},indent=2))
sys.exit(report['result']!='pass')
