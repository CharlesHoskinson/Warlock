import sys,json,os,hashlib,subprocess
from pathlib import Path
Q=Path('/home/hoskinson/window-integration-qa');sys.path.insert(0,str(Q));from qa_launch import require_qa_scope
scope=require_qa_scope();P=Path(__file__).parent;B=Q/'family-preparation-thumbnail-v9'
code="import sys,unittest;sys.path.insert(0,sys.argv[1]);import service_observer,module_binding;assert not module_binding._observe('focused-bootstrap')['errors'];suite=unittest.defaultTestLoader.loadTestsFromNames(['test_collector_closure_alias','test_renderer_collector_binding.RendererBindingKernelTests.test_foreign_genuine_keeper_same_root_and_environment_refuses_binding','test_freezer_v2']);r=unittest.TextTestRunner(verbosity=2).run(suite);raise SystemExit(not r.wasSuccessful())"
log=P/'cpu.log'
with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:r=subprocess.run(['/usr/bin/python3','-B','-c',code,str(B)],cwd='/home/hoskinson',env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),stdout=f,stderr=subprocess.STDOUT,timeout=120)
row={'result':'pass'if r.returncode==0 else'fail','scope':scope,'exitCode':r.returncode,'log':str(log),'logSHA256':hashlib.sha256(log.read_bytes()).hexdigest(),'nativeLaunch':False}
with os.fdopen(os.open(P/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n')
print(json.dumps(row));raise SystemExit(r.returncode)
