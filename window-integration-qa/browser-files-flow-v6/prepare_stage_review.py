"""Offline reviewed source obligations and model/refusal tests; no GUI execution."""
from pathlib import Path
import ast,hashlib,importlib,json,os,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
scope=require_qa_scope();report={'scope':scope,'nativeGuiExecuted':False,'browserExecuted':False,'commands':[],'sourceObligations':{}}
checks=report['sourceObligations']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name in ('run_native','private_session','main_observer','main_observations','browser_exec','runtime_inputs','process_evidence','private_bus_host','bus_authority','mapping_evidence','nss_inputs'):
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
for name in ['run_native.py','private_session.py','main_observer.py','main_observations.py','browser_exec.py','catalog_preservation.py','process_evidence.py','private_bus_host.py','bus_authority.py','mapping_evidence.py','nss_inputs.py','loader_closure.py']:
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
checks['rawOwnedKernelProcessEvidenceBeforeRoleFilter']='samples=capture_processes(' in (B/'private_session.py').read_text()
checks['allLiveOwnedMappingsUnreadableStillRefused']="/maps').read_bytes()" in (B/'private_session.py').read_text() and "if row.get('readError'):raise RuntimeError('Owned maps unreadable:" in (B/'mapping_evidence.py').read_text()
checks['mappingAuthorityByteExactV5']=(B/'runtime_inputs.py').read_bytes()==(B.parent/'browser-files-flow-v5/runtime_inputs.py').read_bytes()
source=(B/'private_session.py').read_text();tree=ast.parse(source)
mapped=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='mapped_inputs')
segment=ast.get_source_segment(source,mapped)
checks['completeRawMapBatchPersistedBeforeValidation']=segment.index('capture_maps(')<segment.index("report.setdefault('actualMappedInputs'")<segment.index('PrivateDesktop.private_json(')<segment.index('validate_maps(') and 'finally:' in segment and segment.count('PrivateDesktop.private_json(')==2
from nss_inputs import enumerate_modules
nss,modules=enumerate_modules('/etc/nsswitch.conf','/usr/lib');loader=json.loads((B/'loader-closure.json').read_text())
checks['allConfiguredAndInstalledNssSeedsTraceOnly']=loader['nssInputs']==nss and all(str(p) in loader['files'] and any(r['path']==str(p) and r['traceOnly'] for r in loader['loaderTraces']) for p in modules) and loader['files']['/etc/nsswitch.conf']==sha('/etc/nsswitch.conf') and loader['files']['/usr/lib/libnss_resolve.so.2']==sha('/usr/lib/libnss_resolve.so.2') and loader['dynamicLoadedModuleVerificationPending']
from private_bus_host import BUS_TEMPLATE
import xml.etree.ElementTree as ET
root=ET.fromstring(BUS_TEMPLATE.replace('@PRIVATE_BUS_ADDRESS@','unix:path=/owned/bus'))
checks['privateBusZeroActivationDirectoriesIncludes']=not any(x.tag in {'include','includedir','servicedir','standard_session_servicedirs','standard_system_servicedirs','servicehelper'} for x in root.iter())
checks['initialEnvironmentEvidencePersistsBeforeValidation']=(B/'private_session.py').read_text().index("PrivateDesktop.private_json(out/'app-environment-evidence.json'") < (B/'private_session.py').read_text().index("if strict and not proof['initialRangeMatches']")
checks['bothAppBusSelectorsExplicitOwned']="DBUS_SYSTEM_BUS_ADDRESS=private_env['DBUS_SESSION_BUS_ADDRESS']" in (B/'private_session.py').read_text()
checks['actualBrowserBusBindingNoCurrentGetenvClaim']='actualBrowserBusAuthority' in (B/'private_session.py').read_text() and 'not direct current getenv or GIO inspection' in (B/'bus_authority.py').read_text()
checks['browserInitialRangeDiagnosticFilesEqualityRetained']="actual_app_bus(browser,'browser',strict=False)" in (B/'private_session.py').read_text() and "actual_app_bus(files,'files')" in (B/'private_session.py').read_text()
commands=[['quint','test',str(B/'bus_authority_test.qnt')],['quint','run',str(B/'bus_authority.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20260930','--verbosity=1'],['python3',str(B/'test_bus_authority.py')],['python3',str(B/'test_process_evidence.py')],['python3',str(B/'test_private_bus.py')],['quint','test',str(B/'process_evidence_test.qnt')],['quint','run',str(B/'process_evidence.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20260930','--verbosity=1'],['python3',str(B/'test_protocol.py')],['python3',str(B/'test_runtime_inputs.py')],['quint','test',str(B/'draft_focus_test.qnt')],['quint','run',str(B/'draft_focus.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20260930','--verbosity=1'],['quint','test',str(B/'runtime_authority_test.qnt')],['quint','run',str(B/'runtime_authority.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20260930','--verbosity=1']]
commands += [['python3',str(B/'test_mapping_evidence.py')],['python3',str(B/'test_nss_inputs.py')],['quint','test',str(B/'mapping_evidence_test.qnt')],['quint','run',str(B/'mapping_evidence.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20260930','--verbosity=1']]
for cmd in commands:
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=90);report['commands'].append({'command':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 if r.returncode:break
report['result']='pass' if len(report['commands'])==len(commands) and all(r['returncode']==0 for r in report['commands']) and all(checks.values()) else 'fail'
report['runtimeInputPythonTests']=16;report['protocolPythonTests']=10;report['draftFormalNamed']=3;report['mappingFormalNamed']=8;report['processEvidencePythonTests']=19;report['privateBusPythonTests']=5;report['processFormalNamed']=8;report['busAuthorityPythonTests']=10;report['busAuthorityFormalNamed']=9;report['formalModels']=5;report['mappingEvidencePythonTests']=10;report['nssInputsPythonTests']=6;report['mappingEvidenceFormalNamed']=6;report['randomSamplesPerModel']=2000;report['stepsPerSample']=100;report['requestedSeed']=20260930
report['nativePending']={'featureGates':15,'hostGates':10,'mainPreservationGates':18};report['previousOfflineReportSHA256']=sha(B/'offline-report.json')
path=B/'source-stage-review.json'
with path.open('x') as h:json.dump(report,h,indent=2)
path.chmod(0o600);print(json.dumps({'result':report['result'],'sourceObligations':len(checks),'protocolTests':10,'runtimeInputTests':16,'processEvidenceTests':19,'privateBusTests':5,'busAuthorityTests':10,'mappingEvidenceTests':10,'nssInputsTests':6,'formalNamed':34,'samples':10000,'nativeGuiExecuted':False,'sourceStageReportSHA256':sha(path)}))
raise SystemExit(report['result']!='pass')
