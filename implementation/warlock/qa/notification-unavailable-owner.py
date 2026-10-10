"""Private real notification-name owner; stop through an owned file, not SIGKILL."""
import json,os,pathlib,signal,stat,sys,time
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'adapter'))
from notification_service import Service
ready,stop=map(pathlib.Path,sys.argv[1:])
assert ready.parent==stop.parent and not ready.exists() and not stop.exists()
parent=ready.parent.stat();assert parent.st_uid==os.getuid() and stat.S_IMODE(parent.st_mode)==0o700
cancelled=False
def cancel(*_):
 global cancelled
 cancelled=True
signal.signal(signal.SIGTERM,cancel)
with Service() as service:
 assert service.available
 fd=os.open(ready,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as stream:json.dump({'pid':os.getpid(),'service':service.service,'available':True},stream)
 while not cancelled and not stop.exists():time.sleep(.05)
print('Notification fixture owner released normally',flush=True)
