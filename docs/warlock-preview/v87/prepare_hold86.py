"""Prepare complete bounded native freeze and preserve failed Elm retirement derivative."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
s=(r/'docs/warlock-preview/v85/hold85.py').read_text().replace('warlock-preview-provider-v85','warlock-preview-provider-v86').replace('warlock-preview/v85','warlock-preview/v87').replace('GUI85','GUI86')
s=s.replace("files = {}",'''actor_path=only('qa/actor-retirement-check-v3-*/report.json')
actor=verify(actor_path)
assert actor['checks']==9068 and actor['evidence'][1]['sequentialSubjects']==280
assert not actor['actorTurnoverAccepted'] and not actor['nativeAcceptance'] and not actor['fullReleaseAccepted']
reports['actorRetirementReport']=str(actor_path)
files = {}''')
s=s.replace("'scope': 'Full95 current Elm/native build and all eleven existing regression suites.", "'scope': 'Actual all-native aggregate retirement: C registry, frame/current+predecessor intent, scheduler, Broker, original receiver and journal shrink only after native Retired plus no actual Broker records and exact final ACK. CPU C/socket turnover280 with retained original neighbor:9068checks. This does not qualify real compositor destruction, Elm settlement or full GUI retirement. Full95 current Elm/native build and all twelve existing regression suites.")
s=s.replace('Current explicit bounded C membership and monotonic entry serials compile; native123 qualification and atomic actor turnover remain open;', 'Current aggregate all-native transaction compiles and synthetic own-socket ownership controls pass; real native/Elm turnover qualification remains open;')
s=s.replace("'buildCommands': 95,", "'buildCommands': 95, 'actorRetirementChecks':9068, 'syntheticSequentialSubjects':280, 'actorRetirementReport':str(actor_path),")
s=s.replace("'next': 'Qualify current GUI85/native123 typed C retirement observations on core16/plugin18, preserving all original native121 runtime identities/deadlines, then atomic actor/history retirement beyond256, ordinary capture and all original release gates.'", "'next': 'Fix GUI87 Elm duplicate ACK after readiness and immediate accepted-packet release in fresh GUI88, establish explicit WebKit control continuity, qualify exact full native/Elm turnover and all original release gates.'")
start=s.index("    ['PROGRESS GUI86 held:")
end=s.index("    'progress',",start)
s=s[:start]+"    ['PROGRESS GUI86 held full95, original12 regression suites, selected retirement decoder13/25/439states/3mutants, C96 and aggregate C/socket9068 controls through280 synthetic subjects with retained live neighbor. Exact journals/physical records block erasure until final ACK. Real native/Elm turnover is unaccepted. GUI87 actual compiled replay exposed duplicate ACK emitted after readiness; accepted cache also needs immediate permanent retirement release. Fresh GUI88 fixes these and adds ordered control continuity before native activation. All original gates remain.'],\\n"+s[end:]
(r/'docs/warlock-preview/v87/hold86.py').write_text(s)
