"""Pure same-object frontend observations; no IPC, launch or input side effects."""
from decimal import Decimal
import base64,json,math,os,re
from native_authority import token,public,complete,integer_point,input_safe,protected_order
from root_pin_helper import command,strict_json

def integer(v,low=1,high=2**53-1):
 if type(v)is not int or not low<=v<=high:raise ValueError('Typed bounded integer required')
 return v
def numeric(v):
 if type(v)not in(int,float)or not math.isfinite(v):raise ValueError('Finite typed allocation coordinate required')
 return Decimal(str(v))
def exact(a,b):return json.dumps(a,sort_keys=True,allow_nan=False,separators=(',',':'))==json.dumps(b,sort_keys=True,allow_nan=False,separators=(',',':'))
def layer(native,shell_pid,namespace):
 integer(shell_pid,high=2147483647)
 rows=native.get('layers')
 if type(rows)is not list:raise ValueError('Actual owning-layer enumeration required')
 found=[r for r in rows if type(r)is dict and type(r.get('pid'))is int and r['pid']==shell_pid and r.get('namespace')==namespace and r.get('mapped')is True and r.get('visible')is True]
 if len(found)!=1:raise ValueError('One actual current QS-owned layer required')
 row=found[0]
 if type(row.get('address'))is not str or not re.fullmatch(r'0x[1-9a-f][0-9a-f]{0,15}',row['address']):raise ValueError('Actual native layer identity required')
 if type(row.get('box'))is not list or len(row['box'])!=4:raise ValueError('Actual native logicalBox required')
 x,y,w,h=map(numeric,row['box'])
 if w<=0 or h<=0:raise ValueError('Positive actual layer allocation required')
 return dict(row)
def binding(menu,native,shell_scope,width=1600,height=1000):
 if type(shell_scope)is not dict or set(shell_scope)!= {'pid','start','configSHA256','engineEpoch'}:raise ValueError('Exact external shell/config/engine scope required')
 integer(shell_scope['pid'],high=2147483647);integer(shell_scope['engineEpoch'])
 if type(shell_scope['start'])is not str or not re.fullmatch(r'[1-9][0-9]*',shell_scope['start'])or type(shell_scope['configSHA256'])is not str or not re.fullmatch(r'[0-9a-f]{64}',shell_scope['configSHA256']):raise ValueError('External scope representation differs')
 if type(menu)is not dict or menu.get('open')is not True or menu.get('status')!='ready' or menu.get('sent')is not False:raise ValueError('Actual current captured eligible menu required')
 captured=token(menu.get('captured'));integer(menu.get('nonce'))
 if not exact(menu.get('publicIdentity'),public(captured))or menu.get('layerNamespace')!='hoskinson-pin-window-menu':raise ValueError('Same captured actual menu member required')
 row=layer(native,shell_scope['pid'],menu['layerNamespace']);button=menu.get('button')
 if type(button)is not dict or button.get('visible')is not True or button.get('enabled')is not True or button.get('label')!='Toggle pin':raise ValueError('Actual enabled per-window Toggle pin row required')
 local=[numeric(button.get(k))for k in('x','y','width','height')];x,y,w,h=map(numeric,row['box']);bx,by,bw,bh=local
 if bx<0 or by<0 or bw<=0 or bh<=0 or bx+bw>w or by+bh>h:raise ValueError('Whole actual row must lie inside witnessed layer')
 point=integer_point([str(x+bx),str(y+by),str(bw),str(bh)],width,height)
 return dict(shell=dict(shell_scope),nonce=menu['nonce'],captured=captured,layer=row,button=dict(button),point=point)
def current(menu,native,shell_scope,expected):
 value=binding(menu,native,shell_scope)
 if not exact(value,expected):raise ValueError('Current menu/object/output/row/engine witness changed')
 return value
def pointer(native,expected):
 input_safe(native)
 if native.get('pointerSurfacePresent')is not True or not exact(native.get('pointerLayerOwner'),expected['layer']):raise ValueError('Actual selected pointer layer required')
 cursor=native.get('cursor')
 if type(cursor)is not list or len(cursor)!=2 or any(numeric(v)!=Decimal(p)for v,p in zip(cursor,expected['point'])):raise ValueError('Exact actual integer cursor required')
 return True
def keyboard(native,expected):
 input_safe(native)
 if native.get('keyboardSurfacePresent')is not True or not exact(native.get('keyboardLayerOwner'),expected['layer']):raise ValueError('Actual Seat keyboard layer required; Core focus insufficient')
 return True
def process_identity(value):
 if type(value)is not dict or set(value)!= {'pid','start','parent','pgid'}:raise ValueError('Exact actual helper process lifetime required')
 for key in('pid','parent','pgid'):integer(value[key],high=2147483647)
 if type(value['start'])is not str or not re.fullmatch(r'[1-9][0-9]*',value['start']):raise ValueError('Exact helper start required')
 return value
def helper(receipt,captured,before_pinned,requester,compositor):
 token(captured);process_identity(requester);process_identity(compositor)
 if type(receipt)is not dict or receipt.get('result')!='complete' or receipt.get('nativeCompletionClaimed')is not True or type(receipt.get('automaticRetries'))is not int or receipt['automaticRetries']!=0 or not exact(token(receipt.get('captured')),captured):raise ValueError('Actual complete helper receipt required')
 authority=receipt.get('authority')
 if type(authority)is not dict or authority.get('role')!='shell' or not exact(process_identity(authority.get('requester')),requester)or not exact(process_identity(authority.get('compositor')),compositor):raise ValueError('Genuine QS requester and private compositor required')
 own=process_identity(authority.get('frontend'))
 if own['parent']!=requester['pid']or own['pid']in(requester['pid'],compositor['pid']):raise ValueError('Actual distinct QS-child helper required')
 transport=receipt.get('transport')
 if type(transport)is not dict or transport.get('sendStarted')is not True or transport.get('completeServerEOF')is not True:raise ValueError('Exact complete actual private IPC transport required')
 peer=transport.get('peer')
 if type(peer)is not dict or type(peer.get('pid'))is not int or peer['pid']!=compositor['pid']or type(peer.get('uid'))is not int or peer['uid']!=os.getuid():raise ValueError('Exact actual private compositor peer required')
 if type(transport.get('commandBase64'))is not str or base64.b64decode(transport['commandBase64'],validate=True)!=command(captured):raise ValueError('Exact actual captured native request bytes required')
 if type(transport.get('rawReplyBase64'))is not str:raise ValueError('Actual complete raw native reply required')
 raw=base64.b64decode(transport['rawReplyBase64'],validate=True)
 if not 0<len(raw)<=65536 or type(transport.get('replyBytes'))is not int or len(raw)!=transport['replyBytes']or not exact(strict_json(raw.decode()),receipt.get('rawNativeResult'))or 'error'in transport:raise ValueError('Raw native reply/EOF observation differs')
 complete(receipt.get('rawNativeResult'),captured,before_pinned)
 return own

class FrontendCase:
 def __init__(self,expected):self.expected=expected;self.pressed=False;self.released=False;self.current=True;self.receipt=False;self.observed=False
 def press(self,menu,native,scope,route):
  if not self.current:raise ValueError('Retired menu witness cannot input')
  current(menu,native,scope,self.expected)
  if route=='pointer':pointer(native,self.expected)
  elif route=='return':keyboard(native,self.expected)
  else:raise ValueError('Genuine admitted frontend input route required')
  self.pressed=True;self.released=False
 def release(self,actual):
  if actual is not True or not self.current or not self.pressed:raise ValueError('Actual matching release required')
  self.released=True
 def invalidate(self):self.current=False;self.receipt=False;self.observed=False
 def accept(self):
  if not(self.current and self.pressed and self.released and self.receipt and self.observed):raise ValueError('No completion without actual release/current receipt/state')
  return True

def shell_requester(config,shell_pid):
 integer(shell_pid,high=2147483647)
 roots=config.get('requestRoots')
 if type(roots)is not list:raise ValueError('Actual registered request roots required')
 found=[r for r in roots if type(r)is dict and r.get('role')=='shell']
 if len(found)!=1:raise ValueError('One actual registered shell requester required')
 own=process_identity(found[0].get('identity'))
 if own['pid']!=shell_pid:raise ValueError('Registered shell requester differs from actual QS')
 return own

def completion_current(menu,native,scope,expected):
 # The same real row becomes disabled after its one-shot action is sent.
 if type(menu)is not dict or menu.get('open')is not True or menu.get('status')!='complete' or menu.get('sent')is not True or type(menu.get('nonce'))is not int or menu['nonce']!=expected['nonce'] or not exact(token(menu.get('captured')),expected['captured']) or not exact(scope,expected['shell']):raise ValueError('Completed menu/action/engine identity changed')
 if not exact(menu.get('publicIdentity'),public(expected['captured']))or menu.get('layerNamespace')!=expected['layer']['namespace']or not exact(layer(native,scope['pid'],menu['layerNamespace']),expected['layer']):raise ValueError('Same completed real native layer/member required')
 button=dict(expected['button'],enabled=False)
 if not exact(menu.get('button'),button):raise ValueError('Completed actual row allocation/label/visibility changed')
 return True

def focus_projection(scene):
 # Input history/keymap/device diagnostics are retained raw, not focus authority.
 seat=scene.get('seat');native=scene.get('native')
 if type(seat)is not dict or type(native)is not dict or 'nativeFocus'not in native:raise ValueError('Actual Core and Seat observation required')
 keys=('keyboardOwner','coreNativeFocus','keyboardSurfacePresent','keyboardResourcePresent')
 if any(k not in seat for k in keys)or any(type(seat[k])is not bool for k in keys[2:]):raise ValueError('Typed actual Seat owner/presence fields required')
 return dict(core=native['nativeFocus'],seat={k:seat[k]for k in keys})

def one_native_event(before,after,receipt):
 if type(before)is not list or type(after)is not list or len(after)!=len(before)+1 or not exact(after[:-1],before)or not exact(after[-1],receipt):raise ValueError('One actual native event exactly bound to helper raw result required')
 return after[-1]
