"""Prepare exact-owner current C/native retirement observation publication60."""
import ast,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
report=json.loads((repo/'docs/warlock-preview/v84/report.json').read_text());assert report['passed'] and report['typedNativeRetirementObservationBoundedQualified']
out=repo/'docs/warlock-repository/v60/publication';assert not out.exists();out.mkdir(parents=True)
text=(repo/'docs/warlock-repository/v59/publication/publish.py').read_text()
text=text.replace("BASE='027373f918c5cd94396c3b24dd3e784723c5c3aa'","BASE='ba21f432bdccd8ac82c1e5a461ee6c5b251988cb'")
text=text.replace('bc11d4628efce0617f871f2e8c3d03653ddfbe5e..','83e294879448f428b980001ea80d6ea7b1048133..')
allowed=('docs/warlock-preview/v84/','docs/warlock-repository/v59/publication/','docs/warlock-repository/v60/publication/',
 'implementation/warlock-preview-provider-v83/','implementation/warlock-preview-provider-v84/',
 'implementation/warlock-client-provider-native-v122/','openspec/changes/warlock-preview-actor-retirement/tasks.md')
start=text.index('allowed=');end=text.index('\nassert all',start);text=text[:start]+'allowed='+repr(allowed)+text[end:]
start=text.index(' qualification=');end=text.index('\n published=',start)
message='Qualify typed native retirement observations through the current GUI bridge\n\nCurrent GUI84 full95, all original regressions, 13 selected decoder cases/25 implementation traces/439 states/three unsafe decoder mutations, and five actual C/socket modes96 controls pass. Preserve failedGUI83 receiver-fixture and early-cleanup leak evidence. Native122 on exact core16/plugin18/currentGUI84 passes2462 checks and277 normal owned exits with complete ordered cleanup. Real own C/bootstrap/socket/ImportedClients observes Active then permanently Retired after native destruction and an unaffected Active neighbor; exact lifetime/binding/clock and monotonic sequence/time/frontier remain. Original jobs, reservations and journal survive observations, then drain only by exact terminal proof and final C ACK. Retain every original121 runtime oracle/deadline and validate each real allocator reuse trial. Update the additive retirement task evidence. Actor removal, Elm retirement settlement, actual turnover beyond256, ordinary preview eligibility and all original GUI release gates remain open. Mutable GUI85 entry-serial work is separate and excluded.\n'
qualification=" qualification=json.loads((REPO/'docs/warlock-preview/v84/report.json').read_text());assert qualification['passed'] and qualification['typedNativeRetirementObservationBoundedQualified'] and qualification['nativeChecks']==2462 and qualification['normalOwnedExits']==277 and qualification['retirementCChecks']==96 and not qualification['actorTurnoverAccepted'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']\n message="+repr(message)+'\n'
text=text[:start]+qualification+text[end:];ast.parse(text);(out/'publish.py').write_text(text)
text=(repo/'docs/warlock-repository/v59/publication/record_delivery.py').read_text().replace('docs/warlock-preview/v83','docs/warlock-preview/v84').replace('warlock-client-provider-native-v121','warlock-client-provider-native-v122').replace('warlock-family-style-crop-capture-v18','warlock-preview-provider-v84').replace('warlock-repository/v59','warlock-repository/v60')
start=text.index("['PROGRESS PUBLIC exactowner publication59 ");end=text.index(",'progress'",start)
note="['PROGRESS PUBLIC exactowner publication60 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' blobs. Exact core16/plugin18/currentGUI84/native122 '+str(report['nativeChecks'])+'/'+str(report['normalOwnedExits'])+'normalclean real typed C/bootstrap/socket Active/Retired/liveNeighbor with original reservations and exact final terminal ACKs. Current full95/original regressions/decoder13/25/439states/3mutants/C96 pass; failed83 preserved. Next mutableGUI85 serial registry build66449 then atomic proof-safe actor/history/Elm retirement beyond256 and ordinary capture; all original release gates active. Main desktop/drafts/fiveforeignchanges preserved; no fullreleaseclaim.']"
text=text[:start]+note+text[end:];ast.parse(text);(out/'record_delivery.py').write_text(text)
text=(repo/'docs/warlock-preview/v83/commit_owned.py').read_text()
text=text.replace('23c4ba2ab193fe16aca5cb81c5bcb4e91209119e','70d888093ee589e48a4b6bd22919e225df0807ed')
old="[('warlock-family-style-crop-capture-v18',True),('warlock-client-provider-native-v119',False),('warlock-client-provider-native-v120',False),('warlock-client-provider-native-v121',True),('warlock-preview-provider-v82',False)]"
new="[('warlock-preview-provider-v83',False),('warlock-preview-provider-v84',True),('warlock-client-provider-native-v122',True)]";assert old in text;text=text.replace(old,new)
text=text.replace("foreign=git(['diff','--name-only'],text=True).splitlines();", "ownTracked='openspec/changes/warlock-preview-actor-retirement/tasks.md'\nforeign=[p for p in git(['diff','--name-only'],text=True).splitlines() if p!=ownTracked];")
text=text.replace("paths=set()","paths={ownTracked}")
text=text.replace("[r/'docs/warlock-preview/v83',r/'docs/warlock-repository/v59/publication']", "[r/'docs/warlock-preview/v84',r/'docs/warlock-repository/v60/publication']")
text=text.replace('Qualify authenticated native window incarnation retirement observations','Qualify current GUI typed C native retirement observations')
ast.parse(text);(repo/'docs/warlock-preview/v84/commit_owned.py').write_text(text);print(out)
