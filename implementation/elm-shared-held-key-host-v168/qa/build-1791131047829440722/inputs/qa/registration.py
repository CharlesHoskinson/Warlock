import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('review-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'commands':[],'sources':{}}
for p in [ROOT/'elm.json',ROOT/'upstream.json',*sorted((ROOT/'src').glob('*.elm')),*sorted((ROOT/'qa').glob('*.*'))]:
 d=INPUT/p.relative_to(ROOT);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d);report['sources'][str(p.relative_to(ROOT))]=sha(p)
fixture=REPO/'implementation/elm-menu-retirement-native-forensics-v94/qa/native-evidence.json';shutil.copy2(fixture,INPUT/'evidence.json');report['fixtureSHA256']=sha(fixture)
def run(name,args):
 p=subprocess.run(args,cwd=INPUT,capture_output=True,text=True,timeout=120);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exit':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr[-3000:]
try:
 up=json.loads((ROOT/'upstream.json').read_text());source=Path(up['parent']);assert sha(source/'component-manifest.json')==up['componentManifestSHA256']
 pass
 run('compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/BatchReplay.elm','--output='+str(OUT/'worker.js')])
 run('registration',['node',str(INPUT/'qa/registration.cjs'),str(OUT/'worker.js'),str(INPUT/'evidence.json'),str(OUT/'checks.json')])
 result=json.loads((OUT/'checks.json').read_text());assert result['passed'];report['checks']=result['checks'];report['findings']=result['findings']
 for relative,digest in report['sources'].items():assert sha(ROOT/relative)==digest
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
