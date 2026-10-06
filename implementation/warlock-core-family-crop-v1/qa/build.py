"""Protected two owning TUs, ordered archive preservation and exact relink."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
from archive import archive_payloads,replace_payload
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2';PRIOR=REPO/'implementation/warlock-core-family-render-v4/build-1791258416417807170'
OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'installed':False,'scope':'Owning native family crop bounds and framebuffer; Renderer/OpenGL compiled,431 ordered archive members retained; existing public object layouts unchanged; native qualification separate','commands':[]}
def run(name,argv):
 p=subprocess.run(list(map(str,argv)),cwd=OWNER/'build',capture_output=True,timeout=240);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':list(map(str,argv)),'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr.decode(errors='replace')[-2500:];return p.stdout
try:
 prior=json.loads((PRIOR/'report.json').read_text());assert prior['passed'] and sha(PRIOR/'libhyprland_lib.a')==prior['archiveSHA256']
 old=archive_payloads(PRIOR/'libhyprland_lib.a');assert len(old)==433
 oldObjects={'Renderer':prior['rebuiltArchiveMembers']['Renderer.cpp.o'],'OpenGL':sha(OWNER/'build/CMakeFiles/hyprland_lib.dir/src/render/OpenGL.cpp.o')}
 assert sha(PRIOR/'Renderer.cpp.o')==oldObjects['Renderer']
 for unit,digest in oldObjects.items():assert sum(x['sha256']==digest and x['name']==unit+'.cpp.o' for x in old)==1
 assert 'Desktop::WindowPolicy::isMinimized' in (ROOT/'candidate/src/render/Renderer.cpp').read_text()
 tree=OUT/'owning-headers';headers=dict(prior['owningHeaders'])
 for rel,digest in headers.items():
  p=PRIOR/'owning-headers'/rel;assert sha(p)==digest;q=tree/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 for p in (ROOT/'candidate').rglob('*'):
  if not p.is_file():continue
  rel=str(p.relative_to(ROOT/'candidate'));q=tree/rel;q.parent.mkdir(parents=True,exist_ok=True)
  if q.exists():q.chmod(0o644)
  shutil.copy2(p,q)
  if rel.endswith('.hpp'):headers[rel]=sha(q)
 def deps(p):
  names=shlex.split(p.read_text().replace('\\\n',' ').split(':',1)[1]);names=names[:next((i for i,n in enumerate(names) if n.endswith(':')),len(names))];return {str((pathlib.Path(n) if pathlib.Path(n).is_absolute() else OWNER/'build'/n).resolve()):sha(pathlib.Path(n) if pathlib.Path(n).is_absolute() else OWNER/'build'/n) for n in names}
 policyInclude=OUT/'inputs/candidate';policyInclude.mkdir(parents=True)
 for path,digest in prior['retainedPolicyHeaders'].items():assert sha(path)==digest;shutil.copy2(path,policyInclude/pathlib.Path(path).name)
 compileDeps={};objects={};originals={}
 for unit in ['Renderer','OpenGL']:
  original=OWNER/('src/render/'+unit+'.cpp');originals[unit]=sha(original)
  archived=subprocess.check_output(['git','show','HEAD:'+str(original.relative_to(REPO))],cwd=REPO);assert archived==original.read_bytes()
  entry=next(x for x in json.loads((OWNER/'build/compile_commands.json').read_text()) if x['file']==str(original));args=shlex.split(entry['command']);cmd=[];i=0
  while i<len(args):
   a=args[i]
   if a in ['-o','-include']:i+=2;continue
   if a=='-c' or a==str(original):i+=1;continue
   if a.startswith('-I'+str(OWNER)) and '/build/' not in a and '/subprojects/' not in a:a='-I'+str(tree)+a[len('-I'+str(OWNER)):]
   cmd.append(a);i+=1
  obj=OUT/(unit+'.cpp.o');dep=OUT/(unit+'.d');cmd+=['-I'+str(policyInclude),'-MD','-MF',str(dep),'-o',str(obj),'-c',str(tree/('src/render/'+unit+'.cpp'))];run('compile-'+unit,cmd);objects[unit]=obj;compileDeps.update(deps(dep))
 assert not any(p.startswith('/usr/include/hyprland') or p.startswith(str(OWNER)+'/src/') for p in compileDeps)
 archive=OUT/'libhyprland_lib.a';temporary=OUT/'archive-first.tmp';replace_payload(PRIOR/'libhyprland_lib.a',temporary,oldObjects['Renderer'],objects['Renderer']);replace_payload(temporary,archive,oldObjects['OpenGL'],objects['OpenGL']);temporary.unlink();run('archive-index',['ar','s',archive]);new=archive_payloads(archive);assert len(new)==433
 replacements={oldObjects[unit]:sha(objects[unit]) for unit in objects}
 for a,b in zip(old,new):
  assert a['name']==b['name'];assert b['sha256']==replacements[a['sha256']] if a['sha256'] in replacements else a==b
 (OUT/'ancestor-archive-payloads.json').write_text(json.dumps(old,indent=2)+'\n');(OUT/'new-archive-payloads.json').write_text(json.dumps(new,indent=2)+'\n')
 link=list(next(x['command'] for x in prior['commands'] if x['name']=='link'))
 for i,a in enumerate(link):
  if i and link[i-1]=='-o':link[i]=str(OUT/'Hyprland')
  elif a==str(PRIOR/'libhyprland_lib.a'):link[i]=str(archive)
  elif a.startswith('-Wl,--dependency-file='):link[i]='-Wl,--dependency-file='+str(OUT/'link.d')
 run('link',link);actual=deps(OUT/'link.d');expected={str(archive) if p==str(PRIOR/'libhyprland_lib.a') else p:sha(archive) if p==str(PRIOR/'libhyprland_lib.a') else digest for p,digest in prior['linkDependencies'].items()};assert actual==expected
 replay=list(link)
 for i,a in enumerate(replay):
  if i and replay[i-1]=='-o':replay[i]=str(OUT/'Hyprland-relink')
  elif a.startswith('-Wl,--dependency-file='):replay[i]='-Wl,--dependency-file='+str(OUT/'relink.d')
 run('relink',replay);assert sha(OUT/'Hyprland')==sha(OUT/'Hyprland-relink') and deps(OUT/'relink.d')==actual
 exports=[]
 for name,p in [('ancestor',prior['binary']),('candidate',OUT/'Hyprland')]:exports.append({tuple(row.split()[1:]) for row in run(name+'-exports',['nm','-D','--defined-only',p]).decode().splitlines()})
 assert not exports[0]-exports[1],str(sorted(exports[0]-exports[1]))[:2000]
 for symbol in ['makeFamilySnapshotFB','makeFamilyCropFB','familyCropBounds','familyCropPixelBounds','appliedSurfaceRevision']:assert any(symbol in x[1] for x in exports[1])
 linked={}
 for line in run('libraries',['ldd',OUT/'Hyprland']).decode().splitlines():
  assert 'not found' not in line
  for word in line.split():
   if word.startswith('/') and pathlib.Path(word).is_file():linked[str(pathlib.Path(word).resolve())]=sha(pathlib.Path(word).resolve())
 retained={}
 for path,digest in prior['retainedPolicyHeaders'].items():q=policyInclude/pathlib.Path(path).name;assert sha(path)==digest and sha(q)==digest;retained[str(q)]=digest
 for rel,digest in headers.items():assert sha(tree/rel)==digest
 r.update(passed=True,binary=str(OUT/'Hyprland'),binarySHA256=sha(OUT/'Hyprland'),archiveSHA256=sha(archive),owningHeaders=headers,owningVersionHeaderSHA256=prior['owningVersionHeaderSHA256'],rebuiltArchiveMembers={unit+'.cpp.o':sha(objects[unit]) for unit in objects},originalArchiveMembers=oldObjects,unchangedArchiveMembers=431,existingPublicHeadersUnchanged=False,existingObjectLayoutsUnchanged=True,ancestor={'report':str(PRIOR/'report.json'),'reportSHA256':sha(PRIOR/'report.json')},retainedPolicyHeaders=retained,dependencies=compileDeps,linkDependencies=actual,linkedLibraries=linked,tools={str(pathlib.Path(shutil.which(n)).resolve()):sha(pathlib.Path(shutil.which(n)).resolve()) for n in ['c++','ar','nm','ldd']},aqLibrary=prior['aqLibrary'],aqLibrarySHA256=prior['aqLibrarySHA256'],inputs={str(p.relative_to(ROOT)):sha(p) for p in [*sorted((ROOT/'candidate').rglob('*')),*sorted((ROOT/'qa').glob('*')),ROOT/'SPEC.md'] if p.is_file()},sourceSHA256=sha(ROOT/'candidate/src/render/Renderer.cpp'),originalSources=originals)
except Exception as e:
 import traceback
 r['error']=repr(e);r['traceback']=traceback.format_exc()
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:
 files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in ROOT.rglob('*') if p.is_file()};(ROOT/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'buildReport':str(OUT/'report.json'),'buildReportSHA256':sha(OUT/'report.json'),'files':files},indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
