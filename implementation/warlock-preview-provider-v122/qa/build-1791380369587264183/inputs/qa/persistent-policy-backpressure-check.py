"""Actual C/JSC WOULD_BLOCK refuses before invocation and retains exact Elm intent."""
import hashlib,json,os,pathlib,resource,selectors,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('persistent-policy-backpressure-check-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[str(p.relative_to(root)) for p in (root/'src').glob('*') if p.is_file()]+['elm.json','native/elm-preview-policy.h','native/elm-preview-policy.cpp','native/persistent-policy-lifetime-fixture.cpp','qa/persistent-policy-backpressure-check.py','qa/native-source-fixture.json','qa/toolchain.py','qa/toolchain.json']
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual sanitizer C/JSC optimized single retained Elm worker at capacity one. Native ticket and terminal/close facts are explicitly synthetic inputs, never original Native issuance/physical-close proof. Same original retained intents and Unknown obligations remain; refusal before processing is distinct from unknown execution.'}
child=None;steps=[];checks=0
def run(name,args,env=None):
 p=subprocess.run(args,cwd=out/'inputs',env=env,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p.stdout
def check(ok,label):
 global checks
 assert ok,label
 checks+=1
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 sys.path.insert(0,str(root/'qa'));from toolchain import verify
 held=verify();shutil.copytree(root/held['elmHome'],out/'mutable-elm-home');worker=out/'policy.js'
 run('optimized-elm',[str(root/held['compiler']),'make','src/NativePreviewPolicy.elm','--optimize','--output='+str(worker)],dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')))
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-2.0','json-glib-1.0','javascriptcoregtk-4.1']));binary=out/'backpressure'
 run('compile-owner',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/persistent-policy-lifetime-fixture.cpp','native/elm-preview-policy.cpp','-o',str(binary),*flags])
 child=subprocess.Popen([str(binary),str(worker)],cwd=out/'inputs',stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 selector=selectors.DefaultSelector();selector.register(child.stdout,selectors.EVENT_READ)
 def call(step):
  child.stdin.write(json.dumps(step)+'\n');child.stdin.flush();assert selector.select(3),'Original three-second policy output timeout';line=child.stdout.readline();assert line,'Missing owned C projection';row=json.loads(line);steps.append({'input':step,'result':row});return row
 def send(kind,value=None):
  row=call({'op':'invoke','input':json.dumps({'kind':kind,'value':value},separators=(',',':'))});check(row['ok'] and row['code']==0,'Original owned invocation succeeds');return row['projection']
 fixture=json.loads((root/'qa/native-source-fixture.json').read_text());source=fixture['clientScope'];binding=source['binding'];job=fixture['terminalReceipts'][0]['event']['event']['frame']['job'];identity='family:'+source['scope']['context']['incarnation'];domain={'binding':binding,'receiverEpoch':'1'}
 wrap=lambda event:{'previewProtocol':3,'kind':'native-preview-realm-event',**domain,'event':event}
 kinds=lambda result:[command['kind'] for row in result['commands']['entries'] for command in row['commands']]
 send('grant',{**domain,'capacity':1})
 send('presentation',{'surfaceProtocol':2,'publication':'1','lease':'1','mode':'picker','status':'','bar':[],'popup':[{'id':identity,'domId':'window-'+identity,'label':'Window','ariaLabel':'Window','detail':'','enabled':True}]})
 send('native',wrap({'kind':'source-seed','publication':'1','lease':'1','identity':identity,'source':source,'title':'Native source','application':'fixture'}))
 trigger={k:v for k,v in job.items() if k!='request'};r=send('native',wrap({'kind':'event','identity':identity,'event':{'kind':'request','trigger':trigger}}));check(kinds(r)==['acquire'],'Original acquisition retained');acquire=r['realm']['ingress']['intents'][0]
 r=send('quarantine',domain);check(r['realm']['deferred']==2 and r['realm']['inputBlocked'],'Full queue retains original reconciliation/cancellation');check(r['models'][0]['model']['known']==[job] and not r['models'][0]['model']['demand'],'Unknown job retained while demand revoked')
 before=send('status');seed={'detachProtocol':1,'kind':'native-preview-detach-seed','identity':identity,**domain,'subject':source['scope']['context']['incarnation'],'entry':'1','entryIssuedThrough':'1','requestFloor':'1'}
 for kind,value in [('native',wrap(seed)),('presentation',{}),('legacy',{})]:
  refusal=call({'op':'invoke','input':json.dumps({'kind':kind,'value':value})});check(refusal=={'ok':False,'code':3,'held':True},'Ordinary input explicitly refuses before processing');check(send('status')==before,'Exact retained policy remains after WOULD_BLOCK')
 r=send('quarantine',domain);check(r['realm']==before['realm'] and r['models']==before['models'],'Urgent quarantine remains admissible and bounded while blocked')
 refusal=call({'op':'close'});check(refusal=={'ok':False,'code':5,'held':True},'Pending/deferred/known state cannot be normally destroyed')
 r=send('closed',domain);check(not r['realm']['closed'],'Unissued cleanup prevents trusted Elm close')
 def issued(row,ordinal):
  packet={'previewProtocol':3,'kind':'preview-commands',**domain,'controlOrdinal':str(ordinal),'entries':[row]}
  fact={'previewProtocol':3,'kind':'preview-control-ticket',**domain,'controlOrdinal':str(ordinal),'alreadyDelivered':False,'wire':json.dumps(packet,separators=(',',':'))}
  return send('issued',fact)
 r=issued(acquire,1);check(r['realm']['ingress']['pending']==0 and r['realm']['deferred']==2 and r['models'][0]['model']['known']==[job],'Synthetic issuance removes intent only')
 r=send('retry',domain);check(kinds(r)==['reconcile'] and r['realm']['deferred']==1,'Oldest reconciliation transfers first');issued(r['realm']['ingress']['intents'][0],2)
 r=send('retry',domain);check(kinds(r)==['cancel'] and not r['realm']['inputBlocked'],'Cancellation transfers without dropping original order');issued(r['realm']['ingress']['intents'][0],3)
 r=send('native',wrap(seed));check(r['models'][0]['model']['known']==[job],'Retried original ordinary input is accepted after capacity admits it')
 r=send('native',wrap({'kind':'event','identity':identity,'event':{'kind':'receipt','sequence':'4','event':{'kind':'cancelled','job':job}}}));check(kinds(r)==['acknowledge'] and r['realm']['deferred']==1 and r['models'][0]['model']['known']==[],'Synthetic terminal fact keeps ACK before readiness');issued(r['realm']['ingress']['intents'][0],4)
 r=send('retry',domain);check(kinds(r)==['detach-ready'],'Exact retained readiness remains');issued(r['realm']['ingress']['intents'][0],5)
 r=send('native',wrap({'detachProtocol':1,'kind':'native-preview-binding-detach-delivery',**domain,'deliveryOrdinal':'1','event':{'kind':'native-preview-actor-detached','identity':identity,'subject':seed['subject'],'entry':'1','entryIssuedThrough':'1','requestFloor':'1'}}));check(r['models']==[] and kinds(r)==['detach-delivery-ack'],'Original final fact leaves retained processing intent')
 check(call({'op':'close'})=={'ok':False,'code':5,'held':True},'Empty membership still cannot destroy unissued intent');r=send('closed',domain);check(not r['realm']['closed'],'Final unissued processing intent still blocks close')
 issued(r['realm']['ingress']['intents'][0],6);r=send('closed',domain);check(r['realm']['closed'] and r['realm']['ingress']['pending']==0,'Original empty ingress accepts explicit synthetic trusted close');check(call({'op':'close'})=={'ok':True,'code':0,'held':False},'Owner finally destroys normally')
 child.stdin.close();child.wait(timeout=3);stderr=child.stderr.read();(out/'fixture.stderr').write_text(stderr);assert child.returncode==0 and stderr=='';selector.close()
 verify();assert all(sha(root/n)==v for n,v in report['inputs'].items());report.update(passed=True,checks=checks,syntheticNativeIssuedFacts=True,normalOwnedExit=True,explicitWouldBlockControls=3,singlePreviewPolicy=True)
except Exception as error:
 report['error']=repr(error)
 if child and child.poll() is None:child.terminate();child.wait(timeout=3)
 if child and child.stderr:(out/'fixture.stderr').write_text(child.stderr.read())
(out/'steps.json').write_text(json.dumps(steps,indent=2)+'\n')
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and 'mutable-elm-home' not in p.parts and 'elm-stuff' not in p.parts}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2200]}),flush=True);sys.exit(not report['passed'])
