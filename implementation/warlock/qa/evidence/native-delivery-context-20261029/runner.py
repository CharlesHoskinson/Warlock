#!/usr/bin/env python3
"""Current direct-host first-use persistence and actual AT; root review required."""
import ast,hashlib,importlib.util,os,pathlib,resource,sys
HERE=pathlib.Path(__file__).resolve().parent
BASE=HERE.parent
REPO=pathlib.Path('/home/charles/Warlock')
FRAMEWORK=BASE/'taskbar-new-instance/compiled-runtime.py'
FRAMEWORK_SHA='bb12e30c5e59c653441e18e580f5404f89ddb34a7d6cdb26629c6a0f63af5f4e'
CANDIDATE=HERE/'fresh_candidate.py'
CANDIDATE_SHA='a4f481d6b1452ce50ed3623008766fe13fd13b961adbb87d07296a6e58272350'
AT_GUARD=BASE/'at-prefix-host/guard-v3.py'
AT_GUARD_SHA='117e56afe2a72e686fa2fcaedd18204da593af51e8be495764cd7e75d500d148'
AT_ACTION=BASE/'taskbar-pin-semantics/at-action.py'
AT_ACTION_SHA='e4ce2c23b852a1bea40c27d0c47f68e810705531a8e41f8ae8ae046ce76cb157'
BRANCH=BASE/'first-use-direct-terra2-v2/branch.inc'
BRANCH_SHA='c0f51f5ba7de7641230b13cd370af93842d58e584195ef84ab54f48e0cb7fd7b'
def checked(path,expected):
 body=path.read_bytes()
 if hashlib.sha256(body).hexdigest()!=expected:raise RuntimeError('Pinned input changed: '+str(path))
 return body
def one(source,old,new):
 if source.count(old)!=1:raise RuntimeError('Unique framework boundary unavailable: '+old[:80])
 return source.replace(old,new)
def module(path,sha,name):
 raw=checked(path,sha);spec=importlib.util.spec_from_loader(name,loader=None);m=importlib.util.module_from_spec(spec);m.__file__=str(path);exec(compile(raw,str(path),'exec'),m.__dict__);return m
def compose():
 source=checked(FRAMEWORK,FRAMEWORK_SHA).decode()
 source=one(source,"if sys.argv[1:] not in ([], ['--new-instance']):raise SystemExit('Only explicit new-instance mode is supported')\nsys.argv[1:]=['--new-instance']","if sys.argv[1:]!=['--keyboard-shell']:raise SystemExit('first-use direct route only')")
 source=one(source,"adapter=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-qa/fresh_candidate.py')",'adapter=pathlib.Path('+repr(str(CANDIDATE))+')')
 source=one(source,"assert sha(adapter)=='cb29ebe89b051223037264a366b9616815284b88e3cc452bc18a8993680eb8ab'",'assert sha(adapter)=='+repr(CANDIDATE_SHA))
 source=one(source,"spec=importlib.util.spec_from_file_location('fresh_candidate',adapter);host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)","host=load_module(adapter,"+repr(CANDIDATE_SHA)+",'fresh_candidate')")
 source=one(source,'host.original.qa.require_qa_scope();','host.original.original.qa.require_qa_scope();')
 source=one(source,'isolate_session_host(host)\n','isolate_session_host(host.original)\n')
 source=one(source,"OUT=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance')/('native-primary-keyboard-'+str(time.time_ns()));OUT.mkdir(parents=True)","OUT=pathlib.Path("+repr(str(HERE))+")/('first-use-direct-'+str(time.time_ns()));OUT.mkdir(mode=0o700)")
 source=one(source,"      chord([125,56],57)\n      return wait(lambda:(body:=body_for('applications'))", "      key(88)\n      return wait(lambda:(body:=body_for('applications'))")
 anchor="if KEYBOARD or PRIMARYKEY or DRAG or NEWINSTANCE:LUA+=(ROOT/'native/shell-bindings.lua').read_bytes()"
 fixture='''\nif KEYBOARD:
 LUA+=b'\\nhl.bind("SUPER + ALT + SPACE", hl.dsp.focus({window="title:ELM-ACTIVATION-PEER"}), {description="Existing Apps shortcut"})\\nhl.bind("F12", function() hl.plugin.warlock.apps_menu() end, {description="User Apps shortcut"})\\n'
'''
 source=one(source,anchor,anchor+fixture)
 start=source.index('     # Establish the original attached, observed surface before user input.\n');end=source.index('    elif DENSE:\n',start)
 source=source[:start]+checked(BRANCH,BRANCH_SHA).decode()+source[end:]
 source=one(source,"fixture=None;at_registry=None\ntry:","fixture=None;at_registry=None\nreport.update(requirements=['ELM-UI-020'],scenarios=['first-use'],scope='Direct current host and authority restart; physical explicit shortcut choice, actual assistive observations and recipient. Independent original acceptance, offline recovery and release remain separate.',nativeFirstUseDirectObserved=False,nativeAcceptance=False,assistiveTechnologyAccepted=False,fullReleaseAccepted=False)\ntry:")
 source=one(source,"report['nativeFocusJourneyObserved']=FOCUS","report['nativeFocusJourneyObserved']=False")
 ast.parse(source,filename=str(FRAMEWORK));return source
def main():
 if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise SystemExit('protected no-bytecode root launch only')
 sys.path.insert(0,str(REPO/'window-integration-qa'))
 from qa_launch import require_qa_scope
 require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('core limit must remain (1,1)')
 checked(CANDIDATE,CANDIDATE_SHA);checked(AT_ACTION,AT_ACTION_SHA)
 for p,h in {REPO/'implementation/warlock/qa/native-shortcut-preferences.py':'8ba22b198fd22d729fdd3cde471104eb1dc7c86e6fe3a6c52b996075f2835afa',REPO/'implementation/warlock/qa/native-shortcut-generation.py':'1a1baa1c395df47b6d11cea2a260bb0a416b8ed2ec6b8979dd5afae30e5d4789',REPO/'implementation/warlock/qa/evidence/shortcut-reload-dismissal/manifest.json':'8f7a1dc5599e544dcd7f7657a506c5969ca02134fd0ab4041c1dc167610106da',REPO/'implementation/warlock/qa/evidence/shortcut-reload-dismissal/current-native-report.json':'fd6196e2215e0be32479f0cd1ceec73a16ef3475ddb6b4d04a3251e8b55fecb3',REPO/'implementation/warlock/qa/accessibility-session.py':'69bc3b33c2b99f0b9d54805e18afcb85ff02314dc9aa4d002f4df409a0e57524',REPO/'implementation/warlock/qa/accessibility-inspector.py':'bc4fe7adba15c29f97137b91848971b65b994c1b8f6282109d7edf1e13bd5c27',BASE/'taskbar-primary-at/accessibility-reader.py':'9ce02ecb92a182cc5a21dbfea0680970a45b122402e35e387f40acc2a7b4699e'}.items():checked(p,h)
 guard=module(AT_GUARD,AT_GUARD_SHA,'at_guard')
 if guard.PACKET_SHA256!='78016e94c06d11f71c5ba18694fadd876cd17d0d8643b361009733ba4ab57726':raise RuntimeError('Unexpected AT provider packet')
 guard.validate();source=compose();sys.argv=[str(FRAMEWORK),'--keyboard-shell']
 exec(compile(source,str(FRAMEWORK),'exec'),{'__name__':'__main__','__file__':str(HERE/'runner.py'),'load_module':module,'at_guard':guard,'AT_ACTION':AT_ACTION})
if __name__=='__main__':main()
