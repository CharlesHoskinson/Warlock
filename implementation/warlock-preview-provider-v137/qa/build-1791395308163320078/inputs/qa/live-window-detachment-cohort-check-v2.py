"""Actual original Bootstrap receipt detach/reattach through strict C close."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('live-window-detachment-cohort-check-v2-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]+[str(pathlib.Path(__file__).relative_to(root))]
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual controlled C owners and one original Bootstrap reused across two settled realm epochs, its own ReceiptDelivery channels, original synthetic authenticated Native socket/Endpoint/Broker/permanent-incarnation retirement/final processing/independent-confirmation close. Each original refused close retains borrowed delivery. A different actual Native Bootstrap refuses before settled owner mutation. Strict owning close releases receipt before Endpoint destruction; later lookup/poll refuse safely, next original realm attaches new channel on unchanged binding. No live-window detachment/actual Core/WebKit acceptance.'}
def run(name,args,cwd=None,required=True):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']).stdout)
 args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/live-window-detachment-cohort-test-v2.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags]
 run('compile',args);e=json.loads(run('actual-scoped-detachment-and-live-subject-reenrollment',[str(out/'checks')]).stdout);assert e['passed'] and e['normalOwnedExit'] and e['actualColdZeroFloor'] and e['actualMixedDomains'] and e['oneCandidatePerPoll']
 assert all(sha(root/rel)==v for rel,v in report['inputs'].items())
 report.update(passed=True,evidence=e,actualSyntheticNativeActiveFact=True,actualWaylandWindowAcceptance=False,scope='Actual controlled C/Bootstrap/Native socket/Endpoint/Broker scoped detached completion/final processing/independent confirmation and strict close; original synthetic Native incarnation facts remain Active, two issued neighboring jobs and a physically capacity-refused unissued zero-floor actor retain exact independent native/control ownership. Mixed permanent/scoped journals complete at most one candidate per poll and both within two polls after original final job ACKs. Scoped final processing does not consume the permanent journal. No fabricated permanent retirement fact, actual Wayland window/Core/WebKit acceptance or frontend activation.')
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1600]}),flush=True);sys.exit(not report['passed'])
