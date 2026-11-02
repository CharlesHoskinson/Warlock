#!/usr/bin/env python3
"""ROOT-EXECUTED supplemental CURRENT cgroup scan. Never reruns authentication."""
import datetime, hashlib, json, os, re, stat, sys, time, uuid
from pathlib import Path
BASE=Path('/home/charl/warlock-del010-cross-user-20261102T011435Z')
ATTEMPT=BASE/'root-auth-d258019003f44c2c9298ebc4cba1544f'
UNIT='qa-harness-del010-d258019003f44c2c9298ebc4cba1544f.scope'
CONTEXT_SHA='086819be03fb5593a69469ef8ee2375943422c6ff29e3076757666dbfc1cc02b'
OLD_GUARDIAN_REPORT_SHA='a7458c66a65f1db7690c93c9a9ce6e0547566d420e104f5ca295a90a4507252e'
def require(ok,reason):
 if not ok: raise RuntimeError(reason)
def read_pin(path):
 require(path.resolve(strict=True)==path,'Unexpected receipt symlink')
 fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
 try:
  before=os.fstat(fd);require(stat.S_ISREG(before.st_mode) and before.st_uid==0 and stat.S_IMODE(before.st_mode)==0o600,'Expected private root receipt')
  raw=b''
  while True:
   part=os.read(fd,65536)
   if not part: break
   raw+=part;require(len(raw)<=16*1024*1024,'Receipt bound')
  after=os.fstat(fd);require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),'Receipt changed during read')
  return raw,{'path':str(path),'device':before.st_dev,'inode':before.st_ino,'size':before.st_size,'sha256':hashlib.sha256(raw).hexdigest()}
 finally: os.close(fd)
def groups(raw):
 rows=[line.split(':',2) for line in raw.splitlines()]
 require(len(rows)==1 and rows[0][0]=='0' and rows[0][1]=='' and rows[0][2].startswith('/'),'Expected unified cgroup observation')
 return rows[0][2]
def matches(value,target): return value==target or value.startswith(target+'/')
def birth(path): return (path/'stat').read_text().rsplit(')',1)[1].split()[19]
def scan(target):
 result={'target':target,'startedMonotonic':time.monotonic(),'examined':0,'remaining':[],'readErrors':[]}
 for path in Path('/proc').iterdir():
  if not path.name.isdigit(): continue
  try:
   stamp=birth(path)
   with (path/'cgroup').open() as stream: raw=stream.read(65537)
   require(len(raw)<=65536,'Proc cgroup bound');value=groups(raw)
   require(birth(path)==stamp,'PID birth changed during scan')
   result['examined']+=1
   if matches(value,target): result['remaining'].append({'pid':int(path.name),'birth':stamp,'cgroup':value})
  except (OSError,RuntimeError,IndexError) as error: result['readErrors'].append({'pid':int(path.name),'error':type(error).__name__+': '+str(error)})
 result['finishedMonotonic']=time.monotonic()
 return result
def main():
 require(len(sys.argv)==1 and os.getresuid()==(0,0,0),'Fixed root postscan only')
 os.umask(0o077)
 info=ATTEMPT.lstat();require(stat.S_ISDIR(info.st_mode) and info.st_uid==0 and stat.S_IMODE(info.st_mode)==0o700,'Expected preserved private root attempt')
 raw,context_pin=read_pin(ATTEMPT/'runner-context-before.json');require(context_pin['sha256']==CONTEXT_SHA,'Original context bytes differ')
 old_raw,old_pin=read_pin(ATTEMPT/'guardian-report.json');require(old_pin['sha256']==OLD_GUARDIAN_REPORT_SHA,'Original guardian report bytes differ')
 context=json.loads(raw);old=json.loads(old_raw);target=groups(context['cgroup'])
 require(old['unit']==UNIT and old['attempt']==str(ATTEMPT),'Original attempt identity mismatch')
 require(re.fullmatch(r'/qa\.slice/qa-harness\.slice/qa-harness-del010-[0-9a-f]{32}\.scope',target) and target.endswith('/'+UNIT),'Recorded exact owned scope invalid')
 self_pid=os.getpid();self_birth=birth(Path('/proc/self'));self_group=groups(Path('/proc/self/cgroup').read_text())
 positive=scan(self_group)
 positive_ok=any(row['pid']==self_pid and row['birth']==self_birth for row in positive['remaining']) and not positive['readErrors']
 boundary_ok=matches(target,target) and matches(target+'/subgroup',target) and not matches(target+'-unrelated',target) and not matches(target+'.other',target)
 observed=scan(target)
 current_empty=positive_ok and boundary_ok and observed['examined']>0 and not observed['remaining'] and not observed['readErrors']
 require(read_pin(ATTEMPT/'runner-context-before.json')[1]==context_pin and read_pin(ATTEMPT/'guardian-report.json')[1]==old_pin,'Historical receipts changed during postscan')
 report={'schema':1,'kind':'supplemental-current-scope-postscan','atUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'targetFromActualRunnerContext':target,'contextPin':context_pin,'originalGuardianReportPin':old_pin,'positiveSelfControl':positive,'positiveSelfMatchedPidBirth':positive_ok,'negativeBoundaryPrefixControl':boundary_ok,'actualScopeScan':observed,'currentEmpty':bool(current_empty),'historicalGuardianCleanupQualified':False,'historicalGuardianBug':'Executed scanner omitted qa.slice parent; its negative scan does not establish historical cleanup','authRerun':False,'originalReceiptsModified':False,'nativeAccepted':False,'releaseAccepted':False,'scope':'Fresh current process observation only; never retroactive cleanup, authentication or original acceptance'}
 destination=ATTEMPT/('cleanup-postscan-'+uuid.uuid4().hex+'.json')
 fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 with os.fdopen(fd,'w') as output: json.dump(report,output,indent=2);output.write('\n')
 print(json.dumps({'currentEmpty':bool(current_empty),'positiveSelfControl':positive_ok,'negativeBoundaryPrefixControl':boundary_ok,'report':str(destination),'authRerun':False,'historicalCleanupQualified':False}),flush=True)
 return 0 if current_empty else 1
if __name__=='__main__': raise SystemExit(main())
