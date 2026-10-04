import hashlib,json,pathlib,re,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa';rows=[]
def run(name,args,expected=0):
 p=subprocess.run(['quint',*args],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120);(OUT/(name+'.log')).write_text(p.stdout);rows.append({'name':name,'command':['quint',*args],'exit':p.returncode,'expected':expected,'ok':p.returncode==expected,'outputSHA256':hashlib.sha256(p.stdout.encode()).hexdigest()});return p
run('version',['--version']);run('typecheck',['typecheck',str(ROOT/'archive.qnt')]);names=re.findall(r'run (\w+)=',(ROOT/'archive.qnt').read_text());p=run('named',['test',str(ROOT/'archive.qnt'),'--main=archive','--match=^('+'|'.join(names)+')$','--seed=62901','--max-samples=1','--backend=typescript','--out-itf='+str(OUT/'accepted_{test}_{seq}.itf.json')]);executed=re.findall(r'ok (\w+) passed 1 test\(s\)',p.stdout)
run('traces',['run',str(ROOT/'archive.qnt'),'--main=archive','--invariant=safety','--seed=62902','--max-samples=1500','--max-steps=70','--backend=typescript'])
mutants=[
 ('effect-before-root-sync','s.locked and s.rootReady and has(s,k,0) and not(has(s,k,2))','s.locked and s.visible.contains(k*10) and not(has(s,k,2))','visibleManifestRestartBarrierTest'),
 ('powerloss-keeps-visible','visible:s.archive,visibleMark:s.mark','visible:s.visible,visibleMark:s.visibleMark','unsyncedManifestPowerLossTest'),
 ('skip-page-fsync','if(s.pageDirSynced) {...s,manifestWritten:true}','if(s.pagesWritten) {...s,manifestWritten:true}','pagesBeforeManifestTest'),
 ('erase-on-compaction','visible:s.archive,visibleMark:s.mark,visibleMigration:s.migration,pagesWritten:true','visible:Set(),visibleMark:s.mark,visibleMigration:s.migration,pagesWritten:true','immutableMigrationAndCompactionTest'),
 ('unbounded-hot','hot(st).size()<2','hot(st).size()<3','hotExhaustionBeforeEffectTest'),
 ('skip-quota','and s.archive.size()+1<=s.quota','and true','archiveQuotaRefusesBeforeEffectTest'),
 ('late-released-resurrects','if(has(s,k,4) and s.rootReady) s','if(false) s','lateExactReleasedCAdmissionTest'),
 ('unlink-skips-restart','s.locked and s.rootReady and has(s,k,3)','s.locked and has(s,k,3)','preparedUnlinkNeedsRestartBarrierTest'),
 ('released-without-admission-fsync','has(st,k,3) and not(st.durableFiles.contains(k))','has(st,k,3)','unlinkPowerLossRetainsReservationTest'),
 ('unanchored-certificate','else if(t==5) has(st,k,4)','else if(t==5) has(st,k,0)','unanchoredDeliveryRefusedTest')]
for label,old,new,name in mutants:
 d=OUT/'mutants'/label;d.mkdir(parents=True,exist_ok=True);s=(ROOT/'archive.qnt').read_text();assert s.count(old)==1,(label,s.count(old));(d/'archive.qnt').write_text(s.replace(old,new));run(label+'-typecheck',['typecheck',str(d/'archive.qnt')]);p=run(label+'-counterexample',['test',str(d/'archive.qnt'),'--main=archive','--match=^'+name+'$','--seed=62903','--max-samples=1','--backend=typescript'],1);rows[-1]['actualAssertionFailure']='Assertion failed' in p.stdout
r={'passed':names==executed and all(c['ok'] and c.get('actualAssertionFailure',True) for c in rows),'selected':names,'executed':executed,'namedCount':len(names),'sampledTraces':1500,'maxTransitions':70,'typedMutants':len(mutants),'commands':rows,'sourceHashes':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'archive.qnt',pathlib.Path(__file__)]},'nativeAcceptance':False,'scope':'CPU symbolic paged archive commit ordering/conservation; not filesystem/C/native scalability'};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'named':len(executed),'expected':len(names),'mutants':len(mutants)}));raise SystemExit(not r['passed'])
