"""Draft fixed B-only setup. No host edit, backend fallback, or implicit invocation."""
import json,time

SECOND='PIN-B-2'
PRIVATE_MONITOR_LUA=b'\nhl.monitor({output="PIN-B-2",mode="1600x1000@60",position="1600x0",scale=1,transform=0})\n'
def require(value,message):
 if value is not True:raise ValueError(message)
def complete_outputs(rows):
 require(type(rows)is list and len(rows)==2 and all(type(r)is dict for r in rows),'two actual complete outputs')
 by={r['name']:r for r in rows};require(set(by)=={'WAYLAND-1',SECOND}and len({r['id']for r in rows})==2,'distinct native outputs')
 for name,x in [('WAYLAND-1',0),(SECOND,1600)]:
  row=by[name]
  for key,value in [('width',1600),('height',1000),('x',x),('y',0),('transform',0)]:require(type(row.get(key))is int and row[key]==value,'actual typed output '+key)
  require(type(row.get('scale'))in {int,float}and not isinstance(row['scale'],bool)and row['scale']==1,'actual exact unit scale')
  require(type(row.get('disabled'))is bool and row['disabled']is False and row.get('dpmsStatus')is True,'actual enabled outputs')
 return rows
def create(session,record,attest):
 # The second monitor declaration must already be in the root-owned startup
 # config. No monitor reload, guessed name or arbitrary backend request.
 attest('before-private-second-output');session.guard()
 before=record('actual outputs before fixed creation',lambda:session.data('monitors'))
 require(type(before)is list and len(before)==1 and before[0].get('name')=='WAYLAND-1','one initial reviewed parent-backed output')
 record('fixed explicit wayland output setup ACK only',lambda:session.ctl('output','create','wayland',SECOND))
 deadline=time.monotonic()+5
 while time.monotonic()<deadline:
  session.guard();rows=record('actual second configure/readiness',lambda:session.data('monitors'))
  if type(rows)is list and len(rows)==2:
   complete_outputs(rows);attest('after-private-second-output');return rows
  require(type(rows)is list and len(rows)==1 and rows[0].get('name')=='WAYLAND-1','no unknown/replaced output during preparation')
  time.sleep(.04)
 raise TimeoutError('Fixed original observation budget; no output/backend retry')
