import hashlib,json,os,stat,sys,time,unittest
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa')
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-hidden-capture-fusion-v29')
sys.path.insert(0,str(QA));from qa_launch import require_qa_scope
sys.path.insert(0,str(B))
import test_hidden_capture_fusion as tests
def stamp(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def main():
 scope=require_qa_scope();folder=QA/'hidden-capture-v29-focused-proof-v1';folder.mkdir(mode=0o700,exist_ok=False)
 paths=[p for p in B.iterdir()if p.is_file()and p.suffix in ('.py','.c')];paths.append(Path(__file__));before={str(p):stamp(p)for p in paths}
 with os.fdopen(os.open(folder/'tests.log',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as log:
  result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
 exact=before=={str(p):stamp(p)for p in paths}
 row={'result':'pass'if result.wasSuccessful()and exact else 'fail','pythonTests':result.testsRun,'errors':[(str(t),s)for t,s in result.errors],'failures':[(str(t),s)for t,s in result.failures],'sources':before,'sourceUnchanged':exact,'log':str(folder/'tests.log'),'logSHA256':stamp(folder/'tests.log')['sha256'],'evidence':tests.EVIDENCE,'scope':scope,'nativeLaunch':False,'grimIsCPUFixture':True,'realMagick':True,'realOwnedCommandsAndKeeper':True,'nativeAccepted':False}
 with os.fdopen(os.open(folder/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({k:row[k]for k in ('result','pythonTests','sourceUnchanged','log')}));return int(row['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
