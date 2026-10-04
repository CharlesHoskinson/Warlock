"""Rebuild the complete XDG header consumer closure against a captured overlay."""
import hashlib,json,os,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[2]
OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2'
PRIOR=REPO/'implementation/elm-core-parent-hit-test-v72/build-1791104632059591332'
GEOMETRY=REPO/'implementation/elm-window-geometry-default-limits-v40/core/build-1791101053270682069'
HEADER_BUILD=REPO/'implementation/elm-geometry-authority-pair-v34/qa/build-1791098894593705078'
OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
r={'passed':False,'installed':False,'nativeAcceptance':False,'scope':'Actual full XDG header consumer closure rebuild, exact ancestor source retention and ordered archive/link closure; no plugin or GUI qualification','commands':[]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def payloads(p):
 entries=[];longnames=b''
 with Path(p).open('rb') as f:
  assert f.read(8)==b'!<arch>\n'
  while True:
   header=f.read(60)
   if not header:break
   assert len(header)==60 and header[58:60]==b'`\n';name=header[:16].decode().strip();size=int(header[48:58]);remaining=size
   if name=='//':longnames=f.read(size);assert len(longnames)==size;remaining=0
   elif name not in ['/','/SYM64/']:
    if name.startswith('/'):
     start=int(name[1:]);end=longnames.index(b'/\n',start);name=longnames[start:end].decode()
    else:name=name.rstrip('/')
    h=hashlib.sha256()
    while remaining:
     part=f.read(min(remaining,1024*1024));assert part;remaining-=len(part);h.update(part)
    entries.append({'name':name,'size':size,'sha256':h.hexdigest()})
   if remaining:f.seek(remaining,1)
   if size%2:assert f.read(1)==b'\n'
 return entries

def run(name,command,cwd=None):
 p=subprocess.run(list(map(str,command)),cwd=cwd,capture_output=True,timeout=240)
 (OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
 r['commands'].append({'name':name,'command':list(map(str,command)),'cwd':str(cwd) if cwd else None,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr.decode(errors='replace')[-6000:]
 return p.stdout
try:
 shutil.copy2(Path(__file__),OUT/'initial-build.py')
 previous=json.loads((PRIOR/'report.json').read_text());assert previous['passed'] and sha(previous['binary'])==previous['binarySHA256']
 for path,wanted in previous['dependencies'].items():assert sha(path)==wanted,path
 for rel,wanted in previous['inputs'].items():assert sha(PRIOR/'inputs'/rel)==wanted,rel
 tools={str(Path(shutil.which(name)).resolve()):sha(Path(shutil.which(name)).resolve()) for name in ['c++','ar','ld','nm','ldd']};r['tools']=tools
 archive=PRIOR/'libhyprland_lib.a';archive_hash=sha(archive);assert archive_hash==previous['archiveSHA256']
 before=payloads(archive);assert len(before)==433;byname={row['name']:row for row in before}
 r['ancestor']={'report':str(PRIOR/'report.json'),'reportSHA256':sha(PRIOR/'report.json'),'binary':previous['binary'],'binarySHA256':previous['binarySHA256'],'archive':str(archive),'archiveSHA256':archive_hash}
 db=OWNER/'build/compile_commands.json';rows=json.loads(db.read_text());r['compileDatabaseSHA256']=sha(db)
 target=(OWNER/'src/protocols/XDGShell.hpp').resolve();affected=[];scan={}
 for row in rows:
  if not row['output'].endswith('.o'):continue
  dep=OWNER/'build'/(row['output']+'.d');assert dep.is_file(),str(dep);scan[str(dep)]=sha(dep)
  paths=shlex.split(dep.read_text().replace('\\\n',' ').split(':',1)[1]);paths=[(Path(p) if Path(p).is_absolute() else OWNER/'build'/p).resolve() for p in paths]
  if target in paths or row['file'].endswith('/FullscreenController.cpp'):affected.append(row)
 pch=OWNER/'build/CMakeFiles/hyprland_lib.dir/cmake_pch.hxx.gch.d';scan[str(pch)]=sha(pch)
 assert str(target) not in pch.read_text(),'Changed header entered PCH; recompute consumer closure'
 assert len(affected)==17,len(affected)
 r['consumerDependencyInventories']=scan;r['affectedTranslationUnits']=[str(Path(row['file']).relative_to(OWNER)) for row in affected]
 # Capture source changes and both tests before compilation; adapters/native plugins are outside V40.
 own=[Path(__file__),ROOT/'qa/limits-test.py',*sorted((ROOT/'candidate').rglob('*'))];own=[p for p in own if p.is_file()]
 inputs={str(p.relative_to(ROOT)):sha(p) for p in own};r['inputs']=inputs
 for p in own:
  dest=OUT/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);dest.chmod(0o444)
 header_report=json.loads((HEADER_BUILD/'report.json').read_text());assert header_report['passed'] and len(header_report['owningHeaders'])==660
 header_sources={}
 # Capture every owning header, including additional core-only dependencies.
 for base in ['src','protocols','subprojects/udis86']:
  for p in (OWNER/base).rglob('*'):
   if p.is_file() and p.suffix in ['.hpp','.h','.inl','.inc','.hxx'] and '.git' not in p.parts:
    header_sources[str(p.relative_to(OWNER))]=sha(p)
 for rel,wanted in header_report['owningHeaders'].items():
  assert sha(HEADER_BUILD/'owning-headers'/rel)==sha(OWNER/rel)==wanted,rel
  header_sources[rel]=wanted
 tree=OUT/'owning-headers';tree.mkdir();header_hashes={}
 for rel,wanted in header_sources.items():
  source=OWNER/rel;dest=tree/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
  if rel=='src/protocols/XDGShell.hpp':shutil.copy2(ROOT/'candidate'/rel,dest)
  header_hashes[rel]=sha(dest);dest.chmod(0o444)
 assert sum(header_hashes[k]!=v for k,v in header_sources.items())==1
 parent_headers={}
 for source in sorted((ROOT/'candidate/src/pointer').glob('*.hpp')):
  rel=str(source.relative_to(ROOT/'candidate'));dest=tree/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);dest.chmod(0o444)
  header_hashes[rel]=sha(dest);parent_headers[rel]=sha(source)
 r['parentHitTestHeaders']=parent_headers
 r['owningHeaderOrigins']=header_sources;r['owningHeaders']=header_hashes
 for name in ['WindowPolicy.hpp','SceneModal.hpp','SceneTrace.hpp']:
  source=PRIOR/'inputs/candidate'/name;dest=OUT/'inputs/candidate'/name;shutil.copy2(source,dest);dest.chmod(0o444)
 r['retainedPolicyHeaders']={str(OUT/'inputs/candidate'/name):sha(OUT/'inputs/candidate'/name) for name in ['WindowPolicy.hpp','SceneModal.hpp','SceneTrace.hpp']}
 geometry_report=json.loads((GEOMETRY/'report.json').read_text());assert geometry_report['passed']
 for path,digest in geometry_report['dependencies'].items():assert sha(path)==digest,path
 r['geometryAncestor']={'report':str(GEOMETRY/'report.json'),'sha256':sha(GEOMETRY/'report.json')}
 r['sourceOrigins']={};r['dependencies']={};objects=[]
 for row in affected:
  rel=str(Path(row['file']).relative_to(OWNER));member=Path(rel).name+'.o';assert sum(b['name']==member for b in before)==1
  source=GEOMETRY/'owning-headers'/rel
  assert str(source) in geometry_report['dependencies'] and sha(source)==geometry_report['dependencies'][str(source)],rel
  candidate=ROOT/'candidate'/rel
  if candidate.exists():
   if rel=='src/desktop/view/Window.cpp':
    addition='    // GTK/client buffer and input-region updates can arrive after monitor layout.\n    // Only a current nested-parent anchor schedules work; normal hit testing\n    // retains grabs, surface ownership and focus policy.\n    Pointer::refreshParentHitTest(m_self.lock());\n'
    assert candidate.read_text().replace(addition,'').replace('#include "../../pointer/ParentPointerFocus.hpp"\n','')==source.read_text()
   else:assert sha(candidate)==sha(source),rel
   selected=candidate
  else:selected=source
  evidence={'geometrySource':str(source),'geometrySourceSHA256':sha(source),'selectedSource':str(selected),'selectedSourceSHA256':sha(selected),'ancestorArchiveMember':byname[member]}
  source=selected;r['sourceOrigins'][rel]=evidence
  dest=tree/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);dest.chmod(0o444)
  r['sourceOrigins'][rel]=evidence
  obj=OUT/member;dep=OUT/(member+'.d');command=shlex.split(row['command']);clean=[];i=0
  while i<len(command):
   arg=command[i]
   if arg=='-include':i+=2;continue # Never reuse an owning mutable precompiled header.
   if i and command[i-1]=='-c':arg=str(dest)
   elif i and command[i-1]=='-o':arg=str(obj)
   elif arg.startswith('-I'):
    path=arg[2:]
    if path.startswith(str(OWNER)) and not path.startswith(str(OWNER/'build')):arg='-I'+str(tree)+path[len(str(OWNER)):]
   clean.append(arg);i+=1
  clean[1:1]=['-I'+str(OUT/'inputs/candidate'),'-MD','-MF',str(dep)]
  run(Path(rel).stem+'-compile',clean,OWNER/'build')
  for name in shlex.split(dep.read_text().replace('\\\n',' ').split(':',1)[1]):
   p=Path(name);p=(p if p.is_absolute() else OWNER/'build'/p).resolve();r['dependencies'][str(p)]=sha(p)
  objects.append(obj)
 assert not any(p.startswith(str(OWNER/'src')+'/') or p.startswith(str(OWNER/'protocols')+'/') or p.startswith('/usr/include/hyprland') for p in r['dependencies']),'Owning header overlay bypassed'
 target_archive=OUT/'libhyprland_lib.a';shutil.copy2(archive,target_archive);run('archive',['/usr/bin/ar','r',target_archive,*objects])
 after=payloads(target_archive);changed={obj.name:sha(obj) for obj in objects};seen=set()
 assert len(before)==len(after)==433
 for b,a in zip(before,after):
  assert b['name']==a['name']
  if a['name'] in changed:assert a['sha256']==changed[a['name']];seen.add(a['name'])
  else:assert b==a,b['name']
 assert seen==set(changed)
 (OUT/'ancestor-archive-payloads.json').write_text(json.dumps(before,indent=2)+'\n');(OUT/'new-archive-payloads.json').write_text(json.dumps(after,indent=2)+'\n')
 link=list(previous['commands'][-1]['command'])
 for i,arg in enumerate(link):
  if i and link[i-1]=='-o':link[i]=str(OUT/'Hyprland')
  elif arg==str(archive):link[i]=str(target_archive)
  elif arg.startswith('-Wl,--dependency-file='):link[i]='-Wl,--dependency-file='+str(OUT/'link.d')
 def link_dependencies(path):
  names=shlex.split(path.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]);names=names[:next((i for i,n in enumerate(names) if n.endswith(':')),len(names))]
  paths={(Path(n) if Path(n).is_absolute() else OWNER/'build'/n).resolve() for n in names};assert paths and all(p.is_file() for p in paths)
  return {str(p):sha(p) for p in sorted(paths)}
 old_link_dependencies=link_dependencies(PRIOR/'link.d');r['ancestorLinkDependencies']=old_link_dependencies
 run('link',link,OWNER/'build')
 link_inputs=link_dependencies(OUT/'link.d');r['linkDependencies']=link_inputs
 expected_link={str(target_archive.resolve()) if p==str(archive.resolve()) else p:sha(target_archive) if p==str(archive.resolve()) else value for p,value in old_link_dependencies.items()}
 assert link_inputs==expected_link,'Link closure differs beyond selected archive'
 replay=list(link)
 for i,arg in enumerate(replay):
  if i and replay[i-1]=='-o':replay[i]=str(OUT/'Hyprland-relink')
  elif arg.startswith('-Wl,--dependency-file='):replay[i]='-Wl,--dependency-file='+str(OUT/'relink.d')
 run('relink',replay,OWNER/'build');assert sha(OUT/'Hyprland')==sha(OUT/'Hyprland-relink') and link_dependencies(OUT/'relink.d')==link_inputs
 symbols={}
 for name,binary in [('ancestor',previous['binary']),('candidate',OUT/'Hyprland')]:
  rows=run(name+'-exports',['/usr/bin/nm','-D','--defined-only',binary]).decode().splitlines();assert all(len(line.split())==3 for line in rows)
  symbols[name]={(line.split()[1],line.split()[2]) for line in rows}
 missing=sorted(symbols['ancestor']-symbols['candidate']);assert not missing,missing
 r['exportClosure']={'ancestorCount':len(symbols['ancestor']),'candidateCount':len(symbols['candidate']),'missingSymbols':missing}
 linked={}
 text=run('binary-libraries',['/usr/bin/ldd',OUT/'Hyprland']).decode();assert 'not found' not in text
 for line in text.splitlines():
  for word in line.split():
   if word.startswith('/') and Path(word).is_file():path=Path(word).resolve();linked[str(path)]=sha(path)
 r['linkedLibraries']=linked
 for section in [tools,link_inputs,old_link_dependencies,linked]:
  for path,wanted in section.items():assert sha(path)==wanted,path
 for rel,wanted in inputs.items():assert sha(ROOT/rel)==sha(OUT/'inputs'/rel)==wanted,rel
 for rel,wanted in header_sources.items():assert sha(OWNER/rel)==wanted,rel
 for rel,wanted in header_hashes.items():assert sha(tree/rel)==wanted,rel
 for rel,entry in r['sourceOrigins'].items():
  assert sha(entry['geometrySource'])==entry['geometrySourceSHA256'],rel
  assert sha(entry['selectedSource'])==entry['selectedSourceSHA256'],rel
  member=Path(rel).name+'.o'
  assert entry['ancestorArchiveMember']==byname[member],rel
  assert sha(tree/rel)==entry['selectedSourceSHA256'],rel
 for p,wanted in r['dependencies'].items():assert sha(p)==wanted,p
 for p,wanted in scan.items():assert sha(p)==wanted,p
 assert sha(archive)==archive_hash and sha(previous['binary'])==previous['binarySHA256']
 r.update(passed=True,binary=str(OUT/'Hyprland'),binarySHA256=sha(OUT/'Hyprland'),archiveSHA256=sha(target_archive),rebuiltArchiveMembers=changed,unchangedArchiveMembers=416,owningVersionHeaderSHA256=sha(OWNER/'src/version.h'))
except Exception as error:r['error']=repr(error)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}),flush=True);raise SystemExit(not r['passed'])
