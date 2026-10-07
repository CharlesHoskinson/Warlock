"""Explicit Quint/native refinement, compiled guards and seeded counter boundaries."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('visual-channel-refinement-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=root/'qa/visual-channel-check-1791371205851102125';prior=json.loads((base/'report.json').read_text());assert prior['passed'] and prior['evidence']['checks']==67
names=list(prior['inputs'])+['spec/visual_channel.qnt','spec/visual_channel_tests.qnt','qa/visual-channel-refinement.py']
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'priorReport':{'path':str(base/'report.json'),'sha256':sha(base/'report.json')},'scope':'Explicit symbolic native visual custody scenarios coupled to actual sanitizer C/JSC observable refusal codes, native lease/floor/sequence and normal ownership teardown. The model abstracts native context identity and committed visual version; it does not qualify actual WebKit callbacks, receiver DOM, ongoing freshness or physical concealment. Guard mutants and seeded counter boundary builds are labeled derivatives. Native grant/closed authority in empty-realm fixture is explicitly synthetic. Original policy/native effect ordinals and physical authority remain unchanged.'}
def run(name,args,cwd=None,stdin=None,required=True):
 p=subprocess.run(args,cwd=cwd or out/'inputs',input=stdin,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
def decoded(v):
 if isinstance(v,list):return [decoded(x) for x in v]
 if isinstance(v,dict):return int(v['#bigint']) if '#bigint' in v else {k:decoded(x) for k,x in v.items()}
 return v
try:
 for rel,value in prior['inputs'].items():assert sha(root/rel)==value,rel
 for rel,value in prior['artifacts'].items():assert sha(base/rel)==value,rel
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 binary=base/'channel';worker=base/'policy.js';fixture=json.loads((root/'qa/native-source-fixture.json').read_text());domain={'binding':fixture['clientScope']['binding'],'receiverEpoch':'1'}
 def invocation(kind,value=None):return {'op':'invoke','input':json.dumps({'kind':kind,'value':value},separators=(',',':'))}
 grant=invocation('grant',{**domain,'capacity':1});closed=invocation('closed',domain)
 def command(action,context=0,input=None,foreign=False):return {'op':'foreign-channel' if foreign else 'channel','action':action,'context':context,**({'input':input} if input is not None else {})}
 def receipt(packet):return json.dumps({k:('native-preview-projection-accepted' if k=='kind' else v) for k,v in packet.items() if k!='visual'},separators=(',',':'))
 def execute(name,steps,executable=binary,required=True):
  p=run(name,[str(executable),str(worker)],stdin=''.join(json.dumps(s)+'\n' for s in steps),required=required)
  return [json.loads(line) for line in p.stdout.splitlines()]
 tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint';folder=out/'inputs/spec'
 selected=re.findall(r'run (\w+)\s*=',(folder/'visual_channel_tests.qnt').read_text());assert len(selected)==14
 run('typecheck',[tool,'typecheck','visual_channel_tests.qnt'],folder)
 run('selected',[tool,'test','visual_channel_tests.qnt','--main=visual_channel_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1190001','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],folder)
 assert len(list(out.glob('named-*.itf.json')))==14
 run('samples',[tool,'run','visual_channel.qnt','--main=visual_channel','--backend=typescript','--invariant=safety','--seed=1190002','--max-samples=200','--max-steps=30','--n-traces=12','--out-itf='+str(out/'sample-{seq}.itf.json')],folder)
 def trace_check(path,executable=binary):
  states=[v['s'] for v in decoded(json.loads(path.read_text()))['states']];history=states[-1]['history'];steps=[grant,{'op':'contexts'}];last_packet=None
  # Receipt bytes and snapshot counters are known from the native-issued sequence
  # and exact committed visual version, not from renderer-created control ordinals.
  for index,event in enumerate(history,1):
   state=next(s for s in states if len(s['history'])==index)
   if event=='Change':
    surface={'surfaceProtocol':2,'publication':str(state['version']),'lease':'1','mode':'picker','status':'version'+str(state['version']),'bar':[],'popup':[]};steps.append(invocation('presentation',surface))
   elif event=='ForeignContext':steps.append(command('invalidate',1))
   elif event=='ForeignThread':steps.append(command('close',foreign=True))
   else:
    action={'Attach':'attach','Offer':'offer','Retry':'retry','Ack':'ack','Current':'current','Invalidate':'invalidate','Detach':'detach','Destroy':'close'}[event]
    if event=='Ack':
     expected={'channelProtocol':1,'kind':'native-preview-projection-accepted',**domain,'rendererLease':str(last_packet['lease']),'visualSequence':str(last_packet['sequence'])} if last_packet else {}
     steps.append(command(action,input=json.dumps(expected,separators=(',',':'))))
    else:steps.append(command(action))
    if event=='Offer' and state['code']==0:last_packet=state
  final=states[-1]
  if final['held']:
   if final['attached']:steps.append(command('detach'))
   steps.append(command('close'))
  steps.extend([closed,{'op':'close'}]);rows=execute('refine-'+executable.parent.name+'-'+path.stem,steps,executable);assert len(rows)==len(steps)
  for state in states:
   index=len(state['history']);row=rows[index+1];assert row['code']==state['code'],(path.name,index,state,row)
   if state['history'] and row['ok']:
    event=state['history'][-1]
    if event=='Attach':assert row['projection']['rendererLease']==str(state['lease']) and row['projection']['sequenceFloor']==str(state['sequence']),(path.name,index,state,row)
    if event in {'Offer','Retry'}:assert row['projection']['rendererLease']==str(state['lease']) and row['projection']['visualSequence']==str(state['sequence']),(path.name,index,state,row)
  assert rows[-1]=={'ok':True,'code':0,'held':False};return len(states)
 traces=[]
 for path in sorted(out.glob('*.itf.json')):traces.append({'trace':path.name,'observableStatesCompared':trace_check(path),'normalOwnedExit':True})
 report.update(namedScenarios=14,selectedNames=selected,invariantSamples=200,coupledTraces=traces,observableStatesCompared=sum(t['observableStatesCompared'] for t in traces))
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-2.0','json-glib-1.0','javascriptcoregtk-4.1']).stdout)
 original=(root/'native/preview-visual-channel.cpp').read_text()
 def compiled(name,source):
  target=out/name;shutil.copytree(out/'inputs/native',target/'native');(target/'native/preview-visual-channel.cpp').write_text(source);binary=target/'channel'
  run(name+'-compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/visual-channel-fixture.cpp','native/elm-preview-policy.cpp','native/preview-visual-channel.cpp','-o',str(binary),*flags],target);return binary
 variants=[('foreign-thread','self->creator!=g_thread_self()','false','foreignThreadCannotDestroy'),('foreign-context','!target || self->context!=target','!target','foreignContextCannotInvalidate'),('stale-cache','bytes!=self.visual || domain!=self.domain','false','changedPolicyRefusesReceipt'),('early-destroy','self->context || !self->packet.empty()','false','attachedContextPreventsDestroy')]
 mutants=[]
 for name,old,new,witness in variants:
  assert original.count(old)==1;variant=compiled(name,original.replace(old,new));path=next(out.glob('named-'+witness+'-*.itf.json'))
  try:trace_check(path,variant)
  except AssertionError as mismatch:mutants.append({'name':name,'compiled':True,'witness':witness,'observableMismatch':str(mismatch)[:1800]})
  else:raise AssertionError('Undetected compiled guard '+name)
 report['compiledNativeVariantsDetected']=len(mutants);report['mutants']=mutants
 counters=[]
 for name,seed in [('sequence-exhaustion','guint64 lease{}, sequence{G_MAXUINT64-1};'),('lease-exhaustion','guint64 lease{G_MAXUINT64-1}, sequence{};')]:
  old='guint64 lease{}, sequence{};';assert original.count(old)==1;variant=compiled(name,original.replace(old,seed))
  if name=='sequence-exhaustion':
   steps=[grant,command('attach'),command('offer'),command('retry'),command('offer'),command('current'),command('detach'),command('attach',1),command('offer',1),command('detach',1),command('close',1),closed,{'op':'close'}]
   rows=execute(name+'-boundaries',steps,variant);assert rows[2]['projection']['visualSequence']=='18446744073709551615';assert rows[3]['projection']==rows[2]['projection'];assert rows[4]['code']==5 and rows[5]['code']==4;assert rows[7]['projection']['rendererLease']=='2' and rows[7]['projection']['sequenceFloor']=='18446744073709551615';assert rows[8]['code']==5
  else:
   steps=[grant,command('attach'),command('offer'),command('detach'),command('attach',1),command('close'),closed,{'op':'close'}]
   rows=execute(name+'-boundaries',steps,variant);assert rows[1]['projection']['rendererLease']=='18446744073709551615' and rows[2]['projection']['visualSequence']=='1';assert rows[4]['code']==5
  assert rows[-1]=={'ok':True,'code':0,'held':False};counters.append({'name':name,'compiledSeededBoundary':True,'originalGuardPreserved':True,'normalOwnedExit':True})
 report['counterBoundaries']=counters;assert all(sha(root/n)==v for n,v in report['inputs'].items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and 'mutable-elm-home' not in p.parts and 'elm-stuff' not in p.parts}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2200]}),flush=True);sys.exit(not report['passed'])
