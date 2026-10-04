"""Replace only PointerManager.cpp.o in the frozen exact V7 core archive."""
import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2'
PREVIOUS=REPO/'implementation/elm-native-buffer-size-v7/build-1791090562611157328'
OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir()
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'installed':False,'nativeAcceptance':False,'scope':'Scaled/rotated cursor buffer sizing CPU and owning core incremental build; native and exact plugin pairing remain open','commands':[]}
files=[ROOT/'build.py',ROOT/'qa/cursor-extent.cpp',*sorted((ROOT/'candidate').rglob('*.hpp')),*sorted((ROOT/'candidate').rglob('*.cpp'))]
report['inputs']={str(p.relative_to(ROOT)):digest(p) for p in files}
for p in files:
 dest=OUT/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);dest.chmod(0o444)
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
 p=subprocess.run(command,cwd=OWNER/'build',capture_output=True,timeout=180)
 (OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
 report['commands'].append({'name':name,'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==expected,p.stderr.decode(errors='replace')[-4000:]
 return p.stdout
try:
 prior_path=PREVIOUS/'report.json';prior=json.loads(prior_path.read_text());assert prior['passed']
 assert digest(prior['binary'])==prior['binarySHA256']
 archive=PREVIOUS/'libhyprland_lib.a';archive_hash=digest(archive);assert archive_hash==prior['archiveSHA256']
 report.update(priorReportSHA256=digest(prior_path),ancestorCore={'path':prior['binary'],'sha256':prior['binarySHA256']},ancestorArchive={'path':str(archive),'sha256':archive_hash})
 source=OUT/'inputs/candidate/src/pointer/PointerManager.cpp';original=OWNER/'src/pointer/PointerManager.cpp'
 report['originalPointerSHA256']=digest(original);report['owningVersionHeaderSHA256']=digest(OWNER/'src/version.h')
 assert report['owningVersionHeaderSHA256']==prior['owningVersionHeaderSHA256']
 shutil.copy2(original,OUT/'inputs/original-PointerManager.cpp')
 test=OUT/'inputs/qa/cursor-extent.cpp';helper=OUT/'inputs/candidate/src/pointer/CursorBufferExtent.hpp'
 run('test-compile',['/usr/bin/c++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-I'+str(helper.parent),str(test),'-o',str(OUT/'cursor-extent')])
 result=run('cursor-extent-tests',[str(OUT/'cursor-extent')]);report['checks']=int(result.decode().split('checks: ')[1].strip())
 mutant_dir=OUT/'mutant';mutant_dir.mkdir();mutant=helper.read_text().replace('return PixelSize{static_cast<int>(w), static_cast<int>(h)};', 'return PixelSize{static_cast<int>(width), static_cast<int>(height)};')
 (mutant_dir/helper.name).write_text(mutant)
 run('mutation-compile',['/usr/bin/c++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-I'+str(mutant_dir),str(test),'-o',str(OUT/'cursor-extent-unsafe')])
 run('raw-size-mutation',[str(OUT/'cursor-extent-unsafe')],expected=1)
 members=run('archive-members',['/usr/bin/ar','t',str(archive)]).decode().splitlines();assert members.count('PointerManager.cpp.o')==1
 old=run('old-pointer-object',['/usr/bin/ar','p',str(archive),'PointerManager.cpp.o'])
 owning_object=OWNER/'build/CMakeFiles/hyprland_lib.dir/src/pointer/PointerManager.cpp.o'
 report['oldPointerObjectSHA256']=hashlib.sha256(old).hexdigest();assert report['oldPointerObjectSHA256']==digest(owning_object)
 entries=json.loads((OWNER/'build/compile_commands.json').read_text());entry=next(e for e in entries if Path(e['file'])==original)
 command=shlex.split(entry['command']);report['originalCompileEntry']=entry
 command.insert(1,'-I'+str(OWNER/'src/pointer'));command.insert(1,'-I'+str(OUT/'inputs/candidate'))
 obj=OUT/'PointerManager.cpp.o';dep=OUT/'PointerManager.cpp.d'
 for i,arg in enumerate(command):
  if i and command[i-1]=='-c':command[i]=str(source)
  elif i and command[i-1]=='-o':command[i]=str(obj)
 command.extend(['-MD','-MF',str(dep)])
 run('pointer-compile',command)
 paths=shlex.split(dep.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]);report['dependencies']={str(Path(p).resolve()):digest(Path(p).resolve()) for p in paths}
 assert not any(p.startswith('/usr/include/hyprland') for p in report['dependencies'])
 targetarchive=OUT/'libhyprland_lib.a';shutil.copy2(archive,targetarchive);run('archive',['/usr/bin/ar','r',str(targetarchive),str(obj)])
 newmembers=run('new-archive-members',['/usr/bin/ar','t',str(targetarchive)]).decode().splitlines();assert newmembers==members
 old_entries=archive_payloads(archive);new_entries=archive_payloads(targetarchive)
 assert len(old_entries)==len(new_entries)
 for before,after in zip(old_entries,new_entries):
  assert before['name']==after['name']
  if before['name']=='PointerManager.cpp.o':assert after['sha256']==digest(obj)
  else:assert before==after,before['name']
 (OUT/'ancestor-archive-payloads.json').write_text(json.dumps(old_entries,indent=2)+'\n')
 (OUT/'new-archive-payloads.json').write_text(json.dumps(new_entries,indent=2)+'\n')
 link=list(prior['commands'][-1]['command'])
 for i,arg in enumerate(link):
  if i and link[i-1]=='-o':link[i]=str(OUT/'Hyprland')
  elif arg==str(archive):link[i]=str(targetarchive)
  elif arg.startswith('-Wl,--dependency-file='):link[i]='-Wl,--dependency-file='+str(OUT/'link.d')
 run('link',link)
 assert digest(archive)==archive_hash and digest(prior['binary'])==prior['binarySHA256']
 assert digest(original)==report['originalPointerSHA256'] and digest(owning_object)==report['oldPointerObjectSHA256']
 for rel,sha in report['inputs'].items():assert digest(ROOT/rel)==sha,rel
 report.update(passed=True,unsafeRawSizeMutationRejected=True,binary=str(OUT/'Hyprland'),binarySHA256=digest(OUT/'Hyprland'),archiveSHA256=digest(targetarchive),newPointerObjectSHA256=digest(obj),unchangedArchiveMembers=len(members)-1,ancestorBinaryPreserved=True,ancestorArchivePreserved=True,originalPointerPreserved=True)
except Exception as e:report['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json',flush=True);raise SystemExit(not report['passed'])
