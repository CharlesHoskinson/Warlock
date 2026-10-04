"""Actual integrated Elm/host build, protected CPU only. No native acceptance."""
import hashlib,json,resource,shlex,shutil,subprocess,time,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected launcher'
OUT=ROOT/'qa'/('build-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
lanes=json.loads((ROOT/'qa/native-contract.json').read_text())['sourceLanes']
files={};origins={};commands=[]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def capture(source,target):
 dest=INPUT/target;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
 files[target]=sha(source);origins[target]=str(source)
def run(name,args):
 proc=subprocess.run(args,cwd=INPUT,capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(proc.stdout);(OUT/(name+'.stderr')).write_text(proc.stderr)
 commands.append({'name':name,'argv':args,'exitCode':proc.returncode});print(name,proc.returncode,flush=True)
 assert proc.returncode==0,proc.stdout+proc.stderr
 return proc.stdout
report={'passed':False,'scope':'Actual combined Elm and host CPU build/replay; no native GUI, ABI load or release acceptance','commands':commands,'inputs':files,'origins':origins}
try:
 capture(ROOT/'qa/build.py','qa/build.py')
 capture(ROOT/'qa/native-contract.json','qa/native-contract.json')
 contract=json.loads((ROOT/'qa/native-contract.json').read_text())
 parent=Path(contract['sourceLineageParent']);assert sha(parent/'component-manifest.json')==contract['sourceLineageParentManifestSHA256']
 capture(parent/'component-manifest.json','lineage/previous-build-held.json')
 elm=REPO/lanes['elm'];broker=REPO/lanes['broker'];carrier=REPO/lanes['host'];base=REPO/lanes['assets'];qa=REPO/contract['qaLane']
 qaheld=qa/'qa/held-source-manifest.json'
 assert qaheld.is_file(),'V71 QA hold required'
 assert sha(qaheld)=='c3172da2ef407113e440e27ed419ccc8e62c909ce08943c53fed16a56c4681ca','V71 exact hold hash'
 qa_packet=json.loads(qaheld.read_text());assert qa_packet['sourceHeld'] and qa_packet['evidenceIntegrityPassed']
 for rel,row in qa_packet['files'].items():assert sha(qa/rel)==row['sha256'],rel
 capture(qaheld,'lineage/post-close-qa-held.json')
 held=elm/'qa/held-source-manifest.json'
 assert sha(held)=='c3172da2ef407113e440e27ed419ccc8e62c909ce08943c53fed16a56c4681ca'
 manifest=json.loads(held.read_text());assert manifest['sourceHeld'] and manifest['evidenceIntegrityPassed']
 for relative,row in manifest['files'].items():assert sha(elm/relative)==row['sha256'],relative
 capture(held,'lineage/elm-held.json')
 for contributor,label in ((broker,'broker'),(carrier,'host')):
  held_path=contributor/'qa/held-source-manifest.json'
  assert held_path.is_file(),'Contributor hold required: '+str(held_path)
  if label=='host':assert sha(held_path)=='60e40d823ffcaa2bf1e3d5250d41a57ad5e41630fa62e1bb3a97939bd36e3d7c'
  if label=='broker':assert sha(held_path)=='3aa379a0c7c694455d32f08c69d047b4ac0dd9200015d30b40e68593938b2161'
  parent=json.loads(held_path.read_text());assert parent['sourceHeld'] and parent['evidenceIntegrityPassed']
  parent_rows=parent['files'].items() if isinstance(parent['files'],dict) else ((row['path'],row) for row in parent['files'])
  for relative,row in parent_rows:assert sha(contributor/relative)==row['sha256'],relative
  capture(held_path,'lineage/'+label+'-held.json')
 for source in sorted((elm/'src').glob('*.elm')):capture(source,'src/'+source.name)
 capture(elm/'elm.json','elm.json')
 for folder in ('native','assets'):
  for source in sorted((base/folder).glob('*')):
   if source.is_file():capture(source,folder+'/'+source.name)
 capture(carrier/'native/host.c','native/host.c')
 capture(carrier/'native/geometry-carrier-test.c','native/geometry-carrier-test.c')
 for source in sorted((carrier/'native').glob('*.h')):capture(source,'native/'+source.name)
 for source in sorted((broker/'adapter').glob('*.py')):capture(source,'adapter/'+source.name)
 for name in ('menu.cjs','geometry.cjs','refresh.cjs','fixtures.json','geometry-fixtures.json'):
  capture(qa/'semantic/qa/original'/name,'qa/original/'+name)
 capture(elm/'src/MenuSurfaceReplay.elm','source-worker/MenuSurfaceReplay.elm')
 capture(qa/'semantic/src/MenuSurfaceReplay.elm','src/MenuSurfaceReplay.elm')
 capture(qa/'post-close/qa/post-close.cjs','qa/post-close.cjs')
 capture(qa/'post-close/qa/upstream.json','qa/post-close-upstream.json')
 for source in sorted((qa/'semantic/qa/staged').glob('*.cjs')):capture(source,'qa/staged/'+source.name)
 for name in ('adapter','popup-adapter','context'):run(name+'-syntax',['node','--check','assets/'+name+'.js'])
 for entry,artifact in (('Main','elm'),('Popup','popup')):
  run(entry+'-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/'+entry+'.elm','--optimize','--output=assets/'+artifact+'.js'])
 run('replay-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/MenuSurfaceReplay.elm','--output='+str(OUT/'replay.js')])
 report['originalSuites']={}
 for suite in ('menu','geometry','refresh'):
  args=['node','qa/original/'+suite+'.cjs',str(OUT/'replay.js'),'qa/original/fixtures.json']
  if suite!='menu':args.append('qa/original/geometry-fixtures.json')
  path=OUT/(suite+'-original-checks.json');args.append(str(path))
  proc=subprocess.run(args,cwd=INPUT,capture_output=True,text=True,timeout=45)
  (OUT/(suite+'-original.stdout')).write_text(proc.stdout);(OUT/(suite+'-original.stderr')).write_text(proc.stderr)
  commands.append({'name':suite+'-original-diagnostic','argv':args,'exitCode':proc.returncode,'diagnosticOnly':True})
  result=json.loads(path.read_text()) if path.exists() else {'passed':False,'cases':[],'checks':None}
  report['originalSuites'][suite]={'exitCode':proc.returncode,'completedReport':path.exists(),'result':result,'accepted':False}
 run('post-close-checks',['node','qa/post-close.cjs',str(OUT/'replay.js'),'qa/original/fixtures.json','qa/original/geometry-fixtures.json',str(OUT/'post-close-checks.json')])
 result=json.loads((OUT/'post-close-checks.json').read_text());assert result['passed'] and result['checks']==59
 report['postCloseChecks']=result
 report['semanticSuites']={}
 for suite,expected in [('menu',78),('geometry',53),('refresh',21)]:
  args=['node','qa/staged/'+suite+'.cjs',str(OUT/'replay.js'),'qa/original/fixtures.json']
  if suite!='menu':args.append('qa/original/geometry-fixtures.json')
  path=OUT/(suite+'-staged-checks.json');args.append(str(path));run(suite+'-staged-checks',args)
  data=json.loads(path.read_text());assert data['passed'] and data['checks']==expected and all(x['passed'] for x in data['cases'])
  report['semanticSuites'][suite]={'passed':True,'checks':expected,'caseIds':[x['name'] for x in data['cases']]}
 report['separateCpuEvidence']={}
 for label,relative in [
  ('postClose59','post-close/qa/replay-1791108165648889457/report.json'),
  ('family6','family/qa/family-1791108381750401231/report.json'),
  ('postCloseFiveMutants','post-close/qa/mutations-1791108165634785258/report.json')]:
  source=qa/relative;data=json.loads(source.read_text());assert data['passed']
  capture(source,'lineage/'+label+'.json');report['separateCpuEvidence'][label]={'path':str(source),'sha256':sha(source),'scope':'Separate exact held V87 CPU evidence; synthetic observations/outcomes only'}
 flags=shlex.split(run('pkg-config',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']))
 run('host-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MMD','-MF',str(OUT/'host.d'),'native/host.c','-o',str(OUT/'elm-host'),*flags])
 run('host-self-test',[str(OUT/'elm-host'),'--self-test'])
 run('geometry-carrier-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','native/geometry-carrier-test.c','-o',str(OUT/'geometry-carrier-tests'),*flags]);run('geometry-carrier-tests',[str(OUT/'geometry-carrier-tests')])
 run('surface-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','native/surface-test.c','-o',str(OUT/'surface-tests'),*flags]);run('surface-tests',[str(OUT/'surface-tests')])
 run('context-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','native/context-keys-test.c','-o',str(OUT/'context-tests')]);run('context-tests',[str(OUT/'context-tests')])
 for target,source in origins.items():assert sha(Path(source))==files[target],source
 report['binarySHA256']=sha(OUT/'elm-host');report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
