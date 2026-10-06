"""Prepare full GUI92 closure; preserve original GUI89 qualification assertions."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');out=pathlib.Path(__file__).parent/'hold92.py';assert not out.exists()
s=(repo/'docs/warlock-preview/v89/hold89.py').read_text().replace('warlock-preview-provider-v89','warlock-preview-provider-v92').replace('docs/warlock-preview/v89','docs/warlock-preview/v91')
start=s.index("ancestor=only(");end=s.index('\nfiles = {}',start)
s=s[:start]+'''channel_path=only('qa/retirement-delivery-check-*/report.json');channel=verify(channel_path);assert channel['evidence']['checks']==45
delivery_path=only('qa/retirement-delivery-model-check-*/report.json');delivery=verify(delivery_path)
assert delivery['namedScenarios']==14 and delivery['invariantSamples']==300 and delivery['unsafeModelMutantsDetected']==3
assert len(delivery['evidence']['coupledTraces'])==34 and delivery['evidence']['statesCompared']==667
delivery_mutant_path=only('qa/retirement-delivery-elm-mutants-*/report.json');delivery_mutants=verify(delivery_mutant_path)
assert delivery_mutants['unsafeCompiledElmMutantsDetected']==3 and all(row['compiled'] and row['observableMismatch'] for row in delivery_mutants['mutants'])
roundtrip_path=only('qa/retirement-native-elm-check-v3-*/report.json');roundtrip=verify(roundtrip_path)
assert roundtrip['evidence']['checks']==18 and roundtrip['evidence']['nativeCChecks']==30 and roundtrip['evidence']['normalOwnedExit']
for failed_pattern in ['qa/retirement-native-elm-check-[0-9]*/report.json','qa/retirement-native-elm-check-v2-*/report.json']:
    failed_path=only(failed_pattern);failed=json.loads(failed_path.read_text());assert not failed['passed']
    for rel,value in failed['inputs'].items():assert sha(root/rel)==value,rel
    for rel,value in failed['artifacts'].items():assert sha(failed_path.parent/rel)==value,rel
reports.update(retainedDeliveryReport=str(channel_path),retainedDeliveryModelReport=str(delivery_path),retainedDeliveryElmMutantsReport=str(delivery_mutant_path),retainedDeliveryNativeElmReport=str(roundtrip_path))
regressions=only('../../docs/NO-SUCH-PATTERN') if False else repo/'docs/warlock-preview/v91/regressions92-1791326662431424853/report.json'
assert json.loads(regressions.read_text())['passed']
reports['originalRegressionReport']=str(regressions)
'''+s[end:]
start=s.index("    'scope': 'Actual aggregate-native");end=s.index('\n}, indent=2)',start)
s=s[:start]+"    'scope': 'Current GUI92 full95/all original12 and all original retirement/control regressions. Retained processing channel45 controls and14 selected Quint scenarios/34 compiled Elm traces/667 state-command comparisons with3 precise model and3 separately compiled Elm mutants. Actual C/socket/native/Elm round trip18 frontend and30 C checks: original request/cancellation/proofs/ACK/readiness, lost final and lost processing ACK, exact retained neighbor, close barrier and normal exit. Synthetic native retirement and untouched reservations; actual WebKit retained routing, captured resources and continuing real native windows remain unqualified. Original S01-S16 and all release gates remain open.'"+s[end:]
s=s.replace("'next': 'Qualify full current GUI89/core16/plugin18 through fresh serialized native126 preserving every original124 oracle/deadline. Integrate exact own native retirement observation/readiness/completion routing in a fresh derivative; qualify actual continuing native/Elm turnover beyond256 and all original release gates.'", "'retainedDeliveryControls':45,'retainedDeliveryScenarios':14,'retainedDeliveryTraces':34,'retainedDeliveryStates':667,'unsafeRetainedDeliveryModelMutants':3,'unsafeRetainedDeliveryElmMutants':3,'retainedNativeElmControls':48,'next':'Qualify current GUI92 on exact unchanged core16/plugin18 through native127 preserving every original126 gate. FreshGUI93 must retain typed native channel/observations/readiness/final retry and outgoing control delivery liveness in actual shared host; real >256-window turnover and all original release gates remain.'")
start=s.index("    ['PROGRESS GUI89 held");end=s.index("\n    'progress'",start)
s=s[:start]+"    ['PROGRESS heldGUI92 full95/all original12/legacy retirement and prefix regressions; retained45/14selected/34actualElmtraces/667state-command comparisons/3model+3compiledElm mutants, actualCnativeElm48controls/normalexit/lostfinal/lostACK/neighbor/closebarrier. Native127 exact core16/plugin18 must preserve all original126 gates. FreshGUI93 actual host/channel routing and reliable outgoing transport; real windows/capture and all original GUI gates remain.'],"+s[end:]
ast.parse(s);out.write_text(s);print(out)
