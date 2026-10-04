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
 destination=OUT/'inputs'/path.relative_to(ROOT);destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,destination);destination.chmod(0o444)
def archive_payloads(path):
 # GNU ar allows duplicate basenames. Hash every ordered payload, not ar p's
 # first matching name. Ignore only the rebuilt symbol/long-name metadata.
 entries=[];longnames=b''
 with Path(path).open('rb') as stream:
  assert stream.read(8)==b'!<arch>\n','Expected regular GNU archive'
  while True:
   header=stream.read(60)
   if not header:break
   assert len(header)==60 and header[58:60]==b'`\n','Archive header'
   name=header[:16].decode('ascii').strip();size=int(header[48:58]);remaining=size
   if name=='//':longnames=stream.read(size);assert len(longnames)==size
   else:
    hasher=hashlib.sha256()
    while remaining:
     chunk=stream.read(min(remaining,1048576));assert chunk,'Truncated archive'
     hasher.update(chunk);remaining-=len(chunk)
    if name not in ('/','/SYM64/'):
     assert not name.startswith('#1/'),'Unsupported BSD member names'
     if name.startswith('/'):
      offset=int(name[1:]);end=longnames.index(b'/\n',offset);name=longnames[offset:end].decode('utf-8')
     else:name=name.removesuffix('/')
     entries.append({'name':name,'size':size,'sha256':hasher.hexdigest()})
   if size%2:assert len(stream.read(1))==1
 return entries

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
 original_snapshot=OUT/'inputs/original-Monitor.cpp';shutil.copy2(original,original_snapshot);original_snapshot.chmod(0o444)
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
 # GNU archives have repeated basenames; verify every ordered member payload.
 old_entries=archive_payloads(archive);new_entries=archive_payloads(targetarchive)
 assert [entry['name'] for entry in old_entries]==members
 assert len(old_entries)==len(new_entries)
 for before,after in zip(old_entries,new_entries):
  assert before['name']==after['name']
  if before['name']=='Monitor.cpp.o':assert after['sha256']==digest(obj)
  else:assert before==after,before['name']
 (OUT/'ancestor-archive-payloads.json').write_text(json.dumps(old_entries,indent=2)+'\n')
 (OUT/'new-archive-payloads.json').write_text(json.dumps(new_entries,indent=2)+'\n')
 report['ancestorArchivePayloadsSHA256']=digest(OUT/'ancestor-archive-payloads.json')
 report['newArchivePayloadsSHA256']=digest(OUT/'new-archive-payloads.json')
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
