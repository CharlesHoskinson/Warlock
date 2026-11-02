#!/usr/bin/env python3
"""ROOT-EXECUTED VM kernel-credential component QA. No GUI/native acceptance."""
import hashlib, json, os, re, resource, stat, subprocess, sys, time
from pathlib import Path
BASE=Path('/home/charl/warlock-del010-cross-user-20261102T011435Z')
SOURCE=Path('/home/charl/warlock-mvp-20261101T1058Z/source')
QA=Path('/home/charl/warlock-live-usability-typed-model-20261102T000451Z/qa-mocks')
QA_HASHES={'qa_run.py':'656f118c268e9f762f2d62c859d146043d74c83b72cd5457b779f1e30cb183a1','qa_launch.py':'6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23'}
MANIFEST_SHA='fa356aa702473e64adef24144016ceda84416c0dd69b1620cb1aa0f7d0dc3b16'
CHILD=BASE/'assets/credential-peer-child'
TEST=BASE/'assets/persistent-bootstrap-controls'
ASSET_HASHES={'child':'3e869bdd1db2675afb768a5b57a2a35e8ccbcf2dea9770fe6880b59f41f602d8','test':'73b70e273f8b00d688823a75f29f2d0a09a1261999b087e03e115950ad3085a2'}
ENV={'PATH':'/usr/bin:/bin','HOME':'/root','LANG':'C','LC_ALL':'C','XDG_RUNTIME_DIR':'/run/user/0'}
def require(ok,why):
 if not ok: raise RuntimeError(why)
def pin(path,elf=False,allow_link=False):
 path=Path(path);resolved=path.resolve(strict=True)
 require(allow_link or path==resolved,'Unexpected source/asset symlink: '+str(path))
 fd=os.open(resolved,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
 try:
  before=os.fstat(fd);require(stat.S_ISREG(before.st_mode),'Expected regular file: '+str(path))
  digest=hashlib.sha256();head=os.read(fd,4);digest.update(head)
  while True:
   data=os.read(fd,1024*1024)
   if not data: break
   digest.update(data)
  after=os.fstat(fd);current=resolved.lstat()
  stamp=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  require(stamp(before)==stamp(after)==stamp(current),'File changed while pinning: '+str(path))
  require(not elf or head==b'\x7fELF','Expected compiled ELF: '+str(path))
  return {'path':str(path),'resolvedPath':str(resolved),'device':before.st_dev,'inode':before.st_ino,'size':before.st_size,'sha256':digest.hexdigest(),'uid':before.st_uid,'gid':before.st_gid,'mode':stat.S_IMODE(before.st_mode)}
 finally: os.close(fd)
def write(path,value):
 raw=value if isinstance(value,bytes) else (json.dumps(value,indent=2)+'\n').encode()
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 with os.fdopen(fd,'wb') as stream: stream.write(raw)
def context():
 status=Path('/proc/self/status').read_text()
 return {'pid':os.getpid(),'uid':os.getresuid(),'gid':os.getresgid(),'userNamespace':os.readlink('/proc/self/ns/user'),'pidNamespace':os.readlink('/proc/self/ns/pid'),'uidMap':Path('/proc/self/uid_map').read_text(),'gidMap':Path('/proc/self/gid_map').read_text(),'cgroup':Path('/proc/self/cgroup').read_text(),'core':resource.getrlimit(resource.RLIMIT_CORE),'capabilityLines':[row for row in status.splitlines() if row.startswith(('Cap','NoNewPrivs:','Seccomp:'))]}
def sources():
 require(pin(BASE/'source-manifest.json')['sha256']==MANIFEST_SHA,'Reviewed source manifest changed')
 manifest=json.loads((BASE/'source-manifest.json').read_text());expected=manifest['completeHaskellSources']
 require(len(expected)==217,'Expected exact 217 source inputs')
 rows={}
 for name,sha in expected.items():
  require(name.startswith('implementation/warlock/haskell/') and '..' not in Path(name).parts and not Path(name).is_absolute(),'Invalid manifest source path')
  row=pin(SOURCE/name);require(row['sha256']==sha,'Reviewed source changed: '+name);rows[name]=row
 for name,sha in QA_HASHES.items(): require(pin(QA/name)['sha256']==sha,'Unchanged QA helper pin mismatch: '+name)
 return {'manifest':pin(BASE/'source-manifest.json'),'sources':rows,'qaHelpers':{name:pin(QA/name) for name in QA_HASHES}}
def dependencies(path,attempt,phase):
 command=['/usr/bin/ldd',str(path)]
 result=subprocess.run(command,stdin=subprocess.DEVNULL,capture_output=True,env=ENV,timeout=10,check=False)
 stem=path.name+'-'+phase+'-ldd'
 write(attempt/(stem+'.stdout'),result.stdout);write(attempt/(stem+'.stderr'),result.stderr)
 require(result.returncode==0 and b'not found' not in result.stdout,'ELF dependency resolution failed')
 paths=set()
 for line in result.stdout.decode().splitlines():
  words=line.split()
  if not words: continue
  if words[0].startswith('linux-vdso.'): continue
  selected=words[2] if len(words)>2 and words[1]=='=>' else words[0]
  require(selected.startswith('/'),'Unrecognized ldd dependency row')
  paths.add(selected)
 require(paths,'No ELF dependencies recorded')
 return {'command':command,'libraries':{name:pin(name,elf=True,allow_link=True) for name in sorted(paths)}}
def artifact_manifest(assets,dependencies):
 observed=pin(BASE/'guest-artifacts.json');manifest=json.loads((BASE/'guest-artifacts.json').read_text())
 require(manifest['originalBuildExitStatus']==0 and manifest['sourceInputCount']==217 and manifest['sourceInputsStable'] is True,'Guest artifact qualification mismatch')
 require(set(manifest['artifacts'])=={CHILD.name,TEST.name},'Expected exact two qualified artifacts')
 def matches(actual,expected):
  return all(str(actual[key])==str(expected[key]) for key in ('path','resolvedPath','device','inode','size','sha256'))
 for kind,path in [('child',CHILD),('test',TEST)]:
  held=manifest['artifacts'][path.name]
  require(matches(assets[kind],held['image']),'Qualified asset identity changed')
  libraries=dependencies[path.name]['libraries'];expected={row['path']:row for row in held['dependencies']}
  require(set(libraries)==set(expected) and all(matches(libraries[name],expected[name]) for name in libraries),'Qualified dependency identity changed')
 return observed
def main():
 require(len(sys.argv)==1 and os.getresuid()==(0,0,0),'Fixed root runner only; no caller commands')
 attempt=Path(os.environ['WARLOCK_DEL010_ATTEMPT']);token=attempt.name.removeprefix('root-auth-')
 require(attempt.parent==BASE and re.fullmatch(r'[0-9a-f]{32}',token),'Invalid owned attempt')
 unit='qa-harness-del010-'+token+'.scope'
 require(os.environ.get('WARLOCK_DEL010_UNIT')==unit,'Scope identity mismatch')
 info=attempt.lstat();require(stat.S_ISDIR(info.st_mode) and info.st_uid==0 and stat.S_IMODE(info.st_mode)==0o700,'Private root attempt required')
 report={'schema':1,'scope':'VM actual kernel-credential component only; not protected/native GUI or release acceptance','passed':False,'nativeAccepted':False,'releaseAccepted':False,'forced':False,'startedMonotonic':time.monotonic(),'unit':unit}
 code=1
 try:
  before=context();write(attempt/'runner-context-before.json',before)
  require(before['core']==(1,1) and not os.environ.get('WINDOW_QA_BACKTRACE'),'Exact core1 required')
  require(any(line.endswith('/qa-harness.slice/'+unit) for line in before['cgroup'].splitlines()),'Not in exact owned system-manager QA scope')
  report['sourceBefore']=sources()
  assets={name:pin(path,elf=True) for name,path in [('child',CHILD),('test',TEST)]}
  require(all(row['mode']==0o755 and row['uid'] in (0,1000) and row['sha256']==ASSET_HASHES[kind] for kind,row in assets.items()),'Expected exact qualified installed 0755 assets')
  report['assetsBefore']=assets
  report['dependenciesBefore']={path.name:dependencies(path,attempt,'before') for path in (CHILD,TEST)}
  report['artifactManifestBefore']=artifact_manifest(assets,report['dependenciesBefore'])
  private=attempt/'context';private.mkdir(mode=0o700)
  require(private.lstat().st_uid==0 and stat.S_IMODE(private.lstat().st_mode)==0o700,'Fresh root context directory required')
  child=assets['child'];command=[str(TEST),str(CHILD),str(child['device']),str(child['inode']),str(child['size']),child['sha256'],'full','1',str(private)]
  report['command']=command;write(attempt/'runner-start.json',report)
  out=os.open(attempt/'test.stdout',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC,0o600)
  err=os.open(attempt/'test.stderr',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC,0o600)
  try:
   result=subprocess.run(command,stdin=subprocess.DEVNULL,stdout=out,stderr=err,env=ENV,check=False)
  finally: os.close(out);os.close(err)
  report['returncode']=result.returncode
  raw=(attempt/'test.stdout').read_bytes();rows=[json.loads(line) for line in raw.splitlines() if line.strip()]
  cases=[row for row in rows if 'case' in row];verdicts=[row for row in rows if row.get('kind')=='persistent-auth-verdict']
  report['caseCount']=len(cases);report['caseNames']=[row['case'] for row in cases];report['verdicts']=verdicts
  cross=[row for row in cases if row.get('case')=='actual-cross-user'];report['contextEvidenceComplete']=len(cross)==1 and cross[0].get('credentialContextEvidence',{}).get('contextEvidenceComplete') is True
  report['jsonlValid']=len(cases)==15 and len(set(report['caseNames']))==15 and all(row.get('passed') is True for row in cases) and len(verdicts)==1 and verdicts[0].get('passed') is True and verdicts[0].get('cases')==15 and verdicts[0].get('crossUserIncluded') is True
  report['sourceAfter']=sources();report['assetsAfter']={name:pin(path,elf=True) for name,path in [('child',CHILD),('test',TEST)]}
  report['dependenciesAfter']={path.name:dependencies(path,attempt,'after') for path in (CHILD,TEST)}
  report['artifactManifestAfter']=artifact_manifest(report['assetsAfter'],report['dependenciesAfter'])
  require(report['artifactManifestAfter']==report['artifactManifestBefore'],'Qualified artifact manifest changed')
  require(report['sourceAfter']==report['sourceBefore'] and report['assetsAfter']==assets and report['dependenciesAfter']==report['dependenciesBefore'],'Source, assets or dependencies changed during test')
  report['contextFiles']={str(path.relative_to(private)):pin(path) for path in private.rglob('*') if path.is_file()}
  report['logs']={name:pin(attempt/name) for name in ('test.stdout','test.stderr')}
  report['passed']=result.returncode==0 and report['jsonlValid'] and report['contextEvidenceComplete'];code=0 if report['passed'] else 1
 except BaseException as error: report['error']=type(error).__name__+': '+str(error)
 finally:
  report['finishedMonotonic']=time.monotonic();report['contextAfter']=context();write(attempt/'runner-report.json',report)
 return code
if __name__=='__main__': raise SystemExit(main())
