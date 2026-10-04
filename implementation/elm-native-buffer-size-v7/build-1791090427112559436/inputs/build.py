"""Replace exactly Monitor.cpp.o in the frozen v23 archive; CPU-only, no install."""
import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2'
PREVIOUS=REPO/'implementation/elm-input-hit-v23/build-1791066816123172452'
OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir()
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
report={'passed':False,'installed':False,'scope':'Actual extracted Monitor buffer selection CPU tests and exact v23 incremental core build; no AQ, native presentation, plugin pairing or GUI acceptance','commands':[]}
files=[ROOT/'build.py',ROOT/'qa/buffer-selection.cpp',*sorted((ROOT/'candidate').rglob('*.hpp')),*sorted((ROOT/'candidate').rglob('*.cpp'))]
report['inputs']={str(p.relative_to(ROOT)):digest(p) for p in files}
for path in files:
 destination=OUT/'inputs'/path.relative_to(ROOT);destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,destination)
def run(name,command,expected=0):
 process=subprocess.run(command,cwd=OWNER/'build',capture_output=True,timeout=180)
 (OUT/(name+'.stdout')).write_bytes(process.stdout);(OUT/(name+'.stderr')).write_bytes(process.stderr)
 report['commands'].append({'name':name,'command':command,'exitCode':process.returncode});print(name,process.returncode,flush=True)
 assert process.returncode==expected,process.stderr.decode(errors='replace')
 return process.stdout
try:
 prior_path=PREVIOUS/'report.json';prior=json.loads(prior_path.read_text());assert prior['passed']
 assert digest(prior['binary'])==prior['binarySHA256']
 archive=PREVIOUS/'libhyprland_lib.a';archive_hash=digest(archive);report['priorReportSHA256']=digest(prior_path)
 report['ancestorCore']={'path':prior['binary'],'sha256':prior['binarySHA256']}
 report['ancestorArchive']={'path':str(archive),'sha256':archive_hash}
 source=OUT/'inputs/candidate/src/output/Monitor.cpp';text=source.read_text()
 original=OWNER/'src/output/Monitor.cpp';report['originalMonitorSHA256']=digest(original)
 report['owningVersionHeaderSHA256']=digest(OWNER/'src/version.h')
 assert report['owningVersionHeaderSHA256']==prior['owningVersionHeaderSHA256']
 begin=text.index('void CMonitorState::ensureBufferPresent() {');end=text.index('\nbool CMonitorState::commit()',begin)
 function=text[begin:end]
 template=(OUT/'inputs/qa/buffer-selection.cpp').read_text()
 test=OUT/'buffer-selection.cpp';test.write_text(template.replace('// ACTUAL_PRODUCTION_FUNCTION',function))
 testbinary=OUT/'buffer-selection'
 run('test-compile',['/usr/bin/c++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(test),'-o',str(testbinary)])
 result=run('buffer-selection-tests',[str(testbinary)]);assert b'checks: 12' in result
 mutant=OUT/'buffer-selection-unsafe.cpp';mutant.write_text(test.read_text().replace('STATE.buffer && MODE && STATE.buffer->size == MODE->pixelSize','STATE.buffer && MODE'))
 mutantbinary=OUT/'buffer-selection-unsafe';run('mutation-compile',['/usr/bin/c++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(mutant),'-o',str(mutantbinary)])
 run('size-guard-mutation',[str(mutantbinary)],expected=1)
 members=run('archive-members',['/usr/bin/ar','t',str(archive)]).decode().splitlines();assert members.count('Monitor.cpp.o')==1
 old=run('old-monitor-object',['/usr/bin/ar','p',str(archive),'Monitor.cpp.o']);report['oldMonitorObjectSHA256']=hashlib.sha256(old).hexdigest()
 command=list(prior['commands'][0]['command']);obj=OUT/'Monitor.cpp.o';dep=OUT/'Monitor.cpp.d'
 for i,arg in enumerate(command):
  if arg.startswith('-I') and arg.endswith('/inputs'):command[i]='-I'+str(OUT/'inputs/candidate')
  elif arg.startswith('-I') and arg.endswith('/src/desktop/state'):command[i]='-I'+str(OWNER/'src/output')
  elif i and command[i-1]=='-c':command[i]=str(source)
  elif i and command[i-1]=='-o':command[i]=str(obj)
  elif i and command[i-1]=='-MF':command[i]=str(dep)
 command.insert(1,'-I'+str(OWNER/'src/output'));command.insert(1,'-I'+str(OUT/'inputs/candidate'))
 run('Monitor-compile',command)
 paths=shlex.split(dep.read_text().replace('\\\n',' ').split(':',1)[1]);report['dependencies']={str(Path(p).resolve()):digest(Path(p).resolve()) for p in paths}
 assert not any(p.startswith('/usr/include/hyprland') for p in report['dependencies'])
 targetarchive=OUT/'libhyprland_lib.a';shutil.copy2(archive,targetarchive);run('archive',['/usr/bin/ar','r',str(targetarchive),str(obj)])
 newmembers=run('new-archive-members',['/usr/bin/ar','t',str(targetarchive)]).decode().splitlines();assert newmembers==members
 replaced=run('new-monitor-object',['/usr/bin/ar','p',str(targetarchive),'Monitor.cpp.o']);assert hashlib.sha256(replaced).hexdigest()==digest(obj)
 # Compare every untouched member byte-for-byte without extracting over sources.
 for member in members:
  if member=='Monitor.cpp.o':continue
  before=subprocess.run(['/usr/bin/ar','p',str(archive),member],capture_output=True,check=True).stdout
  after=subprocess.run(['/usr/bin/ar','p',str(targetarchive),member],capture_output=True,check=True).stdout
  assert before==after,member
 link=list(prior['commands'][-1]['command'])
 for i,arg in enumerate(link):
  if i and link[i-1]=='-o':link[i]=str(OUT/'Hyprland')
  elif arg==str(archive):link[i]=str(targetarchive)
  elif arg.startswith('-Wl,--dependency-file='):link[i]='-Wl,--dependency-file='+str(OUT/'link.d')
 run('link',link)
 assert digest(archive)==archive_hash and digest(prior['binary'])==prior['binarySHA256']
 assert digest(original)==report['originalMonitorSHA256']
 for relative,value in report['inputs'].items():assert digest(ROOT/relative)==value
 report.update(passed=True,checks=12,unsafeSizeGuardMutationRejected=True,binary=str(OUT/'Hyprland'),binarySHA256=digest(OUT/'Hyprland'),archiveSHA256=digest(targetarchive),newMonitorObjectSHA256=digest(obj),unchangedArchiveMembers=len(members)-1,ancestorBinaryPreserved=True,ancestorArchivePreserved=True,originalMonitorPreserved=True)
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'),flush=True);raise SystemExit(not report['passed'])
