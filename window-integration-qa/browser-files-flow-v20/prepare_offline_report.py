from pathlib import Path
import hashlib,json,subprocess,sys
B=Path(__file__).resolve().parent
commands=[['python3',str(B/'test_protocol.py')],['quint','test',str(B/'draft_focus_test.qnt')],['quint','run',str(B/'draft_focus.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20260930','--verbosity=1']]
rows=[]
for command in commands:
 p=subprocess.run(command,capture_output=True,text=True,timeout=30);rows.append({'command':command,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,rows[-1]
for source in B.glob('*.py'):compile(source.read_bytes(),str(source),'exec')
proofs={name:{'sha256':hashlib.sha256((B/name).read_bytes()).hexdigest(),'report':json.loads((B/name).read_text())} for name in ['namespace-report.json','pipe-fd-report-2.json']}
loader=json.loads((B/'loader-closure.json').read_text())
report={'result':'pass','protocolTests':10,'namedFormalScenarios':3,'randomSamples':2000,'randomSteps':100,'requestedSeed':20260930,'actualPipeSubprocessCases':3,'actualNamespaceProbe':True,'nativeGuiExecuted':False,'browserExecuted':False,'commands':rows,'subprocessProofs':proofs,'loader':{'result':loader['result'],'files':len(loader['files']),'symlinks':len(loader['symlinks']),'traces':len(loader['loaderTraces']),'sourceSHA256':hashlib.sha256((B/'loader-closure.json').read_bytes()).hexdigest()},'pythonCompile':True,'nativeFeatureGatesPending':15,'hostGatesPending':10,'qmlLint':'actual exit0 in core1 scope qa-harness-6f14764b7aec4e2a93d2838198ca2d16; syntax parsing only, qs.Commons/unqualified warnings (no QML runtime proof)'}
with (B/'offline-report.json').open('x') as h:json.dump(report,h,indent=2)
print(json.dumps({k:v for k,v in report.items() if k not in ['commands','subprocessProofs']}))
