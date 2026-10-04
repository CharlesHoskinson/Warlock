import json,os,sys,time
from pathlib import Path
directory=Path(sys.argv[1]);ordinal=int(sys.argv[2])
for index in range(8):
 child=os.fork()
 if child==0:
  if index%2:os.setsid()
  pid=os.getpid();start=Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]
  (directory/('born-'+str(pid)+'.json')).write_text(json.dumps({'pid':pid,'start':start}))
  time.sleep(.04+.005*index+.001*ordinal)
  (directory/('complete-'+str(pid))).write_text('normal0')
  os._exit(0)
 time.sleep(.0002*ordinal)
os._exit(0)
