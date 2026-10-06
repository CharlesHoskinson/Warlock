"""Prepare exact current native128 freeze and source/ABI report."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');out=pathlib.Path(__file__).parent/'freeze_native128.py';assert not out.exists()
s=(repo/'docs/warlock-preview/v89/freeze_native126.py').read_text().replace('warlock-client-provider-native-v126','warlock-client-provider-native-v128').replace('warlock-preview-provider-v89','warlock-preview-provider-v92').replace('docs/warlock-preview/v89','docs/warlock-preview/v91')
s=s.replace("assert len(proof['checks'])==2465 and len(proof['ownedExitCodes'])==277", "prior126=json.loads(pathlib.Path(preflight['retainedNative126Report']).read_text());comparison126=audit.compare(prior126,proof,stable)\nassert comparison126['fixedOrderedControls']==2458\nassert any(row['name']=='allPriorNative126FixedOrderedAndActualRetryAssertionsRetained' and row['passed'] and row['evidence']==comparison126 for row in proof['checks'])\nassert len(proof['checks'])==2466+comparison126['current']['actualAttemptChecks']-2 and len(proof['ownedExitCodes'])==277+comparison126['current']['attempts']-1")
old=" evidence=pathlib.Path(gui[field]);checked=json.loads(evidence.read_text());assert checked['passed']"
# Three omitted legacy reference keys are derived and hashed by preflight;
# reference the unchanged held evidence through that recorded adapter.
start=s.index("for field in ['asynchronousRetirementReport'");end=s.index('\nfiles={}',start)
part=s[start:end];assert part.count(old)==1
part=part.replace(old," evidence=pathlib.Path(preflight[field]);checked=json.loads(evidence.read_text());assert checked['passed']")
part+="""\nfor field in ['retainedDeliveryReport','retainedDeliveryModelReport','retainedDeliveryElmMutantsReport','retainedDeliveryNativeElmReport']:
 evidence=pathlib.Path(gui[field]);checked=json.loads(evidence.read_text());assert checked['passed']
 for rel,value in checked['inputs'].items():
  file=pathlib.Path(rel);file=file if file.is_absolute() else provider.parent/file;assert sha(file)==value,rel
 for rel,value in checked.get('artifacts',{}).items():assert sha(evidence.parent/rel)==value,rel
"""
s=s[:start]+part+s[end:]
start=s.index('report.update(');end=s.index("\n(repo/'docs/warlock-preview/v91/report.json')",start)
s=s[:start]+"report.update(prior125FixedOrderedControls=2457,prior126FixedOrderedControls=comparison126['fixedOrderedControls'],asynchronousRetirementControls=9,asynchronousRetirementScenarios=10,asynchronousRetirementTraces=30,asynchronousRetirementStates=641,unsafeAsynchronousModelMutants=3,unsafeAsynchronousElmMutants=3,retainedDeliveryControls=45,retainedDeliveryScenarios=14,retainedDeliveryTraces=34,retainedDeliveryStates=667,unsafeRetainedDeliveryModelMutants=3,unsafeRetainedDeliveryElmMutants=3,retainedNativeElmControls=48,next='Qualified heldGUI92/native128 on unchanged exactcore16/plugin18, preserving all original126 controls and allocator/expiry oracles. FreshGUI93 retains one-shot ready while native receiver/physical/proof gates block; compile and couple exact native polling without another Elm effect. Actual shared-host reliable outgoing control and retirement/completion routing, captured retirement, >256 real windows, ordinary capture and all original release gates remain open. Public63 bc6dfc11 verified; current bounded qualification awaits publication64.')"+s[end:]
start=s.index(" ['PROGRESS native126");end=s.index("\n 'progress'",start)
s=s[:start]+" ['PROGRESS currentGUI92/native128 exactcore16/plugin18 passed current native campaign with normal exits/complete cleanup and all2458prior126fixed controls; actual allocator trial counts verified without changing expiry. GUI92 full95/alloriginal12/legacy retirement/control regression, retained45/14selected/34actualElmtraces/667state-command comparisons/3model+3compiledElm mutants and48CnativeElm loss/ACK/neighbor/close/normalexit controls held. Failed native127 preflight reference omission retained without launching native. FreshGUI93 one-shot readiness retention/poll pending qualification. PUBLIC63 verified; prepare publication64 of qualified92/native128, held91/failed127 and contracts; actual host/transport/captured resources/realwindows/full release gates remain.'],"+s[end:]
ast.parse(s);out.write_text(s);print(out)
