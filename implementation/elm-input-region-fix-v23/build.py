"""Replace only the owning hit-test object in the frozen V20 archive."""
import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1), 'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2'
PRIOR=REPO/'implementation/elm-surface-facts-v20/build-1791065974847738580'
HIT=REPO/'implementation/elm-minimize-lifecycle-v14/build-1791060004170871924'
OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'installed':False,'scope':'Exact owning native compile/link only; no native acceptance','commands':[]}
def run(name,command):
 p=subprocess.run(command,cwd=OWNER/'build',capture_output=True,timeout=180)
 (OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
 report['commands'].append({'name':name,'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr.decode(errors='replace')
try:
 prior=json.loads((PRIOR/'report.json').read_text());hit=json.loads((HIT/'report.json').read_text())
 assert prior['passed'] and hit['passed'] and sha(prior['binary'])==prior['binarySHA256']
 archive=PRIOR/'libhyprland_lib.a';original_archive=sha(archive)
 for relative in ('SceneModal.hpp','WindowPolicy.hpp','SceneTrace.hpp','src/desktop/state/ViewHitTester.cpp'):
  source=ROOT/'candidate'/relative;dest=OUT/'inputs'/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
 report['sources']={str(p.relative_to(OUT/'inputs')):sha(p) for p in (OUT/'inputs').rglob('*') if p.is_file()}
 command=list(next(c['command'] for c in hit['commands'] if c['name']=='ViewHitTester-compile'))
 source=OUT/'inputs/src/desktop/state/ViewHitTester.cpp';obj=OUT/'ViewHitTester.cpp.o';dep=OUT/'ViewHitTester.cpp.d'
 for i,arg in enumerate(command):
  if arg.startswith('-I') and '/inputs' in arg:command[i]='-I'+str(OUT/'inputs')
  elif i and command[i-1]=='-c':command[i]=str(source)
  elif i and command[i-1]=='-o':command[i]=str(obj)
  elif i and command[i-1]=='-MF':command[i]=str(dep)
 run('ViewHitTester-compile',command)
 dependencies=shlex.split(dep.read_text().replace('\\\n',' ').split(':',1)[1])
 report['dependencies']={str(Path(p).resolve()):sha(p) for p in dependencies}
 assert not any(p.startswith('/usr/include/hyprland') for p in report['dependencies'])
 shutil.copy2(archive,OUT/'libhyprland_lib.a');run('archive',['/usr/bin/ar','r',str(OUT/'libhyprland_lib.a'),str(obj)])
 link=list(prior['commands'][-1]['command'])
 for i,arg in enumerate(link):
  if i and link[i-1]=='-o':link[i]=str(OUT/'Hyprland')
  elif arg==str(archive):link[i]=str(OUT/'libhyprland_lib.a')
  elif arg.startswith('-Wl,--dependency-file='):link[i]='-Wl,--dependency-file='+str(OUT/'link.d')
 run('link',link)
 assert sha(archive)==original_archive and sha(prior['binary'])==prior['binarySHA256']
 report.update(passed=True,binary=str(OUT/'Hyprland'),binarySHA256=sha(OUT/'Hyprland'),ancestorBinaryPreserved=True,ancestorArchivePreserved=True,ancestorReportSHA256=sha(PRIOR/'report.json'),owningVersionHeaderSHA256=sha(OWNER/'src/version.h'))
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json',flush=True)
if report['passed']:
 (ROOT/'native-build-report.json').write_text(json.dumps({'result':'pass','binary':report['binary'],'sha256':report['binarySHA256'],'buildReport':str(OUT/'report.json'),'buildReportSHA256':sha(OUT/'report.json')},indent=2)+'\n')
raise SystemExit(not report['passed'])
