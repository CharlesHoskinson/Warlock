"""Publish private hold/unlock without unlinking the fixture's opened inode."""
import os,pathlib,stat,sys

def publish(path,command):
 path=pathlib.Path(path)
 if command not in {'hold','unlock'}:raise ValueError('Exact private lock command')
 directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  parent=os.fstat(directory)
  if parent.st_uid!=os.getuid() or stat.S_IMODE(parent.st_mode)!=0o700:raise ValueError('Own private lock directory')
  flags=os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC
  if command=='hold':flags|=os.O_CREAT|os.O_EXCL
  fd=os.open(path.name,flags,0o600,dir_fd=directory)
  try:
   before=os.fstat(fd)
   if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or stat.S_IMODE(before.st_mode)!=0o600 or before.st_nlink!=1:raise ValueError('Own single-link private lock control')
   if command=='unlock' and os.pread(fd,17,0) not in {b'hold\n',b'unlock\n'}:raise ValueError('Existing exact private lock command')
   payload=(command+'\n').encode()
   if os.pwrite(fd,payload,0)!=len(payload):raise OSError('Complete single-write lock command')
   after=os.fstat(fd)
   if (before.st_dev,before.st_ino)!=(after.st_dev,after.st_ino) or after.st_nlink!=1 or stat.S_IMODE(after.st_mode)!=0o600 or os.pread(fd,17,0)!=payload:raise ValueError('Stable exact private lock control')
  finally:os.close(fd)
 finally:os.close(directory)

if __name__=='__main__':
 sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
 require_qa_scope()
 if len(sys.argv)!=3:raise ValueError('Private control path and command')
 publish(sys.argv[1],sys.argv[2])
