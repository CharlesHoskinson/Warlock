"""Fresh fixture: wait for later snapshot without refusing known first record."""
import ast,hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
docs=pathlib.Path(__file__).parent;r=docs.parents[2]
root=r/'implementation/warlock-client-provider-native-v177';p=next(root.glob('qa/native-controlled-*/report.json'));d=json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not d['passed'] and d['cleanupPassed'] and len(d['checks'])==23 and all(c['passed'] for c in d['checks'])
assert 'image.name.startswith' in d['traceback']
log=(p.parent/'private-evidence/controlled-host.log').read_text();assert 'controlled-native-reopened: previousEpoch=1 nativeEpoch=2 samePolicy=1 sameBinding=1' in log and 'native-client-webkit-snapshot-job: request=1 ' in log and 'native-client-webkit-snapshot-job: request=2 ' not in log
receipt=docs/'native177-first-snapshot-wait-failure.json';assert not receipt.exists()
receipt.write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','report':str(p),'reportSHA256':sha(p),'runnerSHA256':sha(root/'qa/native-controlled-host.py'),'failed':True,'reachedChecks':23,'allReachedControlsPassed':True,'failure':'Observer prematurely asserts later snapshot filename against known original request1 log before request2 exists. Finally terminates host with current native custody, causing host1/strict teardown refusal/GLib criticals.','correction':'Fresh184 observer accepts exact known first record as pending, still requires request2 and actual source/current-output/final strict close/all normal owned exits under unchanged6 seconds. Original176/177 retained; no production changes.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
s=(docs/'native176_renderer_reload_runner.py').read_text();needle="    image=pathlib.Path(lines[-1].split(' path=',1)[1]);assert image.parent==private and image.name.startswith('reload-webkit.png.request-')"
assert s.count(needle)==1
s=s.replace(needle,"    image=pathlib.Path(lines[-1].split(' path=',1)[1]);assert image.parent==private\n    if image.name=='reload-webkit.png':\n     assert lines[-1].startswith('native-client-webkit-snapshot-job: request=1 ');return None\n    assert image.name.startswith('reload-webkit.png.request-')")
out=docs/'native184_renderer_reload_runner.py';assert not out.exists();ast.parse(s);out.write_text(s)
s=(docs/'prepare_native177_renderer_reload.py').read_text().replace("root=repo/'implementation/warlock-client-provider-native-v177'","root=repo/'implementation/warlock-client-provider-native-v184'").replace('native176_renderer_reload_runner.py','native184_renderer_reload_runner.py').replace('ownNative177','ownNative184')
out=docs/'prepare_native184_renderer_reload.py';assert not out.exists();ast.parse(s);out.write_text(s);print(out)
