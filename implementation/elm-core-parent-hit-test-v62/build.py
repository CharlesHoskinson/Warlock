"""Rebuild pointer and visible-window commit objects atop the accepted V47 monitor-reload core."""
import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
from archive import archive_payloads
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;IMPL=ROOT.parent
OWNER=IMPL/'maximized-stack-v1/native-core-v2'
PRIOR=IMPL/'elm-core-monitor-reload-v47/build-1791101203494513446'
AQ=IMPL/'elm-nested-input-status-v30/build-1791098020734308423'
OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'passed':False,'installed':False,'nativeAcceptance':False,'scope':'Owning parent hit-test incremental core compile; unchanged V47 reload object and V30 AQ; fresh plugin/native qualification required','commands':[]}
def run(name,cmd):
 p=subprocess.run(cmd,cwd=OWNER/'build',capture_output=True,timeout=180)
 (OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
 r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr.decode(errors='replace')[-4000:];return p.stdout
try:
 model_path=IMPL/'elm-parent-hit-test-model-v63/qa/model-1791103227852833622/report.json'
 cpus=sorted((ROOT/'qa').glob('test-*/report.json'));assert cpus
 cpu_path=cpus[-1];model=json.loads(model_path.read_text());cpu=json.loads(cpu_path.read_text())
 assert model['passed'] and cpu['passed'] and model['mutantsRejected']==5 and cpu['mutantsRejected']==4
 for path,digest in cpu['inputs'].items():assert sha(path)==digest,path
 for packet,path in [(model,model_path),(cpu,cpu_path)]:
  for rel,digest in packet['artifacts'].items():assert sha(path.parent/rel)==digest,rel
 r['proofReports']=[{'path':str(p),'sha256':sha(p)} for p in [model_path,cpu_path]]
 files=[ROOT/'build.py',ROOT/'archive.py',ROOT/'qa/test.py',ROOT/'qa/template.cpp',ROOT/'qa/test2.py',ROOT/'qa/template2.cpp',*sorted(p for p in (ROOT/'candidate').rglob('*') if p.is_file())]
 r['inputs']={str(p.relative_to(ROOT)):sha(p) for p in files}
 for p in files:
  dst=OUT/'inputs'/p.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
 prior=json.loads((PRIOR/'report.json').read_text());assert prior['passed']
 archive=PRIOR/'libhyprland_lib.a';assert sha(archive)==prior['archiveSHA256'] and sha(prior['binary'])==prior['binarySHA256']
 r.update(ancestorReport=str(PRIOR/'report.json'),ancestorReportSHA256=sha(PRIOR/'report.json'),ancestorCore={'path':prior['binary'],'sha256':prior['binarySHA256']},ancestorArchive={'path':str(archive),'sha256':prior['archiveSHA256']},owningVersionHeaderSHA256=sha(OWNER/'src/version.h'),aqLibrary=prior['aqLibrary'],aqLibrarySHA256=prior['aqLibrarySHA256'])
 assert sha(r['aqLibrary'])==r['aqLibrarySHA256']
 original=OWNER/'src/pointer/PointerManager.cpp';owning_object=OWNER/'build/CMakeFiles/hyprland_lib.dir/src/pointer/PointerManager.cpp.o'
 r['originalSourceSHA256']=sha(original);r['owningObjectSHA256']=sha(owning_object)
 shutil.copy2(original,OUT/'original-PointerManager.cpp')
 old=archive_payloads(archive);assert sum(e['name']=='PointerManager.cpp.o' for e in old)==1
 old_pointer=IMPL/'elm-core-parent-position-v31/build-1791098227819326160/report.json'
 assert next(e['sha256'] for e in old if e['name']=='PointerManager.cpp.o')==json.loads(old_pointer.read_text())['newPointerObjectSHA256']
 entry=next(e for e in json.loads((OWNER/'build/compile_commands.json').read_text()) if Path(e['file'])==original)
 r['originalCompileEntry']=entry;cmd=shlex.split(entry['command'])
 cmd.insert(1,'-I'+str(AQ/'inputs/candidate/include'));cmd.insert(1,'-I'+str(original.parent));cmd.insert(1,'-I'+str(OUT/'inputs/candidate'))
 source=OUT/'inputs/candidate/src/pointer/PointerManager.cpp';obj=OUT/'PointerManager.cpp.o';dep=OUT/'PointerManager.cpp.d'
 for i,arg in enumerate(cmd):
  if i and cmd[i-1]=='-c':cmd[i]=str(source)
  elif i and cmd[i-1]=='-o':cmd[i]=str(obj)
 cmd.extend(['-MD','-MF',str(dep)]);run('compile',cmd)
 paths=shlex.split(dep.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1])
 r['dependencies']={str(Path(p).resolve()):sha(Path(p).resolve()) for p in paths}
 assert not any(p.startswith('/usr/include/hyprland') for p in r['dependencies'])
 window_original=OWNER/'src/desktop/view/Window.cpp';window_owning=OWNER/'build/CMakeFiles/hyprland_lib.dir/src/desktop/view/Window.cpp.o'
 r['windowOriginalSourceSHA256']=sha(window_original);r['windowOwningObjectSHA256']=sha(window_owning)
 assert sum(e['name']=='Window.cpp.o' for e in old)==1 and next(e['sha256'] for e in old if e['name']=='Window.cpp.o')==sha(window_owning)
 shutil.copy2(window_original,OUT/'original-Window.cpp')
 entry=next(e for e in json.loads((OWNER/'build/compile_commands.json').read_text()) if Path(e['file'])==window_original)
 r['windowCompileEntry']=entry;cmd=shlex.split(entry['command']);cmd.insert(1,'-I'+str(window_original.parent));cmd.insert(1,'-I'+str(OUT/'inputs/candidate'))
 window_obj=OUT/'Window.cpp.o';window_dep=OUT/'Window.cpp.d'
 for i,arg in enumerate(cmd):
  if i and cmd[i-1]=='-c':cmd[i]=str(OUT/'inputs/candidate/src/desktop/view/Window.cpp')
  elif i and cmd[i-1]=='-o':cmd[i]=str(window_obj)
 cmd.extend(['-MD','-MF',str(window_dep)]);run('window-compile',cmd)
 for p in shlex.split(window_dep.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]):r['dependencies'][str(Path(p).resolve())]=sha(Path(p).resolve())
 target=OUT/'libhyprland_lib.a';shutil.copy2(archive,target);run('archive',['ar','r',str(target),str(obj),str(window_obj)])
 new=archive_payloads(target);assert len(new)==len(old)
 for before,after in zip(old,new):
  assert before['name']==after['name']
  if before['name']=='PointerManager.cpp.o':assert after['sha256']==sha(obj)
  elif before['name']=='Window.cpp.o':assert after['sha256']==sha(window_obj)
  else:assert before==after,before['name']
 for name,data in [('ancestor-archive-payloads.json',old),('new-archive-payloads.json',new)]:
  (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
 link=list(prior['commands'][-1]['command']);assert prior['commands'][-1]['name']=='link'
 for i,arg in enumerate(link):
  if i and link[i-1]=='-o':link[i]=str(OUT/'Hyprland')
  elif arg==str(archive):link[i]=str(target)
  elif arg.startswith('-Wl,--dependency-file='):link[i]='-Wl,--dependency-file='+str(OUT/'link.d')
 run('link',link)
 assert sha(window_original)==r['windowOriginalSourceSHA256'] and sha(window_owning)==r['windowOwningObjectSHA256']
 assert sha(archive)==prior['archiveSHA256'] and sha(original)==r['originalSourceSHA256'] and sha(owning_object)==r['owningObjectSHA256']
 for rel,digest in r['inputs'].items():assert sha(ROOT/rel)==sha(OUT/'inputs'/rel)==digest,rel
 r.update(passed=True,binary=str(OUT/'Hyprland'),binarySHA256=sha(OUT/'Hyprland'),archiveSHA256=sha(target),newPointerObjectSHA256=sha(obj),newWindowObjectSHA256=sha(window_obj),unchangedArchiveMembers=len(old)-2,ancestorBinaryPreserved=True,ancestorArchivePreserved=True,originalSourcePreserved=True,existingPublicHeadersUnchanged=True)
except Exception as error:r['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
