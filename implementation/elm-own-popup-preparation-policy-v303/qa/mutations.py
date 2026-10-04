import hashlib,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('mutations-'+str(time.time_ns()));OUT.mkdir();results=[]
for name,old,new in [('external-grab',' && native.exclusiveOwnGrab',''),('missing-close-fence',' || not nativeFence',''),('native-ineligible','not fresh.eligible || ',''),('proof-reuse',' || List.any (sameMenu host) m.retired','')]:
 base=OUT/name;(base/'src').mkdir(parents=True);(base/'qa').mkdir()
 for p in (ROOT/'src').glob('*.elm'):shutil.copyfile(p,base/'src'/p.name)
 shutil.copyfile(ROOT/'elm.json',base/'elm.json');shutil.copyfile(ROOT/'qa/test.py',base/'qa/test.py')
 p=base/'src/OwnPopupPreparation.elm';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
 result=subprocess.run([sys.executable,'-B',str(base/'qa/test.py')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=65,env=dict(os.environ));(base/'stdout').write_bytes(result.stdout);(base/'stderr').write_bytes(result.stderr)
 reports=list((base/'qa').glob('test-*/report.json'));assert len(reports)==1;r=json.loads(reports[0].read_text());assert result.returncode==1 and r['passed'] is False
 tests=list(reports[0].parent.glob('stdout'));assert tests and tests[0].read_bytes(),'mutant must compile and produce independent boolean failures'
 rows=json.loads(tests[0].read_bytes());failures=[x for x in rows if x['passed'] is False];assert failures
 results.append({'name':name,'report':str(reports[0]),'compiledUnsafeBody':True,'failures':failures,'sourceSHA256':hashlib.sha256(p.read_bytes()).hexdigest()})
report={'passed':True,'nativeAcceptance':False,'sourceInputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'src').glob('*.elm')},'mutants':results};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'mutants':len(results),'report':str(OUT/'report.json')}))
