"""Owned GTK role native campaign: explicit bootstrap diagnostic, full gates retained."""
import argparse,hashlib,json,os,resource,shutil,sys,time,traceback
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from preflight import verify,sha
from actor import Actor,remaining
from scene import bind,same
from observer import roles,selected
from pixels import capture,yellow_marker
from journal import Refused
from bounded import BoundedSession
SLICE=Path(__file__).resolve().parents[1];REPO=SLICE.parents[1]
LUA=b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'

def run(diagnostic=False):
 out=SLICE/'qa'/('native-'+str(time.time_ns()));out.mkdir();output=Path('/home/hoskinson/window-integration-qa')/('gtk-role-'+str(time.time_ns()));report={'passed':False,'nativeAcceptance':False,'fullCampaignPassed':False,'diagnosticBootstrap':diagnostic,'mainDesktopActions':False,'physicalHardwareAccepted':False,'checks':[],'remainingScenarios':['GTK01','GTK02','GTK03','GTK04','GTK05','GTK06','GTK07','GTK08']};session=None;actor=None;loaded=False;observer_loaded=False
 def check(name,value,**evidence):
  report['checks'].append({'name':name,'passed':bool(value),**evidence});assert value,name
 try:
  (out/'native.py').write_bytes(Path(__file__).read_bytes())
  if not diagnostic:raise Refused('Full GTK01-08 driver remains incomplete; only explicit root-reviewed diagnostic-bootstrap may launch')
  host,core,fixture,observer,probe,files=verify();report['inputs']=files
  # Final canonical prerequisites only; historical233/240/239 never launch.
  pins=json.loads((SLICE/'pins.json').read_text())['manifests']
  check('safeCanonicalInputsSelected',all(name in pins for name in ['elm-gtk-role-canonical-runtime-v244','elm-toolkit-popup-canonical-observer-v246','elm-parent-keyboard-canonical-observer-v247']) and all(name not in pins for name in ['elm-gtk-role-journal-fixture-v233','elm-toolkit-popup-owned-observer-v240','elm-parent-keyboard-surface-observer-v239']))
  report['inputs'].update({str(p):sha(p) for p in [Path(__file__),*sorted((SLICE/'qa').glob('*.py')),SLICE/'pins.json',SLICE/'REQUIREMENTS.md']})
  (out/'inputs.json').write_text(json.dumps(report['inputs'],indent=2)+'\n')
  with host.PrivateHyprSession(output,dict(os.environ),800,600,LUA,mesa_vendor=True) as session:
   try:
    native=next(row for _,row in session.host.processes if row['name']=='hyprland');report['nativeProcess']=native
    check('owningCoreMapped',session.evidence['hyprlandMaps']['files'].get(str(Path(core['binary']).resolve()))==core['sha256'])
    check('owningAQMapped',session.evidence['privateAquamarine']['mappedVerified'] is True)
    parent=next(row for _,row in session.host.processes if row['name']=='weston');parent_maps=host.original.mapped_files(parent['pid']);report['parentMaps']=parent_maps
    check('canonicalParentInputModuleMapped',parent_maps['files'].get(str(Path(probe['module']['path']).resolve()))==probe['module']['sha256'])
    check('authorityPluginLoad',session.ctl('plugin','load',core['plugin']['path']).strip()=='ok');loaded=True
    check('ownedToolkitObserverLoad',session.ctl('plugin','load',observer['binary']).strip()=='ok');observer_loaded=True
    maps=host.original.mapped_files(native['pid']);report['pluginMaps']=maps
    check('authorityPluginMapped',maps['files'].get(str(Path(core['plugin']['path']).resolve()))==core['plugin']['sha256'])
    check('ownedToolkitObserverMapped',maps['files'].get(str(Path(observer['binary']).resolve()))==observer['binarySHA256'])
    start_deadline=time.monotonic()+6
    bounded=BoundedSession(session,output/'bounded-ipc',start_deadline)
    actor=Actor(bounded,host,fixture['artifact']['path'],output/'gtk-role-client',start_deadline)
    actor.send('create-owners',start_deadline)
    def wait_binding(name,deadline):
     while remaining(deadline):
      value=bind(actor,bounded,name);remaining(deadline)
      if value:return value
      time.sleep(min(.02,remaining(deadline)))
    a=wait_binding('A',start_deadline);c=wait_binding('C',start_deadline);remaining(start_deadline)
    check('actualIndependentGtkRootsMapped',a['native']['address']!=c['native']['address'] and a['identity']['surfaceId']!=c['identity']['surfaceId'],A=a,C=c)
    # Deliberately disjoint measured native placements, not shared-color inference.
    placement_deadline=time.monotonic()+6;bounded.deadline=placement_deadline
    for name,initial,x in [('A',a,40),('C',c,420)]:
     address=initial['native']['address']
     bounded.ctl('dispatch','setfloating','address:'+address)
     bounded.ctl('dispatch','resizewindowpixel',f'exact 320 180,address:{address}')
     bounded.ctl('dispatch','movewindowpixel',f'exact {x} 70,address:{address}')
    actor.send('inspect',placement_deadline);a=wait_binding('A',placement_deadline);c=wait_binding('C',placement_deadline)
    def disjoint(a,c):
     ax,ay=a['native']['at'];aw,ah=a['native']['size'];cx,cy=c['native']['at'];cw,ch=c['native']['size']
     return ax+aw<=cx or cx+cw<=ax or ay+ah<=cy or cy+ch<=ay
    check('deliberatelyDisjointActualNativeExtents',disjoint(a,c) and a['native']['floating'] is True and c['native']['floating'] is True,A=a,C=c)
    # Every capture is a separate named diagnostic stage, with one absolute6s.
    # This does not reset any original GTK01-08 scenario deadline or count as it.
    for name in ('A','C'):
     deadline=time.monotonic()+6;bounded.deadline=deadline;actor.send('inspect',deadline);before=wait_binding(name,deadline)
     inventory=roles(json.loads(bounded.ctl('elm_role_state')),compositor_pid=native['pid']);native_role=selected(inventory,address=before['native']['address'],pid=actor.pid,parent_address='0x0',modal=False,blocked=False)
     remaining(deadline)
     all_before=bounded.data('clients');other=wait_binding('C' if name=='A' else 'A',deadline)
     check(name+':completeSceneAttributionBeforeCapture',len(all_before)==2 and {r['address'] for r in all_before}=={before['native']['address'],other['native']['address']} and all(r['pid']==actor.pid for r in all_before) and disjoint(before,other),clients=all_before,selected=before,other=other)
     popup_before=json.loads(bounded.ctl('elm_popup_state'));check(name+':noPopupOcclusionBeforeCapture',popup_before['pid']==native['pid'] and popup_before['popups']==[],snapshot=popup_before)
     image,measurement=capture(bounded,host,output/(name+'-marker-capture'),deadline,selected={'binding':before,'otherBinding':other,'nativeClients':all_before,'expectedPoint':before['marker']['global'],'expectedRGB':[255,255,0]})
     samples=yellow_marker(image,before['marker']['global']);measurement['markerSamples']=samples
     (output/(name+'-marker-capture')/'record.json').write_text(json.dumps(measurement,indent=2)+'\n')
     actor.send('inspect',deadline);after=wait_binding(name,deadline);same(before,after)
     check(name+':unchangedNativeAndProtocolAcrossCapture',before['native']['at']==after['native']['at'] and before['native']['size']==after['native']['size'] and before['wire']['windowGeometry']==after['wire']['windowGeometry'] and before['wire']['ack']==after['wire']['ack'] and before['wire']['lastCommitIndex']==after['wire']['lastCommitIndex'],before=before,after=after)
     all_after=bounded.data('clients');other_after=wait_binding('C' if name=='A' else 'A',deadline);same(other,other_after)
     check(name+':completeSceneAttributionAfterCapture',len(all_after)==2 and {r['address'] for r in all_after}=={before['native']['address'],other['native']['address']} and all(r['pid']==actor.pid for r in all_after) and disjoint(after,other_after) and all_before==all_after and other['native']['at']==other_after['native']['at'] and other['native']['size']==other_after['native']['size'],clients=all_after,other=other_after)
     popup_after=json.loads(bounded.ctl('elm_popup_state'));check(name+':noPopupOcclusionAfterCapture',popup_after['pid']==native['pid'] and popup_after['popups']==[],snapshot=popup_after)
     remaining(deadline);check(name+':actualGtkMarkerRGB',samples['passed'],measurement=measurement,samples=samples,nativeRole=native_role)
    # Local normal exit is not server retirement; census is independent.
    deadline=time.monotonic()+6;bounded.deadline=deadline;actor.close(deadline)
    while remaining(deadline):
     clients=bounded.data('clients');remaining(deadline)
     if not clients:break
     time.sleep(min(.02,remaining(deadline)))
    check('normalGtkExitAndActualEmptyNativeCensus',actor.record.get('normalExit') is True and clients==[],actor=actor.record,clients=clients)
    check('ownedToolkitObserverUnload',session.ctl('plugin','unload',observer['binary']).strip()=='ok');observer_loaded=False
    check('authorityPluginUnload',session.ctl('plugin','unload',core['plugin']['path']).strip()=='ok');loaded=False
    report['passed']=True
   except BaseException as error:
    report['primaryError']=repr(error);report['primaryTraceback']=traceback.format_exc();raise
   finally:
    if actor and actor.process.poll() is None:actor.abort()
    if observer_loaded or loaded:
     cleanup_deadline=time.monotonic()+3
     try:
      while remaining(cleanup_deadline):
       clients=session.data('clients')
       if clients==[]:break
       time.sleep(min(.02,remaining(cleanup_deadline)))
      if clients!=[]:raise Refused('never unload plugins while native clients remain')
      if observer_loaded:
       report['failureCleanupObserverUnload']=session.ctl('plugin','unload',observer['binary']).strip();observer_loaded=False
      if loaded:
       report['failureCleanupAuthorityUnload']=session.ctl('plugin','unload',core['plugin']['path']).strip();loaded=False
     except BaseException as error:report['failureCleanupError']=repr(error)
    report['sessionEvidence']=session.evidence
 except BaseException as error:
  report['error']=report.get('primaryError',repr(error));report['traceback']=report.get('primaryTraceback',traceback.format_exc())
  if report['error']!=repr(error):report['laterError']=repr(error)
 finally:
  if session:
   report['cleanup']=session.evidence;report['cleanupPassed']=not any(session.evidence.get(k) for k in ('cleanupErrors','unexpectedInnerDescendants','remainingDescendants')) and bool(session.evidence.get('runtimeGone'))
   report['passed']=report['passed'] and report['cleanupPassed'] and not report.get('failureCleanupError')
  if output.exists():shutil.copytree(output,out/'native-evidence',symlinks=True)
  report['nativeAcceptance']=False;report['fullCampaignPassed']=False
  report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
  (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
 return report
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--diagnostic-bootstrap',action='store_true');args=parser.parse_args();result=run(args.diagnostic_bootstrap);raise SystemExit(0 if result['passed'] else 1)
