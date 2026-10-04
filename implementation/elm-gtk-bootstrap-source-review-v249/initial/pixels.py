"""Actual private output RGB capture. A sample is not a canonical scene receipt."""
import hashlib,json,subprocess,time
from pathlib import Path
from actor import remaining
from journal import Refused,integer

def capture(session,directory,deadline):
 directory=Path(directory);directory.mkdir(mode=0o700,parents=True,exist_ok=False);png=directory/'capture.png';rgb=directory/'capture.rgb';record={'nativeAccepted':False,'output':'WAYLAND-1','expectedExtent':[800,600],'startedMonotonic':time.monotonic()}
 def run(name,argv):
  record[name+'Argv']=argv;(directory/'record.json').write_text(json.dumps(record,indent=2)+'\n')
  with (directory/(name+'.stdout')).open('xb') as out,(directory/(name+'.stderr')).open('xb') as err:
   result=subprocess.run(argv,stdout=out,stderr=err,env=session.env,timeout=min(3,remaining(deadline)))
  remaining(deadline);record[name+'ExitCode']=result.returncode
  if result.returncode!=0:raise Refused('normal private capture/decode exit required')
 try:
  session.guard();run('grim',['/usr/bin/grim','-o','WAYLAND-1',str(png)])
  run('extent',['/usr/bin/magick','identify','-format','%w %h',str(png)])
  raw=(directory/'extent.stdout').read_bytes()
  if raw!=b'800 600':raise Refused('exact private output RGB extent required')
  run('decode',['/usr/bin/magick',str(png),'-alpha','off','-depth','8','rgb:'+str(rgb)])
  if rgb.stat().st_size!=800*600*3:raise Refused('exact RGB byte extent required')
  data=rgb.read_bytes();record.update(completedMonotonic=time.monotonic(),pngSHA256=hashlib.sha256(png.read_bytes()).hexdigest(),rgbSHA256=hashlib.sha256(data).hexdigest());remaining(deadline);session.guard();return data,record
 except BaseException as error:record['error']=repr(error);raise
 finally:(directory/'record.json').write_text(json.dumps(record,indent=2)+'\n')

def yellow_marker(data,point):
 if type(data) is not bytes or len(data)!=800*600*3 or type(point) is not list or len(point)!=2:raise Refused('capture/point shape')
 x=integer(point[0],1,798);y=integer(point[1],1,598);samples=[]
 for sy in range(y-1,y+2):
  for sx in range(x-1,x+2):
   offset=(sy*800+sx)*3;actual=list(data[offset:offset+3]);samples.append({'point':[sx,sy],'rgb':actual})
   if actual!=[255,255,0]:raise Refused('actual GTK yellow landmark absent or occluded')
 return samples
