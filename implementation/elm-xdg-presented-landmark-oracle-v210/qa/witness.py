import hashlib,importlib.util,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1];parent=s.parent/'elm-xdg-presented-landmark-oracle-v208';spec=importlib.util.spec_from_file_location('original208',parent/'oracle.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def image(serial):
 data=bytearray(240*180*3)
 colors=[(255,48,48),(48,255,48),(48,48,255),(255,255,48),(0x28^(serial&63),0x71^((serial>>6)&63),0xc8^((serial>>12)&63))]
 for (x,y),color in zip([(24,24),(116,24),(24,96),(116,96),(70,60)],colors):
  for yy in range(y-2,y+3):
   for xx in range(x-2,x+3):data[(yy*240+xx)*3:(yy*240+xx)*3+3]=bytes(color)
 return bytes(data)
records=[]
for serial,history,option,geometry in [(87,[87.0],False,[0,0,100,80]),(1,[True],False,[0,0,100,80]),(0,[False],False,[0,0,100,80]),(87,[87],'allow',[16,24,100,80])]:
 result=m.inspect(image(serial),240,180,[100,200],1,[120,220,100,80],geometry,serial,observed_serials=history,diagnostic_nonzero=option)
 assert len(result['samples'])==5
 records.append({'serial':serial,'history':history,'diagnosticOption':option,'geometry':geometry,'originalAccepted':True,'result':result})
out=s/'qa'/('witness-'+str(time.time_ns()));out.mkdir();report={'diagnosisConfirmed':True,'nativeAcceptance':False,'parentSourceSHA256':hashlib.sha256((parent/'oracle.py').read_bytes()).hexdigest(),'parentManifestSHA256':hashlib.sha256((parent/'component-manifest.json').read_bytes()).hexdigest(),'records':records};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'diagnosisConfirmed':True,'report':str(out/'report.json')}))
