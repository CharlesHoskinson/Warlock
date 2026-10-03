"""Explicit union, selected actual build provenance and bounded runtime manifest."""
from pathlib import Path
import json,os,stat,sys
from io_guard import sha,publish_json,verify,strict
from selection import *
V7=Path('/home/hoskinson/window-behavior-spec/qml-process-provider-v7-fault-projection/current-source-ready-inputs.json')
COMPANION=QA/'process-current-v7-build-provenance-v1/build-provenance-companion.json'
PAIR=QA/'pin-maximized-native-v2/PAIR_READY.json'
CAMPAIGN=QA/'pin-maximized-native-v2/frozen-inputs.json'
def main():
 inputs={};modes={};links={};dirs={};lineage=[]
 def add(path,h=None,mode=None):
  p=Path(path);name=str(p);actual=sha(p);m=stat.S_IMODE(p.stat().st_mode)
  if h is not None and h!=actual or mode is not None and mode!=m:raise ValueError('Declared inherited/build provenance changed: '+name)
  if name in inputs and (inputs[name]!=actual or modes[name]!=m):raise ValueError('Conflicting immutable source union: '+name)
  inputs[name]=actual;modes[name]=m
  for part in [p,*p.parents]:
   if part.is_symlink():
    t=os.readlink(part)
    if str(part)in links and links[str(part)]!=t:raise ValueError('Literal link conflict')
    links[str(part)]=t
 def merge(path):
  row=strict(Path(path).read_bytes());verify(row);add(path);lineage.append(dict(path=str(path),sha256=sha(path),inputs=len(row['inputs']),links=len(row['symlinks'])))
  for p,h in row['inputs'].items():add(p,h,row['inputModes'][p])
  for p,t in row['symlinks'].items():
   if p in links and links[p]!=t:raise ValueError('Ancestral literal link conflict')
   links[p]=t
  for p,m in row.get('directoryModes',{}).items():
   if p in dirs and dirs[p]!=m:raise ValueError('Ancestral directory mode conflict')
   dirs[p]=m
  return row
 base=merge(COMPOSITION/'source-ready-v2.json');assert len(base['inputs'])==1828
 v7=merge(V7);campaign=merge(CAMPAIGN)
 companion=strict(COMPANION.read_bytes());add(COMPANION)
 for p,v in companion['inputs'].items():add(p,v['sha256'],v['mode'])
 for p,t in companion['symlinks'].items():
  if p in links and links[p]!=t:raise ValueError('Actual build companion literal link conflict')
  links[p]=t
 for p in [QA/'popup-composition-root-source-review-v2.json',QA/'review_popup_composition_root_v2.py',QA/'process-terminal-v10-root-component-review-v1.json',QA/'review_process_required_routes_v10.py',QA/'process-current-v7-root-source-review-v1.json',PAIR,CORE_STAGE/'SOURCE_READY.json',CORE_STAGE/'SOURCE_READY_INPUTS.json',QA/'mapping-source-scope-v4-root-source-review-v1.json']:
  add(p)
 build=strict((B/'probe-build-report.json').read_bytes());assert build['result']=='pass'and build['owningCoreHeadersOnly']is True and build['nativeLoaded']is False
 for p,v in build['inputs'].items():add(p,v['sha256'],v['mode'])
 for p,t in build['symlinks'].items():
  if p in links and links[p]!=t:raise ValueError('Probe link conflict')
  links[p]=t
 for p,m in build['directoryModes'].items():dirs[p]=m
 # Selected provider objects, every actual .d, compiler/moc/link and loader proof.
 report_path=PROVIDER_STAGE/'terminal-module-build-v1.json';report=strict(report_path.read_bytes());assert report['result']=='pass';add(report_path)
 for category in ('sources','dependencies','depfiles','objects','tools','outputs'):
  for p,v in report[category].items():add(p,v if type(v)is str else v['sha256'],None if type(v)is str else v['mode'])
 old_payload=strict((QA/'pin-frontend-qa-v1/payload-manifest.json').read_bytes());add(QA/'pin-frontend-qa-v1/private_shell.py');add(QA/'pin-frontend-qa-v1/payload-manifest.json')
 for row in old_payload['copies']:
  add(row['source'],row['sha256']);add(QA/'pin-frontend-qa-v1/payload'/row['relative'],row['sha256'])
 for p,h in old_payload['absoluteAccessibilityImports'].items():add(p,h)
 for p,h in old_payload['generated'].items():add(QA/'pin-frontend-qa-v1/payload'/p,h)
 add(HELPER_STAGE/'pin_config.py');add(HELPER_STAGE/'pin_helper.py',HELPER_SHA);add(HELPER_STAGE/'pin_capture.py',CAPTURE_SHA)
 for name in ('candidate_host.py','host_observation.py','client_closure_binding.py','pair_binding.py','private_output_host.py','run_native.py'):
  add(QA/'pin-maximized-native-v2/proposed'/name)
 for p in [QA/'pin-maximized-native-v2/output_readiness.py',QA/'pin-maximized-native-v2/private-controls.lua',QA/'pin-native-qa-v3/native_cases.py',QA/'pin-native-qa-v3/case_authority.py',QA/'pin-native-qa-v3/input_episode.py',QA/'qa_launch.py',QA/'qa_run.py',QA/'browser-files-flow-v20/main_observer.py',QA/'browser-files-flow-v20/nested-qt.lua',FIXTURE,POINTER,KEYBOARD,WINDOW_PROBE,PROVIDER,PROVIDER_STAGE/'qmldir',QS]:add(p)
 # Qt/QML runtime package spellings are already in the inherited campaign.
 # The helper manifest is the exact accepted V7 source/alias authority union
 # with the selected current build and newly materialized runtime code only.
 runtime=dict(inputs=dict(v7['inputs']),inputModes=dict(v7['inputModes']),symlinks=dict(v7['symlinks']))
 for p in base['inputs']:
  runtime['inputs'][p]=inputs[p];runtime['inputModes'][p]=modes[p]
 for category in ('sources','dependencies','depfiles','objects','tools','outputs'):
  for p in report[category]:runtime['inputs'][p]=inputs[p];runtime['inputModes'][p]=modes[p]
 for p in sorted(B.rglob('*')):
  if p.is_file()and not p.is_symlink()and '__pycache__'not in p.parts and p.name not in ('source-ready.json','process-runtime-inputs.json'):
   add(p);runtime['inputs'][str(p)]=inputs[str(p)];runtime['inputModes'][str(p)]=modes[str(p)]
 for p,t in base['symlinks'].items():
  if p in runtime['symlinks']and runtime['symlinks'][p]!=t:raise ValueError('Runtime source alias conflict')
  runtime['symlinks'][p]=t
 # Aliases for the selected current build are exact, already part of union.
 for name in report['tools']:
  for part in [Path(name),*Path(name).parents]:
   if part.is_symlink():runtime['symlinks'][str(part)]=links[str(part)]
 raw=(json.dumps(runtime,separators=(',',':'),allow_nan=False)+'\n').encode()
 if len(raw)>=16*1024*1024-1024*1024:raise ValueError('Reserve1MiB for actual private source paths within unchanged16MiB Process bound')
 from io_guard import publish
 publish(B/'process-runtime-inputs.json',raw);add(B/'process-runtime-inputs.json')
 cpu=strict((B/'cpu-report.json').read_bytes());assert cpu['result']=='pass'and cpu['sourceStable']is True
 for p,h in cpu['sourceSHA256'].items():
  if sha(p)!=h:raise ValueError('Source changed after actual focused CPU proof: '+p)
 current=dict(inputs=inputs,inputModes=modes,symlinks=links,directoryModes=dirs);verify(current)
 selected=verify_selection();out=dict(schema='pin-private-actual-qs-materialization-source-v1',result='source-ready-awaiting-root-review',**current,lineage=lineage,selection=selected,corePolicyBuild=POLICY,coreSHA256=CORE_SHA,pluginSHA256=PLUGIN_SHA,providerSHA256=sha(PROVIDER),ordinaryHelperSHA256=HELPER_SHA,selectedProbe=dict(path=str(LAYER_PROBE),sha256=sha(LAYER_PROBE),owningHeaders=True,sourceByteExactComposition=True,actualDependencies=len(build['selectedDependencies']),loaded=False),providerWholeBuildAndV7CompanionClosed=True,composition1828Conserved=True,priorFailedCountDescriptorConserved=True,fullCampaignPreflightAndTerminal=True,processRuntimeAuthority=dict(path=str(B/'process-runtime-inputs.json'),sha256=sha(B/'process-runtime-inputs.json'),bytes=len(raw),scope='Accepted V7 source and literal aliases plus current selected objects/tools/dependencies and private runtime copies; excludes unrelated core QA inventory, no mapped unknown code admitted',bound=16*1024*1024,reserveBytes=1024*1024,rootReviewRequired=True),focusedCPU=dict(publicationAndLauncherTests=19,sourceInverseTests=3,QtPositive=False),budgets=dict(helperSeconds=2,workerSeconds=2,epochs=16,receiptSeconds=5,cursorSeconds=3,automaticRetries=0),phaseSelection=dict(coldBaselineHelpers=2,reliabilityQS=2,reliabilitySlots=6,reliabilityHelpers=12,reliabilityRequiresSeparateFiveRouteReview=True),nativeRunnable=False,installedQSPositiveAccepted=False,nonNullPopupAccepted=False,reliabilityAccepted=False,GUI=False,mainChanges=False)
 publish_json(B/'source-ready.json',out);print(json.dumps(dict(path=str(B/'source-ready.json'),sha256=sha(B/'source-ready.json'),inputs=len(inputs),links=len(links),directories=len(dirs),runtimeManifestBytes=len(raw),GUI=False)))
if __name__=='__main__':main()
