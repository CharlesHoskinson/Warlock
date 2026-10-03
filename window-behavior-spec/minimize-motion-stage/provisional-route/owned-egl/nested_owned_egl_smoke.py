#!/usr/bin/env python3
"""Explicit native GUI smoke in a fresh private nested compositor.

Run only in the coordinated GUI slot. Loads/unloads only the candidate in that
new compositor; no installed libraries/configs or main desktop windows mutated.
"""
import argparse,hashlib,json,os,signal,socket,subprocess,tempfile,time,sys
from pathlib import Path
LOCAL=Path(__file__).resolve().parent
ATLAS=LOCAL.parent.parent/"cross-output-design"
sys.path.insert(0,str(ATLAS))
from nested_preservation import project_clients,project_outputs,backup_catalogs,settle_catalogs,reader_status,files_state
HERE=ATLAS
from native_observer import Producer, accepted, cadence, handover

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
 args=parser.parse_args()
 manifest=json.loads((LOCAL/'native-manifest-v2.json').read_text())
 for path,expected in manifest['inputs'].items():
  assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected,'frozen native input changed: '+path
 args.output.mkdir(parents=True,exist_ok=False);args.output.chmod(0o700)
 library=HERE/'native-atlas-v18/hyprbars-v18-atlas-candidate.so'
 assert hashlib.sha256(library.read_bytes()).hexdigest()=='908f134af0fc266d4b4e982c35b3cbd125659d1585584c23f31511b008282eba','candidate binary changed; review/pin before GUI smoke'
 assert library.is_file(),'build candidate first'
 source=(HERE/'native-atlas-v18/main.cpp').read_text()
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
 compositor=None;apps=[];loaded=False;ctl=None;producer=None
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
   report['scope']='Private single-window GPU producer; synthetic icon endpoint; no production service/family authority'
   baseline=capture('source');assert baseline.get('whole') and baseline.get('canonical') and baseline.get('ok'),baseline
   report['baseline']=baseline
   ctl('output','create','headless','EGL-SECOND')
   ctl('repl','hl.monitor({output="EGL-SECOND",mode="960x720@60",position="1100x0",scale=1.5,transform=0})')
   second=wait(lambda:next((m for m in json.loads(ctl('monitors','-j')) if m['name']=='EGL-SECOND'),None),'second output map')
   assert second['width']==960 and second['height']==720 and second['scale']==1.5 and second['transform']==0,second
   report['actualOutputs']=json.loads(ctl('monitors','-j'))
   producer=Producer(LOCAL/'hypr-motion-renderer-staged',nested,args.output/'producer.stderr')
   observed=producer.wait(lambda e:e.get('event')=='outputs','producer outputs')['outputs']
   assert {o['name'] for o in observed}=={'WAYLAND-1','EGL-SECOND'},observed
   report['producerOutputs']=observed
   required=[{'name':o['name'],'generation':o['generation']} for o in observed]
   ident={'stableId':target['stableId'],'pid':target['pid']}
   token=lambda n:'abcdef123456-'+str(n)
   native={'x':target['at'][0],'y':target['at'][1],'width':target['size'][0],'height':target['size'][1]}
   atlas=baseline['rect'];icon={'x':1140,'y':300,'width':28,'height':28}
   raw_path=output/(baseline['captureEpoch']+'.png');raw_path.chmod(0o600)
   digest=hashlib.sha256(raw_path.read_bytes()).hexdigest()
   producer.send(command='seed',**ident,token=token(1),path=str(raw_path),digest=digest,nativeRect=native,atlasRect=atlas,iconRect=icon,insets=baseline['insets'],pixels=baseline['pixels'],captureScale=baseline['pixels'][0]/atlas['width'],operation='minimize',**{'from':atlas},target=icon,durationMs=1000,outputs=required)
   producer.wait(lambda e:e.get('event')=='seeded','seed acceptance')
   producer.send(command='validate',**ident,token=token(1))
   producer.wait(lambda e:e.get('event')=='ready' and e.get('token')==token(1),'actual all-output image readiness')
   ctl('dispatch',f'hl.dsp.window.move({{workspace="special:egl-route-qa",follow=false,window="address:{target["address"]}"}})')
   hidden=next(w for w in clients() if w['stableId']==target['stableId'] and w['pid']==target['pid'])
   report['checks']['nativeHiddenWithExactGeometry']=hidden['workspace']['name']=='special:egl-route-qa' and hidden['at']+hidden['size']==before
   # Static pixel proof is separate from the uninstrumented cadence run.
   static=args.output/'full-presented.png'
   subprocess.run(['grim','-o','WAYLAND-1',str(static)],env=nested,check=True,timeout=4)
   pixels=subprocess.check_output(['magick',str(static),'-depth','8','rgba:-'],timeout=4)
   actual_output=next(m for m in report['actualOutputs'] if m['name']=='WAYLAND-1')
   def pixel(x,y):
    i=(y*actual_output['width']+x)*4;return tuple(pixels[i:i+4])
   red=pixel(390,370);gold=pixel(230,230)
   report['staticPixelProof']={'client':red,'caption':gold,'sourceDigest':digest}
   report['checks']['wholeSourcePixelsActuallyPresented']=red[0]>180 and red[1]<50 and red[2]<50 and gold[0]>180 and gold[1]>100 and gold[2]<100
   focus=json.loads(ctl('activewindow','-j'))
   report['checks']['passiveLayerPreservesPrivateFocus']=focus.get('stableId')==cover['stableId'] and focus.get('pid')==cover['pid']
   # No screenshots or compositor polling from start through rapid endpoint.
   start_index=len(producer.rows)
   producer.send(command='start',**ident,token=token(1))
   producer.wait(lambda e:accepted(e,token(1)) and .2<e['progress']<.65,'first active motion')
   producer.send(command='retarget',**ident,token=token(2),operation='restore',target=atlas,durationMs=1000)
   reverse=producer.wait(lambda e:e.get('event')=='retargeted' and e.get('token')==token(2),'actual presented-origin reversal')
   producer.wait(lambda e:accepted(e,token(2)) and .15<e['progress']<.6,'provisional motion while validation withheld')
   producer.send(command='retarget',**ident,token=token(3),operation='minimize',target=icon,durationMs=1000)
   third=producer.wait(lambda e:e.get('event')=='retargeted' and e.get('token')==token(3),'rapid third presented-origin reversal')
   producer.send(command='validate',**ident,token=token(2))
   producer.wait(lambda e:e.get('event')=='rejected' and 'validation' in e.get('reason',''),'stale validation rejection')
   producer.send(command='validate',**ident,token=token(3))
   producer.wait(lambda e:e.get('event')=='endpoint' and e.get('token')==token(3),'latest promoted endpoint')
   records=[e for e in producer.rows[start_index:] if accepted(e)]
   report['rapidRecords']=records;report['handoverDiagnostics']=[handover(producer.rows,event) for event in (reverse,third)]
   report['checks']['actualPerOutputInteriorOrigins']=all(d['passes'] for d in report['handoverDiagnostics'])
   report['checks']['unvalidatedMotionHasNoNativeAuthority']=not any(e.get('event') in ('ready','endpoint') and e.get('token')==token(2) for e in producer.rows)
   report['cadence']=cadence(records,observed)
   report['checks']['actualPresentationCadenceNoMetadataPause']=all(d['passes'] for d in report['cadence'].values())
   report['checks']['oneImmutableUploadAcrossRapidIntent']=len([e for e in producer.rows if e.get('event')=='uploaded'])==1 and all(e.get('digest')==digest and e.get('stableId')==ident['stableId'] and e.get('pid')==ident['pid'] for e in records)
   producer.send(command='cancel',**ident,token=token(3))
   producer.wait(lambda e:e.get('event')=='cancelled','latest cancel')
   def motion_layers():return 'hoskinson-window-motion' in ctl('layers','-j')
   wait(lambda:not motion_layers(),'cancel left motion layer')
   report['checks']['cancelDestroysAllOwnedLayers']=not motion_layers()
   current=next(w for w in clients() if w['stableId']==target['stableId'] and w['pid']==target['pid'])
   report['checks']['nativeGeometryStillExact']=current['at']+current['size']==before
   old_generations={o['name']:o['generation'] for o in observed}
   producer.send(command='prepareOutputs')
   fresh=producer.wait(lambda e:e.get('event')=='outputs' and all(o['generation']!=old_generations.get(o['name']) for o in e['outputs']),'fresh owned surface generations')['outputs']
   producer.send(command='seed',**ident,token=token(4),path=str(raw_path),digest=digest,nativeRect=native,atlasRect=atlas,iconRect=icon,insets=baseline['insets'],pixels=baseline['pixels'],captureScale=baseline['pixels'][0]/atlas['width'],operation='minimize',**{'from':atlas},target=icon,durationMs=1000,outputs=[{'name':o['name'],'generation':o['generation']} for o in fresh])
   producer.send(command='validate',**ident,token=token(4))
   producer.wait(lambda e:e.get('event')=='ready' and e.get('token')==token(4),'replacement surfaces actual readiness')
   producer.send(command='start',**ident,token=token(4))
   producer.wait(lambda e:accepted(e,token(4)) and .2<e['progress']<.65,'active output-removal scene')
   ctl('output','remove','EGL-SECOND')
   removed=producer.wait(lambda e:e.get('event')=='cancelled' and e.get('token')==token(4),'output removal retires route')
   report['outputRemoval']=removed
   wait(lambda:not motion_layers(),'output removal left owned surfaces')
   report['checks']['activeOutputRemovalRetiresAllSurfaces']=removed.get('nativeAuthority') is False and not motion_layers()
   producer.send(command='stop');producer.process.wait(timeout=4)
   report['checks']['producerCleanExit']=producer.process.returncode==0
  except Exception as error:report['error']=repr(error)
  finally:
   if producer:
    producer.close()
    report['producerEvents']=producer.rows
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
