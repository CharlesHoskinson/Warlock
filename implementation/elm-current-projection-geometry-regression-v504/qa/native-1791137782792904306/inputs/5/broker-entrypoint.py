"""QA-only host-compatible entrypoint: one private wrapper configuration argument."""
import json,os,stat,sys
from pathlib import Path
from wrapper import HoldFailure,MAX_BYTES,counter,decode,directory,exact,main as wrapper_main

def configuration(path):
 p=Path(path)
 if not p.is_absolute() or p.resolve(strict=True)!=p:raise HoldFailure('QA wrapper config canonical path')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  s=os.fstat(fd)
  if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or s.st_nlink!=1 or stat.S_IMODE(s.st_mode)!=0o600:raise HoldFailure('QA private wrapper config')
  value=decode(os.read(fd,MAX_BYTES+1))
 finally:os.close(fd)
 fields=['authorityConfig','controlDirectory','incarnation','effectOperation']
 if isinstance(value,dict) and 'selectorOrdinal' in value:fields.append('selectorOrdinal')
 exact(value,fields)
 ordinal=value.get('selectorOrdinal',1)
 if type(ordinal) is not int or ordinal not in (1,2):raise HoldFailure('QA selector ordinal bound')
 counter(value['incarnation'])
 if value['effectOperation'] not in ('maximize','restore-geometry'):raise HoldFailure('QA closed geometry operation')
 if type(value['authorityConfig']) is not str or type(value['controlDirectory']) is not str:raise HoldFailure('QA config path types')
 directory(value['controlDirectory'])
 authority=Path(value['authorityConfig'])
 if not authority.is_absolute() or authority.resolve(strict=True)!=authority or not authority.is_file() or authority.is_symlink():raise HoldFailure('QA authority config canonical regular path')
 # Contents remain owned by the ordinary endpoint's verified process/socket
 # decoder; the QA entrypoint never synthesizes native identity or capabilities.
 return value

def main():
 sys.path.insert(0,'/home/hoskinson/window-integration-qa')
 from qa_launch import require_qa_scope
 require_qa_scope()
 if len(sys.argv)!=2:raise HoldFailure('QA entrypoint requires one private configuration')
 value=configuration(sys.argv[1]);old=sys.argv
 sys.argv=['receipt-wrapper','run','--control-directory',value['controlDirectory'],'--incarnation',value['incarnation'],'--config',value['authorityConfig'],'--effect-operation',value['effectOperation']]
 if 'selectorOrdinal' in value:sys.argv+=['--selector-ordinal',str(value['selectorOrdinal'])]
 try:return wrapper_main()
 finally:sys.argv=old
if __name__=='__main__':raise SystemExit(main())
