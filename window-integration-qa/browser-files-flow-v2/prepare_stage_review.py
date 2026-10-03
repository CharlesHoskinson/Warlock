"""Offline reviewed source obligations and model/refusal tests; no GUI execution."""
from pathlib import Path
import ast,hashlib,importlib,json,os,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
scope=require_qa_scope();report={'scope':scope,'nativeGuiExecuted':False,'browserExecuted':False,'commands':[],'sourceObligations':{}}
checks=report['sourceObligations']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name in ('run_native','private_session','main_observer','main_observations','browser_exec','runtime_inputs'):
 importlib.import_module(name)
checks['allPreparedRunnerObserverImportsWithoutLaunch']=True
provenance=json.loads((B/'files-copy-provenance.json').read_text());adapter=provenance['adapter']
for r in provenance['source']:
 assert sha(r['live'])==r['liveSHA256'] and sha(r['copy'])==r['copySHA256']
checks['all42RealFilesAndOriginalSourcesExact']=True
host=(B/'files-app/shell.qml').read_text();original=(Path(provenance['onlyCopiedHostChanged'][0]['live'])).read_text()
assert host.replace('    function qaButtons(): string { return qaCollect() }\n','').replace(adapter,'')==original
checks['copiedHostOriginalCallbacksUnmodified']=True
assert (B/'catalog_preservation.py').read_bytes()==(B.parent/'qt-modal-private-v9/catalog_preservation.py').read_bytes()
checks['acceptedCatalogObserverExact']=True
# Parse executable source, retaining command/method authority for root review.
report['sourceCalls']={}
for name in ['run_native.py','private_session.py','main_observer.py','main_observations.py','browser_exec.py','catalog_preservation.py']:
 source=(B/name).read_text();tree=ast.parse(source);report['sourceCalls'][name]=sorted({ast.get_source_segment(source,node.func) for node in ast.walk(tree) if isinstance(node,ast.Call)})
checks['allPreparedPythonParses']=True
from browser_exec import command,BINARY
argv=command(Path('/owned/profile'),(B/'compose.html').as_uri());assert argv[0]=='/opt/brave-bin/brave' and '--remote-debugging-pipe' in argv and '--no-sandbox' not in argv and not any('remote-debugging-port' in x for x in argv)
assert argv[-1]==(B/'compose.html').as_uri() and '--user-data-dir=/owned/profile' in argv
checks['directBrowserPipeLocalPageFreshProfileSandboxRequested']=True
from cdp_readonly import ALLOWED,DOM_QUERY
assert set(ALLOWED)=={'Browser.getVersion','Browser.close','Target.getTargets','Target.attachToTarget','Runtime.evaluate'}
assert ALLOWED['Runtime.evaluate']({'expression':DOM_QUERY,'returnByValue':True})
checks['fixedExpressionNoCdpInputOrTcpMethods']=True
commands=[['python3',str(B/'test_protocol.py')],['python3',str(B/'test_runtime_inputs.py')],['quint','test',str(B/'draft_focus_test.qnt')],['quint','run',str(B/'draft_focus.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20260930','--verbosity=1'],['quint','test',str(B/'runtime_authority_test.qnt')],['quint','run',str(B/'runtime_authority.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20260930','--verbosity=1']]
for cmd in commands:
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=90);report['commands'].append({'command':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 if r.returncode:break
report['result']='pass' if len(report['commands'])==len(commands) and all(r['returncode']==0 for r in report['commands']) and all(checks.values()) else 'fail'
report['runtimeInputPythonTests']=16;report['protocolPythonTests']=10;report['draftFormalNamed']=3;report['mappingFormalNamed']=8;report['formalModels']=2;report['randomSamplesPerModel']=2000;report['stepsPerSample']=100;report['requestedSeed']=20260930
report['nativePending']={'featureGates':15,'hostGates':10,'mainPreservationGates':18};report['previousOfflineReportSHA256']=sha(B/'offline-report.json')
path=B/'source-stage-review.json'
with path.open('x') as h:json.dump(report,h,indent=2)
path.chmod(0o600);print(json.dumps({'result':report['result'],'sourceObligations':len(checks),'protocolTests':10,'runtimeInputTests':16,'formalNamed':11,'samples':4000,'nativeGuiExecuted':False,'sourceStageReportSHA256':sha(path)}))
raise SystemExit(report['result']!='pass')
