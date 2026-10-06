"""Prepare exact held serial-registry publication61; mutable GUI86 excluded."""
import ast,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
proof=json.loads((r/'docs/warlock-preview/v86/report.json').read_text())
assert proof['passed'] and proof['boundedCSerialRegistryQualified'] and proof['nativeChecks']==2463 and proof['normalOwnedExits']==277
out=r/'docs/warlock-repository/v61/publication';assert not out.exists();out.mkdir(parents=True)
def put(name,text):ast.parse(text);(out/name).write_text(text)
text=(r/'docs/warlock-repository/v60/publication/publish.py').read_text()
text=text.replace("BASE='ba21f432bdccd8ac82c1e5a461ee6c5b251988cb'","BASE='03582f63a0612b972bf0ad71033e3d4e8b46531b'")
text=text.replace('83e294879448f428b980001ea80d6ea7b1048133..','a0dd6aeca3b8beaa0266b5f535506f1dc5cc06bb..')
allowed=('docs/warlock-preview/v85/','docs/warlock-preview/v86/','docs/warlock-repository/v60/publication/','docs/warlock-repository/v61/publication/','implementation/warlock-preview-provider-v85/','implementation/warlock-client-provider-native-v123/','implementation/warlock-client-provider-native-v124/')
start=text.index('allowed=');end=text.index('\nassert all',start);text=text[:start]+'allowed='+repr(allowed)+text[end:]
start=text.index(' qualification=');end=text.index('\n published=',start)
message='Qualify bounded native window registry with nonreused entry serials\n\nGUI85 full95, original twelve suites, C96 and typed decoder13/25/439states/three unsafe mutants pass. Native124 on exact core16/plugin18/GUI85 passes2463 checks and277 normal owned exits with complete ordered cleanup and all2455 prior122 fixed controls. Preserve failednative123 strict lock-guard race and actual unchanged-C reproduction; correct only parent hold/unlock publication with a validated stable inode, keeping original fixture guard, deadlines and runtime oracles. Native C subjects now use bounded active membership with strictly increasing entry serials instead of vector offsets. Authenticated retirement remains observation-only in this qualified version. Coordinated actor removal, Elm settlement, actual greater-than256-window turnover, ordinary capture and all original GUI release gates remain open; mutableGUI86 is excluded.\n'
text=text[:start]+" qualification=json.loads((REPO/'docs/warlock-preview/v86/report.json').read_text());assert qualification['passed'] and qualification['boundedCSerialRegistryQualified'] and qualification['nativeChecks']==2463 and qualification['normalOwnedExits']==277 and qualification['prior122FixedOrderedControls']==2455 and not qualification['actorTurnoverAccepted'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']\n message="+repr(message)+'\n'+text[end:]
put('publish.py',text)
text=(r/'docs/warlock-repository/v60/publication/record_delivery.py').read_text().replace('warlock-repository/v60','warlock-repository/v61').replace('warlock-preview/v84','warlock-preview/v86').replace('warlock-preview-provider-v84','warlock-preview-provider-v85').replace('warlock-client-provider-native-v122','warlock-client-provider-native-v124')
start=text.index("['PROGRESS PUBLIC exactowner publication60 ");end=text.index(",'progress'",start)
text=text[:start]+"['PROGRESS PUBLIC exactowner publication61 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' blobs. Exact core16/plugin18/GUI85/native124 passed2463/277normal/orderedcleanup, all2455 prior122 fixed controls retained. Full95/original12/C96/decoder13-25-439states-3mutants. Failed123 and actual unchanged strict C lock guard race preserved; stable-inode parent publisher corrected. Next mutableGUI86 aggregate native retirement, Elm settlement and control barrier, actual >256window turnover then ordinary capture and all original release gates. Main desktop/drafts/five foreign tracked changes preserved.']"+text[end:]
# Independent GitHub branch read, as well as ls-remote in publisher.
text=text.replace("report=json.loads", "observed=subprocess.check_output(['gh','api','repos/CharlesHoskinson/Warlock/branches/feature%2Felm','--jq','.commit.sha'],text=True).strip();assert observed==d['publishedCommit']\n(base/'branch.json').write_text(json.dumps({'commit':observed,'verified':True},indent=2)+'\\n')\nreport=json.loads")
put('record_delivery.py',text)
text=(r/'docs/warlock-preview/v84/commit_owned.py').read_text()
text=text.replace('70d888093ee589e48a4b6bd22919e225df0807ed','70c6f9db74e9a70647ee94b5b32f5950f2adde58')
text=text.replace("ownTracked='openspec/changes/warlock-preview-actor-retirement/tasks.md'\nforeign=[p for p in git(['diff','--name-only'],text=True).splitlines() if p!=ownTracked];before={p:sha(r/p) for p in foreign};paths={ownTracked}", "foreign=git(['diff','--name-only'],text=True).splitlines();before={p:sha(r/p) for p in foreign};paths=set()")
text=text.replace("[('warlock-preview-provider-v83',False),('warlock-preview-provider-v84',True),('warlock-client-provider-native-v122',True)]","[('warlock-preview-provider-v85',True),('warlock-client-provider-native-v123',False),('warlock-client-provider-native-v124',True)]")
text=text.replace("[r/'docs/warlock-preview/v84',r/'docs/warlock-repository/v60/publication']", "[r/'docs/warlock-preview/v85',r/'docs/warlock-preview/v86',r/'docs/warlock-repository/v61/publication']")
text=text.replace('Qualify current GUI typed C native retirement observations','Qualify bounded native window registry and strict lock control publication')
ast.parse(text);(r/'docs/warlock-preview/v86/commit_owned.py').write_text(text)
text=(r/'docs/warlock-repository/v60/publication/commit_receipt.py').read_text()
text=text.replace("assert git(['rev-parse','HEAD'],text=True).strip()=='a0dd6aeca3b8beaa0266b5f535506f1dc5cc06bb'", "assert git(['rev-parse','HEAD'],text=True).strip()==d['sourceCommit']")
text=text.replace("d=json.loads((base/'delivery.json').read_text())\n","")
text=text.replace("sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()","sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()\nd=json.loads((base/'delivery.json').read_text())")
text=text.replace("assert d['pushCompleted'] and d['ownedFiles']==8175 and d['sourceCommit']=='a0dd6aeca3b8beaa0266b5f535506f1dc5cc06bb'", "assert d['pushCompleted'] and d['ownedFiles']>1000 and len(d['inventory'])==d['ownedFiles'] and d['priorPublication']=='03582f63a0612b972bf0ad71033e3d4e8b46531b'")
text=text.replace("assert d['publishedCommit']=='03582f63a0612b972bf0ad71033e3d4e8b46531b' and d['remoteObserved']==d['publishedCommit']", "assert d['remoteObserved']==d['publishedCommit'] and json.loads((base/'branch.json').read_text())=={'commit':d['publishedCommit'],'verified':True}")
text=text.replace('Record public typed C native retirement observation qualification','Record public native serial registry qualification')
put('commit_receipt.py',text)
print(out)
