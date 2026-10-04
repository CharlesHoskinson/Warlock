import hashlib,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('mutations-'+str(time.time_ns()));OUT.mkdir();results=[]
mutants=[('lost-process-start','scene.py'," or integer(role.get('processStarted'),1,2**63-1)!=started",''),('lost-native-popup-root','scene.py',"!=parent['identity']['surfaceId']:raise Refused('native popup T1 root differs')", "!=resource(n['t1Root'],pid=pid,uid=uid):raise Refused('native popup T1 root differs')"),('wrong-scale-multiply','geometry.py','global_point=[rx+window[0]-gx,ry+window[1]-gy]','global_point=[(rx+window[0]-gx)*role["devicePixelRatio"],(ry+window[1]-gy)*role["devicePixelRatio"]]')]
for name,file,old,new in mutants:
 root=OUT/name;(root/'qa').mkdir(parents=True)
 for p in (ROOT/'qa').glob('*.py'):shutil.copyfile(p,root/'qa'/p.name)
 p=root/'qa'/file;s=p.read_text();assert s.count(old)==1,(name,s.count(old));p.write_text(s.replace(old,new))
 result=subprocess.run([sys.executable,'-B',str(root/'qa/test.py')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15,env=dict(os.environ))
 (root/'stdout').write_bytes(result.stdout);(root/'stderr').write_bytes(result.stderr)
 reports=list((root/'qa').glob('test-*/report.json'));assert len(reports)==1
 r=json.loads(reports[0].read_text());assert result.returncode==1 and r['passed'] is False and r['checks'],(name,result.returncode,r)
 results.append({'name':name,'mutantSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'exitCode':result.returncode,'report':str(reports[0]),'error':r.get('error'),'checksBeforeKill':len(r['checks'])})
report={'passed':True,'nativeAcceptance':False,'sourceInputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'qa').glob('*.py')},'mutants':results};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'mutants':len(results),'report':str(OUT/'report.json')}))
