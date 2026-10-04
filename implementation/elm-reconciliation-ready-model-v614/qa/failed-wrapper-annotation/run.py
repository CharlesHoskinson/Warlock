import hashlib,json,pathlib,re,subprocess
import sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa';rows=[];selected={};executed={}
def run(name,args,expected=0):
 p=subprocess.run(['quint',*args],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
 (OUT/(name+'.log')).write_text(p.stdout);rows.append({'name':name,'command':['quint',*args],'exit':p.returncode,'expected':expected,'ok':p.returncode==expected,'outputSHA256':hashlib.sha256(p.stdout.encode()).hexdigest()});return p
run('version',['--version'])
for file,main in [('tests.qnt','tests'),('protocol_tests.qnt','protocol_tests')]:
 run(main+'-typecheck',['typecheck',str(ROOT/file)])
 names=re.findall(r'run (\w+) =|run (\w+)=',(ROOT/file).read_text());names=[a or b for a,b in names];selected[main]=names
 p=run(main+'-named',['test',str(ROOT/file),'--main='+main,'--match=^('+'|'.join(names)+')$','--seed=61401','--max-samples=1','--backend=typescript','--out-itf='+str(OUT/('accepted_'+main+'_{test}_{seq}.itf.json'))]);executed[main]=re.findall(r'ok (\w+) passed 1 test\(s\)',p.stdout)
run('traces',['run',str(ROOT/'protocol.qnt'),'--main=protocol','--init=start','--step=tick','--invariant=protocolProps','--seed=61402','--max-samples=2000','--max-steps=80','--backend=typescript'])
mutants=[
 ('skipping-ready','q.ready and r.scope==q.active','true and r.scope==q.active',2,'ackEnqueuedNotProcessedTest'),
 ('not-resetting-next-scope','delivered:false,ackQueued:false,ready:false,actionExpected:0,geometryExpected:0,actionAccepted:0,geometryAccepted:0,actionOutput:0,geometryOutput:0','delivered:false,ackQueued:false,ready:false,actionExpected:0,geometryExpected:0,actionOutput:0,geometryOutput:0',1,'nextScopeClearsAcceptedTest'),
 ('qualifying-preack-queued-read','r.fresh and q.ready','true and q.ready',2,'queuedAfterProofBeforeAckTest'),
 ('release-unannounced','if(joined(q) and s.ack and s.rootReady and releaseReady(s) and count>0','if(s.ack and s.rootReady and releaseReady(s) and count>0',1,'unannouncedScopeCannotReleaseTest'),
 ('duplicate-ready-resets','{...q,ready:true} else q','{...q,ready:true,actionAccepted:0,geometryAccepted:0} else q',1,'duplicateReadyRetainsReadsTest'),
 ('retry-keeps-old-accept','actionExpected:r.id,actionAccepted:0','actionExpected:r.id',1,'retryLatestActionInvalidatesTest'),
 ('skip-output-join','st.actionOutput==st.geometryOutput','true',1,'differentOutputBlocksTest')]
for label,old,new,count,name in mutants:
 d=OUT/'mutants'/label;d.mkdir(parents=True,exist_ok=True);s=(ROOT/'protocol.qnt').read_text();assert s.count(old)==count,(label,s.count(old));(d/'protocol.qnt').write_text(s.replace(old,new));
 for f in ['release.qnt','protocol_tests.qnt']:(d/f).write_bytes((ROOT/f).read_bytes())
 run(label+'-typecheck',['typecheck',str(d/'protocol_tests.qnt')]);p=run(label+'-counterexample',['test',str(d/'protocol_tests.qnt'),'--main=protocol_tests','--match=^'+name+'$','--seed=61403','--max-samples=1','--backend=typescript'],1);rows[-1]['actualAssertionFailure']='Assertion failed' in p.stdout
r={'passed':selected==executed and all(row['ok'] and row.get('actualAssertionFailure',True) for row in rows),'selected':selected,'executed':executed,'namedCount':sum(map(len,selected.values())),'sampledTraces':2000,'maxTransitions':80,'typedMutants':len(mutants),'commands':rows,'sourceHashes':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'release.qnt',ROOT/'tests.qnt',ROOT/'protocol.qnt',ROOT/'protocol_tests.qnt',pathlib.Path(__file__)]},'nativeAcceptance':False,'scope':'CPU bounded abstract ready enqueue/processing protocol composed with V605 durability'}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'named':r['namedCount'],'executed':sum(map(len,executed.values())),'mutants':len(mutants)}));raise SystemExit(not r['passed'])
