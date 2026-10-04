import hashlib,json,pathlib,re,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa';rows=[]
def run(name,args,expected=0):
 p=subprocess.run(['quint',*args],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120);(OUT/(name+'.log')).write_text(p.stdout);rows.append({'name':name,'command':['quint',*args],'exit':p.returncode,'expected':expected,'ok':p.returncode==expected,'outputSHA256':hashlib.sha256(p.stdout.encode()).hexdigest()});return p
run('version',['--version']);run('typecheck',['typecheck',str(ROOT/'frontier.qnt')]);names=re.findall(r'run (\w+)=',(ROOT/'frontier.qnt').read_text());p=run('named',['test',str(ROOT/'frontier.qnt'),'--main=frontier','--match=^('+'|'.join(names)+')$','--seed=62001','--max-samples=1','--backend=typescript','--out-itf='+str(OUT/'accepted_{test}_{seq}.itf.json')]);executed=re.findall(r'ok (\w+) passed 1 test\(s\)',p.stdout)
run('traces',['run',str(ROOT/'frontier.qnt'),'--main=frontier','--invariant=safety','--seed=62002','--max-samples=1000','--max-steps=40','--backend=typescript'])
mutants=[
 ('request-erases-accepted','expectedA:st.next,expectedG:st.next+1,next:st.next+2','acceptedA:NONE,acceptedG:NONE,expectedA:st.next,expectedG:st.next+1,next:st.next+2','pendingRequestRetainsAcceptedTest'),
 ('release-requires-latest-request','st.reserved and st.durable','st.reserved and st.durable and p.a.id==st.expectedA and p.g.id==st.expectedG','finalGeometryDrainQueuedReleaseTest'),
 ('phase-hides-accepted-final-reply','if(admittedState.dirty) batch(admittedState)','if(admittedState.dirty) batch(st)','finalGeometryDrainQueuedReleaseTest'),
 ('ignore-new-accepted-action','{...st,acceptedA:r,pendingA:false}','{...st,acceptedA:if(st.acceptedA.id>0) st.acceptedA else r,pendingA:false}','actualAcceptedActionInvalidatesTest'),
 ('ignore-new-accepted-geometry','{...st,acceptedG:r,pendingG:false}','{...st,acceptedG:if(st.acceptedG.id>0) st.acceptedG else r,pendingG:false}','actualAcceptedGeometryInvalidatesTest'),
 ('release-emits-effect','{...st,reserved:false,releaseA:p.a.id,releaseG:p.g.id}','{...st,reserved:false,releaseA:p.a.id,releaseG:p.g.id,effects:st.effects+1}','noAutomaticEffectAfterReleaseTest'),
 ('pending-allows-explicit','not(st.reserved) and complete(st) and st.phase==2','not(st.reserved)','finalGeometryDrainQueuedReleaseTest'),
 ('context-ignored','p.a==st.acceptedA and p.g==st.acceptedG','p.a.id==st.acceptedA.id and p.g.id==st.acceptedG.id','changedContextSameIdRefusedTest'),
 ('fifo-reversed','st.wire.head()','st.wire.nth(st.wire.length()-1)','fifoReleaseBeforeNewReplyTest')]
for label,old,new,name in mutants:
 d=OUT/'mutants'/label;d.mkdir(parents=True,exist_ok=True);s=(ROOT/'frontier.qnt').read_text();assert s.count(old)==1,(label,s.count(old));(d/'frontier.qnt').write_text(s.replace(old,new));run(label+'-typecheck',['typecheck',str(d/'frontier.qnt')]);p=run(label+'-counterexample',['test',str(d/'frontier.qnt'),'--main=frontier','--match=^'+name+'$','--seed=62003','--max-samples=1','--backend=typescript'],1);rows[-1]['actualAssertionFailure']='Assertion failed' in p.stdout
r={'passed':names==executed and all(row['ok'] and row.get('actualAssertionFailure',True) for row in rows),'selected':names,'executed':executed,'namedCount':len(names),'sampledTraces':1000,'maxTransitions':40,'typedMutants':len(mutants),'commands':rows,'sourceHashes':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'frontier.qnt',pathlib.Path(__file__)]},'nativeAcceptance':False,'scope':'CPU accepted frontier and ordered reply/release queue; durability is an assumed prerequisite'};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'named':len(executed),'expected':len(names),'mutants':len(mutants)}));raise SystemExit(not r['passed'])
