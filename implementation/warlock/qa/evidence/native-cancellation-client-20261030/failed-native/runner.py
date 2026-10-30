#!/usr/bin/env python3
"""Private native Restore cancellation order fixture; no Elm or WebKit host."""
import copy,hashlib,importlib.util,json,os,pathlib,resource,select,signal,sys,time,traceback
from pathlib import Path
R=Path('/home/charles/Warlock');B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild');D=Path(__file__).resolve().parent
CLIENT=B/'cancellation-client-terra1-v1/adapter';P=R/'implementation/warlock';FIX=R/'implementation/warlock-client-provider-native-v204/fixture.py'
RUNTIME=D/'runtime_candidate.py';RUNTIME_SHA='91a8acd88af2a60075f4ec2ae0c3775dd6917286408052ec338823b18cfcf6de'
CLIENT_SHA='42247d6a560093b8a46a3369065d7debfe78baa94b78b67490a61c96fafab6f0';EFFECT_SHA='e01aa144ef2b80cf1b259fd45a926ec9ee6e101040402134efeef1ad184667ca';ENDPOINT_SHA='e254b870922a46b935de9d85db1de56129838ea2cf73eeb55c9fa16e8539d731'
PLUGIN_SHA='12959a5dd6083fb9e37333bd62574495304afe48f8ad0376587ab0fcc5a7cc2b';CORE_SHA='b1c58200342f3cb8f5442bc34b92563ca21801194a0d63afc6e74280ca3abd0e'
LUA=b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
def raw(path,expected):
 data=Path(path).read_bytes()
 if hashlib.sha256(data).hexdigest()!=expected:raise RuntimeError('input changed: '+str(path))
 return data
def module(name,path,expected):
 data=raw(path,expected);spec=importlib.util.spec_from_loader(name,loader=None);m=importlib.util.module_from_spec(spec);m.__file__=str(path);sys.modules[name]=m;exec(compile(data,str(path),'exec'),m.__dict__);return m
def main():
 if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise SystemExit('protected no-bytecode launcher required')
 sys.path.insert(0,str(R/'window-integration-qa'));from qa_launch import require_qa_scope
 scope=require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('core limit differs')
 raw(FIX,'c6628d141b75bb20cc2fa526d85ef2a14025a28b832ebae57f1d996c76552f06')
 host=module('cancellation_current_host',RUNTIME,RUNTIME_SHA);qa=R/'implementation/warlock-client-provider-native-v204/qa';sys.path.insert(0,str(qa));from session_bus import isolate_session_host
 isolate_session_host(host)
 endpoint=module('endpoint',P/'adapter/endpoint.py',ENDPOINT_SHA);module('cancellation_endpoint',CLIENT/'cancellation_endpoint.py',CLIENT_SHA);effect=module('effect_endpoint',CLIENT/'effect_endpoint.py',EFFECT_SHA)
 out=D/('orders-'+str(time.time_ns()));out.mkdir(mode=0o700);runtime=Path.home()/'window-integration-qa'/('cancellation-orders-'+str(time.time_ns()))
 report={'passed':False,'nativeAcceptance':False,'requirementAccepted':False,'physicalEscapeObserved':False,'resourceRetirementProof':False,'scope':scope,'checks':[],'limits':['Native owner token counts not exported; exact token retirement is not directly observed','No forced Unknown or native wrong-key injection; validated caller wrong-key refusal is not producer proof','No Elm, WebKit, durable production caller, physical Escape or full ARC012 acceptance']};s=None;fixture=None;loaded=False
 def check(name,value,**e):
  report['checks'].append({'name':name,'passed':bool(value),**e})
  if not value:raise RuntimeError(name)
 def wait(fn):
  end=time.monotonic()+6
  while time.monotonic()<end:
   s.guard();v=fn()
   if v:return v
   time.sleep(.025)
  raise RuntimeError('original six-second observation deadline')
 def retain(name,decision):
  p=out/(name+'.json');fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w') as f:json.dump(decision,f,sort_keys=True,separators=(',',':'));f.flush();os.fsync(f.fileno())
  fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:os.fsync(fd)
  finally:os.close(fd)
  return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'callerFsyncedBeforeAck':True}
 try:
  verified=host.verify_tuple();plugin=verified['slots']['authority'];check('ExactNewPluginTuple',plugin['sha256']==PLUGIN_SHA and verified['slots']['core']['sha256']==CORE_SHA)
  with host.PrivateHyprSession(runtime,dict(os.environ),1600,1000,LUA,mesa_vendor=True) as s:
   try:
    core=next(row for proc,row in s.host.processes if proc is s.child);proc_pid=core['pid'];proc_start=endpoint.start_time(proc_pid)
    check('ActualOwningCoreBeforePluginLoad',proc_start==core['start'] and hashlib.sha256(Path('/proc/'+str(proc_pid)+'/exe').read_bytes()).hexdigest()==CORE_SHA,pid=proc_pid,start=proc_start)
    check('NoPriorChildPlugins',s.data('plugin','list')==[])
    check('NewOwningPluginLoads',s.ctl('plugin','load',plugin['path']).strip()=='ok');loaded=True
    inventory=s.data('plugin','list');check('ExactLoadedPluginInventory',len(inventory)==1 and inventory[0]['name']=='elm-observation-authority' and inventory[0]['author']=='local' and inventory[0]['version']=='0.2',inventory=inventory)
    maps=Path('/proc/'+str(proc_pid)+'/maps').read_text();resolved=str(Path(plugin['path']).resolve());check('ExactPluginMapped',any(line.rstrip().endswith(resolved) for line in maps.splitlines()) and hashlib.sha256(Path(resolved).read_bytes()).hexdigest()==PLUGIN_SHA)
    client=effect.Endpoint(runtime=str(s.host.runtime),instance=s.env['HYPRLAND_INSTANCE_SIGNATURE'],pid=proc_pid,expected_start=int(proc_start),binary_sha256=CORE_SHA);attached=client.hello();cap=client.cancellation_negotiate('1');report['binding']=attached['binding'];report['capabilities']=cap
    from system_isolation import supply,validate
    env=supply(s.env,s.host.runtime);validate(env,s.host.runtime);control=runtime/'fixture-control.json';fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(FIX),str(control)],env=env);fixture_start=endpoint.start_time(fixture.pid);fixture_fd=os.pidfd_open(fixture.pid)
    try:
     def facts():return client.scene_facts('400')
     def roots():
      snapshot=client.snapshot('399'); f=facts();labels=['ELM-AUTHORITY-FIXTURE','ELM-ACTIVATION-PEER'];matches={label:[w for w in snapshot['windows'] if w['label']==label] for label in labels}
      if any(len(rows)>1 for rows in matches.values()):raise RuntimeError('Ambiguous native target labels')
      if any(len(rows)!=1 for rows in matches.values()):return None
      rows={label:entries[0] for label,entries in matches.items()};native={w['incarnation']:w for w in f['facts']['windows']}
      if not all(rows[label]['incarnation'] in native for label in labels):return None
      if any(native[rows[label]['incarnation']]['owner'] is not None for label in labels):raise RuntimeError('Fixture target is not an independent native root')
      return f,rows
     initial,rows=wait(roots);target=rows['ELM-AUTHORITY-FIXTURE']['incarnation'];peer=rows['ELM-ACTIVATION-PEER']['incarnation']
     actual_clients=s.data('clients');owned=[w for w in actual_clients if w.get('pid')==fixture.pid and w.get('title') in ('ELM-AUTHORITY-FIXTURE','ELM-ACTIVATION-PEER')]
     check('DistinctRealGtkRoots',target!=peer and fixture.poll() is None and endpoint.start_time(fixture.pid)==fixture_start and len(owned)==2 and len(actual_clients)==2 and {w['title'] for w in owned}=={'ELM-AUTHORITY-FIXTURE','ELM-ACTIVATION-PEER'},target=target,peer=peer,clients=owned,pid=fixture.pid,start=fixture_start)
     def intent(request,generation,operation,state):return {'request':str(request),'generation':str(generation),'incarnation':target,'operation':operation,'context':client.context(state)}
     minimized=client.effect(intent(1,1,'minimize',initial));check('InitialActualMinimizeCommitted',minimized['status']=='Committed',receipt=minimized)
     def minimized_facts():
      f=facts();w=next((w for w in f['facts']['windows'] if w['incarnation']==target),None);return f if w and w['minimized'] else None
     before=wait(minimized_facts);peer_before=next(w for w in before['facts']['windows'] if w['incarnation']==peer);original_focus=before['facts']['focused']
     first_intent=intent(2,2,'restore',before);deadline1=str(time.monotonic_ns()+6_000_000_000);first=client.prepare_effect(first_intent,deadline1);check('FirstPreparedOriginalDeadline',first['kind']=='effect-prepared' and first['deadlineMonotonicNs']==deadline1,prepared=first)
     check('PreparedQueryNoExecution',client.query_effect_decision(first)==first)
     forged=copy.deepcopy(first);forged['preparedId']=str(int(first['preparedId'])+1)
     try:client.cancel_effect(forged);wrong=False
     except endpoint.Refused:wrong=True
     check('CallerWrongKeyRefusedWithoutChangingPreparation',wrong and client.query_effect_decision(first)==first)
     cancelled=client.cancel_effect(first);check('CancelBeforeCommitIsCancelled',cancelled['status']=='Cancelled',receipt=cancelled)
     after_cancel=facts();target_after=next(w for w in after_cancel['facts']['windows'] if w['incarnation']==target);peer_after=next(w for w in after_cancel['facts']['windows'] if w['incarnation']==peer)
     check('CancelledLeavesTargetAndPeerAndFocus',target_after['minimized'] and peer_after==peer_before and after_cancel['facts']['focused']==original_focus,before=before,after=after_cancel)
     check('CommitAfterCancelReturnsIdenticalReceipt',client.commit_effect(first)==cancelled and client.query_effect_decision(first)==cancelled)
     after_late_commit=facts();check('LateCommitCannotMutateCancelledTargetPeerOrFocus',next(w for w in after_late_commit['facts']['windows'] if w['incarnation']==target)==target_after and next(w for w in after_late_commit['facts']['windows'] if w['incarnation']==peer)==peer_before and after_late_commit['facts']['focused']==original_focus,facts=after_late_commit)
     saved1=retain('cancelled-terminal',cancelled);ack1=client.ack_effect_decision(cancelled);report['cancelFirst']={'prepared':first,'decision':cancelled,'durableCallerCopy':saved1,'ack':ack1}
     before2=wait(minimized_facts);second_intent=intent(3,3,'restore',before2);deadline2=str(time.monotonic_ns()+6_000_000_000);second=client.prepare_effect(second_intent,deadline2);check('SecondPreparedOriginalDeadline',second['kind']=='effect-prepared' and second['deadlineMonotonicNs']==deadline2,prepared=second)
     committed=client.commit_effect(second);check('CommitBeforeCancelIsCommitted',committed['status']=='Committed',receipt=committed)
     def restored():
      f=facts();w=next((w for w in f['facts']['windows'] if w['incarnation']==target),None);return f if w and not w['minimized'] and f['facts']['focused']==target else None
     after_commit=wait(restored);check('CommittedRestoresTargetAndPreservesPeer',all(next(w for w in after_commit['facts']['windows'] if w['incarnation']==peer)[k]==v for k,v in peer_before.items() if k!='stackPosition'),facts=after_commit)
     check('CancelAfterCommitReturnsIdenticalReceipt',client.cancel_effect(second)==committed and client.query_effect_decision(second)==committed)
     after_late_cancel=wait(restored);check('LateCancelCannotRollbackCommittedTargetOrPeer',next(w for w in after_late_cancel['facts']['windows'] if w['incarnation']==target)==next(w for w in after_commit['facts']['windows'] if w['incarnation']==target) and next(w for w in after_late_cancel['facts']['windows'] if w['incarnation']==peer)==next(w for w in after_commit['facts']['windows'] if w['incarnation']==peer),facts=after_late_cancel)
     saved2=retain('committed-terminal',committed);ack2=client.ack_effect_decision(committed);report['commitFirst']={'prepared':second,'decision':committed,'durableCallerCopy':saved2,'ack':ack2,'actualRestoredFacts':after_commit}
    finally:
     try:
      if fixture.poll() is None:
       check('GtkOwnerIdentityBeforeQuit',endpoint.start_time(fixture.pid)==fixture_start);temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'quit'}));temp.replace(control)
       check('GtkOwnerExitedWithinFiveSeconds',bool(select.select([fixture_fd],[],[],5)[0]));fixture.wait(timeout=5)
      check('GtkOwnerNormalExit',fixture.returncode==0,returncode=fixture.returncode)
     finally:os.close(fixture_fd)
   finally:
    if loaded:
     check('NewOwningPluginUnloads',s.ctl('plugin','unload',plugin['path']).strip()=='ok');loaded=False
     check('PluginInventoryEmptyAfterUnload',s.data('plugin','list')==[])
   check('AllGtkClientsRetired',wait(lambda:not s.data('clients')))
   check('CompositorIdentityBeforeNormalExit',endpoint.start_time(s.child.pid)==proc_start)
   s.ctl('dispatch','exit');s.child.wait(timeout=5);check('CompositorNormalExit',s.child.returncode==0,returncode=s.child.returncode)
   report['normalExits']=[{'name':'hyprland','pid':s.child.pid,'returncode':s.child.returncode}]
   for name in ['weston','privateBus']:
    process,row=next((proc,row) for proc,row in s.host.processes if row['name']==name)
    check(name+'IdentityBeforeNormalExit',process.poll() is None and endpoint.start_time(process.pid)==row['start'])
    descriptor=os.pidfd_open(process.pid)
    try:
     signal.pidfd_send_signal(descriptor,signal.SIGTERM);check(name+'ExitedWithinFiveSeconds',bool(select.select([descriptor],[],[],5)[0]));process.wait(timeout=5)
    finally:os.close(descriptor)
    check(name+'NormalExit',process.returncode==0,returncode=process.returncode);report['normalExits'].append({'name':name,'pid':process.pid,'returncode':process.returncode})
  host.verify_tuple();report['passed']=True
 except Exception as e:report['error']=repr(e);report['traceback']=traceback.format_exc()
 report['privateHost']=s.evidence if s else None;report['cleanupPassed']=bool(s and not s.evidence.get('cleanupErrors') and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'));report['passed']=report['passed'] and report['cleanupPassed'];report['runtimeEvidenceDirectory']=str(runtime)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
