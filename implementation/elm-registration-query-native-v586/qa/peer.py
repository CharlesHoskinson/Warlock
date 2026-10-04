import json,os,sys,time
from pathlib import Path
config_path,control,output=map(Path,sys.argv[1:]);config=json.loads(config_path.read_text())
sys.path.insert(0,config.pop('adapter'));from effect_endpoint import Endpoint
from endpoint import ValidatedNativeRefusal
endpoint=Endpoint(**config);last=0;deadline=time.monotonic()+90
while time.monotonic()<deadline:
 if not control.exists():time.sleep(.01);continue
 command=json.loads(control.read_text());seq=command['sequence']
 if seq<=last:time.sleep(.01);continue
 last=seq
 if command['operation']=='quit':break
 try:
  response=endpoint.hello() if command['operation']=='hello' else endpoint.request(command['request']);row={'sequence':seq,'ok':True,'response':response,'pid':os.getpid()}
 except ValidatedNativeRefusal as error:row={'sequence':seq,'ok':False,'reason':error.reason,'pid':os.getpid()}
 temp=output.with_suffix('.tmp');temp.write_text(json.dumps(row)+'\n');temp.replace(output)
else:raise RuntimeError('Peer observation deadline')
