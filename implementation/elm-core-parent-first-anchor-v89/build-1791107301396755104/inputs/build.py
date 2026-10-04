"""Replace one pointer object in the frozen merged geometry/monitor archive."""
import hashlib,json,os,resource,shlex,shutil,subprocess,time
from pathlib import Path
from archive import archive_payloads
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;IMPL=ROOT.parent;OWNER=IMPL/'maximized-stack-v1/native-core-v2'
PRIOR=IMPL/'elm-geometry-monitor-core-v73/core/build-1791106255338249967';COMPONENT=IMPL/'elm-geometry-monitor-core-v73/component-manifest.json'
AQ=IMPL/'elm-seat-publication-v79/build-1791106084855005199/cmake/libaquamarine.so.0.15.0'
OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'installed':False,'scope':'One owning Pointer object replacement on complete merged geometry73 ABI; guarded AQ79 link; original MAX/XDG/reload and 432 other archive payloads retained; fresh geometry plugin/native qualification required','commands':[]}
def run(name,cmd):
 p=subprocess.run(list(map(str,cmd)),cwd=OWNER/'build',capture_output=True,timeout=240);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':list(map(str,cmd)),'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr.decode(errors='replace')[-5000:];return p.stdout
def linkdeps(path):
 names=shlex.split(path.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]);names=names[:next((i for i,n in enumerate(names) if n.endswith(':')),len(names))]
 paths={(Path(n) if Path(n).is_absolute() else OWNER/'build'/n).resolve() for n in names};assert paths and all(p.is_file() for p in paths);return {str(p):sha(p) for p in sorted(paths)}
try:
 prior=json.loads((PRIOR/'report.json').read_text());assert prior['passed'];component=json.loads(COMPONENT.read_text());assert component['sourceHeld'] and component['evidenceIntegrityPassed']
 assert sha(COMPONENT)=='ea95dbdcac7b61ca0c43338338ea73cf135d4b9b806fe1effb72cc9debad84bf'
 for rel,row in component['files'].items():assert sha(COMPONENT.parent/rel)==row['sha256'],rel
 archive=PRIOR/'libhyprland_lib.a';assert sha(archive)==prior['archiveSHA256'] and sha(prior['binary'])==prior['binarySHA256']
 r['ancestor']={'report':str(PRIOR/'report.json'),'reportSHA256':sha(PRIOR/'report.json'),'binary':prior['binary'],'binarySHA256':prior['binarySHA256'],'archive':str(archive),'archiveSHA256':sha(archive),'componentManifest':str(COMPONENT),'componentManifestSHA256':sha(COMPONENT)}
 r['tools']={str(Path(shutil.which(name)).resolve()):sha(Path(shutil.which(name)).resolve()) for name in ['c++','ar','ld','nm','ldd']}
 proof=[]
 for pattern,key,value in [('qa/warp-*/report.json','mutantsRejected',5),('qa/model-*/report.json','mutantsRejected',6),('qa/test-*/report.json','checks',29)]:
  p=sorted(ROOT.glob(pattern))[-1];d=json.loads(p.read_text());assert d['passed'] and d[key]==value,p
  for rel,wanted in d['artifacts'].items():assert sha(p.parent/rel)==wanted,rel
  for path,wanted in d.get('inputs',{}).items():assert sha(path)==wanted,path
  proof.append({'path':str(p),'sha256':sha(p)})
 r['proofReports']=proof
 files=[ROOT/'build.py',ROOT/'archive.py',*sorted((ROOT/'candidate').rglob('*')),*sorted((ROOT/'qa').glob('*.py')),*sorted((ROOT/'qa').glob('*.cpp')),*sorted((ROOT/'spec').glob('*'))];files=[p for p in files if p.is_file()]
 inputs={str(p.relative_to(ROOT)):sha(p) for p in files};r['inputs']=inputs
 for p in files:
  dest=OUT/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);dest.chmod(0o444)
 headers=prior['owningHeaders'];assert len(headers)==694;tree=OUT/'owning-headers';r['owningHeaders']=headers
 for rel,wanted in headers.items():
  p=PRIOR/'owning-headers'/rel;assert sha(p)==wanted,rel;dest=tree/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);dest.chmod(0o444)
 for rel,wanted in prior['inputs'].items():
  if rel.startswith('candidate/') and (ROOT/rel).exists():assert sha(ROOT/rel)==wanted,rel
 r['retainedPolicyHeaders']={}
 for path,wanted in prior['retainedPolicyHeaders'].items():
  p=Path(path);dest=OUT/'inputs/candidate'/p.name;assert sha(p)==wanted;shutil.copy2(p,dest);r['retainedPolicyHeaders'][str(dest)]=wanted
 old=archive_payloads(archive);assert len(old)==433;ancestor_pointer=IMPL/'elm-core-parent-hit-test-v72/build-1791104632059591332'
 assert next(v for v in old if v['name']=='PointerManager.cpp.o')['sha256']==sha(ancestor_pointer/'PointerManager.cpp.o')
 ancestor_source=ancestor_pointer/'inputs/candidate/src/pointer/PointerManager.cpp';r['pointerAncestor']={'source':str(ancestor_source),'sha256':sha(ancestor_source),'report':str(ancestor_pointer/'report.json'),'reportSHA256':sha(ancestor_pointer/'report.json'),'objectSHA256':sha(ancestor_pointer/'PointerManager.cpp.o')}
 source=tree/'src/pointer/PointerManager.cpp';shutil.copy2(ROOT/'candidate/src/pointer/PointerManager.cpp',source)
 original=OWNER/'src/pointer/PointerManager.cpp';db=OWNER/'build/compile_commands.json';entry=next(e for e in json.loads(db.read_text()) if Path(e['file'])==original);r['compileDatabaseSHA256']=sha(db);r['originalCompileEntry']=entry
 cmd=shlex.split(entry['command']);clean=[];i=0;obj=OUT/'PointerManager.cpp.o';dep=OUT/'PointerManager.cpp.d'
 while i<len(cmd):
  arg=cmd[i]
  if arg=='-include':i+=2;continue
  if i and cmd[i-1]=='-c':arg=str(source)
  elif i and cmd[i-1]=='-o':arg=str(obj)
  elif arg.startswith('-I') and arg[2:].startswith(str(OWNER)) and not arg[2:].startswith(str(OWNER/'build')):arg='-I'+str(tree)+arg[2+len(str(OWNER)):]
  clean.append(arg);i+=1
 clean[1:1]=['-I'+str(IMPL/'elm-seat-publication-v79/build-1791106084855005199/inputs/candidate/include'),'-I'+str(OUT/'inputs/candidate'),'-MD','-MF',str(dep)]
 run('pointer-compile',clean)
 r['dependencies']={}
 for name in shlex.split(dep.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]):
  p=Path(name);p=(p if p.is_absolute() else OWNER/'build'/p).resolve();r['dependencies'][str(p)]=sha(p)
 assert not any(p.startswith(str(OWNER/'src')+'/') or p.startswith(str(OWNER/'protocols')+'/') or p.startswith('/usr/include/hyprland') for p in r['dependencies'])
 target=OUT/'libhyprland_lib.a';shutil.copy2(archive,target);run('archive',['/usr/bin/ar','r',target,obj]);new=archive_payloads(target)
 assert len(new)==len(old)
 for b,a in zip(old,new):
  assert b['name']==a['name']
  if a['name']=='PointerManager.cpp.o':assert a['sha256']==sha(obj)
  else:assert b==a,b['name']
 for name,data in [('ancestor-archive-payloads.json',old),('new-archive-payloads.json',new)]: (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
 link=list(next(c['command'] for c in prior['commands'] if c['name']=='link'));oldaq=next(a for a in link if Path(a).name=='libaquamarine.so.0.15.0');assert sha(AQ)=='ee8c53016d47a1a9ef6804130e40dc4f1dd2f1106b4f2794798bd6ca2b98e674'
 for i,a in enumerate(link):
  if i and link[i-1]=='-o':link[i]=str(OUT/'Hyprland')
  elif a==str(archive):link[i]=str(target)
  elif a==oldaq:link[i]=str(AQ)
  elif a.startswith('-Wl,--dependency-file='):link[i]='-Wl,--dependency-file='+str(OUT/'link.d')
 run('link',link);deps=linkdeps(OUT/'link.d');r['ancestorLinkDependencies']=prior['linkDependencies'];r['linkDependencies']=deps
 expected={str(target.resolve()) if p==str(archive.resolve()) else str(AQ.resolve()) if p==str(Path(oldaq).resolve()) else p:sha(target) if p==str(archive.resolve()) else sha(AQ) if p==str(Path(oldaq).resolve()) else value for p,value in prior['linkDependencies'].items()};assert deps==expected,'Link closure differs beyond archive and selected AQ'
 replay=list(link)
 for i,a in enumerate(replay):
  if i and replay[i-1]=='-o':replay[i]=str(OUT/'Hyprland-relink')
  elif a.startswith('-Wl,--dependency-file='):replay[i]='-Wl,--dependency-file='+str(OUT/'relink.d')
 run('relink',replay);assert sha(OUT/'Hyprland')==sha(OUT/'Hyprland-relink') and linkdeps(OUT/'relink.d')==deps
 exports={}
 for name,binary in [('ancestor',prior['binary']),('candidate',OUT/'Hyprland')]:exports[name]={(l.split()[1],l.split()[2]) for l in run(name+'-exports',['/usr/bin/nm','-D','--defined-only',binary]).decode().splitlines()}
 missing=sorted(exports['ancestor']-exports['candidate']);assert not missing,missing;r['exportClosure']={'ancestorCount':len(exports['ancestor']),'candidateCount':len(exports['candidate']),'missingSymbols':missing}
 linked={};text=run('binary-libraries',['/usr/bin/ldd',OUT/'Hyprland']).decode();assert 'not found' not in text
 for line in text.splitlines():
  for word in line.split():
   if word.startswith('/') and Path(word).is_file():p=Path(word).resolve();linked[str(p)]=sha(p)
 r['linkedLibraries']=linked
 for section in [r['tools'],r['dependencies'],r['linkDependencies'],r['ancestorLinkDependencies'],linked]:
  for p,wanted in section.items():assert sha(p)==wanted,p
 for rel,wanted in headers.items():assert sha(tree/rel)==wanted,rel
 for rel,wanted in inputs.items():assert sha(ROOT/rel)==sha(OUT/'inputs'/rel)==wanted,rel
 assert sha(archive)==prior['archiveSHA256'] and sha(prior['binary'])==prior['binarySHA256']
 r.update(passed=True,binary=str(OUT/'Hyprland'),binarySHA256=sha(OUT/'Hyprland'),archiveSHA256=sha(target),rebuiltArchiveMembers={'PointerManager.cpp.o':sha(obj)},unchangedArchiveMembers=432,owningVersionHeaderSHA256=headers['src/version.h'],existingPublicHeadersUnchanged=True,geometryAndReloadArchivePayloadsPreserved=True,aqLibrary=str(AQ),aqLibrarySHA256=sha(AQ))
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
