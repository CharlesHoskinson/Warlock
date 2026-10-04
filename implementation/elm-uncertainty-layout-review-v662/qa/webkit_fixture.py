"""EXPLICIT renderer fixture variant: actual640 HTML/Elm/CSS/adapter files.
Synthetic compiled-root presentations enter the real adapter presentation port.
No native authority/backend/effect is installed or simulated here.
"""
import json,os,pathlib,sys
import gi
gi.require_foreign('cairo')
gi.require_version('Gtk','3.0');gi.require_version('WebKit2','4.1')
from gi.repository import Gtk,WebKit2,GLib,Gio
ASSETS=pathlib.Path(sys.argv[1]).resolve();CONTROL=pathlib.Path(sys.argv[2]);OUTPUT=pathlib.Path(sys.argv[3]);ROLE=sys.argv[4]
assert ROLE in ['bar','popup'];OUTPUT.mkdir(mode=0o700,exist_ok=True)
ctx=WebKit2.WebContext.new_ephemeral();ctx.set_sandbox_enabled(True)
ALLOWED={'bar.html','bar.js','bar-adapter.js','popup.html','popup.js','popup-adapter.js','shell.css','context.js'}
def scheme(request,*_):
 name=request.get_uri().removeprefix('elm-layout://app/')
 if name not in ALLOWED:request.finish_error(GLib.Error.new_literal(Gio.io_error_quark(),'Asset not allowed',0));return
 data=(ASSETS/name).read_bytes();stream=Gio.MemoryInputStream.new_from_bytes(GLib.Bytes.new(data));mime='text/html' if name.endswith('.html') else 'text/css' if name.endswith('.css') else 'application/javascript';request.finish(stream,len(data),mime)
ctx.register_uri_scheme('elm-layout',scheme,None);ctx.get_security_manager().register_uri_scheme_as_local('elm-layout');ctx.get_security_manager().register_uri_scheme_as_secure('elm-layout')
manager=WebKit2.UserContentManager();manager.register_script_message_handler('native')
def receive(_manager,result):print('fixture-native: '+result.get_js_value().to_string(),flush=True)
manager.connect('script-message-received::native',receive)
view=WebKit2.WebView(web_context=ctx,user_content_manager=manager)
settings=view.get_settings();settings.set_enable_html5_local_storage(False);settings.set_javascript_can_open_windows_automatically(False);settings.set_hardware_acceleration_policy(WebKit2.HardwareAccelerationPolicy.ALWAYS)
def policy(_view,decision,kind):
 if kind==WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION:decision.ignore();return True
 if kind==WebKit2.PolicyDecisionType.NAVIGATION_ACTION and decision.get_navigation_action().get_request().get_uri()!='elm-layout://app/'+ROLE+'.html':decision.ignore();return True
 return False
view.connect('decide-policy',policy)
window=Gtk.Window(title='ELM-LAYOUT-662-'+ROLE);window.set_default_size(320,420 if ROLE=='popup' else 120);window.add(view);window.connect('destroy',lambda *_:Gtk.main_quit());window.show_all()
def loaded(_view,event):
 if event==WebKit2.LoadEvent.FINISHED:print('fixture-loaded: '+ROLE,flush=True)
view.connect('load-changed',loaded);view.load_uri('elm-layout://app/'+ROLE+'.html')
MEASURE=r'''JSON.stringify((()=>{
const box=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}};
function glyphs(e){if(!e)return null;const raw=e.textContent;const clip={left:0,top:0,right:innerWidth,bottom:innerHeight};let n=e;
while(n){const s=getComputedStyle(n),r=n.getBoundingClientRect();if(['hidden','clip','auto','scroll'].includes(s.overflowX)){clip.left=Math.max(clip.left,r.left);clip.right=Math.min(clip.right,r.right)}if(['hidden','clip','auto','scroll'].includes(s.overflowY)){clip.top=Math.max(clip.top,r.top);clip.bottom=Math.min(clip.bottom,r.bottom)}n=n.parentElement}
const walker=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let textNode,visible=0,total=0,rects=[];
while(textNode=walker.nextNode()){for(let i=0;i<textNode.length;i++){const range=document.createRange();range.setStart(textNode,i);range.setEnd(textNode,i+1);const r=range.getBoundingClientRect();total++;const fits=r.width>0&&r.left>=clip.left-.5&&r.right<=clip.right+.5&&r.top>=clip.top-.5&&r.bottom<=clip.bottom+.5;if(fits)visible++;rects.push({x:r.x,y:r.y,width:r.width,height:r.height,visible:fits})}}
return {text:raw,visible,total,clip,rect:box(e),glyphRects:rects};}
return {width:innerWidth,height:innerHeight,role:document.body.className,active:document.activeElement?.id,publication:document.querySelector('[data-publication]')?.dataset.publication,buttons:[...document.querySelectorAll('button')].map(b=>({id:b.id,identity:b.dataset.surfaceControl,disabled:b.disabled,ariaLabel:b.getAttribute('aria-label'),text:b.textContent,rect:box(b),detail:glyphs(b.querySelector('.control-detail')),style:{whiteSpace:getComputedStyle(b).whiteSpace,overflowX:getComputedStyle(b).overflowX,textOverflow:getComputedStyle(b).textOverflow}})),status:[...document.querySelectorAll('[role=status]')].map(glyphs),bodyText:document.body.innerText};})())'''
def evaluated(_view,result,identity):
 try:value=view.evaluate_javascript_finish(result);print('layout-report: '+json.dumps({'command':identity,'body':json.loads(value.to_string())}),flush=True)
 except Exception as e:print('fixture-error: '+str(e),flush=True);Gtk.main_quit()
def snapshot(_view,result,identity):
 try:surface=view.get_snapshot_finish(result);surface.write_to_png(str(OUTPUT/(str(identity)+'.png')));print('fixture-snapshot: '+str(identity),flush=True)
 except Exception as e:print('fixture-error: '+str(e),flush=True);Gtk.main_quit()
last=0
def poll():
 global last
 try:
  if not CONTROL.exists():return True
  c=json.loads(CONTROL.read_bytes())
  if c['id']==last:return True
  assert type(c['id']) is int and c['id']>last;last=c['id'];kind=c['kind']
  if kind=='present':script='window.receivePresentation('+json.dumps(c['frame'])+');';view.evaluate_javascript(script,-1,None,None,None,None,None)
  elif kind=='measure':view.evaluate_javascript(MEASURE,-1,None,None,None,evaluated,last)
  elif kind=='focus':view.evaluate_javascript('window.receiveFocus('+json.dumps(c['frame'])+');',-1,None,None,None,None,None)
  elif kind=='resize':assert c['width'] in [320,480,800];window.resize(c['width'],420 if ROLE=='popup' else 120)
  elif kind=='reload':view.reload()
  elif kind=='snapshot':view.get_snapshot(WebKit2.SnapshotRegion.VISIBLE,WebKit2.SnapshotOptions.NONE,None,snapshot,last)
  elif kind=='quit':window.destroy();return False
  else:raise AssertionError('unknown fixture command')
 except Exception as e:print('fixture-error: '+str(e),flush=True);window.destroy();return False
 return True
GLib.timeout_add(20,poll);Gtk.main()
