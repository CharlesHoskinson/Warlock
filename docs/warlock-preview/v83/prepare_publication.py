"""Prepare exact-owner native retirement observation publication59."""
import ast, json, pathlib, resource, sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
report=json.loads((repo/'docs/warlock-preview/v83/report.json').read_text());assert report['passed'] and report['nativeIncarnationRetirementObservationBoundedQualified']
out=repo/'docs/warlock-repository/v59/publication';assert not out.exists();out.mkdir(parents=True)
text=(repo/'docs/warlock-repository/v58/publication/publish.py').read_text()
text=text.replace("BASE='5d78ac5941d2639b1ea84fb3d2459441dfbecadc'","BASE='027373f918c5cd94396c3b24dd3e784723c5c3aa'")
text=text.replace('269ec84e9c0cce199363b400127f6a1d61769985..','bc11d4628efce0617f871f2e8c3d03653ddfbe5e..')
allowed=('docs/warlock-preview/v83/','docs/warlock-repository/v58/publication/','docs/warlock-repository/v59/publication/',
 'implementation/warlock-family-style-crop-capture-v18/','implementation/warlock-client-provider-native-v119/',
 'implementation/warlock-client-provider-native-v120/','implementation/warlock-client-provider-native-v121/',
 'implementation/warlock-preview-provider-v82/')
start=text.index('allowed=');end=text.index('\nassert all',start);text=text[:start]+'allowed='+repr(allowed)+text[end:]
start=text.index(' qualification=');end=text.index('\n published=',start)
message='Observe permanent native window incarnation retirement\n\nAdd authenticated native Active/Retired/Future observations from the owner membership table and lifetime monotonic issuance frontier. Preserve minimized/suspended members as Active and expose exact binding/request/subject/native clock/sequence/frontier; no resource or actor history is erased. Module18 compiles against unchanged owning core16 with strong symbol closure. Classifier8 selected cases/20 actual helper traces/438 states/two unsafe native mutants pass. Native121 retains current GUI81 and every original runtime oracle/deadline;2458 checks and276 normal exits pass with real live/minimized/future/foreign/zero/closed/neighborhood observations. Retain all2437 fixed118 ordered controls and separately verify every conditional address reuse trial against its original frame expiry and normal exit; eight unsafe audit mutations are detected. Preserve unlaunched119 preparation, failed120 comparison and GUI82 C-fixture compile failure. GUI82 production retirement decoder/query passed full95 and13 selected decoder cases/25 traces/439 states/three unsafe native mutations; its separate C fixture and successor GUI83 qualification remain open. Native/full release, ordinary capture, proof-safe actor turnover beyond256, accessibility/hardware and original GUI gates remain open.\n'
qualification=" qualification=json.loads((REPO/'docs/warlock-preview/v83/report.json').read_text());assert qualification['passed'] and qualification['nativeIncarnationRetirementObservationBoundedQualified'] and qualification['nativeChecks']==2458 and qualification['normalOwnedExits']==276 and qualification['prior118FixedOrderedControls']==2437 and not qualification['actorTurnoverAccepted'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']\n message="+repr(message)+'\n'
text=text[:start]+qualification+text[end:];ast.parse(text);(out/'publish.py').write_text(text)
text=(repo/'docs/warlock-repository/v58/publication/record_delivery.py').read_text().replace('docs/warlock-preview/v82','docs/warlock-preview/v83').replace('warlock-client-provider-native-v118','warlock-client-provider-native-v121').replace('warlock-preview-provider-v81','warlock-family-style-crop-capture-v18').replace('warlock-repository/v58','warlock-repository/v59')
start=text.index("['PROGRESS PUBLIC exactowner publication58 ");end=text.index(",'progress'",start)
note="['PROGRESS PUBLIC exactowner publication59 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' blobs. Native18 authenticated incarnation retirement observation/core16 strong closure/classifier8/20/438states/2mutants; fullGUI81/native121 '+str(report['nativeChecks'])+'/'+str(report['normalOwnedExits'])+'normalclean live/minimizedActive/future/foreign/zero/closedRetired/liveNeighbor verified, all2437fixed118 +every actual conditional reuse trial originalexpiry/clock/normalexit preserved, comparator8mutants detected. Prepared119/unlaunched and failed120 audit/GUI82 fixture held. Next currentGUI83 typed decoder/Csocket qualification then atomic proof-safe actor/history retirement beyond256 and ordinary eligible capture; all original release gates active. Main desktop/drafts/fiveforeignchanges preserved; no fullreleaseclaim.']"
text=text[:start]+note+text[end:];ast.parse(text);(out/'record_delivery.py').write_text(text)
text=(repo/'docs/warlock-preview/v82/commit_owned.py').read_text()
text=text.replace('50f5e2305d512eead83cda64b0502ef55e25f388','23c4ba2ab193fe16aca5cb81c5bcb4e91209119e')
text=text.replace("[('warlock-preview-provider-v81',True),('warlock-client-provider-native-v117',False),('warlock-client-provider-native-v118',True)]","[('warlock-family-style-crop-capture-v18',True),('warlock-client-provider-native-v119',False),('warlock-client-provider-native-v120',False),('warlock-client-provider-native-v121',True),('warlock-preview-provider-v82',False)]")
old="[r/'docs/warlock-preview/v82',r/'docs/warlock-repository/v58/publication',r/'openspec/changes/warlock-preview-next-resume',r/'openspec/changes/warlock-preview-actor-retirement']"
new="[r/'docs/warlock-preview/v83',r/'docs/warlock-repository/v59/publication']";assert old in text;text=text.replace(old,new)
text=text.replace('Qualify expired waiting preview resumes across native picker leases','Qualify authenticated native window incarnation retirement observations')
ast.parse(text);(repo/'docs/warlock-preview/v83/commit_owned.py').write_text(text)
print(out)
