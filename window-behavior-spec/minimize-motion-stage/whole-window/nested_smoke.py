#!/usr/bin/env python3
"""Explicit native GUI smoke in a fresh private nested compositor.

Run only in the coordinated GUI slot. Loads/unloads only the candidate in that
new compositor; no installed libraries/configs or main desktop windows mutated.
"""
import argparse,hashlib,json,os,signal,socket,subprocess,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent

def wait(predicate,message,timeout=12):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  result=predicate()
  if result:return result
  time.sleep(.05)
 raise AssertionError(message)

def a11y():
 path=Path('/run/user')/str(os.getuid())/'at-spi/bus_0'
 stat=path.stat() if path.exists() else None
 connected=False
 if stat:
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as sock:
   sock.settimeout(.2)
   try:sock.connect(str(path));connected=True
   except OSError:pass
 return {'identity':[stat.st_dev,stat.st_ino] if stat else None,'connects':connected}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
 args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 library=HERE/'native/hyprbars-v14-snapshot-candidate.so'
 assert library.is_file(),'build candidate first'
 source=(HERE/'native/main.cpp').read_text()
 assert 'HASH != CLIENT_HASH' in source and '__hyprland_api_get_client_hash()' in source,'compositor/header ABI gate must precede hook installation'
 def outer(*a):return subprocess.check_output(['hyprctl',*a],text=True,timeout=4).strip()
 original=json.loads(outer('clients','-j'));active=json.loads(outer('activewindow','-j'));pointer=json.loads(outer('cursorpos','-j'))
 report={'mainOriginal':original,'mainFocusBefore':active,'mainCursorBefore':pointer,'checks':{},'librarySHA256':hashlib.sha256(library.read_bytes()).hexdigest(),'mainA11yBefore':a11y()}
 compositor=None;apps=[];loaded=False;ctl=None
 with tempfile.TemporaryDirectory(prefix='ws-',dir='/tmp',ignore_cleanup_errors=True) as temp:
  runtime=Path(temp);runtime.chmod(0o700)
  config=runtime/'whole-snapshot-nested.lua';config.write_text((HERE/'nested.lua').read_text())
  env=dict(os.environ,XDG_RUNTIME_DIR=temp,XDG_CONFIG_HOME=str(runtime/'config'),AQ_BACKENDS='wayland',GIO_USE_VFS='local',GTK_USE_PORTAL='0')
  display=env.get('WAYLAND_DISPLAY','wayland-1')
  if not display.startswith('/'):env['WAYLAND_DISPLAY']=str(Path(os.environ['XDG_RUNTIME_DIR'])/display)
  for name in ('DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','HYPRLAND_INSTANCE_SIGNATURE','DISPLAY','SESSION_MANAGER'):env.pop(name,None)
  try:
   with (args.output/'nested.log').open('w') as log:
    compositor=subprocess.Popen(['dbus-run-session','--','Hyprland','--config',str(config)],env=env,start_new_session=True,stdout=log,stderr=subprocess.STDOUT)
   def instance():
    assert compositor.poll() is None,'nested compositor exited'
    try:
     found=json.loads(subprocess.check_output(['hyprctl','instances','-j'],env=env,text=True,stderr=subprocess.DEVNULL,timeout=2))
     return next((i for i in found if str(config).encode() in Path(f'/proc/{i["pid"]}/cmdline').read_bytes()),None)
    except (OSError,ValueError,subprocess.SubprocessError):return None
   selected=wait(instance,'nested compositor startup timeout')
   nested=dict(env,HYPRLAND_INSTANCE_SIGNATURE=selected['instance'],WAYLAND_DISPLAY=selected['wl_socket'])
   for item in Path(f'/proc/{selected["pid"]}/environ').read_bytes().split(b'\0'):
    if item.startswith(b'DBUS_SESSION_BUS_ADDRESS='):nested['DBUS_SESSION_BUS_ADDRESS']=item.split(b'=',1)[1].decode()
   def ctl(*arguments):return subprocess.check_output(['hyprctl',*map(str,arguments)],env=nested,text=True,timeout=4).strip()
   assert ctl('plugin','load',library)=='ok';loaded=True
   ctl('repl','hl.config({plugin={hyprbars={bar_height=28,bar_color=0xffffcc33,["col.text"]=0xff000000}}})')
   def clients():return json.loads(ctl('clients','-j'))
   def fixture(role):
    process=subprocess.Popen(['python3',str(HERE/'snapshot_fixture.py'),role],env=nested,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);apps.append(process)
    return wait(lambda:next((w for w in clients() if w['pid']==process.pid),None),'fixture map timeout')
   target=fixture('target');cover=fixture('cover')
   def place(w,x,y,width,height):
    ctl('dispatch',f'hl.dsp.window.resize({{x={width},y={height},window="address:{w["address"]}"}})')
    ctl('dispatch',f'hl.dsp.window.move({{x={x},y={y},window="address:{w["address"]}"}})')
   place(target,200,250,380,240);place(cover,700,450,260,180)
   ctl('dispatch',f'hl.dsp.focus({{window="address:{cover["address"]}"}})');time.sleep(.3)
   target=next(w for w in clients() if w['address']==target['address']);before=target['at']+target['size']
   output=runtime/'hypr-window-motion/smoke';output.mkdir(parents=True,mode=0o700)
   def capture(name,pid=None,stable=None):
    path=output/(name+'.png')
    expression='print(hl.plugin.hyprbars.window_snapshot('+','.join((json.dumps(target['address']),json.dumps(stable or target['stableId']),str(pid or target['pid']),json.dumps(str(path))))+'))'
    metadata=json.loads(ctl('repl',expression))
    if metadata.get('ok'):
     destination=args.output/path.name;destination.write_bytes(path.read_bytes());metadata['artifact']=str(destination)
    return metadata
   baseline=capture('baseline');assert baseline.get('whole') and baseline.get('ok'),baseline
   place(cover,190,200,410,330);time.sleep(.2)
   occluded=capture('occluded');assert occluded.get('whole') and occluded.get('ok'),occluded
   subprocess.run(['grim','-o','WAYLAND-1',str(args.output/'monitor-occluded.png')],env=nested,check=True,timeout=4)
   def rgba(path,*options):return subprocess.check_output(['magick',path,*options,'-depth','8','rgba:-'],timeout=4)
   first=rgba(baseline['artifact']);second=rgba(occluded['artifact'])
   report['checks']['occluderIndependent']=first==second
   inset=baseline['insets'];scale=baseline['pixels'][0]/baseline['rect']['width'];left=round(inset['left']*scale);top=round(inset['top']*scale)
   captionWidth=baseline['pixels'][0]-left-round(inset['right']*scale)-40
   caption=rgba(baseline['artifact'],'-crop',f'{captionWidth}x20+{left+20}+{max(0,top-24)}','+repage')
   gold=sum(1 for offset in range(0,len(caption),4) if caption[offset+3]>200 and caption[offset]>180 and caption[offset+1]>100 and caption[offset+2]<100)
   report['checks']['serverCaptionPixels']=top>=28 and gold>100
   report['captionGoldPixels']=gold;report['baseline']=baseline;report['occluded']=occluded
   width,height=baseline['pixels'];center=left+round(target['size'][0]*scale/2)
   redRows=[]
   for row in range(height):
    offset=(row*width+center)*4;r,g,b,a=first[offset:offset+4]
    if r>180 and g<50 and b<50 and a>200:redRows.append(row)
   report['clientRedRows']=[min(redRows),max(redRows)] if redRows else []
   report['checks']['clientPixelsMatchInsets']=bool(redRows) and abs(min(redRows)-top)<=2 and abs(max(redRows)-(top+round(target['size'][1]*scale)-1))<=2
   monitorPixel=rgba(str(args.output/'monitor-occluded.png'),'-crop',f'1x1+{target["at"][0]+target["size"][0]//2}+{target["at"][1]+target["size"][1]//2}','+repage')
   report['checks']['monitorActuallyOccluded']=len(monitorPixel)==4 and monitorPixel[2]>180 and monitorPixel[0]<50 and monitorPixel[1]<60

   stale=capture('stale-pid',target['pid']+1);stale_id=capture('stale-id',stable='ffffffffffffffff')
   report['checks']['stalePIDRejected']=not stale.get('ok') and not (output/'stale-pid.png').exists()
   report['checks']['staleIDRejected']=not stale_id.get('ok') and not (output/'stale-id.png').exists()
   actual=next(w for w in clients() if w['address']==target['address'])
   report['checks']['exactGeometry']=actual['at']+actual['size']==before
   report['edgeTrials']=[]
   for label,x,y in [('left-edge',0,250),('right-edge',620,250),('top-edge',400,28)]:
    place(target,x,y,380,240);time.sleep(.1)
    edge_before=next(w for w in clients() if w['address']==target['address'])
    edge=capture(label);assert edge.get('ok') and edge.get('whole'),edge
    edge_after=next(w for w in clients() if w['address']==target['address'])
    data=rgba(edge['artifact']);ew,eh=edge['pixels'];ei=edge['insets']
    et=round(ei['top']);ex=round(ei['left'])+190
    red=[]
    for row in range(eh):
     offset=(row*ew+ex)*4;r,g,b,a=data[offset:offset+4]
     if r>180 and g<50 and b<50 and a>200:red.append(row)
    caption=rgba(edge['artifact'],'-crop',f'{max(1,ew-40)}x{max(1,et-6)}+20+2','+repage')
    gold=sum(1 for offset in range(0,len(caption),4) if caption[offset+3]>200 and caption[offset]>180 and caption[offset+1]>100 and caption[offset+2]<100)
    agreement=all(abs(edge['rect'][name]+ei[side]-edge_before['at'][index])<.02 for name,side,index in [('x','left',0),('y','top',1)])
    dimensions=abs(edge['rect']['width']-ei['left']-ei['right']-380)<.02 and abs(edge['rect']['height']-ei['top']-ei['bottom']-240)<.02
    clipped=(ei['left']==0 if label=='left-edge' else ei['right']==0 if label=='right-edge' else edge['rect']['y']==0 and ei['top']==28)
    passed=edge_after['at']+edge_after['size']==edge_before['at']+edge_before['size'] and agreement and dimensions and clipped and gold>100 and bool(red) and abs(min(red)-et)<=2 and abs(max(red)-(et+239))<=2
    report['edgeTrials'].append({'edge':label,'metadata':edge,'geometryBefore':edge_before['at']+edge_before['size'],'goldPixels':gold,'redRows':[min(red),max(red)] if red else [],'passed':passed})
    report['checks'][label]=passed
   place(target,-4,250,380,240);time.sleep(.1)
   spanning=capture('client-spanning')
   report['checks']['clientSpanningRejected']=not spanning.get('ok') and not (output/'client-spanning.png').exists()
   report['spanningResult']=spanning
   # Snapshot must preserve premultiplied edge alpha; no opaque monitor crop.
   report['checks']['transparentRoundedCorners']=any(a<255 for a in first[3::4]) and any(0<a<255 for a in first[3::4])
   assert ctl('plugin','unload',library)=='ok';loaded=False
   report['checks']['cleanUnload']=not any(p.get('name')=='hyprbars' for p in json.loads(ctl('plugin','list','-j')))
  except Exception as error:report['error']=repr(error)
  finally:
   (args.output/'snapshot-intermediate.json').write_text(json.dumps(report,indent=2))
   for app in apps:
    app.terminate()
    try:app.wait(timeout=4)
    except subprocess.TimeoutExpired:app.kill();app.wait()
   if loaded and ctl:
    try:report['cleanupUnload']=ctl('plugin','unload',library)
    except subprocess.SubprocessError as error:report['cleanupUnload']=str(error)
   if compositor:
    try:os.killpg(compositor.pid,signal.SIGTERM)
    except ProcessLookupError:pass
    try:compositor.wait(timeout=6)
    except subprocess.TimeoutExpired:os.killpg(compositor.pid,signal.SIGKILL);compositor.wait()
 current=json.loads(outer('clients','-j'))
 if any(w.get('stableId')==active.get('stableId') and w.get('pid')==active.get('pid') for w in current):
  outer('dispatch',f'hl.dsp.focus({{window="address:{active["address"]}"}})')
 outer('dispatch',f'hl.dsp.cursor.move({{x={pointer["x"]},y={pointer["y"]}}})')
 time.sleep(.1)
 report['mainFocusAfter']=json.loads(outer('activewindow','-j'));report['mainCursorAfter']=json.loads(outer('cursorpos','-j'))
 report['checks']['mainFocusRestored']=not active or (report['mainFocusAfter'].get('stableId')==active.get('stableId') and report['mainFocusAfter'].get('pid')==active.get('pid'))
 report['checks']['mainCursorRestored']=report['mainCursorAfter']==pointer
 after={w['address']:w for w in json.loads(outer('clients','-j'))}
 report['checks']['mainGeometryPreserved']=all(w['address'] in after and after[w['address']].get('stableId')==w.get('stableId') and after[w['address']].get('pid')==w.get('pid') and after[w['address']]['at']+after[w['address']]['size']==w['at']+w['size'] for w in original)
 report['mainA11yAfter']=a11y();report['checks']['mainA11yUnchanged']=report['mainA11yAfter']==report['mainA11yBefore']
 report['result']='pass' if not report.get('error') and all(report['checks'].values()) else 'fail'
 (args.output/'snapshot-smoke.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
 assert report['result']=='pass'

if __name__=='__main__':main()
