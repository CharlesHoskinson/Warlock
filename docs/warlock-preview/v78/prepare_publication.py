"""Prepare bounded feedback publication over the existing public history."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');old=r/'docs/warlock-repository/v55/publication';out=r/'docs/warlock-repository/v56/publication';assert not out.exists();out.mkdir(parents=True)
s=(old/'publish.py').read_text();s=s.replace("BASE='0374bad7c76b9696c8453bbc7cba75437d76ba68'","BASE='e79e5e7dc4027e559444b50f44ddd44f8f19cf52'")
s=s.replace("d2ddb6c3c697787abdccf8d76e763d46ded50f70..","1d5bbecf561cb3ba9b9f8e5ef6cc0556e324b5fe..")
start=s.index('allowed=(');end=s.index('\nassert all(',start)
allowed=['docs/warlock-preview/v77/','docs/warlock-preview/v78/','docs/warlock-repository/v55/publication/','docs/warlock-repository/v56/publication/','openspec/changes/warlock-preview-local-feedback/']+['implementation/warlock-preview-provider-v'+str(n)+'/' for n in range(72,77)]+['implementation/warlock-client-provider-native-v'+str(n)+'/' for n in range(110,115)]
s=s[:start]+'allowed='+repr(tuple(allowed))+s[end:]
# Avoid argument-limit failures without narrowing the exact path inventory.
marker='rows=[]\n';assert s.count(marker)==1
helper="def tree_rows(call,commit,paths):\n ordered=sorted(paths)\n for offset in range(0,len(ordered),400):\n  yield from call(['ls-tree','-rz',commit,'--',*ordered[offset:offset+400]]).split(b'\\0')\n"
s=s.replace(marker,helper+marker)
s=s.replace("source(['ls-tree','-rz',head,'--',*sorted(paths)]).split(b'\\0')","tree_rows(source,head,paths)")
s=s.replace("mirror(['ls-tree','-rz',published,'--',*sorted(paths)]).split(b'\\0')","tree_rows(mirror,published,paths)")
start=s.index(' qualification=json.loads(');end=s.index('\n published=mirror(',start)
replacement=" qualification=json.loads((REPO/'docs/warlock-preview/v78/report.json').read_text());assert qualification['passed'] and qualification['feedbackStates']==413 and qualification['feedbackControls']==110 and qualification['nativeCapacityStatusShown'] and qualification['nativeChecks']>=2419 and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']\n"
message='Show native capacity and expiration in the Elm window picker\n\nCarry actual unissued native admission outcomes through the existing trusted C bridge and shared GTK host into the immutable Elm presenter. Local feedback preserves the original native identity, clock, presentation stamp, request sequence and cutoff, emits no capture or cleanup effects, and cannot consume terminal ownership. Idle demand seeds, monotonic floors, concealment and accessible status markup keep waits distinct from issued jobs. Current full95 build, feedback9 selected cases/21 traces/413 state comparisons, 110 guard/C/Elm controls and original resume79/current receipt/metadata/catalog checks pass. Five native model suites were rerun against current production. Full native114 preserves every stable109 control and qualifies a three-window same-application GUI using the original two-item pool, actual labels, cutoffs, owned URIs and exact normal cleanup on the owning ABI. Failed attempts are retained. Ordinary eligible capture, actual AT/hardware acceptance and all original GUI release gates remain open.\n'
replacement+=' message='+repr(message)+'\n';s=s[:start]+replacement+s[end:];ast.parse(s);(out/'publish.py').write_text(s)
(out/'record_delivery.py').write_text('''import json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=pathlib.Path(__file__).parent;d=json.loads((base/'delivery.json').read_text());assert d['pushCompleted'] and d['ownedFiles']>7000
v=json.loads(subprocess.check_output(['gh','repo','view','CharlesHoskinson/Warlock','--json','name,url,visibility'],text=True));assert v['visibility']=='PUBLIC';(base/'visibility.json').write_text(json.dumps(v,indent=2)+'\\n')
report=json.loads((r/'docs/warlock-preview/v78/report.json').read_text())
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2','implementation/warlock-client-provider-native-v114',['PROGRESS PUBLIC exactowner publication56 '+d['publishedCommit']+' verified '+str(d['ownedFiles'])+' blobs. FullGUI76 typedlocalfeedback full95/new9/413states110controls/legacy79/currentreceiptmetadata/catalog/nativehelperModels newlypassed; native114 fullownABI '+str(report['nativeChecks'])+'/'+str(report['normalOwnedExits'])+'normalclean withactualsameappGUI3 capacity/cutoff/issuedonlyownership/URI/cleanup; alloriginal109stablecontrols preserved. All source/QA/native/publication work terminal atrecord. Next distinctlaterunissuedintent/boundedhistory, ordinaryeligiblesources and all originalS01–S16/S09/recovery/drag/input/hardware/ATIME/resources/journeys/reversibledeployment remain active. Main desktop/drafts/foreignchanges preserved; no fullreleaseclaim.'],'progress',['docs/warlock-preview/v78/report.json','implementation/warlock-preview-provider-v76/component-manifest.json','implementation/warlock-client-provider-native-v114/component-manifest.json','docs/warlock-repository/v56/publication/delivery.json']);print(e)
''')
print(out)
