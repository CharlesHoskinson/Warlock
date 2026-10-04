import hashlib,importlib.util,json,math,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1]
def load(path):
 spec=importlib.util.spec_from_file_location('candidate',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
m=load(s/'oracle.py')
def image(serial):
 data=bytearray(240*180*3)
 rgb=(0x28^(serial&63),0x71^((serial>>6)&63),0xc8^((serial>>12)&63))
 colors=[(255,48,48),(48,255,48),(48,48,255),(255,255,48),rgb]
 for (x,y),color in zip([(24,24),(116,24),(24,96),(116,96),(70,60)],colors):
  for yy in range(y-2,y+3):
   for xx in range(x-2,x+3):data[(yy*240+xx)*3:(yy*240+xx)*3+3]=bytes(color)
 return bytes(data)
HISTORY_DEFAULT=object()
def invoke(module,serial=87,history=HISTORY_DEFAULT,option=False,geometry=None):
 return module.inspect(image(serial if type(serial) is int else 87),240,180,[100,200],1,[120,220,100,80],geometry or [0,0,100,80],serial,observed_serials=[serial] if history is HISTORY_DEFAULT else history,diagnostic_nonzero=option)
def suite(module):
 checks=[]
 def accept(name,**kwargs):
  result=invoke(module,**kwargs);assert len(result['samples'])==5 and result['nonzeroCapabilityAccepted'] is False,name;checks.append(name)
 def refuse(name,**kwargs):
  try:invoke(module,**kwargs)
  except module.Refused:checks.append(name);return
  raise AssertionError(name+': unsafe metadata accepted')
 for serial in [0,1,87,2**31-1,2**31,2**32-1]:accept('integer endpoint '+str(serial),serial=serial,history=[serial])
 accept('tuple valid history',history=(86,87));accept('duplicate exact integer history',history=[87,87]);accept('distinct integer colors',serial=0,history=[2**32-1,0]);accept('maximum bounded history',history=[87]*8192)
 accept('diagnostic true literal',option=True,geometry=[16,24,100,80]);accept('zero origin true literal',option=True)
 refuse('float equality history',history=[87.0]);refuse('bool equality one',serial=1,history=[True]);refuse('bool equality zero',serial=0,history=[False])
 for bad in [-1,2**32,86.0,True,False,'87',None,[],{},float('nan'),float('inf')]:refuse('invalid history entry '+repr(bad),history=[bad,87])
 for bad in [[],(),None,[87]*8193,'87',{87}, {0:87},87,True]:refuse('invalid history container '+repr(type(bad)),history=bad)
 for bad in [-1,2**32,87.0,True,False,'87',None]:refuse('invalid selected serial '+repr(bad),serial=bad,history=[87])
 for bad in [0,1,'allow','',None,[],{},0.0,float('nan')]:
  refuse('invalid option zero '+repr(bad),option=bad);refuse('invalid option nonzero '+repr(bad),option=bad,geometry=[16,24,100,80])
 refuse('literal false nonzero refused',option=False,geometry=[16,24,100,80]);refuse('distinct color alias',history=[87,87+2**18]);refuse('wrap low18 alias',serial=0,history=[0,2**18]);refuse('valid but absent selected',history=[86])
 return checks
checks=suite(m)
out=s/'qa'/('test-'+str(time.time_ns()));out.mkdir();report={'passed':True,'checks':checks,'sourceSHA256':hashlib.sha256((s/'oracle.py').read_bytes()).hexdigest(),'testSourceSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Actual oracle metadata boundaries using independent synthetic landmark RGB; no captured pixels/GUI/native acceptance','nativeAcceptance':False};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks),'report':str(out/'report.json')}))
