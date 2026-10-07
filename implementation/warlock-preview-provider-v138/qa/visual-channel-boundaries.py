"""Actual sanitizer channel invalid argument, currency and closed-owner boundaries."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('visual-channel-boundaries-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=root/'qa/visual-channel-check-1791371205851102125';prior=json.loads((base/'report.json').read_text());assert prior['passed']
names=list(prior['inputs'])+['native/visual-channel-boundary-fixture.cpp','qa/visual-channel-boundaries.py']
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual sanitizer C/JSC missing native output/context/policy/receipt and absent/closed/destroyed channel boundaries. Refusals before valid processing retain exact accepted visual custody; missing current policy clears currency. Synthetic empty native grant/closed notifications do not qualify actual Native closure or WebKit/DOM/physical concealment.'}
def run(name,args,cwd=None,stdin=None):
 p=subprocess.run(args,cwd=cwd or out/'inputs',input=stdin,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p.stdout
try:
 for rel,value in prior['inputs'].items():assert sha(root/rel)==value
 for rel,value in prior['artifacts'].items():assert sha(base/rel)==value
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-2.0','json-glib-1.0','javascriptcoregtk-4.1']));binary=out/'boundaries'
 run('compile-owner',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/visual-channel-boundary-fixture.cpp','native/elm-preview-policy.cpp','native/preview-visual-channel.cpp','-o',str(binary),*flags])
 binding=json.loads((root/'qa/native-source-fixture.json').read_text())['clientScope']['binding'];domain={'binding':binding,'receiverEpoch':'1'}
 def invocation(kind,value=None):return {'op':'invoke','input':json.dumps({'kind':kind,'value':value},separators=(',',':'))}
 def command(action,input=None):return {'op':'channel','action':action,'context':0,**({'input':input} if input is not None else {})}
 expected={'channelProtocol':1,'kind':'native-preview-projection-accepted',**domain,'rendererLease':'1','visualSequence':'1'}
 steps=[];codes=[]
 def add(step,code):steps.append(step);codes.append(code)
 add(command('attach-null-context'),1);add(command('attach-no-output'),1);add(command('attach'),6)
 add(invocation('grant',{**domain,'capacity':1}),0);add(command('attach-null-policy'),1);add(command('attach'),0);add(command('offer'),0);add(command('ack',json.dumps(expected,separators=(',',':'))),0)
 for action,code in [('offer-no-output',1),('retry-no-output',1),('offer-null-context',3),('retry-null-context',3),('ack-no-input',4)]:add(command(action),code);add(command('current'),0)
 add(command('current-null-policy'),1);add(command('current'),4);add(command('retry'),4);add(command('offer'),0)
 add(invocation('closed',domain),0);add(command('retry'),6);add(command('current'),6);add(command('detach'),0);add(command('close'),0);add(command('offer'),1);add(command('retry'),1);add(command('ack'),1);add(command('current'),1);add(command('close'),1);add({'op':'close'},0)
 rows=[json.loads(line) for line in run('boundaries',[str(binary),str(base/'policy.js')],stdin=''.join(json.dumps(s)+'\n' for s in steps)).splitlines()];assert len(rows)==len(steps)
 for step,row,code in zip(steps,rows,codes):assert row['code']==code and row['ok']==(code==0),(step,row,code);assert code==0 or 'projection' not in row
 assert rows[6]['projection']['visualSequence']=='1' and rows[21]['projection']['visualSequence']=='2';assert rows[-1]=={'ok':True,'code':0,'held':False}
 (out/'steps.json').write_text(json.dumps([{'input':s,'result':r} for s,r in zip(steps,rows)],indent=2)+'\n');report.update(checks=len(steps),normalOwnedExit=True,syntheticNativeGrantAndClose=True)
 assert all(sha(root/n)==v for n,v in report['inputs'].items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and 'mutable-elm-home' not in p.parts and 'elm-stuff' not in p.parts}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2200]}),flush=True);sys.exit(not report['passed'])
