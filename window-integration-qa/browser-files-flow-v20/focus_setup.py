"""Pure exact setup guards and Lua command construction; no process/input access."""
import re
from viewport_witness import clear,vector,move_command

def identity_valid(identity,session):
 if not isinstance(identity,dict) or set(identity)!={'address','stableId','pid','start'}:raise ValueError('Exact Browser lifetime required')
 if type(identity['pid'])is not int or identity['pid']<=0:raise ValueError('Positive exact Browser PID required')
 for name,pattern in [('address',r'0x[0-9a-f]+'),('stableId',r'[0-9a-f]+'),('start',r'[1-9][0-9]*')]:
  if not isinstance(identity[name],str) or re.fullmatch(pattern,identity[name])is None:raise ValueError('Exact native identity syntax required:'+name)
 if not isinstance(session,str) or not session:raise ValueError('Exact attached private page session required')

def command(identity,session):
 identity_valid(identity,session)
 address=identity['address'];stable=identity['stableId'];pid=identity['pid']
 ack=f'qa-browser-focus-setup-ack:{address}:{stable}:{pid}'
 script=f'''do
local w=hl.get_window("address:{address}")
assert(w,"Exact captured private Browser absent")
local a,s,p=hl.plugin.hyprbars.window_lifetime(w)
assert(a=="{address}" and s=="{stable}" and p=={pid},"Private Browser lifetime changed before focus setup")
local result=hl.dispatch(hl.dsp.focus({{window="address:{address}"}}))
local z=hl.get_window("address:{address}")
assert(z,"Exact captured private Browser absent after focus setup")
local aa,ss,pp=hl.plugin.hyprbars.window_lifetime(z)
assert(aa==a and ss==s and pp==p,"Private Browser lifetime changed during focus setup")
local fields={{}}
if type(result)=="table" then
 for k,v in pairs(result) do fields[#fields+1]=tostring(k).."="..tostring(v) end
 table.sort(fields)
end
print("qa-browser-focus-setup-result:"..type(result)..":"..table.concat(fields,","))
print("{ack}")
end'''
 return script,ack

def validate_ack(raw,ack):
 if not isinstance(raw,str):raise ValueError('Raw command acknowledgement required')
 lines=raw.splitlines()
 if len(lines)!=2 or not lines[0].startswith('qa-browser-focus-setup-result:') or lines[1]!=ack:raise ValueError('Exact complete setup command acknowledgement required')
 # IPC completion/returned-result diagnostics are deliberately separate from
 # actual native focus authority. No inferred checkResult field schema.

def observed(snapshot,identity,session,expected_focus=None):
 identity_valid(identity,session)
 if not clear(snapshot) or snapshot['pointerSurfacePresent']is not True:raise ValueError('Clear actual native pointer delivery required')
 for role in ('nativeFocus','pointerOwner'):
  peer=snapshot[role]
  if not peer or any(peer.get(k)!=identity[k]for k in ('address','stableId','pid')):raise ValueError('Exact observed Browser '+role+' required')
  if peer.get('mapped')is not True or peer.get('hidden')is not False or peer.get('acceptsInput')is not True:raise ValueError('Current eligible Browser '+role+' required')
 if expected_focus is not None and snapshot['nativeFocus']!=expected_focus:raise ValueError('Exact setup focus snapshot changed')
 return dict(snapshot['nativeFocus'])

def ordered_points(first,second,cursor):
 move_command(first);move_command(second);current=vector(cursor,2)
 if any(first[i]==second[i]for i in (0,1)):raise ValueError('Two distinct candidate axes required')
 return [second,first] if current==vector(first,2) else [first,second]

def require_displacement(point,cursor):
 move_command(point)
 if vector(point,2)==vector(cursor,2):raise ValueError('Calibration requires actual nonzero cursor displacement')
