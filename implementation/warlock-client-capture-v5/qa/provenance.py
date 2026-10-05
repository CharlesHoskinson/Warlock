"""Verify the linked Renderer.cpp ancestry without substituting an audit checkout."""
import hashlib,json,pathlib,resource,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
 return h.hexdigest()
OUT=ROOT/'qa'/('provenance-'+str(time.time_ns()));OUT.mkdir()
report={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'chain':[]}
try:
 p=REPO/'implementation/elm-core-keyboardless-focus-v205/build-1791139089126747676/report.json'
 renderer=None
 for i in range(5):
  d=json.loads(p.read_text());assert d['passed']
  archive=p.parent/'libhyprland_lib.a';assert sha(archive)==d['archiveSHA256']
  obj=subprocess.check_output(['ar','p',str(archive),'Renderer.cpp.o'],timeout=90);digest=hashlib.sha256(obj).hexdigest()
  if renderer is None:renderer=digest
  assert digest==renderer
  report['chain'].append({'report':str(p),'reportSHA256':sha(p),'archive':str(archive),'archiveSHA256':d['archiveSHA256'],'rendererObjectSHA256':digest})
  if i<4:
   a=d['ancestor'];p=pathlib.Path(a['report']);assert sha(p)==a['reportSHA256'];assert 'Renderer.cpp.o' not in d['rebuiltArchiveMembers']
 source=next(pathlib.Path(k) for k in d['dependencies'] if k.endswith('/Renderer.cpp'))
 assert sha(source)==d['dependencies'][str(source)] and d['rebuiltArchiveMembers']['Renderer.cpp.o']==renderer
 (OUT/'Renderer.cpp').write_bytes(source.read_bytes())
 # These reference files explain public core behavior. Their baseline objects
 # are compared to the final archive; this is not a claim that a mutable source
 # tree is itself a frozen compiler input closure.
 refs={}
 base=REPO/'implementation/maximized-stack-v1/native-core-v2'
 for rel in ['src/render/GLRenderer.cpp','src/render/OpenGL.cpp','src/render/pass/Pass.cpp']:
  member=pathlib.Path(rel).name+'.o'
  digest=hashlib.sha256(subprocess.check_output(['ar','p',str(report['chain'][0]['archive']),member],timeout=90)).hexdigest()
  obj=base/'build/CMakeFiles/hyprland_lib.dir'/ (rel+'.o');assert sha(obj)==digest
  dest=OUT/'reference'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((base/rel).read_bytes())
  refs[rel]={'referenceSourceSHA256':sha(base/rel),'baselineObjectSHA256':digest,'finalArchiveMemberSHA256':digest,'sourceCompilerClosureQualified':False}
 report.update(passed=True,source=str(source),sourceSHA256=sha(source),rendererObjectSHA256=renderer,referenceSources=refs,scope='Renderer source dependency and unchanged linked object verified through core73/89/450/470/205; baseline GL/Pass objects unchanged, reference source closure separately unqualified')
except Exception as e:report['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'error':report.get('error'),'report':str(OUT/'report.json')}));raise SystemExit(not report['passed'])
