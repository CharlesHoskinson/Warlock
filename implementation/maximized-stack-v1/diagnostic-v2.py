"""Isolated source-counterexample check; no main-desktop window actions."""
import importlib.util,json,os,subprocess,sys,time
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa')
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
require_qa_scope()
spec=importlib.util.spec_from_file_location('reviewed_stack_host',QA/'private-weston-aq-host-v4/weston_host.py')
host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
B=Path(__file__).resolve().parent
output=QA/('maximized-stack-diagnostic-'+str(time.time_ns()))
report={'kind':'isolated installed-core diagnostic; no Brave-specific acceptance','result':'fail','mainDisplayActions':False,'output':str(output)}
lua=b'''hl.config({ xwayland={enabled=false},animations={enabled=false},input={follow_mouse=2,float_switch_override_focus=0} })
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
hl.on("window.open",function(w) hl.dispatch(hl.dsp.window.float({action="set",window="address:"..w.address})) end)
'''
fixture='''import gi,sys\ngi.require_version("Gtk","4.0")\nfrom gi.repository import Gtk,GLib,Gdk\nw=Gtk.Window(title=sys.argv[1]);w.set_default_size(320,240)\np=Gtk.CssProvider();p.load_from_string("window { background: "+sys.argv[2]+"; }")\nGtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(),p,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)\nw.present();GLib.MainLoop().run()\n'''
def wait(fn):
 end=time.monotonic()+6
 while time.monotonic()<end:
  v=fn()
  if v:return v
  time.sleep(.04)
 raise RuntimeError('fixture deadline')
try:
 with host.PrivateHyprSession(output,dict(os.environ),800,600,lua,mesa_vendor=True) as s:
  env=dict(s.env,GTK_A11Y='none',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0')
  windows=[];apps=[]
  for name,color in [('STACK-MAX','#ff0000'),('STACK-PEER','#00ff00')]:
   p=s.host.launch(name,['/usr/bin/python3','-c',fixture,name,color],env=env)
   apps.append(p)
   windows.append(wait(lambda:next((w for w in s.data('clients') if w['pid']==p.pid),None)))
  a,b=[w['address'] for w in windows]
  def dispatch(text):s.ctl('dispatch',text)
  def raise_(address):
   dispatch('hl.dsp.focus({window="address:'+address+'"})')
   dispatch('hl.dsp.window.alter_zorder({mode="top",window="address:'+address+'"})')
  dispatch('hl.dsp.window.fullscreen({mode="maximized",action="set",window="address:'+a+'"})')
  dispatch('hl.dsp.window.move({x=200,y=180,window="address:'+b+'"})')
  dispatch('hl.dsp.window.resize({x=320,y=240,window="address:'+b+'"})')
  raise_(b);time.sleep(.25)
  def snap(name):
   file=output/(name+'.png');s.guard();subprocess.run(['grim',str(file)],env=s.env,check=True,timeout=5)
   pixel=subprocess.check_output(['magick',str(file),'-format','%[pixel:p{300,300}]','info:'],text=True,timeout=5)
   return {'pixel':pixel,'clients':s.data('clients'),'active':s.data('activewindow')['address'],'image':str(file)}
  report['peerRaised']=snap('peer-raised')
  raise_(a);time.sleep(.25);report['maxRaised']=snap('max-raised')
  assert report['peerRaised']['active']==b and report['maxRaised']['active']==a
  pointer='/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer'
  s.guard();subprocess.run([pointer,'800','600'],input='move 300 300\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n',text=True,env=s.env,check=True,timeout=5)
  report['afterClick']=s.data('activewindow')['address']
  report['mismatchReproduced']='0,255,0' in report['maxRaised']['pixel'].replace(' ','') and report['afterClick']==a
  report['result']='counterexample' if report['mismatchReproduced'] else 'not-reproduced'
  # Retire owned fixtures first, then private-bus activated auxiliaries, then
  # let the host retire compositor/Weston/bus and enforce its cleanup checks.
  for proc in reversed(apps):
   row=next(row for owned,row in s.host.processes if owned is proc)
   s.host.stop(row,proc);proc.wait(timeout=4)
  registered={row['pid'] for _,row in s.host.processes}
  auxiliary=[row for row in s.host.descendants() if row['pid'] not in registered]
  report['ownedAuxiliaryShutdown']=auxiliary
  for row in reversed(auxiliary):s.host.stop(row)

except Exception as e:report['error']=repr(e)
report['host']=s.evidence if 's' in locals() else None
(B/('diagnostic-'+str(time.time_ns())+'.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('host','peerRaised','maxRaised')}))
