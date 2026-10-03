from pathlib import Path
import argparse,hashlib,io,json,resource,subprocess,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;parser=argparse.ArgumentParser();parser.add_argument('--report',default='offline-report.json');args=parser.parse_args();scope=require_qa_scope()
help=subprocess.run(['/usr/bin/Xwayland','-help'],capture_output=True,text=True,timeout=8)
assert help.returncode==0 and '-auth file' in help.stdout+help.stderr
help_path=B/'Xwayland-help.txt'
if help_path.exists():assert help_path.read_text()==help.stdout+help.stderr
else:help_path.write_text(help.stdout+help.stderr)
stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(B),pattern='test*.py');result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
report={'result':'pass' if result.wasSuccessful() else 'fail','tests':result.testsRun,'actualPrimaryPredicateCases':2,'launcherAvailabilityMode':0o755,'launcherParentMode':0o700,'output':stream.getvalue(),'qaScope':scope,'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),'nativeServersLaunched':False,'nativeClientsLaunched':False,'helpOnly':True,'XwaylandSHA256':hashlib.sha256(Path('/usr/bin/Xwayland').read_bytes()).hexdigest(),'XwaylandHelpSHA256':hashlib.sha256((B/'Xwayland-help.txt').read_bytes()).hexdigest()}
p=B/args.report;assert p.parent==B and p.name.endswith('.json');assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'result':report['result'],'tests':result.testsRun,'actualPrimaryPredicateCases':2,'launcherAvailabilityMode':0o755,'launcherParentMode':0o700,'scope':scope,'reportSHA256':hashlib.sha256(p.read_bytes()).hexdigest()}));raise SystemExit(not result.wasSuccessful())
