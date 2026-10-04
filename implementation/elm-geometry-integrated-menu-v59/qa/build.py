"""Actual integrated Elm/host build, protected CPU only. No native acceptance."""
import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
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
 elm=REPO/lanes['elm'];broker=REPO/lanes['broker'];carrier=REPO/lanes['host'];base=REPO/lanes['assets']
 held=elm/'qa/held-source-manifest.json'
 assert sha(held)=='27ed7148d101cafb220f3ed21e2d3e14a1df5880f4924d01ff510473dccce450'
 manifest=json.loads(held.read_text());assert manifest['sourceHeld'] and manifest['evidenceIntegrityPassed']
 for relative,row in manifest['files'].items():assert sha(elm/relative)==row['sha256'],relative
 capture(held,'lineage/elm-held.json')
 for contributor,label in ((broker,'broker'),(carrier,'host')):
  held_path=contributor/'qa/held-source-manifest.json'
  assert held_path.is_file(),'Contributor hold required: '+str(held_path)
  if label=='host':assert sha(held_path)=='60e40d823ffcaa2bf1e3d5250d41a57ad5e41630fa62e1bb3a97939bd36e3d7c'
  if label=='broker':assert sha(held_path)=='42aa90628d689727fe0293a95a99ce87d8f2ea10fe68ed1640b8527146f42ef3'
  parent=json.loads(held_path.read_text());assert parent['sourceHeld'] and parent['evidenceIntegrityPassed']
  for relative,row in parent['files'].items():assert sha(contributor/relative)==row['sha256'],relative
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
  capture(elm/'qa'/name,'qa/'+name)
 capture(ROOT/'qa/build.py','qa/build.py');capture(ROOT/'qa/native-contract.json','qa/native-contract.json')
 for name in ('adapter','popup-adapter','context'):run(name+'-syntax',['node','--check','assets/'+name+'.js'])
 for entry,artifact in (('Main','elm'),('Popup','popup')):
  run(entry+'-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/'+entry+'.elm','--optimize','--output=assets/'+artifact+'.js'])
 run('replay-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/MenuSurfaceReplay.elm','--output='+str(OUT/'replay.js')])
 for suite in ('menu','geometry','refresh'):
  args=['node','qa/'+suite+'.cjs',str(OUT/'replay.js'),'qa/fixtures.json']
  if suite!='menu':args.append('qa/geometry-fixtures.json')
  args.append(str(OUT/(suite+'-checks.json')));run(suite+'-checks',args)
  result=json.loads((OUT/(suite+'-checks.json')).read_text());assert result['passed'];report[suite+'Checks']=result
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
