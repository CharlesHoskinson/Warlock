"""Actual sanitizer/JSC lifetime guards, explicit Quint refinement and held faults."""
import hashlib,json,os,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('persistent-policy-lifetime-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[str(p.relative_to(root)) for p in (root/'src').glob('*') if p.is_file()]+['elm.json','native/elm-preview-policy.h','native/elm-preview-policy.cpp','native/persistent-policy-lifetime-fixture.cpp','qa/persistent-policy-lifetime-check.py','qa/native-source-fixture.json','qa/toolchain.py','qa/toolchain.json','spec/native_policy_lifetime.qnt','spec/native_policy_lifetime_tests.qnt']
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual creator-owned sanitizer JavaScriptCore runs optimized original retained Elm policy. Empty-realm lifetime traces use explicitly synthetic trusted grant/closed inputs and do not establish original Native physical closure or real WebKit/Wayland acceptance. Compiled native control guard variants and pre-grant compiled-worker faults are separately labeled.'}
def run(name,args,cwd=None,env=None,stdin=None,required=True):
 p=subprocess.run(args,cwd=cwd or out/'inputs',env=env,input=stdin,capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
def decoded(v):
 if isinstance(v,list):return [decoded(x) for x in v]
 if isinstance(v,dict):return int(v['#bigint']) if '#bigint' in v else {k:decoded(x) for k,x in v.items()}
 return v
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 sys.path.insert(0,str(root/'qa'));from toolchain import verify
 held=verify();shutil.copytree(root/held['elmHome'],out/'mutable-elm-home')
 worker=out/'policy.js';run('optimized-elm',[str(root/held['compiler']),'make','src/NativePreviewPolicy.elm','--optimize','--output='+str(worker)],env=dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')))
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-2.0','json-glib-1.0','javascriptcoregtk-4.1']).stdout)
 binary=out/'lifetime';compile_args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/persistent-policy-lifetime-fixture.cpp','native/elm-preview-policy.cpp','-o',str(binary),*flags]
 run('compile-owner',compile_args)
 binding=json.loads((root/'qa/native-source-fixture.json').read_text())['clientScope']['binding'];domain={'binding':binding,'receiverEpoch':'1'}
 def invocation(kind,value=None):return {'op':'invoke','input':json.dumps({'kind':kind,'value':value},separators=(',',':'))}
 status=invocation('status');grant=invocation('grant',{**domain,'capacity':1});closed=invocation('closed',domain)
 def execute(name,steps,executable=binary,required=True):
  p=run(name,[str(executable),str(worker)],stdin=''.join(json.dumps(s)+'\n' for s in steps),required=required)
  return p,[json.loads(line) for line in p.stdout.splitlines()]
 invalid=[{'op':'invoke'},*[{'op':'invoke','input':wire} for wire in ['no json','null','[]','{}','{"kind":"status"}','{"kind":null,"value":null}','{"kind":1,"value":null}','{"kind":"status","value":null,"extra":true}','{"kind":"foreign","value":null}']],{'op':'missing-output','input':status['input']},{'op':'invoke','input':' '*(16*1024*1024+1)}]
 steps=[status,grant,status]
 for stimulus in invalid:steps.extend([stimulus,status])
 steps.extend([{'op':'foreign-invoke','input':status['input']},status,{'op':'foreign-close'},status,{'op':'close'},status,invocation('closed',{**domain,'receiverEpoch':'2'}),{'op':'close'},status,closed,status,{'op':'close'}])
 _,rows=execute('boundaries',steps);assert len(rows)==len(steps)
 initial=rows[0]['projection'];opened=rows[2]['projection'];checks=0
 def check(ok,label):
  global checks
  assert ok,label
  checks+=1
 check(not initial['realm']['controlled'],'Initial worker has no native authority')
 check(opened['realm']['controlled'] and not opened['realm']['closed'],'Exact grant enters original controlled realm')
 for i in range(3,3+2*len(invalid),2):
  check(rows[i]=={'ok':False,'code':1,'held':True},'Malformed input refuses before invocation')
  check(rows[i+1]['projection']==opened,'Original immutable policy remains unchanged after refusal')
 offset=3+2*len(invalid)
 for relative,code in [(0,2),(2,2),(4,5),(7,5)]:check(rows[offset+relative]=={'ok':False,'code':code,'held':True},'Creator and trusted-close guards retain owner')
 for relative in [1,3,5,8]:check(rows[offset+relative]['projection']==opened,'Refusal remains usable on original creator')
 check(not rows[offset+6]['projection']['realm']['closed'],'Foreign realm cannot supply close authority')
 check(rows[-2]['projection']['realm']['closed'],'Original trusted close reaches same Elm policy')
 check(rows[-1]=={'ok':True,'code':0,'held':False},'Only original empty closed policy is destroyed normally')
 report['boundaryChecks']=checks;report['originalInvalidInputs']=len(invalid)
 # Faults are injected into held optimized worker code before any native grant.
 # Constructor owns cleanup; no unknown live policy is discarded as closed.
 source=worker.read_text();wrapper=lambda body:source+'\n(function(){var init=Elm.NativePreviewPolicy.init;Elm.NativePreviewPolicy.init=function(){var app=init();'+body+';return app;};})();\n'
 fault_sources=[('empty',b'',1),('nul',b'\0',1),('utf8',b'\xff',1),('missing-elm',b'var unrelated=1;',1),('missing-program',b'var Elm={};',1),('missing-init',b'var Elm={NativePreviewPolicy:{}};',1),('missing-ports',b'var Elm={NativePreviewPolicy:{init:function(){return {};}}};',1),('missing-channels',b'var Elm={NativePreviewPolicy:{init:function(){return {ports:{}};}}};',1),('init-exception',wrapper('throw Error("held fault")').encode(),1),('send-exception',wrapper('app.ports.incoming.send=function(){throw Error("held fault");}').encode(),4),('missing-output',wrapper('app.ports.incoming.send=function(){}').encode(),4),('duplicate-output',wrapper('var send=app.ports.incoming.send;app.ports.incoming.send=function(v){send(v);send(v);}').encode(),4),('malformed-output',wrapper('var subscribe=app.ports.outgoing.subscribe;app.ports.outgoing.subscribe=function(f){subscribe(function(){f({foreign:true});});}').encode(),4)]
 for name,data,code in fault_sources:
  asset=out/('fault-'+name+'.js');asset.write_bytes(data)
  p=run('constructor-'+name,[str(binary),str(asset),'construct']);assert json.loads(p.stdout)=={'ok':False,'code':code,'held':False},name
 report['constructorFaults']=[{'name':n,'code':c,'beforeNativeGrant':True,'normalOwnedExit':True} for n,_,c in fault_sources]
 tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint';folder=out/'inputs/spec'
 selected=re.findall(r'run (\w+)\s*=',(folder/'native_policy_lifetime_tests.qnt').read_text());assert len(selected)==8
 run('typecheck',[tool,'typecheck','native_policy_lifetime_tests.qnt'],folder)
 run('selected',[tool,'test','native_policy_lifetime_tests.qnt','--main=native_policy_lifetime_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1160001','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],folder)
 assert len(list(out.glob('named-*.itf.json')))==8
 run('samples',[tool,'run','native_policy_lifetime.qnt','--main=native_policy_lifetime','--backend=typescript','--invariant=safety','--seed=1160002','--max-samples=200','--max-steps=30','--n-traces=12','--out-itf='+str(out/'sample-{seq}.itf.json')],folder)
 def stimulus(event):
  return {'Status':status,'Malformed':{'op':'invoke','input':'invalid'},'WrongThreadInvoke':{'op':'foreign-invoke','input':status['input']},'WrongThreadClose':{'op':'foreign-close'},'Grant':grant,'ForeignClose':invocation('closed',{**domain,'receiverEpoch':'2'}),'TrustedClose':closed,'Destroy':{'op':'close'}}[event]
 compared=0;traces=[]
 def trace_check(path,executable=binary,required=True):
  states=[v['s'] for v in decoded(json.loads(path.read_text()))['states']];history=states[-1]['history'];steps=[status,*[stimulus(e) for e in history]]
  if states[-1]['held']:steps.extend([closed,{'op':'close'}])
  p,rows=execute('refine-'+executable.name+'-'+path.stem,steps,executable,required)
  assert len(rows)==len(steps),(path.name,len(rows),len(steps))
  for state in states:
   index=len(state['history']);row=rows[index];assert row['code']==state['code'] and row['held']==state['held'],(path.name,index,state,row)
   if 'projection' in row:assert row['projection']['realm']['controlled']==state['controlled'] and row['projection']['realm']['closed']==state['closed'] and row['projection']['models']==[],(path.name,index,state,row)
  return len(states)
 for path in sorted(out.glob('*.itf.json')):
  count=trace_check(path);compared+=count;traces.append({'trace':path.name,'statesCompared':count,'normalOwnedExit':True})
 report.update(namedScenarios=8,selectedNames=selected,invariantSamples=200,statesCompared=compared,coupledTraces=traces)
 mutants=[];original=(out/'inputs/native/elm-preview-policy.cpp').read_text()
 close_guard='if (self->creator != g_thread_self()) return fail(error, WARLOCK_POLICY_WRONG_THREAD, "Original policy creator thread required");'
 for name,old,new,witness in [('early-destroy',' || (self->controlled && !self->closed)','', 'openRealmCannotDestroy'),('foreign-destroy',close_guard,'/* deliberately missing creator-close guard */','wrongThreadCannotDestroy'),('foreign-kind','&& name != "status")','&& name != "status" && name != "foreign")',None)]:
  target=out/name;shutil.copytree(out/'inputs/native',target/'native');body=original
  if name=='foreign-destroy':assert body.count(old)==2;where=body.index('gboolean warlock_preview_policy_close(');body=body[:where]+body[where:].replace(old,new,1)
  else:assert body.count(old)==1;body=body.replace(old,new)
  (target/'native/elm-preview-policy.cpp').write_text(body);changed=target/'lifetime';args=compile_args.copy();args[args.index('-o')+1]=str(changed);run(name+'-compile',args,target)
  if witness:
   trace=next(out.glob('named-'+witness+'-*.itf.json'))
   try:trace_check(trace,changed,required=False)
   except AssertionError as mismatch:mutants.append({'name':name,'compiled':True,'witness':witness,'originalObservableMismatch':str(mismatch)[:1800]})
   else:raise AssertionError('Original witness did not detect '+name)
  else:
   p,changed_rows=execute(name+'-witness',[invocation('foreign'),{'op':'close'}],changed)
   assert changed_rows[0]['code']!=1 and changed_rows[-1]['held']==False
   mutants.append({'name':name,'compiled':True,'witness':'Original invalid closed input union','originalObservableMismatch':True})
 report['unsafeCompiledNativeVariantsDetected']=len(mutants);report['mutants']=mutants
 verify();assert all(sha(root/n)==v for n,v in report['inputs'].items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and 'mutable-elm-home' not in p.parts and 'elm-stuff' not in p.parts}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2200]}),flush=True);sys.exit(not report['passed'])
