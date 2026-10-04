import hashlib,json,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
from archive import archive_payloads
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;IMPL=ROOT.parent;OWNER=IMPL/'maximized-stack-v1/native-core-v2';PRIOR=IMPL/'elm-core-parent-first-anchor-v89/build-1791107301396755104';OBJ=IMPL/'elm-core-seat-focus-compile-v448/compile-1791131428386339336';AQ=IMPL/'elm-keyboard-focus-cancellation-v155/build-1791128575548525187/cmake/libaquamarine.so.0.15.0'
OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,args):
 p=subprocess.run(list(map(str,args)),cwd=OWNER/'build',capture_output=True,timeout=240);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode(errors='replace')[-1200:];r['commands'].append({'name':name,'command':list(map(str,args)),'exitCode':p.returncode});print(name,p.returncode,flush=True);return p.stdout
r={'passed':False,'nativeAcceptance':False,'installed':False,'scope':'Complete Core89 archive with sole InputManager focus fallback guard replacement and AQ155 link; no native fix acceptance','commands':[]}
try:
 manifest=IMPL/'elm-keyboard-seat-focus-source-held-v449/qa/slice-manifest.json';assert sha(manifest)=='68e5c454daac62850674e00a695fd28ac3cc3e625ebe95d64a40fe641d7df875'
 for e in json.loads(manifest.read_text())['files']:assert sha(IMPL.parent/e['path'])==e['sha256']
 prior=json.loads((PRIOR/'report.json').read_text());compiled=json.loads((OBJ/'report.json').read_text());assert prior['passed'] and compiled['passed'];assert sha(AQ)=='bfb0383901822a92f2fe945b4b80048f89cc4ffeeb6e9bb8ab748d57317928cb'
 originalArchive=PRIOR/'libhyprland_lib.a';assert sha(originalArchive)==prior['archiveSHA256'];obj=Path(compiled['object']);assert sha(obj)==compiled['objectSHA256'];archive=OUT/'libhyprland_lib.a';shutil.copy2(originalArchive,archive);old=archive_payloads(originalArchive);assert len(old)==433;run('archive',['/usr/bin/ar','r',archive,obj]);new=archive_payloads(archive)
 assert len(new)==433
 for a,b in zip(old,new):
  assert a['name']==b['name']
  if a['name']=='InputManager.cpp.o':assert b['sha256']==sha(obj)
  else:assert a==b
 for name,rows in [('ancestor-archive-payloads.json',old),('new-archive-payloads.json',new)]: (OUT/name).write_text(json.dumps(rows,indent=2)+'\n')
 link=list(next(c['command'] for c in prior['commands'] if c['name']=='link'));oldaq=prior['aqLibrary']
 for i,arg in enumerate(link):
  if i and link[i-1]=='-o':link[i]=str(OUT/'Hyprland')
  elif arg==str(originalArchive):link[i]=str(archive)
  elif arg==oldaq:link[i]=str(AQ)
  elif arg.startswith('-Wl,--dependency-file='):link[i]='-Wl,--dependency-file='+str(OUT/'link.d')
 run('link',link)
 def deps(p):
  names=shlex.split(p.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]);names=names[:next((i for i,n in enumerate(names) if n.endswith(':')),len(names))];return {str((Path(n) if Path(n).is_absolute() else OWNER/'build'/n).resolve()):sha((Path(n) if Path(n).is_absolute() else OWNER/'build'/n).resolve()) for n in names}
 actual=deps(OUT/'link.d');expected={str(archive.resolve()) if p==str(originalArchive.resolve()) else str(AQ.resolve()) if p==str(Path(oldaq).resolve()) else p:sha(archive) if p==str(originalArchive.resolve()) else sha(AQ) if p==str(Path(oldaq).resolve()) else digest for p,digest in prior['linkDependencies'].items()};assert actual==expected
 replay=list(link)
 for i,arg in enumerate(replay):
  if i and replay[i-1]=='-o':replay[i]=str(OUT/'Hyprland-relink')
  elif arg.startswith('-Wl,--dependency-file='):replay[i]='-Wl,--dependency-file='+str(OUT/'relink.d')
 run('relink',replay);assert sha(OUT/'Hyprland')==sha(OUT/'Hyprland-relink') and deps(OUT/'relink.d')==actual
 exports=[]
 for name,p in [('ancestor',prior['binary']),('candidate',OUT/'Hyprland')]:exports.append({(row.split()[1],row.split()[2]) for row in run(name+'-exports',['/usr/bin/nm','-D','--defined-only',p]).decode().splitlines()})
 missing=sorted(exports[0]-exports[1]);assert not missing,missing[:10]
 linked={}
 for line in run('libraries',['/usr/bin/ldd',OUT/'Hyprland']).decode().splitlines():
  assert 'not found' not in line
  for word in line.split():
   if word.startswith('/') and Path(word).is_file():linked[str(Path(word).resolve())]=sha(Path(word).resolve())
 headers=prior['owningHeaders']
 for rel,digest in headers.items():p=PRIOR/'owning-headers'/rel;assert sha(p)==digest;q=OUT/'owning-headers'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 retained={}
 for path,digest in prior['retainedPolicyHeaders'].items():p=Path(path);assert sha(p)==digest;q=OUT/'inputs/candidate'/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);retained[str(q)]=digest
 for section in [compiled['dependencies'],actual,linked]:
  for path,digest in section.items():assert sha(Path(path))==digest
 r.update(passed=True,binary=str(OUT/'Hyprland'),binarySHA256=sha(OUT/'Hyprland'),archiveSHA256=sha(archive),owningHeaders=headers,owningVersionHeaderSHA256=prior['owningVersionHeaderSHA256'],rebuiltArchiveMembers={'InputManager.cpp.o':sha(obj)},unchangedArchiveMembers=432,existingPublicHeadersUnchanged=True,geometryAndReloadArchivePayloadsPreserved=True,retainedPolicyHeaders=retained,ancestor={'report':str(PRIOR/'report.json'),'reportSHA256':sha(PRIOR/'report.json')},dependencies=compiled['dependencies'],linkDependencies=actual,linkedLibraries=linked,tools={str(Path(shutil.which(n)).resolve()):sha(Path(shutil.which(n)).resolve()) for n in ['c++','ar','nm','ldd']},exportClosure={'ancestorCount':len(exports[0]),'candidateCount':len(exports[1]),'missingSymbols':missing},inputs={},aqLibrary=str(AQ),aqLibrarySHA256=sha(AQ),sourceCompileReport=str(OBJ/'report.json'),sourceCompileReportSHA256=sha(OBJ/'report.json'))
except Exception as error:r['error']=repr(error)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:
 files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in ROOT.rglob('*') if p.is_file()};(ROOT/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'buildReport':str(OUT/'report.json'),'buildReportSHA256':sha(OUT/'report.json'),'files':files},indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
