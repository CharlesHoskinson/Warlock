#!/usr/bin/env python3
"""Private reviewed-composition pin independence fixture; root owns execution."""
import ast,hashlib,importlib.util,os,pathlib,resource,sys
HERE=pathlib.Path(__file__).resolve().parent; B=HERE.parent
V5=B/'current-native-runtime-attention-root-v5/runner.py'; V5SHA='1d91bad01cbdb25fc2ace6896f5a60586d976e68befedca96cae7f004b92bb57'
OLD=B/'taskbar-pin-semantics/retained-peer-v2/runner.py'; OLDSHA='bc15f7eabc40e1c41680ea7c969254d8a2779fe46f621056a68e952cca839159'
OLDBRANCH=B/'taskbar-pin-semantics/retained-peer-v2/branch.txt'; OLDBRANCHSHA='dde72e32e7552dc6382a36a8ff757a408262af093754f8d4c84ed286de3a96e8'
BRANCH=HERE/'branch.txt'; BRANCHSHA='05d72e6b6561c6a04c6c18b83d6815fda3a5f6f4f8020b7f8650e36703f552cf'
POPUP_JOIN_SHA='5a73d1639c0c2350bad922c5017e902e5aa20e9075c6c91cb3af9d1bd6019aa3'
ACTION=B/'taskbar-pin-semantics/at-action.py'; ACTIONSHA='e4ce2c23b852a1bea40c27d0c47f68e810705531a8e41f8ae8ae046ce76cb157'
def checked(path,expected):
 raw=path.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=expected:raise RuntimeError('Pinned source changed: '+str(path))
 return raw
def load(path,expected,name):
 raw=checked(path,expected);spec=importlib.util.spec_from_loader(name,loader=None);m=importlib.util.module_from_spec(spec);m.__file__=str(path);exec(compile(raw,str(path),'exec'),m.__dict__);return m
def one(source,old,new):
 if source.count(old)!=1:raise RuntimeError('Unique anchor mismatch: '+old[:80])
 return source.replace(old,new)
def compose():
 attention=load(V5,V5SHA,'reviewed_attention');checked(OLD,OLDSHA);checked(OLDBRANCH,OLDBRANCHSHA);checked(ACTION,ACTIONSHA)
 source=attention.compose()
 source=one(source,"adapter=pathlib.Path("+repr(str(V5.parent/'fresh_candidate.py'))+")","adapter=pathlib.Path("+repr(str(B/'pin-top-runtime-root-v1/fresh_candidate.py'))+")")
 source=one(source,"assert sha(adapter)=='bcc52089ee868c08aa8e5fff367828f81fb5bdf66683e858299c238d6672958a'","assert sha(adapter)=='6e1f46eae9fb5fe9e08ff0db1f8746fdbba34adf4af2afa2253d9b4a2be0dfa7'")
 source=one(source,"host=load_module(adapter,'bcc52089ee868c08aa8e5fff367828f81fb5bdf66683e858299c238d6672958a','fresh_candidate')","host=load_module(adapter,'6e1f46eae9fb5fe9e08ff0db1f8746fdbba34adf4af2afa2253d9b4a2be0dfa7','fresh_candidate')")
 source=one(source,"if sys.argv[1:]!=['--attention']:raise SystemExit('attention mode only')", "if sys.argv[1:]!=['--new-instance']:raise SystemExit('pin independence mode only')")
 source=one(source,"OUT=pathlib.Path("+repr(str(V5.parent))+")/('native-attention-'+str(time.time_ns()));OUT.mkdir(mode=0o700)","OUT=pathlib.Path("+repr(str(HERE))+")/('native-pin-independence-'+str(time.time_ns()));OUT.mkdir(mode=0o700)")
 begin='    elif PINMENUS:\n';end='    elif CHORD:\n'
 if source.count(begin)!=1 or source.count(end)!=1 or source.index(begin)>=source.index(end):raise RuntimeError('branch anchor mismatch')
 source=source[:source.index(begin)]+checked(BRANCH,BRANCHSHA).decode()+source[source.index(end):]
 start=source.index('\n   if PINMENUS:\n')+1;stop=source.index('\n   if REFLOW:\n',start)+1;lines=source[start:stop].splitlines(keepends=True)
 if len(lines)<3 or not lines[2].startswith('    if NEWINSTANCE:'):raise RuntimeError('fixture setup anchor mismatch')
 source=source[:start]+''.join(lines[:2])+source[stop:]
 old="if NEWINSTANCE:report.update(requirements=['ELM-UI-004'],scenarios=['taskbar-inactive'],scope='Explicit New instance and ordinary running pin with real private GTK roots, native GIO receipts; no dense UI-008 or independent acceptance claimed',inputMode='at-action' if new_instance_at else 'pointer-and-keyboard')"
 new="if NEWINSTANCE:report.update(requirements=['ELM-UI-004'],scenarios=[],scope='Application pin and native always-on-top independence; physical secondary opener, pointer keyboard and real AT actions; independent acceptance separate',inputMode='secondary-pointer-plus-pointer-keyboard-real-at',nativePinIndependenceObserved=False)"
 source=one(source,old,new);ast.parse(source);return source
def main():
 if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise RuntimeError('protected no-bytecode pin mode only')
 repo=pathlib.Path('/home/charles/Warlock');sys.path.insert(0,str(repo/'window-integration-qa'))
 from qa_launch import require_qa_scope
 require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('core limit differs')
 attention=load(V5,V5SHA,'reviewed_attention_main')
 guard=attention.module(attention.GUARD,attention.GUARD_SHA,'at_guard')
 if guard.PACKET_SHA256!='78016e94c06d11f71c5ba18694fadd876cd17d0d8643b361009733ba4ab57726':raise RuntimeError('AT guard packet differs')
 for path,digest in {repo/'implementation/warlock/qa/accessibility-session.py':'69bc3b33c2b99f0b9d54805e18afcb85ff02314dc9aa4d002f4df409a0e57524',repo/'implementation/warlock/qa/accessibility-inspector.py':'bc4fe7adba15c29f97137b91848971b65b994c1b8f6282109d7edf1e13bd5c27',pathlib.Path('/home/charles/.local/share/mise/installs/node/26.12.0/bin/node'):'caa24debe02770c92a70677e2a62ca98890150e7ac1c17bcfe31bcc98cc89943',pathlib.Path('/usr/bin/python3'):'375532f83be620283ab780c14ca6bcc5907dc379d2b621de0c5d0a112cf5458b'}.items():checked(path,digest)
 guard.validate()
 collector=load(B/'taskbar-qa/measured_inspection.py','559775d3a39c14b1cea2b5747773665a4817c5b9850d08afc4782d2919a11f9e','pin_collector')
 joiner=load(HERE/'popup_join.py',POPUP_JOIN_SHA,'pin_popup_join')
 def pin_popup_join(text,body,projection,target):return joiner.join(text,body,projection,target,native_bar_epochs=collector.native_bar_epochs)
 source=compose();(HERE/'executed-framework.py').write_text(source)
 sys.argv=[str(attention.FRAMEWORK),'--new-instance']
 exec(compile(source,str(HERE/'executed-framework.py'),'exec'),{'__name__':'__main__','__file__':str(HERE/'runner.py'),'load_module':attention.module,'at_guard':guard,'new_instance_at':False,'PIN_AT_HELPER':ACTION,'pin_popup_join':pin_popup_join})
if __name__=='__main__':main()
