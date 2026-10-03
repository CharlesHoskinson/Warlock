from pathlib import Path
import os,subprocess,json,time
B=Path(__file__).resolve().parent
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QPA_PLATFORMTHEME='',QT_STYLE_OVERRIDE='Fusion',DBUS_SESSION_BUS_ADDRESS='unix:path='+str(B/'no-session-bus'),HOME=str(B/'home'),FILES_STATE=str(B/'state'),FILES_OPEN='home',FILES_DRYRUN='1')
env.pop('WAYLAND_DISPLAY',None);env.pop('DISPLAY',None)
log=(B/'preflight-fixed.log').open('w');p=subprocess.Popen(['qs','-p',str(B/'qa-app')],env=env,stdout=log,stderr=log);r={}
def ipc(n,*a):return subprocess.check_output(['qs','ipc','--pid',str(p.pid),'call','files-keyboard-qa',n,*map(str,a)],text=True,timeout=5).strip()
try:
 time.sleep(.5);ipc('resize',330,320);time.sleep(.3);ipc('open',B/'home/fixture');time.sleep(.6);ipc('key',66,0x04000000);time.sleep(.2)
 r['tree']=json.loads(ipc('focusInfo','Tree.row'));r['height']=json.loads(ipc('uiState'))['windowHeight'];r['sidebarScroll']=json.loads(ipc('uiState'))['sidebarScroll'];r['treeFitsViewport']=r['tree'].get('y',10000)+r['tree'].get('height',1)<=r['height'];assert r['treeFitsViewport']
 for _ in range(12):
  current=json.loads(ipc('focusedInfo'))
  if current.get('logicalIdentity')=='tree:'+str(B/'home/fixture'):break
  ipc('key',16777237,0);time.sleep(.08)
 assert current.get('logicalIdentity')=='tree:'+str(B/'home/fixture'),current
 ipc('key',16777236,0);time.sleep(.5);ipc('key',16777236,0);time.sleep(.15)
 r['deepTree']=json.loads(ipc('focusedInfo'));r['deepTreeFitsViewport']=r['deepTree']['y']>=0 and r['deepTree']['y']+r['deepTree']['height']<=r['height']
 r['deepLogicalPath']=r['deepTree']['logicalIdentity']=='tree:'+str(B/'home/fixture/subfolder')
 assert r['deepTreeFitsViewport'] and r['deepLogicalPath'],r
finally:
 if p.poll() is None:
  ipc('shutdown');p.terminate();p.wait(timeout=8)
 log.close();(B/'preflight-tree-fixed.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
