"""Read-only conservation/hash capture plus exclusive source-plan publication.

No model, compilation, QObject, helper, GUI, IPC, or desktop action is run.
"""
from pathlib import Path
import hashlib,json,os,stat

B=Path(__file__).resolve().parent
QA=Path('/home/hoskinson/window-integration-qa')
SPEC=Path('/home/hoskinson/window-behavior-spec')
HANDOFF=QA/'process-terminal-v10-required-components-actual-handoff-v1.json'
ROOT_REVIEW=QA/'process-terminal-v10-root-component-review-v1.json'
ROOT_TOOL=QA/'review_process_required_routes_v10.py'

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def stamp(path):return stat.S_IMODE(Path(path).stat().st_mode)
def publish(path,value):
 raw=(json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 try:
  view=memoryview(raw)
  while view:
   n=os.write(fd,view)
   if n<=0:raise OSError('Full source-plan publication failed')
   view=view[n:]
  os.fsync(fd)
 finally:os.close(fd)
 fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:os.fsync(fd)
 finally:os.close(fd)

old=json.loads(HANDOFF.read_text())
inputs=dict(old['inputs']);modes=dict(old['inputModes']);links=dict(old.get('symlinks',{}))
errors=[]
for p,h in inputs.items():
 try:
  if digest(p)!=h or stamp(p)!=modes[p]:errors.append({'path':p,'error':'Inherited hash/mode differs'})
 except Exception as e:errors.append({'path':p,'error':repr(e)})
for p,target in links.items():
 try:
  if not Path(p).is_symlink() or os.readlink(p)!=target:errors.append({'path':p,'error':'Inherited link differs'})
 except Exception as e:errors.append({'path':p,'error':repr(e)})
if errors:
 publish(B/'source-conservation-failure.json',{'errors':errors,'accepted':False});raise SystemExit('Inherited source-plan lineage refused')
selected=[HANDOFF,ROOT_REVIEW,ROOT_TOOL,
 QA/'process-terminal-v9-root-component-review-v1.json',
 QA/'process-current-v7-root-source-review-v1.json',
 QA/'process-terminal-v8-first-failure-root-audit-v1.json',
 QA/'popup-v5-root-source-review-v1.json',
 QA/'pin-input-episode-v2-component-handoff-v1.json']
selected += list(B.glob('*.md'))+[Path(__file__).resolve()]
selected += [QA/'pin-frontend-qa-v1'/n for n in
 ('CONTRACT.md','SOURCE_HANDOFF.md','ENGINE_SCOPE_REVIEW.md','FRONTEND_OBSERVATION_CONTRACT.md',
  'frontend_case.qnt','frontend_authority.py','frontend_cases.py','private_shell.py','helper_setup.py','helper_observer.py','native_authority.py','native-probe/probe.cpp')]
selected += [SPEC/'qml-process-provider-v8-terminal-retire'/n for n in
 ('KnownQuickshell.hpp','Provider.hpp','Provider.cpp','Popup.cpp','Seal.cpp','NativeProcess.cpp','NativeProcess.hpp','ProcessRegistry.cpp','ProcessKernel.cpp','MappingBatch.cpp','qmldir',
  'frontend/PinWindowMenu.qml','frontend/Windows.qml','frontend/TaskbarPopup.qml','frontend/PinMenu.js')]
selected += [SPEC/'pin-lifetime-v3/frontend'/n for n in ('pin_config.py','pin_helper.py','pin_capture.py')]
selected += [QA/'pin-native-qa-v2'/n for n in ('input_episode.py','INPUT_EPISODE_CONTRACT.md')]
for p in selected:
 h=digest(p);mode=stamp(p);name=str(p)
 if name in inputs and (inputs[name]!=h or modes[name]!=mode):raise RuntimeError('Selected inherited source drift: '+name)
 inputs[name]=h;modes[name]=mode
report={
 'schema':'private-installed-qs-pin-route-source-plan-v1',
 'stage':str(B),'result':'source-plan-only-awaiting-root-review',
 'inputs':inputs,'inputModes':modes,'symlinks':links,
 'v10Handoff':{'path':str(HANDOFF),'sha256':digest(HANDOFF),'allInputsConserved':len(old['inputs'])},
 'v10IndependentReview':{'path':str(ROOT_REVIEW),'sha256':digest(ROOT_REVIEW),'tool':str(ROOT_TOOL),'toolSHA256':digest(ROOT_TOOL)},
 'sourceCompositionGaps':['Full actual popup tuple replaces weak epoch/reader booleans',
  'Fresh layer/Seat episode replaces intent-only release; A2 window-token routes remain exact'],
 'plannedReliability':{'slots':6,'quickshellLifetimes':2,'helpersPerSlot':2,'helperTransactions':12,
  'helperSeconds':2,'workerSeconds':2,'maximumFreshEpochs':16,'receiptWaitSeconds':5,
  'automaticRetries':0,'actualAccepted':False},
 'execution':{'builds':0,'modelRuns':0,'componentRuns':0,'helpers':0,'guiLaunches':0,'mainChanges':False},
 'installedQSPositiveAccepted':False,'nonNullPopupAccepted':False,'reliabilityAccepted':False,
 'nativeRunnable':False,'rootNativeGrant':False,
 'nextGate':'Root source-plan review, then narrow composition model/source and exact private wrapper/pair closure before any GUI grant'}
publish(B/'source-plan-handoff.json',report)
print(json.dumps({'path':str(B/'source-plan-handoff.json'),'sha256':digest(B/'source-plan-handoff.json'),
 'inputs':len(inputs),'inheritedInputsConserved':len(old['inputs']),'selectedSourceReads':len(selected),
 'builds':0,'modelRuns':0,'guiLaunches':0}))
