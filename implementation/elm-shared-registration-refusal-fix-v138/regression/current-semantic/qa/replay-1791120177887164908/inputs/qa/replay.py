"""Full ancestral semantic equivalents with explicit post-close observations."""
import argparse,hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);args=parser.parse_args()
SOURCE=Path(args.source).resolve(strict=True)
OUT=ROOT/'qa'/('replay-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sourcefiles=[SOURCE/'elm.json',*sorted((SOURCE/'src').glob('*.elm'))]
qafiles=[ROOT/'src/MenuSurfaceReplay.elm',Path(__file__),ROOT/'qa/upstream.json',*sorted((ROOT/'qa/original').glob('*')),*sorted((ROOT/'qa/staged').glob('*'))]
report={'passed':False,'scope':'Independent compiled actual post-close preparation lifecycle; synthetic native facts, no GUI/native execution acceptance','sourceRoot':str(SOURCE),'sourceInputs':{str(p.relative_to(SOURCE)):sha(p) for p in sourcefiles},'qaInputs':{str(p.relative_to(ROOT)):sha(p) for p in qafiles},'commands':[],'originalSuites':{}}
for files,origin in [(sourcefiles,SOURCE),(qafiles,ROOT)]:
 for p in files:
  destination=INPUT/p.relative_to(origin);destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,destination)
  if origin==SOURCE and p.name=='MenuSurfaceReplay.elm':
   captured=INPUT/'source-worker/MenuSurfaceReplay.elm';captured.parent.mkdir(exist_ok=True);shutil.copy2(p,captured)
report['workerInstrumentation']='Byte-exact copied V71 worker overrides only QA input/snapshot instrumentation; upstream worker retained at inputs/source-worker/MenuSurfaceReplay.elm. All production modules come unchanged from sourceRoot.'
def command(name,argv,timeout=180):
 process=subprocess.run(argv,cwd=INPUT,capture_output=True,text=True,timeout=timeout)
 (OUT/(name+'.stdout')).write_text(process.stdout);(OUT/(name+'.stderr')).write_text(process.stderr)
 report['commands'].append({'name':name,'argv':argv,'exitCode':process.returncode})
 print(name,process.returncode,flush=True);return process.returncode
try:
 upstream=json.loads((ROOT/'qa/upstream.json').read_text());parent=Path(upstream['parent'])
 assert sha(parent/'qa/held-source-manifest.json')==upstream['heldManifestSHA256']
 for rel,digest in upstream['files'].items():assert sha(parent/rel)==digest and sha(ROOT/'qa/original'/Path(rel).name)==digest
 code=command('compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/MenuSurfaceReplay.elm','--output='+str(OUT/'replay.js')]);assert code==0,'Replay compile failed'
 # Original semantics intentionally preserved: no injected observations or changed labels.
 for name in ['menu','geometry','refresh']:
  argv=['node',str(INPUT/'qa/original'/(name+'.cjs')),str(OUT/'replay.js'),str(INPUT/'qa/original/fixtures.json')]
  if name!='menu':argv.append(str(INPUT/'qa/original/geometry-fixtures.json'))
  argv.append(str(OUT/(name+'-original-checks.json')))
  code=command(name+'-original',argv,45)
  resultPath=OUT/(name+'-original-checks.json')
  result=json.loads(resultPath.read_text()) if resultPath.exists() else {'passed':False,'checks':None,'cases':[]}
  report['originalSuites'][name]={'exitCode':code,'completedReport':resultPath.exists(),'passed':result['passed'],'checks':result.get('checks'),'casesPassed':sum(x['passed'] for x in result.get('cases',[])),'note':'Byte-exact old traces/oracles; failures/fatal old-protocol setup remain failures, never counted as new protocol passes.'}
 report['stagedSuites']={}
 for name,expected in [('menu',78),('geometry',53),('refresh',21)]:
  argv=['node',str(INPUT/'qa/staged'/(name+'.cjs')),str(OUT/'replay.js'),str(INPUT/'qa/original/fixtures.json')]
  if name!='menu':argv.append(str(INPUT/'qa/original/geometry-fixtures.json'))
  argv.append(str(OUT/(name+'-staged-checks.json')))
  code=command(name+'-staged',argv,45)
  p=OUT/(name+'-staged-checks.json')
  result=json.loads(p.read_text()) if p.exists() else {'passed':False,'checks':None,'cases':[]}
  report['stagedSuites'][name]={'exitCode':code,'expectedChecks':expected,'checks':result.get('checks'),'passed':bool(code==0 and result['passed'] and result['checks']==expected),'casesPassed':sum(x['passed'] for x in result.get('cases',[])),'failedCases':[x['name'] for x in result.get('cases',[]) if not x['passed']]}
  old=(ROOT/'qa/original'/(name+'.cjs')).read_text();new=(ROOT/'qa/staged'/(name+'.cjs')).read_text()
  import difflib
  (OUT/(name+'-trace-adaptation.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='original/'+name,tofile='staged/'+name)))
 assert all(x['passed'] for x in report['stagedSuites'].values()),'Staged semantic equivalents failed'
 for name in ['Main','Popup']:assert command(name+'-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/'+name+'.elm','--output='+str(OUT/(name+'.js'))])==0,name+' compile failed'
 for rel,digest in report['sourceInputs'].items():assert sha(SOURCE/rel)==digest,'Source changed during test: '+rel
 for rel,digest in report['qaInputs'].items():assert sha(ROOT/rel)==digest,'QA changed during test: '+rel
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
