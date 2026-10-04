import json,select,sys,time
from pathlib import Path
path=Path(sys.argv[1]);last=None
while True:
 ready,_,_=select.select([sys.stdin],[],[],.025)
 if ready:
  line=sys.stdin.readline()
  if not line:break
  raise RuntimeError('Presentation fixture forbids backend effect/observation requests')
 if path.exists():
  name=json.loads(path.read_text())['name']
  if name!=last:
   assert name in ('bar','popup','bar-focus');last=name
   print(json.dumps({'protocolVersion':3,'kind':'fixture-presentation','name':name}),flush=True)
