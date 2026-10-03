# Reviewed inert CPU server variant: exactly two independent read-only requests.
# No compositor/control, helper delay, retry or response-before-request.
import json,mmap,os,socket,sys,time
from pathlib import Path
socket_path,module,ready,reply,stop=sys.argv[1:]
fd=os.open(module,os.O_RDONLY);mapping=mmap.mmap(fd,4096,flags=mmap.MAP_PRIVATE,prot=mmap.PROT_READ|mmap.PROT_EXEC)
server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);server.bind(socket_path);server.listen(2);server.settimeout(.05)
Path(ready).write_text(str(os.getpid()));deadline=time.monotonic()+5;received=0
while received<2 and not Path(stop).exists()and time.monotonic()<deadline:
 try:connection=server.accept()[0]
 except TimeoutError:continue
 with connection as conn:
  request=conn.recv(8192);Path(reply+'.request.'+str(received)).write_bytes(request)
  answers=json.loads(Path(reply).read_bytes());assert type(answers)is list and len(answers)==2
  conn.sendall(json.dumps(answers[received]).encode());received+=1
server.close();deadline=time.monotonic()+5
while not Path(stop).exists()and time.monotonic()<deadline:time.sleep(.01)
mapping.close();os.close(fd)
