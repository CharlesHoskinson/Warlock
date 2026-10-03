from pathlib import Path
import json
B=Path(__file__).resolve().parent

def wheel_policy(rows,kind,auth):
 down=set();pending=False;last=-1
 for row in rows:
  if row['pid']!=9 or row['start']!='7' or row['sentNs']<=last:return False
  last=row['sentNs'];command=row['command']
  if pending and command!='sync':return False
  if command.startswith('button '):
   parts=command.split();code,state=int(parts[1]),int(parts[2])
   if (code in down)==bool(state):return False
   if state:down.add(code)
   else:down.remove(code)
  elif command in ('wheel 1','wheel -1'):
   if kind!='pointer' or not auth or down:return False
   pending=True
  elif command=='sync':pending=False
  else:return False
 return not pending and not down

def rows(commands):return [dict(pid=9,start='7',sentNs=i+1,command=c) for i,c in enumerate(commands)]
cases=[('literal-positive',rows(['wheel 1','sync']),'pointer',True,True),('literal-negative',rows(['wheel -1','sync']),'pointer',True,True),('held-refuses',rows(['button 272 1','wheel 1','sync','button 272 0']),'pointer',True,False),('released-pair',rows(['button 272 1','sync','button 272 0','sync','wheel -1','sync']),'pointer',True,True),('unauthorized',rows(['wheel 1','sync']),'pointer',False,False),('keyboard',rows(['wheel 1','sync']),'keyboard',True,False),('missing-sync',rows(['wheel 1']),'pointer',True,False),('interposed-command',rows(['wheel 1','button 272 1','sync']),'pointer',True,False),('duplicate-detent',rows(['wheel 1','wheel 1','sync']),'pointer',True,False)]
for command in ['wheel 0','wheel 2','wheel -2','wheel 1.0','wheel +1','wheel 1 extra','wheel  1',' wheel 1','wheel 1 ']:cases.append(('malformed-'+repr(command),rows([command,'sync']),'pointer',True,False))
changed=rows(['wheel 1','sync']);changed[1]['start']='8';cases.append(('changed-lifetime',changed,'pointer',True,False))
for name,commands,kind,auth,expected in cases:
 actual=wheel_policy(commands,kind,auth)
 if actual!=expected:raise AssertionError(name)
with (B/'cpu-policy-before-runtime.json').open('x') as f:json.dump(dict(result='pass',cases=[c[0] for c in cases],nativeLaunch=False,runtimeImplemented=False),f,indent=2);f.write('\n')
print('PASS',len(cases))
