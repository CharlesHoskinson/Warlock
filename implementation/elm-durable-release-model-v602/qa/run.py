import hashlib,json,pathlib,re,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa';rows=[]
def run(name,args,expected=0):
 p=subprocess.run(['quint',*args],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90);(OUT/(name+'.log')).write_text(p.stdout);row={'name':name,'command':['quint',*args],'exit':p.returncode,'expected':expected,'ok':p.returncode==expected,'outputSHA256':hashlib.sha256(p.stdout.encode()).hexdigest()};rows.append(row);return p
run('version',['--version']);run('typecheck',['typecheck',str(ROOT/'tests.qnt')]);names=re.findall(r'run (\w+) =', (ROOT/'tests.qnt').read_text());selector='^('+'|'.join(names)+')$'
p=run('named',['test',str(ROOT/'tests.qnt'),'--main=tests','--match='+selector,'--seed=60202','--max-samples=1','--backend=typescript','--out-itf='+str(OUT/'accepted_{test}_{seq}.itf.json')]);executed=re.findall(r'ok (\w+) passed 1 test\(s\)',p.stdout)
run('traces',['run',str(ROOT/'release.qnt'),'--main=release','--invariant=allProps','--max-samples=2000','--max-steps=80','--seed=60203','--backend=typescript'])
mutants=[
('premature-ack','| Ack => if (releaseReady(s))','| Ack => if (s.stage>=1)','ackBeforeFinalSyncRefusedTest'),
('restart-prepared-unlocks','file:s.durableFile,releasedRecord:s.stage==2,ack:false','stage:if(s.stage==1) 2 else s.stage,file:s.durableFile,releasedRecord:s.stage==2,ack:false','preparedCrashStaysBlockedTest'),
('unlink-unprepared','if (s.stage==1 and s.proofDurable) {...s,file:false}','if (s.nativeRetired or s.stage==0) {...s,file:false}','unlinkBeforePrepareRefusedTest'),
('registered-proof','s.nativeRetired and p.kind==1 and p.key==1 and p.epoch==1 and p.barrier==1','p.key==1 and p.epoch==1 and p.barrier==1','registeredProofRefusedTest'),
('foreign-proof','and p.key==1','and p.key>=1','foreignProofRefusedTest'),
('future-proof','and p.barrier==1','and p.barrier>=1','futureProofRefusedTest'),
('one-read-proof','if (observations(s)) {...s,proofWritten:true}','if (s.actionRead) {...s,proofWritten:true}','oneReadCannotPrepareTest'),
('crossed-read','o.kind==2 and o.request==12','o.kind==2 and o.request==11','crossedRequestsRefusedTest'),
('stale-observation','and o.seq==2','and o.seq>=1','staleObservationRefusedTest'),
('released-resurrection','if (s.stage==0 and not(s.file))','if (not(s.file))','releasedCrashNeverResurrectsTest'),
('history-committed','| Ack => if (releaseReady(s)) {...s,ack:true}','| Ack => if (releaseReady(s)) {...s,ack:true,committed:true}','historyUnknownNotCommitTest'),
('old-intent-replay','and key==2 and not(s.history.contains(key))','and key>=1','historyUnknownNotCommitTest'),
('stage-regression','if (s.stage==0 and s.recordSynced and observations(s) and s.proofDurable)','if (s.recordSynced and observations(s) and s.proofDurable)','releasedStageCannotRegressTest'),
('old-read-after-crash','o.epoch==s.frontendEpoch','o.epoch==1','oldReadAfterCrashRefusedTest'),
('history-overflow','key==2 and s.history.size()<2','key>=2','boundedHistoryNoOverwriteTest')]
for label,old,new,test in mutants:
 d=OUT/'mutants'/label;d.mkdir(parents=True,exist_ok=True);s=(ROOT/'release.qnt').read_text();assert s.count(old)==1,(label,s.count(old));(d/'release.qnt').write_text(s.replace(old,new));(d/'tests.qnt').write_bytes((ROOT/'tests.qnt').read_bytes())
 run(label+'-typecheck',['typecheck',str(d/'tests.qnt')]);p=run(label+'-counterexample',['test',str(d/'tests.qnt'),'--main=tests','--match=^'+test+'$','--seed=60204','--max-samples=1','--backend=typescript'],1);rows[-1]['actualAssertionFailure']='Assertion failed' in p.stdout
report={'passed':all(r['ok'] and r.get('actualAssertionFailure',True) for r in rows) and executed==names,'scope':'Bounded CPU Quint ledger/crash model, not filesystem fsync or native authority acceptance','namedCount':len(names),'selectedNames':names,'executedNames':executed,'samples':2000,'maxSteps':80,'mutants':len(mutants),'commands':rows,'sourceHashes':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'release.qnt',ROOT/'tests.qnt',pathlib.Path(__file__)]},'nativeActions':False};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'named':len(executed),'expected':len(names),'mutants':len(mutants)}));raise SystemExit(not report['passed'])
