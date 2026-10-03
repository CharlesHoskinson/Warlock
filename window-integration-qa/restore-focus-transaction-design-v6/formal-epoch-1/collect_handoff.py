import hashlib,json,os,stat
from pathlib import Path
HERE=Path(__file__).resolve().parent;QA=HERE.parent
BASE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-planning-v27')
def stamp(path):return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mode':stat.S_IMODE(path.stat().st_mode)}
def verify_map(rows):
 for path,row in rows.items():
  current=stamp(Path(path));assert current['sha256']==row['sha256'] and current['mode']==row['mode'],path
formal=json.loads((HERE/'formal-before-runtime.json').read_text());focused=json.loads((HERE/'intended/focused-proof.json').read_text())
assert formal['result']=='pass' and formal['named']==45 and focused['result']=='pass' and focused['tests']==20
verify_map(formal['sources']);verify_map(focused['sources'])
for row in formal['checks']:assert row['exitCode']==0 and stamp(Path(row['log']))['sha256']==row['sha256']
assert stamp(Path(focused['log']))==focused['logMaterial']
assert stamp(Path(focused['observations']))==focused['observationMaterial']
conservation=json.loads((HERE/'intended/source-conservation.json').read_text())
assert conservation['result']=='pass' and conservation['wholeFileInverses'] and conservation['originalGuardByteExact']
assert stamp(HERE/'intended/intended.patch')['sha256']==conservation['patchSHA256']
for name,row in conservation['conservation'].items():
 assert stamp(BASE/name)==row['original'];assert stamp(HERE/'intended'/(name+'.proposed'))['sha256']==row['proposedSHA256']
for name in ('lua-guard-fixture.json','raw-echo-forgery-replay.json'):
 assert json.loads((HERE/'intended'/name).read_text())['result']=='pass'
paths=set(path for path in HERE.rglob('*') if path.is_file() and path.name!='source-handoff.json')
for version in range(1,6):paths.update(path for path in (QA/('restore-focus-transaction-design-v'+str(version))).rglob('*') if path.is_file())
for path in (QA/'restore-focus-interactive-cli-cpu-v1').rglob('*'):
 if path.is_file():paths.add(path)
for name in ('native_desktop.py','owned_commands.py','scene_controller.py','native_runtime.py','owned_launch.py','helper_supervisor.py','helper_keeper.py','service_runtime.py','scene_manager.py','readonly_ipc.py','recovery_runtime.py','production_motion_6d9.py','family_order.py','manifest-restore-planning-v27.json'):
 paths.add(BASE/name)
for path in [QA/'family-preparation-thumbnail-v13/frozen-inputs.json',QA/'family-preparation-thumbnail-v13/attempt-baseline-1/report.json',QA/'thumbnail-v13-root-failure-audit-v1.json',QA/'thumbnail-v13-agent-causal-replay-v1/report.json',QA/'family-preparation-thumbnail-v13/payload/home/.config/omarchy/plugins/hoskinson.windows/widget_v65/Windows.qml',QA/'family-preparation-thumbnail-v13/payload/omarchy/shell/Ui/BarWidget.qml']:
 paths.add(path)
for row in json.loads((QA/'thumbnail-v13-agent-causal-replay-v1/report.json').read_text()).get('inputs',{}):
 if Path(row).is_file():paths.add(Path(row))
inputs={str(path):stamp(path) for path in sorted(paths)}
row={'result':'ready-for-root-source-review','runtimeApplied':False,'nativeAcceptance':False,'GUIStarted':False,'timingAcceptance':False,
 'design':str(HERE),'contract':str(HERE/'CONTRACT.md'),'sourceMapping':str(HERE/'SOURCE_MAPPING.md'),
 'patch':str(HERE/'intended/intended.patch'),'patchSHA256':conservation['patchSHA256'],'changedProductFiles':list(conservation['conservation']),
 'formal':{'report':str(HERE/'formal-before-runtime.json'),'named':45,'samples':2000,'steps':100},
 'focused':{'report':str(HERE/'intended/focused-proof.json'),'tests':20,'actualOwnedCPUConversations':9,'nativeLuaExecuted':False},
 'luaFixture':{'report':str(HERE/'intended/lua-guard-fixture.json'),'cases':7,'nativeLuaExecuted':False},
 'rawEchoForgery':str(HERE/'intended/raw-echo-forgery-replay.json'),'wholeOriginalFileInverses':True,'originalGuardByteExact':True,
 'originalBaseline38Fault34BudgetsUnchanged':True,'originalObserverRequiredWithoutProfiler':True,'fullOriginalSuiteNotRun':True,
 'durability':'Memory intent becomes durable via existing Keeper->NativeFactory->RuntimeService.persist->JournalStore file+directory fsync; actual fresh client-query publications attach real job link before first stdin. See SOURCE_MAPPING.',
 'sourceCorrespondenceOnly':True,'compilerReproducibilityProven':False,'inputs':inputs,'inputCount':len(inputs)}
with os.fdopen(os.open(HERE/'source-handoff.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as stream:json.dump(row,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
verify_map(inputs)
print(json.dumps({'result':row['result'],'path':str(HERE/'source-handoff.json'),'sha256':stamp(HERE/'source-handoff.json')['sha256'],'inputs':len(inputs),'patchSHA256':row['patchSHA256']}))
