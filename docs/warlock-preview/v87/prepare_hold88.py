"""Prepare full current GUI88 component closure without native release claims."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');out=r/'docs/warlock-preview/v88';out.mkdir(exist_ok=True)
s=(r/'docs/warlock-preview/v87/hold86-v2.py').read_text().replace('warlock-preview-provider-v86','warlock-preview-provider-v88').replace('warlock-preview/v87','warlock-preview/v88').replace('GUI86','GUI88')
s=s.replace('files = {}',"""elm_path=only('qa/elm-retirement-check-*/report.json');elm=verify(elm_path);assert elm['evidence']['checks']==33
prefix_path=only('qa/control-prefix-check-v3-*/report.json');prefix=verify(prefix_path);assert prefix['namedScenarios']==7 and len(prefix['coupledTraces'])==15 and prefix['statesCompared']==180 and prefix['unsafeMutantsDetected']==3
adapter_path=only('qa/control-adapter-check-*/report.json');adapter=verify(adapter_path);assert adapter['evidence']['checks']==10
reports.update(elmRetirementReport=str(elm_path),controlPrefixReport=str(prefix_path),controlAdapterReport=str(adapter_path))
files = {}""")
start=s.index("    'scope': ");end=s.index("\n}, indent=2)",start)
s=s[:start]+"    'scope': 'Actual aggregate-native C/socket retirement9068 checks through280 synthetic subjects with original neighbor. Full current GUI88 build95, all original12 regression suites, typed retirement decoder13/25/439states/three mutants and C96. Elm33 controls verify exact settlement, readiness after ACK, no further controls afterReady, immediate accepted-packet release and native-clock replay cutoff. Actual C control prefix7 selected/15coupled/180states/three unsafe mutations plus actual popup adapter10 controls. Real WebKit/native retirement activation, captured physical retirement and continuing native/Elm turnover remain unqualified; ordinary eligibility and every original release gate remain open.'"+s[end:]
s=s.replace("'buildCommands': 95,", "'buildCommands': 95, 'elmRetirementControls':33, 'controlPrefixScenarios':7, 'controlPrefixTraces':15, 'controlPrefixStates':180, 'unsafeControlPrefixMutants':3, 'controlAdapterControls':10,")
start=s.index("    'next': ");end=s.index("\n}, indent=2)",start)
s=s[:start]+"    'next': 'Qualify full current GUI88/core16/plugin18 through fresh serialized native125 preserving every original124 oracle/deadline. Integrate exact own native retirement observation/readiness/completion routing in a fresh derivative; qualify actual continuing native/Elm turnover beyond256 and all original release gates.'"+s[end:]
start=s.index("    ['PROGRESS GUI88 held");end=s.index("    'progress',",start)
s=s[:start]+"    ['PROGRESS GUI88 held full95/original12/C96/decoder13-25-439states-3mutants/aggregate9068 through280 synthetic subjects, Elm33, Cprefix7-15-180states-3mutants and adapter10. FailedGUI87 duplicate ACK after readiness and early fixture/model failures preserved. Fresh native125 on exact unchanged owning core16/plugin18 must retain all original124 runtime gates. Native retirement observation/readiness/completion routing and real continuing native/Elm turnover remain unqualified; ordinary capture and all full release gates remain open.'],\n"+s[end:]
ast.parse(s);(out/'hold88.py').write_text(s)
