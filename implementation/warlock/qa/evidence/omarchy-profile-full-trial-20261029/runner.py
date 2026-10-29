#!/usr/bin/env python3
"""Private UI-020 full-route composition. Protected root launch only."""
import ast,hashlib,importlib.util,os,pathlib,resource,sys
HERE=pathlib.Path(__file__).resolve().parent
BASE=HERE.parent
REPO=pathlib.Path('/home/charles/Warlock')
FRAMEWORK=BASE/'taskbar-new-instance/compiled-runtime.py'
FRAMEWORK_SHA='bb12e30c5e59c653441e18e580f5404f89ddb34a7d6cdb26629c6a0f63af5f4e'
CANDIDATE=BASE/'omarchy-profile-measure-root-v3/fresh_candidate.py'
CANDIDATE_SHA='6b9b460c7255e7b3c57ee79741e0c5943f421c761c854b35106114396190cf75'
MATERIALIZER=BASE/'omarchy-live-materialization-terra3-v1/materialize.py'
MATERIALIZER_SHA='81d18c83b3c1ff9788eee89cbdb2a8cccd260bb126d4d1f4b59154599c1482de'
PREFERENCE=BASE/'omarchy-effective-preference-terra1-v1/effective_preference.py'
PREFERENCE_SHA='837f993d69bb89e368ed2cc8e8bb270d7e7807a68bca8a8a6485998f3f87e54b'
BOUNDARY=BASE/'omarchy-recovery-trial-v1/boundary.py'
BOUNDARY_SHA='55483418f93b85cdb2ab4b63a03adb15d5b9883947152c37a2f95c6b4263cbe8'
DRAFT=HERE/'draft-observer.py'
DRAFT_SHA='4f3a1f2b34d73fb2c99739f0e96a565df4300ccf705b726fb9fd8c865ad6a387'
PRE=HERE/'prelaunch.inc'
PRE_SHA='4b8e8f5568043ff90fbc952b55f049954ae4ea380aa25d0138210e78886a8df9'
JOURNEY=HERE/'journey.inc'
JOURNEY_SHA='0de60634bec2ac294fb6dd549be9be810cbd969810cede8d76dfa67633d8e320'
def checked(path,expected):
 body=path.read_bytes()
 if hashlib.sha256(body).hexdigest()!=expected:raise RuntimeError('Pinned integration input changed: '+str(path))
 return body
def module(path,expected,name):
 raw=checked(path,expected);spec=importlib.util.spec_from_loader(name,loader=None);m=importlib.util.module_from_spec(spec);m.__file__=str(path);exec(compile(raw,str(path),'exec'),m.__dict__);return m
def one(source,old,new):
 if source.count(old)!=1:raise RuntimeError('Expected unique framework boundary: '+old[:100])
 return source.replace(old,new)
def compose():
 source=checked(FRAMEWORK,FRAMEWORK_SHA).decode()
 source=one(source,"if sys.argv[1:] not in ([], ['--new-instance']):raise SystemExit('Only explicit new-instance mode is supported')\nsys.argv[1:]=['--new-instance']", "if sys.argv[1:]!=['--keyboard-shell']:raise SystemExit('offline route only')")
 source=one(source,'ACCESSIBILITY=True','ACCESSIBILITY=False')
 source=one(source,"     def open_apps():\n      chord([125,56],57)","     def open_apps():\n      chord([125,29,56],57)")
 source=one(source,'host.original.qa.require_qa_scope()','host.original.original.qa.require_qa_scope()')
 source=one(source,"adapter=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-qa/fresh_candidate.py')",'adapter=pathlib.Path('+repr(str(CANDIDATE))+')')
 source=one(source,"assert sha(adapter)=='cb29ebe89b051223037264a366b9616815284b88e3cc452bc18a8993680eb8ab'",'assert sha(adapter)=='+repr(CANDIDATE_SHA))
 source=one(source,"spec=importlib.util.spec_from_file_location('fresh_candidate',adapter);host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)","host=load_module(adapter,"+repr(CANDIDATE_SHA)+",'fresh_candidate')")
 start=source.index('import importlib.util as _at_import\n');end=source.index('Collector=host.Collector\n',start)
 source=source[:start]+"from session_bus import isolate_session_host\nfrom system_isolation import supply,validate\n"+source[end:]
 source=one(source,'isolate_session_host(host)\n','isolate_session_host(host.original)\n')
 source=one(source,'with host.PrivateHyprSession(OUTPUT,dict(os.environ),800 if DRAG else 1600,600 if DRAG else 1000,LUA,mesa_vendor=True) as s:', 'with host.PrivateHyprSession(OUTPUT,dict(os.environ),800,600,LUA,mesa_vendor=True) as s:')
 source=one(source,"OUT=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance')/('native-primary-keyboard-'+str(time.time_ns()));OUT.mkdir(parents=True)","OUT=pathlib.Path("+repr(str(HERE))+")/('offline-recovery-'+str(time.time_ns()));OUT.mkdir(mode=0o700)")
 launch_start=source.index("   web=s.host.launch('warlock',")
 launch_end=source.index('   def text():\n',launch_start)
 source=source[:launch_start]+checked(PRE,PRE_SHA).decode()+source[launch_end:]
 start=source.index('     # Establish the original attached, observed surface before user input.\n')
 end=source.index('    elif DENSE:\n',start)
 source=source[:start]+checked(JOURNEY,JOURNEY_SHA).decode()+source[end:]
 source=one(source,"report['nativeFocusJourneyObserved']=FOCUS","report['nativeFocusJourneyObserved']=False")
 source=one(source,"fixture=None;at_registry=None\ntry:","fixture=None;at_registry=None\nreport.update(requirements=['ELM-UI-020'],scenarios=['offline-recovery'],scope='Actual same-session profile recovery with installed Omarchy; independent acceptance remains open',offlineRecoveryObserved=False,nativeAcceptance=False,assistiveTechnologyAccepted=False,fullReleaseAccepted=False)\ntry:")
 source=one(source,"check('OwnedClientNormalExit',proc.returncode==0 or (ACCESSIBILITY and proc is at_registry and proc.returncode==-signal.SIGTERM)","check('OwnedClientNormalExit',proc.returncode==0 or (proc in globals().get('recovery_managers',[]) and proc.returncode==1 and globals().get('recovery_expected_exits',{}).get(proc.pid)==1) or (ACCESSIBILITY and proc is at_registry and proc.returncode==-signal.SIGTERM)")
 source=one(source,"manager=s.host.launch(name,recovery_cmd+['run'],env=live['validated_environment']());apps.append(manager)","manager=s.host.launch(name,recovery_cmd+['run'],env=live['validated_environment']());apps.append(manager);recovery_managers.append(manager)")
 source=one(source,"profile=live['profile'];recovery_cmd=", "recovery_managers=[];recovery_expected_exits={};profile=live['profile'];recovery_cmd=")
 ast.parse(source,filename=str(FRAMEWORK));return source
def main():
 if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise SystemExit('protected root execution only; no arguments')
 sys.path.insert(0,str(REPO/'window-integration-qa'))
 from qa_launch import require_qa_scope
 require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('core limit must remain (1,1)')
 checked(CANDIDATE,CANDIDATE_SHA)
 materializer=module(MATERIALIZER,MATERIALIZER_SHA,'recovery_materializer');boundary=module(BOUNDARY,BOUNDARY_SHA,'omarchy_boundary');draft_module=module(DRAFT,DRAFT_SHA,'draft_observer');preference=module(PREFERENCE,PREFERENCE_SHA,'effective_preference')
 source=compose();sys.argv=[str(FRAMEWORK),'--keyboard-shell']
 namespace={'__name__':'__main__','__file__':str(HERE/'runner.py'),'load_module':module,'materializer':materializer,'boundary':boundary,'draft_module':draft_module,'preference':preference}
 exec(compile(source,str(FRAMEWORK),'exec'),namespace)
if __name__=='__main__':main()
