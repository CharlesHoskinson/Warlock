import hashlib,importlib.util,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'elm-own-popup-join-decoder-v322';OUT=ROOT/('review-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
r={'passed':False,'nativeAcceptance':False,'authenticated':False,'ownBlockerGrantQualified':False,'scope':'Actual corrected diagnostic parser/matcher replay with synthetic preserved frames; no native query/current peer/host binding/action grant','entries':[],'cases':[]}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def check(p,w=None):
 p=Path(p);d=sha(p);assert w is None or d==w,str(p);r['entries'].append({'path':str(p),'sha256':d,'size':p.stat().st_size})
try:
 p=SOURCE/'component-manifest.json';check(p,'b239ccf97fb1028e90fe77cc929a2a3dfdace1974670a8427a87542e7c14fd79');manifest=json.loads(p.read_text());assert manifest['sourceHeld'] and manifest['evidenceIntegrityPassed'] and manifest['authenticated'] is False and manifest['ownBlockerGrantQualified'] is False
 for rel,row in manifest['files'].items():check(SOURCE/rel,row['sha256'])
 for path,row in manifest.get('externalFiles',{}).items():check(path,row['sha256'])
 for source,rel in [(SOURCE/'join.py','join.py'),(SOURCE/'qa/test.py','test.py')]:
  dest=OUT/rel;shutil.copy2(source,dest);dest.chmod(0o444)
 spec=importlib.util.spec_from_file_location('join',OUT/'join.py');m=importlib.util.module_from_spec(spec);sys.modules['join']=m;spec.loader.exec_module(m)
 for name in ['valid-layer','valid-nested','self-parent','cycle']:
  p=ROOT/'witness-1791155791811742013'/(name+'.json');check(p);raw=p.read_bytes();shutil.copy2(p,OUT/p.name)
  try:
   snapshot=m.parse(raw,core_pid=123);result=m.match_layer_popup(snapshot,host_pid=456,host_uid=1000,popup_id=12,root_id=11);accepted=True;assert result['authenticated'] is False and result['ownBlockerGrantQualified'] is False
  except m.Refused as e:accepted=False;result={'refused':str(e)}
  assert accepted==(name.startswith('valid-')),name
  r['cases'].append({'name':name,'accepted':accepted,'result':result})
 p=subprocess.run([sys.executable,'-B',str(OUT/'test.py'),'--exercise',str(OUT/'join.py')],capture_output=True,timeout=30);(OUT/'suite.stdout').write_bytes(p.stdout);(OUT/'suite.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode(errors='replace');checks=json.loads(p.stdout);assert len(checks)==51;r['originalCurrentSuiteChecks']=checks
 evidence=SOURCE/'qa/test-1791156163998650959/report.json';check(evidence);d=json.loads(evidence.read_text());assert d['passed'] and len(d['checks'])==51 and len(d['mutants'])==6 and all(x['killed'] for x in d['mutants']);r['sourceEvidence']={'path':str(evidence),'sha256':sha(evidence)}
 r['tools']={str(Path(sys.executable).resolve()):sha(Path(sys.executable).resolve())};r['passed']=True
except Exception as e:r['error']=repr(e)
finally:(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');print('PASS '+str(len(r['entries']))+' entries' if r['passed'] else r.get('error'))
if not r['passed']:raise SystemExit(1)
