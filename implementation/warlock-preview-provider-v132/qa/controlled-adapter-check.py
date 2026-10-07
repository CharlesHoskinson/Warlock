"""Adapter generation/DOM gates, with explicitly synthetic browser observations."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('controlled-adapter-check-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['assets/controlled-popup-adapter.js','qa/controlled-adapter-check.js','qa/controlled-adapter-check.py'];report={'passed':False,'inputs':{n:sha(root/n) for n in names},'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual adapter JavaScript under synthetic ports/DOM/RAF observations: one-time flags, no browser window policy, stale initialization/visual generations and original DOM publication/lease gates. Not actual Elm receiver/WebKit/physical frame or GUI acceptance.'}
try:
 for n in names:
  p=out/'inputs'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/n,p)
 p=subprocess.run(['node',str(out/'inputs/qa/controlled-adapter-check.js'),str(out/'inputs/assets/controlled-popup-adapter.js')],capture_output=True,text=True,timeout=30);(out/'stdout').write_text(p.stdout);(out/'stderr').write_text(p.stderr);assert p.returncode==0,p.stderr
 report['evidence']=json.loads(p.stdout);assert report['evidence']['passed'] and not report['evidence']['physicalRevealQualified'];assert all(sha(root/n)==h for n,h in report['inputs'].items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error','')}),flush=True);sys.exit(not report['passed'])
