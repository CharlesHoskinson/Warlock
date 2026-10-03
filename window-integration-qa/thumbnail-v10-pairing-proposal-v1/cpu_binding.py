"""Actual unmodified binding/kernel tests, explicit selected nineteen modules."""
import hashlib,importlib,json,os,sys,time,unittest
from pathlib import Path
OUT=Path(__file__).resolve().parent; B=OUT.parent/'family-preparation-thumbnail-v10';sys.path.insert(0,str(B))
import module_binding as binding
sys.path.insert(0,str(binding.SERVICE))
for name in binding.MODULES:importlib.import_module(name)
observation=binding._observe('v10-cpu-selected-source')
assert not observation['errors'],observation['errors']
assert len(observation['modules'])==19
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name)for name in ('test_actual_binding','test_batch_binding','test_renderer_collector_binding'))
start=time.monotonic();fd=os.open(OUT/'cpu-binding.log',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
with os.fdopen(fd,'w')as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);stream.flush();os.fsync(stream.fileno())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
row={'result':'pass'if result.wasSuccessful()else'fail','testsRun':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'wallSeconds':time.monotonic()-start,'selectedSourceModules':observation['modules'],'selectedSourceErrors':observation['errors'],'actualTestsByteExactFromV9':{n:sha(B/(n+'.py'))==sha(OUT.parent/'family-preparation-thumbnail-v9'/(n+'.py'))for n in ('test_actual_binding','test_batch_binding','test_renderer_collector_binding')},'logSHA256':sha(OUT/'cpu-binding.log'),'scope':Path('/proc/self/cgroup').read_text().strip(),'nativeLaunch':False,'nativeAccepted':False,'mainChanged':False}
with os.fdopen(os.open(OUT/'cpu-binding-report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({k:v for k,v in row.items()if k!='selectedSourceModules'}));raise SystemExit(0 if result.wasSuccessful()else 1)
