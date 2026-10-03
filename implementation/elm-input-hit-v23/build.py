"""Fresh native first-class minimize derivative; preserve prior modal/MAX/renderer fixes."""
import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2'
PREVIOUS=REPO/'implementation/elm-surface-facts-v20/build-1791065974847738580'
OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir()
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
report={'passed':False,'installed':False,'scope':'Native first-class minimized state/core exclusion build; no native acceptance','commands':[]}
sources=['src/desktop/state/ViewHitTester.cpp']
shutil.copy2(__file__,OUT/'build.py')
for path in [ROOT/'candidate/SceneModal.hpp',ROOT/'candidate/WindowPolicy.hpp',ROOT/'candidate/SceneTrace.hpp',*[ROOT/'candidate'/s for s in sources]]:
 dest=OUT/'inputs'/path.relative_to(ROOT/'candidate');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
report['sources']={str(p.relative_to(OUT/'inputs')):digest(p) for p in sorted((OUT/'inputs').rglob('*')) if p.is_file()}
def run(name,command):
 p=subprocess.run(command,cwd=OWNER/'build',capture_output=True,timeout=180)
 (OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
 report['commands'].append({'name':name,'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr.decode(errors='replace')
try:
 prior_path=PREVIOUS/'report.json';prior=json.loads(prior_path.read_text());assert prior['passed'] and digest(prior['binary'])==prior['binarySHA256']
 archive=PREVIOUS/'libhyprland_lib.a';archive_hash=digest(archive);report['priorReportSHA256']=digest(prior_path);report['dependencies']={};objects=[]
 for relative in sources:
  command=list(prior['commands'][0]['command']);source=OUT/'inputs'/relative;obj=OUT/(source.name+'.o');dep=OUT/(source.name+'.d')
  for i,arg in enumerate(command):
   if arg.startswith('-I') and arg.endswith('/inputs'):command[i]='-I'+str(OUT/'inputs')
   elif arg.startswith('-I') and arg.endswith('/src/desktop/state'):command[i]='-I'+str(OWNER/Path(relative).parent)
   elif i and command[i-1]=='-c':command[i]=str(source)
   elif i and command[i-1]=='-o':command[i]=str(obj)
   elif i and command[i-1]=='-MF':command[i]=str(dep)
  command.insert(1,'-I'+str(OWNER/Path(relative).parent));command.insert(1,'-I'+str(OUT/'inputs'));run(source.stem+'-compile',command)
  paths=shlex.split(dep.read_text().replace('\\\n',' ').split(':',1)[1]);report['dependencies'].update({str(Path(p).resolve()):digest(p) for p in paths});objects.append(str(obj))
 assert not any(p.startswith('/usr/include/hyprland') for p in report['dependencies'])
 shutil.copy2(archive,OUT/'libhyprland_lib.a');run('archive',['/usr/bin/ar','r',str(OUT/'libhyprland_lib.a'),*objects])
 link=list(prior['commands'][-1]['command'])
 for i,arg in enumerate(link):
  if i and link[i-1]=='-o':link[i]=str(OUT/'Hyprland')
  elif arg==str(archive):link[i]=str(OUT/'libhyprland_lib.a')
  elif arg.startswith('-Wl,--dependency-file='):link[i]='-Wl,--dependency-file='+str(OUT/'link.d')
 run('link',link);assert digest(archive)==archive_hash and digest(prior['binary'])==prior['binarySHA256']
 report.update(passed=True,binary=str(OUT/'Hyprland'),binarySHA256=digest(OUT/'Hyprland'),ancestorBinaryPreserved=True,ancestorArchivePreserved=True,owningVersionHeaderSHA256=digest(OWNER/'src/version.h'))
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'),flush=True);raise SystemExit(not report['passed'])
