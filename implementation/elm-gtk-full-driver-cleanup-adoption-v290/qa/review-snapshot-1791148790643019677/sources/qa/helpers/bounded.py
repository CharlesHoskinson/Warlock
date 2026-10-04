"""Private IPC clipped to existing native3s and enclosing absolute6s."""
import json,subprocess,time
from pathlib import Path
from actor import remaining
from journal import Refused,pairs,constant
class BoundedSession:
 def __init__(self,session,directory,deadline):
  self.original=session;self.directory=Path(directory);self.directory.mkdir(mode=0o700,parents=True,exist_ok=False);self.deadline=deadline;self.env=dict(session.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GTK_USE_PORTAL='0',GSETTINGS_BACKEND='memory');self.host=session.host;self.evidence=session.evidence
 def guard(self):
  remaining(self.deadline);self.original.guard();remaining(self.deadline)
 def ctl(self,*args):
  self.guard();directory=self.directory/str(time.time_ns());directory.mkdir();argv=['/usr/bin/hyprctl','-i',self.evidence['signature'],*map(str,args)];record={'argv':argv,'deadline':self.deadline,'startedMonotonic':time.monotonic()}
  try:
   with (directory/'stdout').open('xb') as out,(directory/'stderr').open('xb') as err:
    result=subprocess.run(argv,stdout=out,stderr=err,env=self.env,timeout=min(3,remaining(self.deadline)))
   record['exitCode']=result.returncode;self.guard()
   if result.returncode:raise Refused('normal private IPC result required')
   if (directory/'stdout').stat().st_size>2*1024*1024 or (directory/'stderr').stat().st_size>65536:raise Refused('private IPC output bounds')
   return (directory/'stdout').read_text(encoding='utf-8',errors='strict')
  except BaseException as error:record['error']=repr(error);raise
  finally:(directory/'record.json').write_text(json.dumps(record,indent=2)+'\n')
 def data(self,*args):
  try:return json.loads(self.ctl('-j',*args),object_pairs_hook=pairs,parse_constant=constant)
  except (UnicodeError,ValueError,RecursionError) as error:raise Refused('strict private IPC JSON') from error
