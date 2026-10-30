#!/usr/bin/env python3
"""Private UX-009 attention with actual AT snapshots; root review required."""
import ast,hashlib,importlib.util,os,pathlib,resource,sys
HERE=pathlib.Path(__file__).resolve().parent;BASE=HERE.parent;REPO=pathlib.Path('/home/charles/Warlock')
FRAMEWORK=BASE/'taskbar-new-instance/compiled-runtime.py';FRAMEWORK_SHA='bb12e30c5e59c653441e18e580f5404f89ddb34a7d6cdb26629c6a0f63af5f4e'
CANDIDATE=HERE/'fresh_candidate.py';CANDIDATE_SHA='bcc52089ee868c08aa8e5fff367828f81fb5bdf66683e858299c238d6672958a'
GUARD=BASE/'at-prefix-host/guard-v3.py';GUARD_SHA='117e56afe2a72e686fa2fcaedd18204da593af51e8be495764cd7e75d500d148'
BRANCH=HERE/'at-attention.inc';BRANCH_SHA='49eaacdb219fa55cb65a14294ce1b94b7b3f83ba62896e362b2ae9455250595c'
def checked(path,expected):
 body=path.read_bytes()
 if hashlib.sha256(body).hexdigest()!=expected:raise RuntimeError('Pinned input changed '+str(path))
 return body
def one(source,old,new):
 if source.count(old)!=1:raise RuntimeError('Expected unique anchor '+old[:80])
 return source.replace(old,new)
def module(path,sha,name):
 raw=checked(path,sha);spec=importlib.util.spec_from_loader(name,loader=None);m=importlib.util.module_from_spec(spec);m.__file__=str(path);exec(compile(raw,str(path),'exec'),m.__dict__);return m
def compose():
 source=checked(FRAMEWORK,FRAMEWORK_SHA).decode()
 source=one(source,"if sys.argv[1:] not in ([], ['--new-instance']):raise SystemExit('Only explicit new-instance mode is supported')\nsys.argv[1:]=['--new-instance']","if sys.argv[1:]!=['--attention']:raise SystemExit('attention mode only')")
 source=one(source,"adapter=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-qa/fresh_candidate.py')",'adapter=pathlib.Path('+repr(str(CANDIDATE))+')')
 source=one(source,"assert sha(adapter)=='cb29ebe89b051223037264a366b9616815284b88e3cc452bc18a8993680eb8ab'",'assert sha(adapter)=='+repr(CANDIDATE_SHA))
 source=one(source,"spec=importlib.util.spec_from_file_location('fresh_candidate',adapter);host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)","host=load_module(adapter,"+repr(CANDIDATE_SHA)+",'fresh_candidate')")
 source=one(source,'host.original.qa.require_qa_scope();','host.original.original.qa.require_qa_scope();')
 source=one(source,'isolate_session_host(host)\n','isolate_session_host(host.original)\n')
 source=one(source,"subprocess.run(['node','--check',str(assets/'bar-adapter.js')],check=True)","subprocess.run(['/home/charles/.local/share/mise/installs/node/26.12.0/bin/node','--check',str(assets/'bar-adapter.js')],check=True)")

 source=one(source,"OUT=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance')/('native-primary-keyboard-'+str(time.time_ns()));OUT.mkdir(parents=True)","OUT=pathlib.Path("+repr(str(HERE))+")/('native-attention-'+str(time.time_ns()));OUT.mkdir(mode=0o700)")
 source=one(source,"    before_native=attention_facts();before_window=len(journal());",checked(BRANCH,BRANCH_SHA).decode()+"    before_native=attention_facts();before_window=len(journal());")
 anchor="    check('NativeAttentionRequestDoesNotStealFocusOrSubmitWindowEffect',observed['facts']['focused']==origin and len(journal())==before_window)"
 source=one(source,anchor,anchor+"\n    capture_attention_at('Attention','ELM-ACTIVATION-PEER','Attention; Open',target)\n    capture_attention_at('OtherActive','ELM-AUTHORITY-FIXTURE','Active',origin)")
 anchor="    final=attention_facts();check('ActivatingAttentionTargetShowsObservedActiveAndClearsUrgency',not next(w for w in final['facts']['windows'] if w['incarnation']==target)['attention'] and len(journal())==before_window+1,facts=final,requests=journal()[before_window:])"
 source=one(source,anchor,anchor+"\n    capture_attention_at('Activated','ELM-ACTIVATION-PEER','Active',target)\n    activated_image=OUTPUT/'taskbar-native-activated.png';helper(['/usr/bin/grim',str(activated_image)]);report['nativeActivatedImage']={'path':str(activated_image),'sha256':sha(activated_image)}")
 source=one(source,"if ACCESSIBILITY:report.update(requirements=['ELM-UX-025'],scenarios=['actual-surface-at'],scope='Actual private GTK/WebKit taskbar and switcher AT-SPI tree/states/focus and real Orca observations with physical input; independent original acceptance remains separate.')","if ACCESSIBILITY:report.update(requirements=['ELM-UX-025'],scenarios=['actual-surface-at'],scope='Actual private GTK/WebKit taskbar and switcher AT-SPI tree/states/focus and real Orca observations with physical input; independent original acceptance remains separate.')\nif ATTENTION:report.update(requirements=['ELM-UX-009'],scenarios=['ux-009'],scope='Original inactive GTK window attention: actual native amber versus active blue pixels, exported private AT taskbar button identity/name/toggle state, focus retention and physical activation/recipient; independent original acceptance and broader AT/release remain separate.')")
 source=one(source,"report['nativeFeedbackObserved']=not FOCUS and not CATALOG", "report['postComposition']=host.verify_tuple()['sourceQualification'];report['nativeFeedbackObserved']=not FOCUS and not CATALOG")

 ast.parse(source);return source
def main():
 if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise SystemExit('protected no-bytecode only')
 sys.path.insert(0,str(REPO/'window-integration-qa'));from qa_launch import require_qa_scope
 require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('core limit differs')
 checked(CANDIDATE,CANDIDATE_SHA);guard=module(GUARD,GUARD_SHA,'at_guard')
 for path,digest in {REPO/'implementation/warlock/qa/accessibility-session.py':'69bc3b33c2b99f0b9d54805e18afcb85ff02314dc9aa4d002f4df409a0e57524',REPO/'implementation/warlock/qa/accessibility-inspector.py':'bc4fe7adba15c29f97137b91848971b65b994c1b8f6282109d7edf1e13bd5c27',pathlib.Path('/home/charles/.local/share/mise/installs/node/26.12.0/bin/node'):'caa24debe02770c92a70677e2a62ca98890150e7ac1c17bcfe31bcc98cc89943',pathlib.Path('/usr/bin/python3'):'375532f83be620283ab780c14ca6bcc5907dc379d2b621de0c5d0a112cf5458b'}.items():checked(path,digest)
 if guard.PACKET_SHA256!='78016e94c06d11f71c5ba18694fadd876cd17d0d8643b361009733ba4ab57726':raise RuntimeError('AT provider packet differs')
 guard.validate();source=compose();sys.argv=[str(FRAMEWORK),'--attention']
 exec(compile(source,str(FRAMEWORK),'exec'),{'__name__':'__main__','__file__':str(HERE/'runner.py'),'load_module':module,'at_guard':guard})
if __name__=='__main__':main()
