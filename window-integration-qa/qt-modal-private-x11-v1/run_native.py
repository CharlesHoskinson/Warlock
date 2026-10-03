#!/usr/bin/env python3
"""Reviewed private Qt compatibility only: main observations never write."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,subprocess,sys
QA=Path('/home/hoskinson/window-integration-qa');HOST=QA/'private-weston-x11-host-v1';B=Path(__file__).resolve().parent
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
from private_session import run_session
PLUGIN=QA/'modal-ancestor-discovery-v2/native-candidate/hyprbars-v19-modal-candidate.so'
EXPECTED_PLUGIN_SHA256='412c0fee2ed1aa6ace7ded3a4b5ea6007e1da85ff20da93295a4aa168de5bfba'
EXPECTED_TOOLKIT_GATES=19
EXPECTED_HOST_GATES=10
AQ=QA/'aquamarine-nested-lifecycle-v1/prefix/lib/libaquamarine.so.0.15.0'
PROBE=B/'native-probe/libqt-modal-probe.so'

def transport_log_gate(logs):
 forbidden=r'\[libseat\]|DRM Backend failed|Starting the DRM backend|enabling fallbacks|error [0-9]+:|Broken pipe|parent transport failed|xdg_surface[^\n]*never[^\n]*configured'
 text='\n'.join(logs)
 return {'passed':'Private AQ_BACKENDS=wayland: mandatory parent, no DRM or libseat backend' in text and bool(re.search(r'Output WAYLAND-1: configure surface with [0-9]+',text)) and not re.search(forbidden,text,re.I),'mandatoryMarker': 'Private AQ_BACKENDS=wayland: mandatory parent, no DRM or libseat backend' in text,'configureHandlerObserved':bool(re.search(r'Output WAYLAND-1: configure surface with [0-9]+',text)),'forbiddenDiagnostics':re.findall(forbidden,text,re.I)}

def repl_script(text):return 'do\n'+text+'\nend'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verify():
 packet=json.loads((B/'frozen-inputs.json').read_text())
 for row in packet['files']:
  if sha(row['path'])!=row['sha256']:raise RuntimeError('Frozen Qt input changed:'+row['path'])
 for row in packet['symlinks']:
  p=Path(row['path'])
  if not p.is_symlink() or os.readlink(p)!=row['target']:raise RuntimeError('Frozen host symlink changed:'+str(p))
 return packet

def observer(mode,output,main,snapshot,snapshot_sha=None):
 command=[sys.executable,str(B/'main_observer.py'),mode,'--folder',str(output),'--snapshot',str(snapshot),'--main-signature',main['HYPRLAND_INSTANCE_SIGNATURE'],'--main-runtime',main['XDG_RUNTIME_DIR'],'--main-home',main['HOME']]
 if snapshot_sha:command+=['--snapshot-sha256',snapshot_sha]
 result=subprocess.run(command,env=main,capture_output=True,text=True,timeout=30)
 if result.returncode:raise RuntimeError('Read-only main observer failed:'+result.stderr)
 return json.loads(result.stdout)

def write_private(path,value):path.write_text(json.dumps(value,indent=2)+'\n');path.chmod(0o600)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--attempt',type=Path);parser.add_argument('--preflight',action='store_true');args=parser.parse_args()
 packet=verify()
 if args.preflight:
  print(json.dumps({'preflight':'pass','files':len(packet['files']),'symlinks':len(packet['symlinks']),'manifestSHA256':sha(B/'frozen-inputs.json'),'nativeLaunch':False}));return 0
 if not args.attempt:parser.error('--attempt is required for authorized execution')
 scope=require_qa_scope();main_env=dict(os.environ);original_environment=dict(main_env)
 output=args.attempt.resolve();assert output.parent==B and output.name.startswith('attempt-');os.umask(0o077);output.mkdir(mode=0o700)
 frozen=(B/'frozen-inputs.json').read_bytes();snapshot=output/'main-before.json';captured=None;host=None;session_report=None
 report={'scope':'Private Weston headless GL→Hyprland Wayland, public Qt6.11.2 X11/XCB same QApplication WindowModal toolkit compatibility','result':'pending','nativeMainInputProved':False,'physicalHardwareProved':False,'mainGUIWrites':False,'mainRestorationWrites':False,'candidateOnly':True,'productionDeployment':False,'scopeEvidence':scope,'sourceManifestSHA256':sha(B/'frozen-inputs.json'),'hostChecks':[],'toolkitFeatureGates':[],'commandAcknowledgements':[],'mainPreservation':{},'cleanup':{}}
 def gate(name,value,**details):report['hostChecks'].append({'name':name,'passed':bool(value),**details});assert value,name
 try:
  captured=observer('capture',output/'before-main',main_env,snapshot)
  spec=importlib.util.spec_from_file_location('_qt_private_x11_weston_host_v1',HOST/'weston_host.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  host=module.PrivateHyprSession(output/'host',main_env,width=1600,height=1000,nested_lua=(B/'nested-qt.lua').read_bytes(),dri_prime='pci-0000_00_02_0',mesa_vendor=True)
  with host as session:
   loaded=False;probe_loaded=False
   try:
    gate('private host actual DMA-BUF probe succeeded',bool(session.evidence.get('actualDmabuf')),probe=session.evidence.get('actualDmabuf'))
    gate('only exact private1600x1000 scale1 output exists',len(session.data('monitors'))==1 and all(session.data('monitors')[0].get(k)==v for k,v in {'width':1600,'height':1000,'scale':1,'x':0,'y':0,'transform':0}.items()),outputs=session.data('monitors'))
    xwayland=json.loads(session.ctl('getoption','xwayland:enabled','-j'))
    x11=session.evidence.get('x11',{});setups=x11.get('readOnlySetup',[])
    gate('explicit owned private Xwayland with real authenticated/refused setup',xwayland.get('bool') is True and len(setups)==2 and setups[0]['status']==0 and setups[1]['status']==1 and x11['server']['ppid']==session.evidence['compositorPID'],option=xwayland,authority=x11)
    gate('private child has no configuration errors or existing clients/plugins',not session.ctl('configerrors').strip() and session.data('clients')==[] and session.data('plugin','list')==[])
    aq_maps=module.original.mapped_files(session.evidence['compositorPID'])
    gate('actual exact lifecycle Aquamarine module mapped only in private child',aq_maps['files'].get(str(AQ))==sha(AQ),mappedSHA256=aq_maps['files'].get(str(AQ)))
    readiness=session.evidence.get('ipcReadiness',[])
    gate('owned child IPC readiness consumed complete verified read-only JSON reply',len(readiness)==1 and readiness[0]['peer']['pid']==session.evidence['compositorPID'] and readiness[0]['peer']['uid']==os.getuid() and readiness[0]['request']=='j/version' and readiness[0]['completeServerEOF'] is True,readiness=readiness)
    assert sha(PLUGIN)==EXPECTED_PLUGIN_SHA256,'Exact frozen candidate binary required before loading'
    assert session.ctl('plugin','load',str(PLUGIN)).strip()=='ok';loaded=True
    plugin_rows=session.data('plugin','list');maps=module.original.mapped_files(session.evidence['compositorPID'])
    gate('actual exact v19 modal candidate native module mapped privately',len(plugin_rows)==1 and maps['files'].get(str(PLUGIN))==EXPECTED_PLUGIN_SHA256,plugins=plugin_rows,mappedModuleSHA256=maps['files'].get(str(PLUGIN)),expectedModuleSHA256=EXPECTED_PLUGIN_SHA256,candidateOnly=True)
    session.ctl('repl',repl_script((B/'private-plugin.lua').read_text()))
    gate('native modal focus and family APIs published privately',session.ctl('repl','print(hl.plugin.hyprbars.modal_focus_bridge())').strip()=='true' and isinstance(json.loads(session.ctl('repl','print(hl.plugin.hyprbars.window_families())')),list))
    assert session.ctl('plugin','load',str(PROBE)).strip()=='ok';probe_loaded=True
    probe_maps=module.original.mapped_files(session.evidence['compositorPID'])
    probe_state=json.loads(session.ctl('repl','print(hl.plugin.qt_modal_probe.state())'))
    gate('exact private read-only modal diagnostics mapped and callable',probe_maps['files'].get(str(PROBE))==sha(PROBE) and isinstance(probe_state,dict) and 'seatGrab' in probe_state,mappedSHA256=probe_maps['files'].get(str(PROBE)),initialState=probe_state)
    session_report=run_session(session.env,output/'qt',main_env,session.evidence,session.guard)
    report['x11ProtocolGates']=session_report.get('x11ProtocolGates',[]);report['toolkitFeatureGates']=session_report['checks'];report['commandAcknowledgements']=session_report.get('commandAcknowledgements',[]);report['cleanup']['qt']=session_report['preservation']
    if session_report['result']!='pass':raise RuntimeError('Actual private Qt session failed:'+str(session_report.get('error')))
    assert len(report['x11ProtocolGates'])==1 and all(row['passed'] for row in report['x11ProtocolGates'])
    assert len(session_report['checks'])==EXPECTED_TOOLKIT_GATES and all(row['passed'] for row in session_report['checks'])
   finally:
    # Every owned Qt/pointer/motion client must have exited before native unload/host teardown.
    if loaded:
     try:
      host.guard()
      clients=session.data('clients');report['cleanup']['privateClientsBeforeUnload']=clients
      if clients:raise RuntimeError('Owned clients remain: refuse plugin unload before client cleanup')
      if probe_loaded:
       report['cleanup']['nativeButtonObservations']=json.loads(session.ctl('repl','print(hl.plugin.qt_modal_probe.events())'))
       session.ctl('plugin','unload',str(PROBE));report['cleanup']['probeUnloadedNormally']=all(row['name']!='qt_modal_probe' for row in session.data('plugin','list'))
       if not report['cleanup']['probeUnloadedNormally']:raise RuntimeError('Private diagnostic module did not unload')
      session.ctl('plugin','unload',str(PLUGIN));report['cleanup']['pluginUnloadedNormally']=session.data('plugin','list')==[]
      if not report['cleanup']['pluginUnloadedNormally']:raise RuntimeError('Private native plugin did not unload')
     except Exception as error:report['cleanup']['pluginUnloadError']=repr(error);raise
  report['cleanup']['host']=session.evidence
  if not session.evidence.get('x11ServerGoneOnCompositorDisconnect') or not session.evidence.get('x11DisplayArtifactsGone') or session.evidence.get('x11CredentialCleanupErrors'):raise RuntimeError('Private X11 component/authority cleanup failed')
  if not session.evidence.get('runtimeGone') or session.evidence.get('cleanupErrors') or session.evidence.get('unexpectedInnerDescendants') or session.evidence.get('remainingDescendants'):raise RuntimeError('Private host lifecycle failed')
  archives=[row for row in session.evidence.get('archivedRuntime',[]) if Path(row['archive']).name=='hyprland.log']
  if len(archives)!=1:raise RuntimeError('Exact owned archived compositor log required')
  logs=[Path(archives[0]['archive']).read_text(),(output/'host/weston-renderer.log').read_text()]
  transport=transport_log_gate(logs)
  gate('actual mandatory parent configure transport has no protocol/DRM/pipe failures',transport.pop('passed'),**transport,logHashes={archives[0]['archive']:sha(archives[0]['archive']),str(output/'host/weston-renderer.log'):sha(output/'host/weston-renderer.log')})
 except Exception as error:report['error']=repr(error)
 finally:
  if host:report['cleanup']['host']=host.evidence
  if captured:
   try:
    comparison=observer('compare',output/'after-main',original_environment,snapshot,captured['snapshotSHA256']);report['mainPreservation']=comparison['checks']
   except Exception as error:report['mainObservationError']=repr(error)
  report['mainPreservation']['originalProcessEnvironmentUnchanged']=dict(os.environ)==original_environment
  report['mainPreservation']['frozenManifestBytes']=(B/'frozen-inputs.json').read_bytes()==frozen
  try:verify();report['mainPreservation']['allFrozenInputsExact']=True
  except Exception as error:report['sourceError']=repr(error);report['mainPreservation']['allFrozenInputsExact']=False
  passed_toolkit=len(report.get('x11ProtocolGates',[]))==1 and all(row['passed'] for row in report['x11ProtocolGates']) and len(report['toolkitFeatureGates'])==EXPECTED_TOOLKIT_GATES and all(row['passed'] for row in report['toolkitFeatureGates'])
  report['result']='pass' if captured and not report.get('error') and not report.get('mainObservationError') and passed_toolkit and len(report['hostChecks'])==EXPECTED_HOST_GATES and all(row['passed'] for row in report['hostChecks']) and all(report['mainPreservation'].values()) else 'fail'
  write_private(output/'report.json',report)
 print(json.dumps({'result':report['result'],'toolkitFeatureGates':len(report['toolkitFeatureGates']),'toolkitFeaturePassed':sum(row['passed'] for row in report['toolkitFeatureGates']),'hostGates':len(report['hostChecks']),'commandAcknowledgements':len(report['commandAcknowledgements']),'mainPreservation':report['mainPreservation'],'reportSHA256':sha(output/'report.json'),'error':report.get('error')}))
 return int(report['result']!='pass')

if __name__=='__main__':raise SystemExit(main())
