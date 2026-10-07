"""Execute each named realm reuse scenario explicitly, preserving model scope."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path(__file__).resolve().parents[1]
out=r/'qa'/('controlled-reader-lifetime-model-v4-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
names=['spec/controlled_reader_lifetime_v4.qnt','spec/controlled_reader_lifetime_tests_v4.qnt','qa/controlled-reader-lifetime-model-v4.py','spec/host_realm_lifecycle.qnt']
d={'passed':False,'inputs':{n:sha(r/n) for n in names},'quint':{'path':str(tool),'sha256':sha(tool)},'commands':[],'scope':'Original real URI/GIO reader hold/revocation/one close and independent Native Drain abstraction only; original independent physical, terminal, journal and confirmation Drain remains Native authority. Same policy/context replacement/pending intent/stale callback safety is model scope only. Named selection and invariant samples are model evidence, not actual GTK/WebKit, physical reveal or release acceptance.','nativeAcceptance':False,'fullReleaseAccepted':False}
def run(name,args):
 p=subprocess.run(args,cwd=out/'inputs/spec',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 d['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
try:
 for n in names:
  target=out/'inputs'/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/n,target)
 selected=re.findall(r'run (\w+)\s*=',(r/names[1]).read_text());assert len(selected)==6
 run('typecheck',[str(tool),'typecheck','controlled_reader_lifetime_tests_v4.qnt'])
 run('selected',[str(tool),'test','controlled_reader_lifetime_tests_v4.qnt','--main=controlled_reader_lifetime_tests_v4','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1330041','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')])
 assert len(list(out.glob('named-*.itf.json')))==6
 run('samples',[str(tool),'run','controlled_reader_lifetime_v4.qnt','--main=controlled_reader_lifetime_v4','--backend=typescript','--init=initReader','--step=readerStep','--invariant=readerSafety','--seed=1330042','--max-samples=200','--max-steps=32','--out-itf='+str(out/'samples.itf.json')])
 assert all(sha(r/n)==h for n,h in d['inputs'].items()) and sha(tool)==d['quint']['sha256']
 d.update(passed=True,namedScenarios=6,invariantSamples=200)
except Exception as error:d['error']=repr(error)
d['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({'passed':d['passed'],'report':str(out/'report.json'),'error':str(d.get('error',''))[:2200]}),flush=True)
raise SystemExit(not d['passed'])



