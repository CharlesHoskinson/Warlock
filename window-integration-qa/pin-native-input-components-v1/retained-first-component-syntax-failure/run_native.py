#!/usr/bin/python3
"""Explicit root-only component campaign B. Import/preflight never launches a GUI."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,stat,sys,traceback
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent
V2=Path('/home/hoskinson/window-integration-qa/pin-maximized-native-v2')
QA=Path('/home/hoskinson/window-integration-qa')
sys.path.insert(0,str(B/'host'));sys.path.insert(0,str(V2/'proposed'));sys.path.insert(0,str(V2))
import private_output_host,output_readiness,pair_binding
spec=importlib.util.spec_from_file_location('_b_original_root_runner_functions',V2/'proposed/run_native.py')
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
sys.path.insert(0,str(B/'controller'))
from block_controller import BlockController,CASES

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(path):
 packet=json.loads(Path(path).read_bytes())
 for name,digest in packet['inputs'].items():
  p=Path(name);mode=packet['inputModes'].get(name)
  # Intentional ancestral byte/link aliases keep their literal link proof too.
  if type(digest)is not str or type(mode)is not int or not p.is_file()or sha(p)!=digest or stat.S_IMODE(p.stat().st_mode)!=mode:raise ValueError('Exact source bytes/mode changed: '+name)
 for name,target in packet['symlinks'].items():
  if not Path(name).is_symlink()or os.readlink(name)!=target:raise ValueError('Exact source literal link changed: '+name)
 for name,mode in packet['directoryModes'].items():
  p=Path(name)
  if type(mode)is not int or p.is_symlink()or not p.is_dir()or stat.S_IMODE(p.stat().st_mode)!=mode:raise ValueError('Exact current/ancestral source directory mode changed: '+name)
 return packet

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source-check',action='store_true');ap.add_argument('--preflight',action='store_true');ap.add_argument('--attempt',type=Path);ap.add_argument('--component',choices=list(CASES));a=ap.parse_args()
 path=B/('SOURCE_INPUTS.json'if a.source_check else'frozen-inputs.json');packet=verify(path)
 if a.source_check or a.preflight:
  print(json.dumps(dict(result='pass',inputs=len(packet['inputs']),links=len(packet['symlinks']),directories=len(packet['directoryModes']),nativeLaunched=False)));return 0
 if a.attempt is None:ap.error('Explicit fresh root-authorized --attempt required')
 if a.component is None:ap.error('Explicit independent --component B11, B12 or B11+B12 required')
 selectedCases=list(CASES[a.component])
 scope=require_qa_scope();grant=json.loads((B/'ROOT_NATIVE_GRANT.json').read_bytes())
 if grant.get('nativeAuthorized')is not True or grant.get('manifestSHA256')!=sha(path)or grant.get('pairSHA256')!=sha(B/'PAIR_READY.json'):raise ValueError('Exact root source/native grant required')
 if type(grant.get('componentCases'))is not list or grant['componentCases']!=selectedCases:raise ValueError('Exact root independent component grant required')
 pair=pair_binding.read_pair(B/'PAIR_READY.json');output=a.attempt.absolute()
 if output.resolve()!=output or output.parent!=B or not re.fullmatch(r'attempt-[1-9][0-9]*',output.name):raise ValueError('Exact fresh private component attempt required')
 os.umask(0o077);output.mkdir(mode=0o700);main_env=dict(os.environ);manifest=path.read_bytes();snapshot=output/'main-before.json'
 report=dict(result='pending',scope=scope,campaign='B11/B12 independent native-block/noFocus components',componentCases=selectedCases,originalTwelveCaseIncrementAccepted=False,hostChecks=[],mainPreservation={},bindingChecks=[],original14Credit=False,fullCampaignBAccepted=False,fullWindowsParityAccepted=False,componentIncrementAccepted=False,sourceManifestSHA256=sha(path),mainGUIWrites=False,mainRestorationWrites=False)
 host=controller=before=None
 def persist():original.persist(output/'report.json',report)
 def gate(name,ok,**details):
  report['hostChecks'].append(dict(name=name,passed=ok is True,**details));persist()
  if ok is not True:raise AssertionError(name)
 try:
  before=original.observer('capture',output/'before-main',main_env,snapshot)
  api=private_output_host.adapt(original.module('_b_reviewed_host',B/'host/candidate_host.py'))
  lua=(QA/'browser-files-flow-v20/nested-qt.lua').read_bytes()+(V2/'private-controls.lua').read_bytes()
  lua+=(B/'monocle-component.lua').read_bytes()
  keyboard='/home/hoskinson/window-behavior-spec/pin-lifetime-v3/keyboard-chords/physical-keyboard'
  lua+=('\nhl.permission({binary='+json.dumps(keyboard)+',type="keyboard",mode="allow"})\n').encode()
  host=api.PrivateHyprSession(output/'host',main_env,1600,1000,lua,dri_prime='pci-0000_00_02_0',mesa_vendor=True);host.host.b_frozen=packet
  loaded=[]
  with host as session:
   gate('Actual private mandatory parent DMA-BUF probe',bool(session.evidence.get('actualDmabuf')),actual=session.evidence.get('actualDmabuf'))
   report['outputReadiness']=output_readiness.collect(session,output/'host/output-readiness-evidence.json')
   gate('Exact single1600x1000 scale1 private output',output_readiness.exact_outputs(session.data('monitors')))
   gate('Private Xwayland disabled',json.loads(session.ctl('getoption','xwayland:enabled','-j')).get('bool')is False)
   gate('No previous clients/modules/config errors',session.data('clients')==[]and session.data('plugin','list')==[]and not session.ctl('configerrors').strip())
   maps=api.original.mapped_files(session.evidence['compositorPID']);AQ=QA/'aquamarine-nested-bootstrap-v2/prefix/lib/libaquamarine.so.0.15.0'
   gate('Exact mandatory bootstrap AQ actually mapped',maps['files'].get(str(AQ))==packet['inputs'][str(AQ)])
   ready=session.evidence['ipcReadiness'];gate('Complete owned current IPC EOF before clients',len(ready)==1 and ready[0]['peer']['pid']==session.evidence['compositorPID']and ready[0]['peer']['uid']==os.getuid()and ready[0]['completeServerEOF']is True)
   try:
    for key in ['plugin','probe','observer']:
     verify(path);p=pair[key]
     if session.ctl('plugin','load',p).strip()!='ok':raise RuntimeError('Exact matching source-bound QA module load refused: '+key)
     loaded.append((key,p));maps=api.original.mapped_files(session.evidence['compositorPID'])
     gate('Exact matching '+key+' actually mapped',maps['files'].get(p)==packet['inputs'][p])
    native=output/'native';native.mkdir(mode=0o700);controller=BlockController(session,native,B/'PAIR_READY.json',packet)
    controller.attest('before-independent-native-components');report['components']=controller.run_components(a.component);persist()
   finally:
    # Controller closes each genuine Qt actor in its per-case finally; an
    # uncertain failed cleanup cannot be replaced with host forced cleanup.
    session.guard();clients=session.data('clients');report['clientsBeforeUnload']=clients;persist()
    if clients:raise RuntimeError('Unload refused until all declared private clients normally gone')
    if controller:report['producerSeal']=controller.registry.seal_before_host_close()if not controller.registry.sealed else dict(sealed=True)
    for key,p in reversed(loaded):
     verify(path);session.ctl('plugin','unload',p);report[key+'UnloadedNormally']=all(r['name']!=({'plugin':'hyprbars','probe':'qt_modal_probe','observer':'pin_campaign_b'}[key])for r in session.data('plugin','list'));persist()
     if report[key+'UnloadedNormally']is not True:raise RuntimeError('Exact normal unload refused: '+key)
    gate('Every reviewed module normally unloaded',session.data('plugin','list')==[])
  report['hostEvidence']=host.evidence;report['normalHostClosure']=host.evidence.get('campaignBNormalClosure',{});persist()
  gate('Separate exact B producer/base normal closure',report['normalHostClosure'].get('normal')is True)
  gate('Original exact private lifecycle no unknown descendants',host.evidence.get('runtimeGone')is True and not host.evidence.get('cleanupErrors')and not host.evidence.get('unexpectedInnerDescendants')and not host.evidence.get('remainingDescendants'))
  archives=[r for r in host.evidence.get('archivedRuntime',[])if Path(r['archive']).name=='hyprland.log']
  if len(archives)!=1:raise RuntimeError('One exact archived compositor log required')
  gate('Original mandatory transport predicate through teardown',original.transport([Path(archives[0]['archive']).read_text(),(output/'host/weston-renderer.log').read_text()]))
 except BaseException:report['error']=traceback.format_exc()
 finally:
  if host:report['hostEvidence']=host.evidence
  if controller:report['controllerBlocked']=controller.blocked
  if before:
   try:report['mainPreservation']=original.observer('compare',output/'after-main',main_env,snapshot,before['snapshotSHA256'])['checks']
   except BaseException:report['mainObserverError']=traceback.format_exc()
  report['mainPreservation']['originalEnvironmentUnchanged']=dict(os.environ)==main_env;report['mainPreservation']['frozenManifestBytes']=path.read_bytes()==manifest
  try:verify(path);report['mainPreservation']['allFrozenInputsExact']=True
  except BaseException:report['mainPreservation']['allFrozenInputsExact']=False;report['sourceError']=traceback.format_exc()
  results=report.get('components',{}).get('actualComponentResults',[])
  report['componentIncrementAccepted']=bool(before and not report.get('error')and not report.get('mainObserverError')and not report.get('controllerBlocked')and len(results)==len(selectedCases)and [r.get('case')for r in results]==selectedCases and report.get('components',{}).get('originalTwelveCaseIncrementAccepted')is Falseand report.get('normalHostClosure',{}).get('normal')is True and all(r['passed']is True for r in report['hostChecks'])and all(report['mainPreservation'].values()))
  report['result']='pass'if report['componentIncrementAccepted']else'fail';persist()
 print(json.dumps(dict(result=report['result'],componentIncrementAccepted=report['componentIncrementAccepted'],fullCampaignBAccepted=False,original14Credit=False,reportSHA256=sha(output/'report.json'),error=report.get('error'))));return int(report['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
