"""One-shot protected-QA receipt interruption; inert without explicit arming."""
import json,os,re,resource,signal
from pathlib import Path
from endpoint import Refused,start_time

def after_submit(client,journal,outcome):
 if os.environ.get('ELM_WINDOW_RECOVERY_FAULT')!='after-submit':return
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1) or not re.search(r'/qa-harness\.slice/qa-harness-[A-Za-z0-9_-]+\.scope',Path('/proc/self/cgroup').read_text()):raise Refused('Fault injection outside protected QA')
 try:fd=os.open('fault-arm',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=journal.fd)
 except FileNotFoundError:return
 try:
  journal.verify(fd)
  if os.read(fd,32)!=b'after-submit\n':raise Refused('Invalid QA fault arming')
 finally:os.close(fd)
 try:fd=os.open('fault-marker.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=journal.fd)
 except FileExistsError:return
 try:
  original_binding=dict(client.bound)
  renewed=client.hello()['binding']
  before=client.scene_facts('900001')
  replay={'protocolVersion':3,'kind':'window-effect','effectProtocol':outcome['effectProtocol'],'binding':original_binding,'intent':outcome['intent']}
  try:
   stale=client.request(replay)
  except Refused as error:
   stale={'kind':'authenticated-native-refusal','reason':str(error)}
  after=client.scene_facts('900002')
  sender_proof={'pid':os.getpid(),'start':start_time(os.getpid()),'originalBinding':original_binding,'renewedBinding':renewed,'request':replay,'result':stale,'before':before,'after':after}
  record={'pid':os.getpid(),'start':start_time(os.getpid()),'binding':original_binding,'senderProof':sender_proof,'outcome':outcome,'durableRecord':journal.read(),'stage':'after-native-receipt-before-durable-settlement-and-frontend-delivery'}
  with os.fdopen(fd,'w') as stream:json.dump(record,stream);stream.flush();os.fsync(stream.fileno())
  os.fsync(journal.fd)
 except BaseException:
  try:os.close(fd)
  except OSError:pass
  raise
 os.kill(os.getpid(),signal.SIGSTOP)
