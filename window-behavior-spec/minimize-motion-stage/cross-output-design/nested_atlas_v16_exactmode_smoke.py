#!/usr/bin/env python3
"""Explicit native GUI smoke in a fresh private nested compositor.

Run only in the coordinated GUI slot. Loads/unloads only the candidate in that
new compositor; no installed libraries/configs or main desktop windows mutated.
"""
import argparse,hashlib,json,os,signal,socket,subprocess,tempfile,time
from normal_frame_control import settle_frames
from pathlib import Path
from nested_preservation import project_clients,project_outputs,backup_catalogs,settle_catalogs,reader_status,files_state
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
 args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False);args.output.chmod(0o700)
 library=HERE/'native-atlas-v16/hyprbars-v16-atlas-candidate.so'
 assert hashlib.sha256(library.read_bytes()).hexdigest()=='874ace28a96a91dc23447820439e935d461583b82deb9c11c83d58df878b77ce','candidate binary changed; review/pin before GUI smoke'
 assert library.is_file(),'build candidate first'
 source=(HERE/'native-atlas-v16/main.cpp').read_text()
 assert 'HASH != CLIENT_HASH' in source and '__hyprland_api_get_client_hash()' in source,'compositor/header ABI gate must precede hook installation'
 def outer(*a):return subprocess.check_output(['hyprctl',*a],text=True,timeout=4).strip()
 original=json.loads(outer('clients','-j'));active=json.loads(outer('activewindow','-j'));pointer=json.loads(outer('cursorpos','-j'))
 original_outputs=project_outputs(json.loads(outer('monitors','-j')));original_plugins=json.loads(outer('plugin','list','-j'));original_errors=outer('configerrors')
 original_reader=reader_status();assert 'false' in original_reader,'main reader must be disabled at entry'
 original_files=files_state(Path.home());assert not original_files['visible'],'original Files must be hidden at entry'
 catalogs=backup_catalogs(args.output,Path.home())
 assert not original_errors,'main config has errors before smoke'
 report={'mainOriginal':original,'mainFocusBefore':active,'mainCursorBefore':pointer,'checks':{},'librarySHA256':hashlib.sha256(library.read_bytes()).hexdigest(),'mainA11yBefore':a11y()}
 report.update(mainStateBefore=project_clients(original),mainOutputsBefore=original_outputs,mainPluginsBefore=original_plugins,mainConfigErrorsBefore=original_errors,mainFilesBefore=original_files,mainReaderBefore=original_reader,catalogBackup=str(args.output/'catalog-before.json'))
 compositor=None;apps=[];loaded=False;ctl=None
 with tempfile.TemporaryDirectory(prefix='ws-',dir='/tmp',ignore_cleanup_errors=True) as temp:
  runtime=Path(temp);runtime.chmod(0o700)
  config=runtime/'whole-snapshot-nested.lua';config.write_text((HERE/'nested-stable.lua').read_text()+'\nhl.permission({binary='+json.dumps(str(library))+',type="plugin",mode="allow"})\n')
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
   watchdog_option=json.loads(ctl('getoption','misc:disable_watchdog_warning','-j'))
   assert watchdog_option.get('bool') is True and watchdog_option.get('set') is True,'private watchdog warning option not enabled: '+repr(watchdog_option)
   report['nestedWatchdogWarningOption']=watchdog_option
   report['nestedConfigSHA256']=hashlib.sha256(config.read_bytes()).hexdigest()
   (args.output/'nested-config.lua').write_bytes(config.read_bytes())
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
   sequence=0
   def capture(name,pid=None,stable=None):
    nonlocal sequence
    sequence+=1;epoch='0123456789ab-'+str(sequence)
    path=output/(epoch+'.png')
    expression='print(hl.plugin.hyprbars.window_atlas('+','.join((json.dumps(target['address']),json.dumps(stable or target['stableId']),str(pid or target['pid']),json.dumps(str(path)),json.dumps(epoch)))+'))'
    metadata=json.loads(ctl('repl',expression))
    if metadata.get('ok'):
     destination=args.output/(name+'.png');destination.write_bytes(path.read_bytes());metadata['artifact']=str(destination)
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

   legacy_path=output/'compatibility.png'
   legacy=json.loads(ctl('repl','print(hl.plugin.hyprbars.window_snapshot('+','.join((json.dumps(target['address']),json.dumps(target['stableId']),str(target['pid']),json.dumps(str(legacy_path))))+'))'))
   report['legacySnapshot']=legacy;report['checks']['legacySnapshotCompatible']=legacy.get('ok') and legacy.get('canonical') is False and legacy.get('captureEpoch')=='' and rgba(str(legacy_path))==first
   bad_epoch_path=output/'not-the-request-token.png'
   bad_epoch=json.loads(ctl('repl','print(hl.plugin.hyprbars.window_atlas('+','.join((json.dumps(target['address']),json.dumps(target['stableId']),str(target['pid']),json.dumps(str(bad_epoch_path)),json.dumps('0123456789ab-999')))+'))'))
   report['checks']['epochFilenameMismatchRejected']=not bad_epoch.get('ok') and not bad_epoch_path.exists()
   report['epochMismatchResult']=bad_epoch
   stale=capture('stale-pid',target['pid']+1);stale_id=capture('stale-id',stable='ffffffffffffffff')
   report['checks']['stalePIDRejected']=not stale.get('ok') and not stale.get('artifact')
   report['checks']['staleIDRejected']=not stale_id.get('ok') and not stale_id.get('artifact')
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
    clipped=(ei['left']>=0 and ei['right']>=0 and edge.get('canonical')==True)
    passed=edge_after['at']+edge_after['size']==edge_before['at']+edge_before['size'] and agreement and dimensions and clipped and gold>100 and bool(red) and abs(min(red)-et)<=2 and abs(max(red)-(et+239))<=2
    report['edgeTrials'].append({'edge':label,'metadata':edge,'geometryBefore':edge_before['at']+edge_before['size'],'goldPixels':gold,'redRows':[min(red),max(red)] if red else [],'passed':passed})
    report['checks'][label]=passed
   place(target,-4,250,380,240);time.sleep(.1)
   spanning=capture('client-spanning')
   report['checks']['clientSpanningComplete']=bool(spanning.get('ok') and spanning.get('canonical') and spanning['rect']['x']<0)
   report['spanningResult']=spanning
   # Each transform/scale is configured only in this isolated compositor.
   # Full-frame before/after pixels prove normal rendering resumes correctly;
   # uniformStatus itself is private and is not claimed byte-identical.
   report['transformTrials']=[]
   report['nestedOutputsInitial']=json.loads(ctl('monitors','-j'))
   for transform in range(8):
    for output_scale in (1,1.5):
     ctl('repl',f'hl.monitor({{output="WAYLAND-1",mode="960x720@60",position="0x0",scale={output_scale},transform={transform}}})')
     time.sleep(.2)
     place(target,100,120,380,240);place(cover,600,400,200,120);time.sleep(.2)
     actual_outputs=json.loads(ctl('monitors','-j'));actual_output=next(m for m in actual_outputs if m['name']=='WAYLAND-1')
     assert actual_output.get('scale')==output_scale and actual_output.get('transform')==transform,'actual matrix scale/transform differs from request: '+repr(actual_output)
     assert actual_output.get('width')==960 and actual_output.get('height')==720,'actual matrix pixel mode differs from960x720: '+repr(actual_output)
     current=next(w for w in clients() if w['address']==target['address'])
     before_window={key:current.get(key) for key in ('address','stableId','pid','at','size','pinned','workspace','monitor','fullscreen','fullscreenClient')}
     label=f'transform-{transform}-scale-{output_scale}'
     pre=args.output/(label+'-monitor-before.png');control=args.output/(label+'-monitor-no-capture-control.png');post=args.output/(label+'-monitor-after.png')
     control_trials=[]
     def observe_control(index):
      path=args.output/(label+f'-settle-{index}.png')
      subprocess.run(['grim','-o','WAYLAND-1',str(path)],env=nested,check=True,timeout=4)
      control_trials.append(str(path));return rgba(str(path))
     settled=settle_frames(observe_control,time.monotonic,time.sleep,timeout=5,consecutive=3)
     # Fresh complete frames, with no capture between them, are the baseline.
     pre.write_bytes(Path(control_trials[-2]).read_bytes());control.write_bytes(Path(control_trials[-1]).read_bytes())
     stable_control=settled and rgba(str(pre))==rgba(str(control))
     if not stable_control:raise AssertionError('normal compositor frames do not settle before atlas capture: '+label)
     meta=capture(label)
     time.sleep(.1);subprocess.run(['grim','-o','WAYLAND-1',str(post)],env=nested,check=True,timeout=4)
     normal_equal=rgba(str(control))==rgba(str(post))
     assert meta.get('ok') and meta.get('canonical'),meta
     scale=meta['pixels'][0]/meta['rect']['width'];inset=meta['insets'];pixels=rgba(meta['artifact']);width,height=meta['pixels']
     top=round(inset['top']*scale);cx=round((inset['left']+current['size'][0]/2)*scale)
     red=[]
     for row in range(height):
      off=(row*width+cx)*4;r,g,b,a=pixels[off:off+4]
      if r>180 and g<50 and b<50 and a>200:red.append(row)
     caption=rgba(meta['artifact'],'-crop',f'{max(1,width-40)}x{max(1,top-6)}+20+2','+repage')
     gold=sum(1 for off in range(0,len(caption),4) if caption[off+3]>200 and caption[off]>180 and caption[off+1]>100 and caption[off+2]<100)
     place(cover,90,70,410,340);time.sleep(.1)
     blocked=capture(label+'-occluded');assert blocked.get('ok') and blocked.get('canonical'),blocked
     independent=rgba(blocked['artifact'])==pixels
     place(cover,600,400,200,120);time.sleep(.1)
     after_occluded_trials=[]
     def observe_after_occluded(index):
      path=args.output/(label+f'-after-occluded-settle-{index}.png')
      subprocess.run(['grim','-o','WAYLAND-1',str(path)],env=nested,check=True,timeout=4)
      after_occluded_trials.append(str(path));return rgba(str(path))
     after_occluded_stable=settle_frames(observe_after_occluded,time.monotonic,time.sleep,timeout=5,consecutive=3)
     after_occluded_equal=after_occluded_stable and rgba(after_occluded_trials[-1])==rgba(str(control))
     after=next(w for w in clients() if w['address']==target['address'])
     now={key:after.get(key) for key in before_window}
     native_match=abs(meta['rect']['x']+inset['left']-current['at'][0])<.02 and abs(meta['rect']['y']+inset['top']-current['at'][1])<.02 and abs(meta['rect']['width']-inset['left']-inset['right']-current['size'][0])<.02 and abs(meta['rect']['height']-inset['top']-inset['bottom']-current['size'][1])<.02
     passed=before_window==now and native_match and gold>100 and red and abs(min(red)-top)<=2 and abs(max(red)-(top+round(current['size'][1]*scale)-1))<=2 and independent and stable_control and normal_equal and after_occluded_equal
     report['transformTrials'].append({'requestedTransform':transform,'requestedScale':output_scale,'requestedPixelMode':[960,720],'actualOutput':actual_output,'actualOutputs':actual_outputs,'capturePixelsPerLogicalUnit':scale,'metadata':meta,'before':before_window,'after':now,'goldPixels':gold,'redRows':[min(red),max(red)] if red else [],'occludedMetadata':blocked,'occluderIndependent':independent,'normalControlStable':stable_control,'normalFrameEqual':normal_equal,'afterOccludedExportEqual':after_occluded_equal,'afterOccludedControlStable':after_occluded_stable,'afterOccludedFrames':after_occluded_trials,'normalFrameControl':str(control),'normalControlTrials':control_trials,'passed':bool(passed)})
     report['checks'][label]=bool(passed)
   ctl('repl','hl.monitor({output="WAYLAND-1",mode="1000x760@60",position="0x0",scale=1,transform=0})')
   ctl('output','create','headless','ATLAS-GAP')
   ctl('repl','hl.monitor({output="ATLAS-GAP",mode="640x480@60",position="1100x0",scale=1.5})')
   time.sleep(.2)
   place(target,880,180,380,240);time.sleep(.2)
   gap_before=next(w for w in clients() if w['address']==target['address']);gap=capture('full-gap-source');assert gap.get('ok') and gap.get('canonical'),gap
   scale=gap['pixels'][0]/gap['rect']['width'];gx=round((1050-gap['rect']['x'])*scale);gy=round((gap_before['at'][1]+120-gap['rect']['y'])*scale)
   data=rgba(gap['artifact']);gw,gh=gap['pixels'];gap_red=False
   if 0<=gx<gw and 0<=gy<gh:
    off=(gy*gw+gx)*4;r,g,b,a=data[off:off+4];gap_red=r>180 and g<50 and b<50 and a>200
   gap_after=next(w for w in clients() if w['address']==target['address'])
   report['gapTrial']={'actualOutputs':json.loads(ctl('monitors','-j')),'metadata':gap,'sourceBefore':gap_before,'sourceAfter':gap_after,'gapPixelRed':gap_red}
   report['checks']['fullGapPixelsPresent']=gap_red and gap_before['at']+gap_before['size']==gap_after['at']+gap_after['size']
   # Fullscreen should contain the real undecorated client, not synthesize a caption.
   ctl('dispatch',f'hl.dsp.window.fullscreen({{mode="fullscreen",action="set",window="address:{target["address"]}"}})');time.sleep(.2)
   fullscreen_before=next(w for w in clients() if w['address']==target['address'])
   fullscreen=capture('fullscreen');assert fullscreen.get('ok') and fullscreen.get('canonical'),fullscreen
   fullscreen_after=next(w for w in clients() if w['address']==target['address'])
   fpixels=rgba(fullscreen['artifact']);fw,fh=fullscreen['pixels'];offset=((fh//2)*fw+fw//2)*4;fr,fg,fb,fa=fpixels[offset:offset+4]
   fgold=sum(1 for off in range(0,len(fpixels),4) if fpixels[off+3]>200 and fpixels[off]>180 and fpixels[off+1]>100 and fpixels[off+2]<100)
   report['fullscreenTrial']={'before':project_clients([fullscreen_before]),'after':project_clients([fullscreen_after]),'metadata':fullscreen,'goldPixels':fgold}
   report['checks']['fullscreenNativePixelsAndState']=project_clients([fullscreen_before])==project_clients([fullscreen_after]) and bool(fullscreen_before.get('fullscreen')) and fr>180 and fg<50 and fb<50 and fa>200 and fgold==0
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
 report['catalogComparison']=settle_catalogs(catalogs,seconds=4)
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
 report['mainStateAfter']=project_clients(list(after.values()));report['checks']['mainFullClientSetAndStatePreserved']=report['mainStateAfter']==report['mainStateBefore']
 report['mainOutputsAfter']=project_outputs(json.loads(outer('monitors','-j')));report['checks']['mainOutputsPreserved']=report['mainOutputsAfter']==original_outputs
 report['mainPluginsAfter']=json.loads(outer('plugin','list','-j'));report['checks']['mainPluginsPreserved']=report['mainPluginsAfter']==original_plugins
 report['mainConfigErrorsAfter']=outer('configerrors');report['checks']['mainConfigErrorsUnchanged']=report['mainConfigErrorsAfter']==original_errors==''
 report['mainFilesAfter']=files_state(Path.home());report['checks']['originalHiddenFilesPreserved']=report['mainFilesAfter']==original_files and not report['mainFilesAfter']['visible']
 report['mainReaderAfter']=reader_status();report['checks']['mainReaderDisabledPreserved']=report['mainReaderAfter']==original_reader and 'false' in report['mainReaderAfter']
 report['checks']['fourCatalogExactBytesPreserved']=all(row['exactBytes'] for row in report['catalogComparison'].values())
 report['checks']['allFixtureProcessesExited']=all(app.poll() is not None for app in apps) and compositor.poll() is not None
 report['result']='pass' if not report.get('error') and all(report['checks'].values()) else 'fail'
 (args.output/'snapshot-smoke.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
 assert report['result']=='pass'

if __name__=='__main__':main()
