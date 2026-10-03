"""Source-only union: ancestry, exact actual build and focused CPU evidence."""
from pathlib import Path
import hashlib,json,os,stat,re
B=Path(__file__).resolve().parent;QA=B.parent
PLAN=Path('/home/hoskinson/window-behavior-spec/process-private-qs-route-plan-v1/source-plan-handoff.json')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mode(p):return stat.S_IMODE(Path(p).stat().st_mode)
def add_file(inputs,modes,p):
 p=Path(p);name=str(p);h=sha(p);m=mode(p)
 if name in inputs and (inputs[name]!=h or modes[name]!=m):raise RuntimeError('Source union disagreement: '+name)
 inputs[name]=h;modes[name]=m
def main():
 old=json.loads(PLAN.read_text());inputs=dict(old['inputs']);modes=dict(old['inputModes']);links=dict(old.get('symlinks',{}))
 assert all(sha(p)==h and mode(p)==modes[p]for p,h in inputs.items())
 for p in [PLAN,QA/'process-private-qs-plan-root-source-grant-v1.json']:add_file(inputs,modes,p)
 a2=json.loads((QA/'pin-input-episode-v2-component-handoff-v1.json').read_text())
 for p,v in a2['componentSources'].items():
  assert sha(p)==v['sha256'] and mode(p)==v['mode'];add_file(inputs,modes,p)
 build=json.loads((B/'probe-build-report.json').read_text());assert build['result']=='pass'and build['nativeLoaded']is False
 for p,v in build['inputs'].items():
  assert sha(p)==v['sha256']and mode(p)==v['mode'];add_file(inputs,modes,p)
 for p,target in build['symlinks'].items():
  assert Path(p).is_symlink()and os.readlink(p)==target
  if p in links:assert links[p]==target
  links[p]=target
 for name in ['formal-composition-v2-before-source.json','formal-composition-v3-before-source.json','cpu-report.json','cpu-receipt-loop-v2-report.json','qml-js-v2-cpu-report.json','source-conservation-report.json']:
  r=json.loads((B/name).read_text());assert r['result']=='pass'
  if 'sourceSHA256'in r:assert all(sha(p)==h for p,h in r['sourceSHA256'].items())
  if name.startswith('formal-'):assert all(sha(p)==v['sha256']and mode(p)==v['mode']for p,v in r['inputs'].items())
 for p in sorted(B.rglob('*')):
  if p.is_file()and not p.is_symlink()and '__pycache__'not in p.parts and p.name!='source-ready-v2.json':add_file(inputs,modes,p)
 row={'schema':'pin-frontend-full-popup-layer-composition-source-v2','result':'source-ready-awaiting-root-review','stage':str(B),'inputs':inputs,'inputModes':modes,'symlinks':links,
  'inheritedPlan1518Exact':True,'originalA2WindowTokenComponentExact':True,'V8ProviderRegistryHelpersUnchanged':True,
  'formalBeforeImplementation':{'initialNamed':23,'refinedNamed':24,'randomSamples':2000,'steps':100,'models':1,'sourceRefinement':'Actual provider permits content==nativeRoot'},
  'focusedCPU':{'unprojectedDecoderControllerTests':int(re.search(r'Ran (\d+) tests?',json.loads((B/'cpu-report.json').read_text())['stderr']).group(1)),'additionalOriginalReceiptLoopTests':1,'exactQMLFunctionJavaScriptChecks':6,'sourceInverseChecks':48,'controlledDataNotNativeAuthority':True},
  'build':{'path':str(B/'probe-build-report.json'),'sha256':sha(B/'probe-build-report.json'),'actualNewProbeCompiled':True,'depfileDependencies':len(build['selectedDependencies']),'neverLoaded':True,'unchangedModuleNotRebuilt':True},
  'budgets':{'helperSeconds':2,'workerSeconds':2,'maximumFreshEpochs':16,'receiptWaitSeconds':5,'cursorWaitSeconds':3,'automaticRetries':0},
  'installedQSPositiveAccepted':False,'nonNullPopupAccepted':False,'actualInputDeliveryAccepted':False,'reliabilityAccepted':False,'nativeRunnable':False,'GUI':False,'mainChanges':False,
  'supersedesCountOnly':{'path':str(B/'source-ready.json'),'sha256':sha(B/'source-ready.json'),'reason':'Initial descriptor said29 decoder tests; actual28 plus1 separate receipt-loop case. Runtime/model/CPU sources and results unchanged.'},
  'nextGate':'Root source union/diff review and exact private pair/materialization wrapper before root-only GUI grant'}
 path=B/'source-ready-v2.json';assert not path.exists();raw=(json.dumps(row,indent=2)+'\n').encode();fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 try:
  view=memoryview(raw)
  while view:
   n=os.write(fd,view)
   if n<=0:raise OSError('Full ready publication failed')
   view=view[n:]
  os.fsync(fd)
 finally:os.close(fd)
 fd=os.open(B,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:os.fsync(fd)
 finally:os.close(fd)
 print(json.dumps({'path':str(path),'sha256':sha(path),'inputs':len(inputs),'symlinks':len(links),'GUI':False}))
if __name__=='__main__':main()
