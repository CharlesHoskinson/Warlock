#!/usr/bin/python3
"""Root-only actual QS composition. No GUI unless exact new grant is present."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,stat,sys,time,traceback
sys.dont_write_bytecode=True
from io_guard import sha,strict,publish_json,verify,exact
from selection import *
from materialize import prepare,publish_configs,identity,exact_exec
from route_runtime import QuickshellChannel,HelperReceipts,controller,retirement_proof
from cycle_binding import install as install_cycle
sys.path.insert(0,str(QA));from qa_launch import require_qa_scope
sys.path.insert(0,str(QA/'pin-maximized-native-v2/proposed'))
sys.path.insert(1,str(QA/'pin-maximized-native-v2'))
import private_output_host,output_readiness,pair_binding
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
from root_functions import original_functions
original=original_functions()
def native_class():
 p=QA/'pin-native-qa-v3';sys.path.insert(0,str(p))
 try:return load('_pin_qs_original_fixture_controller',p/'native_cases.py').NativeCases
 finally:sys.path.pop(0)
def gate_phase(grant,phase,packet_path):
 if type(grant)is not dict or grant.get('nativeAuthorized')is not True or grant.get('manifestSHA256')!=sha(packet_path)or grant.get('phase')!=phase:raise ValueError('Exact new root native source/phase grant required')
 if phase=='reliability':
  proof_path=Path(grant['requiredRoutesReview']);proof=strict(proof_path.read_bytes())
  if sha(proof_path)!=grant.get('requiredRoutesReviewSHA256')or proof.get('accepted')is not True or proof.get('selectedCoreSHA256')!=CORE_SHA or proof.get('selectedPluginSHA256')!=PLUGIN_SHA or proof.get('providerSHA256')!=sha(PROVIDER)or proof.get('ordinaryHelperSHA256')!=HELPER_SHA or proof.get('sourceManifestSHA256')!=sha(packet_path)or proof.get('requiredRoutes')!={k:True for k in ('normalChanged','sameCommand','cancelledConsumer','stalePopupReload','publicTypedRefusals')}:raise ValueError('All actual required routes reviewed before fixed reliability; no baseline substitution')
def stop_qs(session,p,channel,output):
 before=channel.guard();command=[str(QS),'kill','--pid',str(p['process'].pid)];child=session.host.launch('pin-qs-stop-'+p['life'],command,p['environment']);registered=dict(session.host.processes[-1][1]);child.wait(timeout=2);p['process'].wait(timeout=5)
 row=dict(requesterBefore=before,command=command,registered=registered,exitCode=child.returncode,stopChildGone=not Path('/proc/'+str(child.pid)).exists(),shellExitCode=p['process'].returncode,shellGone=not Path('/proc/'+str(p['process'].pid)).exists(),forced=False)
 publish_json(output/'qs-normal-stop.json',row)
 if child.returncode!=0 or p['process'].returncode!=0 or not row['shellGone']or not row['stopChildGone']:raise ValueError('Actual owned QS kill IPC and normal exit required')
 return row
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source-check',action='store_true');ap.add_argument('--preflight',action='store_true');ap.add_argument('--attempt',type=Path);ap.add_argument('--phase',choices=('cold-baseline','reliability'),default='cold-baseline');a=ap.parse_args()
 packet_path=B/('source-ready.json'if a.source_check else'frozen-inputs.json');packet=verify(strict(packet_path.read_bytes()));verify_selection()
 if a.source_check or a.preflight:
  print(json.dumps(dict(result='pass',inputs=len(packet['inputs']),symlinks=len(packet['symlinks']),GUI=False,nativeLaunched=False)));return 0
 grant=strict((B/'ROOT_NATIVE_GRANT.json').read_bytes());gate_phase(grant,a.phase,packet_path);scope=require_qa_scope()
 if a.attempt is None:raise ValueError('Explicit fresh root-owned attempt required')
 output=a.attempt.absolute()
 if output.resolve()!=output or output.parent!=B or not re.fullmatch('attempt-[1-9][0-9]*',output.name):raise ValueError('Exact fresh QA output only')
 output.mkdir(mode=0o700);main_env=dict(os.environ);before=None;host=None;route=None;qs=None;channel=None;loaded=[];number=0
 report=dict(result='pending',phase=a.phase,scope=scope,hostChecks=[],mainPreservation={},QS=[],slots=[],publicRefusals=[],sourceManifestSHA256=sha(packet_path),baselineAccepted=False,reliabilityAccepted=False,fullRequiredRoutesAccepted=False,fullPinAccepted=False,maxSpecificHelperSelected=False,GUIControlledByRoot=True,mainChanges=False,helpersExpected=2 if a.phase=='cold-baseline'else 12,automaticRetries=0)
 def persist():
  nonlocal number
  number+=1;publish_json(output/('checkpoint-'+str(number)+'.json'),report)
 def gate(name,ok,**details):
  report['hostChecks'].append(dict(name=name,passed=ok is True,**details));persist()
  if ok is not True:raise AssertionError(name)
 try:
  before=original.observer('capture',output/'before-main',main_env,output/'main-before.json');api=private_output_host.adapt(load('_pin_qs_selected_host',B/'candidate_host.py'))
  lua=(QA/'browser-files-flow-v20/nested-qt.lua').read_bytes()+(QA/'pin-maximized-native-v2/private-controls.lua').read_bytes()
  lua+=('\nhl.permission({binary='+json.dumps(str(COMPOSITION/'keyboard/physical-keyboard'))+',type="keyboard",mode="allow"})\n').encode()
  host=api.PrivateHyprSession(output/'host',main_env,1600,1000,lua,dri_prime='pci-0000_00_02_0',mesa_vendor=True);host.host.qs_frozen=packet
  with host as session:
   gate('Mandatory actual private DMA-BUF parent',bool(session.evidence.get('actualDmabuf')))
   report['outputReadiness']=output_readiness.collect(session,output/'host/output-readiness.json');gate('Original exact1600x1000 scale1 output',output_readiness.exact_outputs(session.data('monitors')))
   gate('No previous clients/modules/errors',session.data('clients')==[]and session.data('plugin','list')==[]and not session.ctl('configerrors').strip())
   gate('Private Xwayland disabled',strict(session.ctl('getoption','xwayland:enabled','-j')).get('bool')is False)
   pair=pair_binding.read_pair(QA/'pin-maximized-native-v2/PAIR_READY.json')
   # Max-specific helper remains immutable ancestry; it is not the selected
   # ordinary helper or a frontend/MAX acceptance claim.
   def attest(label):
    observed=pair_binding.attest(session,{**pair,'inputs':packet['inputs']},label,[str(path)for _,path in loaded]);report.setdefault('coreBindings',[]).append(observed);persist()
    if observed['passed']is not True:raise ValueError('Exact actual owning core/registered group/maps required')
   attest('before-private-frontend-clients')
   aq=QA/'aquamarine-nested-bootstrap-v2/prefix/lib/libaquamarine.so.0.15.0';maps=api.original.mapped_files(session.evidence['compositorPID']);gate('Exact mandatory bootstrap AQ actually mapped',maps['files'].get(str(aq))==packet['inputs'].get(str(aq)))
   ready=session.evidence['ipcReadiness'];gate('Original owned complete IPC EOF',len(ready)==1 and ready[0]['peer']['pid']==session.evidence['compositorPID']and ready[0]['peer']['uid']==os.getuid()and ready[0]['completeServerEOF']is True)
   fixture_class=native_class()
   class SceneFixture(fixture_class):
    # Only setup/lifetime/scene/normal quit methods are used; original A14 is not run.
    def persist(self):
     self.counter+=1;publish_json(self.output/('fixture-'+str(self.counter)+'.json'),self.report)
   route=SceneFixture(session,output/'native');route.launch_legacy()
   try:
    for name,path in [('hyprbars',PLUGIN),('qt_modal_probe',WINDOW_PROBE),('toolkit_held_probe',LAYER_PROBE)]:
     verify(packet);reply=session.ctl('plugin','load',str(path));gate('Exact compatible '+name+' load ACK',reply.strip()=='ok');loaded.append((name,path))
     maps=api.original.mapped_files(session.evidence['compositorPID']);gate('Exact selected '+name+' actually mapped',maps['files'].get(str(path))==packet['inputs'].get(str(path)))
    attest('all-owning-ABI-modules-loaded');route.start_pointer();route.focus('peer')
    lives=('A',)if a.phase=='cold-baseline'else('A','B')
    for life in lives:
     env=prepare(session,life);folder=output/('QS-'+life);folder.mkdir(mode=0o700)
     qs=session.host.launch('pin-qs-'+life,env['command'],env['environment']);admission=publish_configs(session,qs,env,packet,folder/'admission.json');channel=QuickshellChannel(session,env,folder/'IPC');channel.call('shell','ping');receipts=HelperReceipts(env,channel,public_refusals=a.phase=='cold-baseline');front=controller(route,qs,channel,receipts)
     binding=install_cycle(session,env);report['QS'].append(dict(life=life,admission=admission,cycleBinding=binding));persist()
     schedule=[(life,1,'owner','right','pointer')]if a.phase=='cold-baseline'else[row for row in LIFE_SCHEDULE if row[0]==life]
     old=None
     for _,index,member,opener,action in schedule:
      front.expected_name=member;row=front.toggle(member,opener,action);raw=row['completion']['helperLifecycle']['rawMenu'];slot=dict(life=life,index=index,member=member,opener=opener,action=action,genuineFeature=row)
      if old:
       slot['retirements']=[retirement_proof(old,raw,role)for role in('capture','toggle')]
       if not exact(raw['captured'],row['captured']):raise ValueError('Actual new command must retain planned current native capture')
      report['slots'].append(slot);old=raw;persist()
     if a.phase=='cold-baseline':
      report['publicRefusals']=receipts.refusals
      gate('Four genuine public malformed argument refusals conserve current record',len(receipts.refusals)==4)
     report['QS'][-1]['helperTerminal']=receipts.terminal();attest('after-genuine-QS-'+life+'-actions');persist()
     expected=2 if a.phase=='cold-baseline'else 6;gate('Exact ordinary helper count for QS '+life,report['QS'][-1]['helperTerminal']['exactDurableCount']==expected)
     report['QS'][-1]['normalStop']=stop_qs(session,env,channel,folder);qs=None;channel=None;persist()
     cycle_files=sorted((Path(env['home'])/'cycle-evidence').glob('*.json'));cycle_rows=[strict(p.read_bytes())for p in cycle_files];report['QS'][-1]['cycleReceipts']=cycle_rows
     expected_cycles=sum(r.get('command',[None,None,None])[-1]=='super-t'for r in front.report['setupInputs'])
     gate('Every genuine private cycle relay normal and accounted',len(cycle_rows)==expected_cycles and all(r.get('result')=='pass'and r.get('gone')is True and r.get('exitCode')==0 for r in cycle_rows))
   finally:
    if qs is not None and channel is not None:
     try:report['failedQSNormalStop']=stop_qs(session,env,channel,folder)
     except BaseException as e:report['failedQSStopError']=repr(e)
    route.close();gate('Original fixture and pointer normally gone',route.report.get('normalCleanup')is True)
    if session.data('clients'):raise ValueError('Unload requires exact private clients normally gone')
    for name,path in reversed(loaded):
     session.ctl('plugin','unload',str(path));gate('Exact '+name+' normally unloaded',all(p['name']!=name for p in session.data('plugin','list')))
    loaded=[]
  report['normalHostClosure']=host.evidence.get('privateQSNormalClosure',{});gate('Declared exact frontend/base normal closure',report['normalHostClosure'].get('normal')is True)
  gate('Original private lifecycle runtime/descendants',host.evidence.get('runtimeGone')is True and not host.evidence.get('cleanupErrors')and not host.evidence.get('unexpectedInnerDescendants')and not host.evidence.get('remainingDescendants'))
  archives=[r for r in host.evidence.get('archivedRuntime',[])if Path(r['archive']).name=='hyprland.log'];gate('Original mandatory no-fallback transport',len(archives)==1 and original.transport([Path(archives[0]['archive']).read_text(),(output/'host/weston-renderer.log').read_text()]))
 except BaseException:report['error']=traceback.format_exc();persist()
 finally:
  if host:report['hostEvidence']=host.evidence
  if before:
   try:report['mainPreservation']=original.observer('compare',output/'after-main',main_env,output/'main-before.json',before['snapshotSHA256'])['checks']
   except BaseException:report['mainObserverError']=traceback.format_exc()
  report['mainPreservation']['originalEnvironmentUnchanged']=dict(os.environ)==main_env
  try:verify(packet);report['mainPreservation']['allFrozenInputsExact']=True
  except BaseException:report['mainPreservation']['allFrozenInputsExact']=False;report['sourceError']=traceback.format_exc()
  good=bool(before and not report.get('error')and not report.get('mainObserverError')and all(report['mainPreservation'].values())and all(r['passed']is True for r in report['hostChecks'])and len(report['slots'])==(1 if a.phase=='cold-baseline'else 6))
  report['baselineAccepted']=good and a.phase=='cold-baseline';report['reliabilityAccepted']=good and a.phase=='reliability';report['result']='pass'if good else'fail';persist();publish_json(output/'report.json',report)
 print(json.dumps(dict(result=report['result'],baselineAccepted=report['baselineAccepted'],reliabilityAccepted=report['reliabilityAccepted'],fullRequiredRoutesAccepted=False,reportSHA256=sha(output/'report.json'))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
