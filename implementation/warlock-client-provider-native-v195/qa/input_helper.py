"""Feed sealed QA input to the exact pointer/keyboard command; retain exit."""
import os,sys,stat
from pathlib import Path
path=Path(sys.argv[1]);info=path.lstat()
assert stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)==0o600 and info.st_nlink==1
fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW);os.dup2(fd,0);os.close(fd)
os.execv(sys.argv[2],sys.argv[2:])
