"""Prepare verified native125 freeze with bounded GUI88 retirement/control evidence."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
s=(r/'docs/warlock-preview/v86/freeze_native124.py').read_text().replace('native124','native125').replace('warlock-client-provider-native-v124','warlock-client-provider-native-v125').replace('warlock-preview-provider-v85','warlock-preview-provider-v88').replace('currentGUI85','currentGUI88').replace('docs/warlock-preview/v86/report.json','docs/warlock-preview/v88/report.json')
marker='files={}\n';assert s.count(marker)==1
extra="""prior124=json.loads(pathlib.Path(preflight['retainedNative124Report']).read_text());comparison124=audit.compare(prior124,proof,stable)
assert comparison124['fixedOrderedControls']==2456
assert any(row['name']=='allPriorNative124FixedOrderedAndActualRetryAssertionsRetained' and row['passed'] and row['evidence']==comparison124 for row in proof['checks'])
for field in ['actorRetirementReport','elmRetirementReport','controlPrefixReport','controlAdapterReport']:
 evidence=pathlib.Path(gui[field]);checked=json.loads(evidence.read_text());assert checked['passed']
 for rel,value in checked['inputs'].items():
  file=pathlib.Path(rel);file=file if file.is_absolute() else provider.parent/file;assert sha(file)==value,rel
 for rel,value in checked['artifacts'].items():assert sha(evidence.parent/rel)==value,rel
assert len(proof['checks'])==2464 and len(proof['ownedExitCodes'])==277
"""
s=s.replace(marker,extra+marker)
s=s.replace("'prior118FixedOrderedControls':2437,","'prior124FixedOrderedControls':comparison124['fixedOrderedControls'],'prior118FixedOrderedControls':2437,")
s=s.replace("'retirementCChecks':96,","'retirementCChecks':96,'elmRetirementControls':33,'controlPrefixScenarios':7,'controlPrefixTraces':15,'controlPrefixStates':180,'unsafeControlPrefixMutants':3,'controlAdapterControls':10,'syntheticActorRetirementChecks':9068,'syntheticSequentialSubjects':280,'nativeGuiControlTransportBoundedQualified':True,")
start=s.index(" 'next':");end=s.index("}\n(repo/",start)
s=s[:start]+" 'next':'Publish exact held GUI86/failedGUI87/GUI88/native125 source and evidence, PUBLIC61 receipt72ee067 and additive control/retirement contracts. Fresh GUI89 addresses delayed cross-actor completion without a global delivery order, then trusted native observation/readiness/completion routing and retained completion delivery. Actual continuing native/Elm turnover beyond256, ordinary capture and every original full release gate remain.'"+s[end:]
start=s.index(" ['PROGRESS native125");end=s.index("\n 'progress',",start)
s=s[:start]+" ['PROGRESS native125 exact core16/plugin18/currentGUI88 PASS2464/277normalclean; all2456 prior124 fixed runtime controls and actual allocator trials/deadlines retained. Full95/original12/C96/decoder13-25-439states-3mutants/aggregate9068through280synthetic/Elm33/Cprefix7-15-180states-3mutants/adapter10 held. This qualifies current full GUI control assets and C typed observation path, not actual native/Elm actor removal. GUI89 fresh asynchronous sibling completion fix builds74457; ancestor88 counterexample retained. PUBLIC61 b78826a/receipt72ee067 preserved. Next exactowner publication62 and native ready/completion transport plus actual continuing >256native/Elm; ordinary eligibility and all original release gates remain.'],"+s[end:]
ast.parse(s);(r/'docs/warlock-preview/v88/freeze_native125.py').write_text(s)
