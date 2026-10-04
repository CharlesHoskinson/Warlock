"""Bind actual compiled cases, compiled unsafe mutants, original failures and V69 hold."""
import hashlib,json,resource,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-menu-post-close-selection-v69'
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir();checks=[]
report={'passed':False,'scope':'Independent compiled post-close CPU source and evidence closure only; original suites retain diagnostic failures; no native acceptance','checks':checks}
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
try:
 selected=ROOT/'qa/replay-1791106215786245435/report.json';mutation=ROOT/'qa/mutations-1791106304028394548/report.json'
 r=json.loads(selected.read_text());mut=json.loads(mutation.read_text())
 check('59 independent compiled cases passed',r['passed'] is True and r['postCloseChecks']['checks']==59 and all(x['passed'] is True for x in r['postCloseChecks']['cases']))
 check('actual Main and Popup compiled',all(any(x['name']==n and x['exitCode']==0 for x in r['commands']) for n in ['compile','Main-compile','Popup-compile']))
 check('five actual compiled mutants killed',mut['passed'] is True and len(mut['mutants'])==5 and all(x['compiled'] and x['namedOracle'] in x['failedCases'] for x in mut['mutants']))
 manifest=SOURCE/'qa/held-source-manifest.json';expected='6b06b40645a8d8fa07cab93756985e4d23151a6f21f2254db7432acc893102ea'
 check('exact held V69 source/evidence manifest',sha(manifest)==expected);m=json.loads(manifest.read_text())
 for rel,row in m['files'].items():check('V69 held '+rel,sha(SOURCE/rel)==row['sha256'])
 for label,packet,path in [('compiled',r,selected),('mutations',mut,mutation)]:
  for rel,digest in packet['sourceInputs'].items():check(label+' production source '+rel,sha(SOURCE/rel)==digest and m['files'][rel]['sha256']==digest)
  for rel,digest in packet['qaInputs'].items():check(label+' QA source '+rel,sha(ROOT/rel)==digest)
  for rel,digest in packet['artifacts'].items():check(label+' retained artifact '+rel,sha(path.parent/rel)==digest)
 original=r['originalSuites'];check('original menu failures remain failures',original['menu']['passed'] is False and original['menu']['checks']==78 and original['menu']['casesPassed']==64)
 check('original refresh failures remain failures',original['refresh']['passed'] is False and original['refresh']['checks']==21 and original['refresh']['casesPassed']==18)
 check('original geometry fatal is not counted as a pass',original['geometry']['passed'] is False and original['geometry']['completedReport'] is False and original['geometry']['exitCode']==1)
 upstream=json.loads((ROOT/'qa/upstream.json').read_text());parent=Path(upstream['parent']);check('V58 original hold',sha(parent/'qa/held-source-manifest.json')==upstream['heldManifestSHA256'])
 for rel,digest in upstream['files'].items():check('byte-exact original oracle '+rel,sha(parent/rel)==digest and sha(ROOT/'qa/original'/Path(rel).name)==digest)
 report['passed']=True
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if report['passed']:
 files={}
 for p in sorted(ROOT.rglob('*')):
  if p.is_symlink():raise RuntimeError('Unexpected QA symlink')
  if p.is_file() and p.name!='held-source-manifest.json':files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':oct(p.stat().st_mode&0o777)}
 packet={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':report['scope'],'files':files,'productionSource':{'path':str(SOURCE),'manifest':str(manifest),'sha256':expected},'acceptedReport':{'path':str(selected.relative_to(ROOT)),'sha256':sha(selected)},'mutationsReport':{'path':str(mutation.relative_to(ROOT)),'sha256':sha(mutation)},'freezeReport':{'path':str((OUT/'report.json').relative_to(ROOT)),'sha256':sha(OUT/'report.json')},'originalResults':original}
 (ROOT/'qa/held-source-manifest.json').write_text(json.dumps(packet,indent=2)+'\n')
print(OUT/'report.json');raise SystemExit(not report['passed'])
