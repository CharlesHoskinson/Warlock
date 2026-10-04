"""Compile actual family guard and root-only/absent guard mutants."""
import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT.parent
OUT=ROOT/'qa'/('family-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sourcefiles=[SOURCE/'elm.json',*sorted((SOURCE/'src').glob('*.elm'))]
qafiles=[ROOT/'src/MenuSurfaceReplay.elm',*sorted((ROOT/'qa').glob('*.cjs')),*sorted((ROOT/'qa').glob('*.json')),Path(__file__)]
report={'passed':False,'nativeAcceptance':False,'scope':'Actual compiled typed full-family barrier, no native execution','sourceInputs':{str(p.relative_to(SOURCE)):sha(p) for p in sourcefiles},'qaInputs':{str(p.relative_to(ROOT)):sha(p) for p in qafiles},'profiles':{}}
def command(name,argv,cwd):
 p=subprocess.run(argv,cwd=cwd,capture_output=True,text=True,timeout=180)
 (cwd.parent/(name+'.stdout')).write_text(p.stdout);(cwd.parent/(name+'.stderr')).write_text(p.stderr)
 return p.returncode
try:
 for name in ['actual','root-only','missing-native-guard']:
  target=OUT/name;workspace=target/'inputs';workspace.mkdir(parents=True)
  for files,base in [(sourcefiles,SOURCE),(qafiles,ROOT)]:
   for p in files:
    dest=workspace/p.relative_to(base);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  file=workspace/'src/MenuBridge.elm';text=file.read_text()
  if name=='root-only':
   needle='Effects.blocked observed.context.lifetime window.incarnation shell.effects'
   assert text.count(needle)==1;text=text.replace(needle,'Effects.blocked observed.context.lifetime family shell.effects')
  if name=='missing-native-guard':
   needle='in blocked || nativeBlocked';assert text.count(needle)==1;text=text.replace(needle,'in blocked')
  file.write_text(text)
  binary=target/'replay.js'
  assert command('compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/MenuSurfaceReplay.elm','--output='+str(binary)],workspace)==0,'Compiler failure is not mutant rejection'
  code=command('checks',['node',str(workspace/'qa/family.cjs'),str(binary),str(workspace/'qa/fixtures.json'),str(workspace/'qa/geometry-fixtures.json'),str(target/'checks.json')],workspace)
  checks=json.loads((target/'checks.json').read_text());failed=[x['name'] for x in checks['cases'] if not x['passed']]
  if name=='actual':assert code==0 and checks['passed'] and checks['checks']==6,checks.get('error')
  else:assert code==1 and 'child-target native Unknown blocks canonical root before any preparation' in failed,(name,failed,checks.get('error'))
  report['profiles'][name]={'compiled':True,'exitCode':code,'checks':checks['checks'],'failedCases':failed,'binarySHA256':sha(binary),'sourceSHA256':sha(file)}
 for relative,wanted in report['sourceInputs'].items():assert sha(SOURCE/relative)==wanted
 for relative,wanted in report['qaInputs'].items():assert sha(ROOT/relative)==wanted
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
