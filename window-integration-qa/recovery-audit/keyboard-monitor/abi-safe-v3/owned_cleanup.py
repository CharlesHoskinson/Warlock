"""Bounded cleanup only for explicitly captured own session leaders."""
from pathlib import Path
import os,signal,time

def process_start(pid):return Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]
def capture(process,role):return {'pid':process.pid,'start':process_start(process.pid),'pgid':os.getpgid(process.pid),'role':role}
def stop_owned(record,seconds=4):
 pid=record['pid'];path=Path('/proc',str(pid));row=dict(record)
 if not path.exists():return dict(row,gone=True,alreadyExited=True)
 if process_start(pid)!=record['start'] or os.getpgid(pid)!=record['pgid'] or record['pgid']!=pid or path.stat().st_uid!=os.getuid():return dict(row,gone=False,error='Owned PID/start/PGID mismatch; refused signal')
 try:os.killpg(pid,signal.SIGTERM)
 except ProcessLookupError:return dict(row,gone=True,alreadyExited=True)
 row['forcedTERM']=True;end=time.monotonic()+seconds
 while path.exists() and time.monotonic()<end:time.sleep(.04)
 if path.exists():
  if process_start(pid)!=record['start'] or os.getpgid(pid)!=pid:return dict(row,gone=False,error='Owned identity changed before kill; refused')
  os.killpg(pid,signal.SIGKILL);row['forcedKILL']=True;end=time.monotonic()+seconds
  while path.exists() and time.monotonic()<end:time.sleep(.04)
 return dict(row,gone=not path.exists())
