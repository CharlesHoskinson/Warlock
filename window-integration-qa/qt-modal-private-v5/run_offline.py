from pathlib import Path
import hashlib,io,json,resource,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from qa_launch import require_qa_scope
import test_cli_packaging
B=Path(__file__).resolve().parent
scope=require_qa_scope();stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(B),pattern='test*.py');result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
report={'result':'pass' if result.wasSuccessful() else 'fail','testsRun':result.testsRun,'output':stream.getvalue(),'qaScope':scope,'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),'actualHyprctlParser':test_cli_packaging.CLI_EVIDENCE,'nativeCompositorLaunched':False,'mainIPCContacted':False,'old203Unchanged':True,'oldV4FailurePreserved':True,'qtFixtureAndLuaBodyUnchanged':True,'sourceHashes':{str(B/n):hashlib.sha256((B/n).read_bytes()).hexdigest() for n in ('run_native.py','private_session.py','fixture.cpp','private-plugin.lua','test_cli_packaging.py','test_offline.py','contract.md','run_offline.py')}}
p=B/'offline-report.json';assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'result':report['result'],'tests':result.testsRun,'actualCliProbes':len(test_cli_packaging.CLI_EVIDENCE),'scope':scope,'reportSHA256':hashlib.sha256(p.read_bytes()).hexdigest()}));raise SystemExit(not result.wasSuccessful())
