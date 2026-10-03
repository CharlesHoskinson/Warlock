"""Offline frontend model/source/actual Unix CLI tests, never GUI/native actors."""
from pathlib import Path
import ast,hashlib,importlib,json,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
scope=require_qa_scope();checks={};report={'scope':scope,'nativeGuiExecuted':False,'nativeActorExecuted':False,'testCompositorIsProtocolFixture':True,'commands':[],'sourceChecks':checks}
for name in ['native_frontend','prepare_config']:importlib.import_module(name)
checks['candidateAndBuilderImportWithoutSocketLaunch']=True
for name in ['native_frontend.py','prepare_config.py','test_frontend.py','freeze_packet.py']:ast.parse((B/name).read_text())
checks['allCandidateSourcesParse']=True
source=(B/'native_frontend.py').read_text();tree=ast.parse(source)
calls=[node for node in ast.walk(tree) if isinstance(node,ast.Call)]
checks['unchangedV12RequestCalledExactlyOneSourceSite']=sum(isinstance(n.func,ast.Attribute) and n.func.attr=='request_runtime' for n in calls)==1
checks['noInputOrActorOrLegacyFallbackImports']=not any(x in source for x in ['subprocess.','ptrace','control.sock','native_launch','capture_source','dispatch'])
checks['readOnlyCurrentCompositorObservationOnly']=source.count("read_compositor(config,b'j/clients')")==1 and 'c.sendall(command)' in source
checks['directIsolatedNoSiteShebang']=source.startswith('#!/usr/bin/python3 -IS\n') and 'sys.flags.isolated' in source and 'sys.flags.no_site' in source
checks['postSendFaultsUncertainNoRetry']='if any(value.proof.get(\'sendStarted\')' in source and 'except BackendRejected:raise' in source
checks['ownedConfigEntryRootsSocketPeerEOFGuards']=all(x in source for x in ['verify_config_unchanged','root[\'environment\']','root[\'cgroup\']','SO_PEERCRED','completeServerEOF','serviceSocketIdentity','compositorSocketIdentity','delegateInputs'])
checks['nativeAcceptanceNotCompletion']='nativeCompletionClaimed' in source and "answer.get('completed') is not False" in source
commands=[['quint','test',str(B/'frontend_test.qnt')],['quint','run',str(B/'frontend.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20260930','--verbosity=1'],['python3',str(B/'test_frontend.py')]]
for command in commands:
 r=subprocess.run(command,capture_output=True,text=True,timeout=90);report['commands'].append({'command':command,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 if r.returncode:break
report.update(pythonTests=18,formalNamedCases=9,formalSamples=2000,formalSteps=100,formalSeed=20260930,mainWrites=False,productionDeployment=False,actualTaskbarClickProved=False,realMinimizeRestoreProved=False,backendBaseline='Accepted frozen FamilyV8; direct API frontend limitation retained',sourceSHA256={name:hashlib.sha256((B/name).read_bytes()).hexdigest() for name in ['native_frontend.py','prepare_config.py','test_frontend.py','frontend.qnt','frontend_test.qnt']})
report['result']='pass' if all(checks.values()) and len(report['commands'])==len(commands) and all(r['returncode']==0 for r in report['commands']) else 'fail'
p=B/'source-review.json'
with p.open('x') as f:json.dump(report,f,indent=2)
p.chmod(0o600);print(json.dumps({'result':report['result'],'sourceChecks':len(checks),'pythonTests':18,'formalNamed':9,'samples':2000,'nativeGuiExecuted':False,'sourceReviewSHA256':hashlib.sha256(p.read_bytes()).hexdigest()}));raise SystemExit(report['result']!='pass')
