"""Pure acceptance rules. These functions neither query nor change a desktop."""
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING
import math, re

FIELDS = ('address','stableId','pid','session','compositorPid','compositorStart','incarnation','epoch','generation')
def token(value):
    if type(value) is not dict or set(value)!=set(FIELDS): raise ValueError('Complete captured native token required')
    patterns={'address':r'0x[1-9a-f][0-9a-f]*','stableId':r'0|[1-9a-f][0-9a-f]{0,15}',
              'session':r'[A-Za-z0-9_]+','compositorStart':r'[1-9][0-9]*','incarnation':r'[0-9a-f]{32}',
              'epoch':r'[1-9][0-9]*','generation':r'[1-9][0-9]*'}
    for name,pattern in patterns.items():
        if type(value[name]) is not str or not re.fullmatch(pattern,value[name]):raise ValueError('Exact token representation: '+name)
    if any(type(value[n]) is not int or not 0<value[n]<=2147483647 for n in ('pid','compositorPid')):raise ValueError('Typed native PID required')
    if any(int(value[n])>2**64-1 for n in ('epoch','generation')):raise ValueError('Native uint64 overflow')
    return dict(value)

def public(value):return {k:token(value)[k] for k in ('address','stableId','pid')}
def matches(row,captured):return type(row) is dict and all(type(row.get(k)) is type(captured[k]) and row.get(k)==captured[k] for k in ('address','stableId','pid'))
def projected(snapshot,captured):
    token(captured)
    fields=('address','stableId','pid','session','incarnation','epoch','generation')
    if type(snapshot) is not dict or any(type(snapshot.get(k)) is not type(captured[k]) or snapshot.get(k)!=captured[k] for k in fields):raise ValueError('Receipt owner/lifetime projection differs')
    for k in ('live','normal','floating','pinned','fullscreen'):
        if type(snapshot.get(k)) is not bool:raise ValueError('Typed receipt state required: '+k)
    return snapshot

def complete(receipt,captured,before_pinned):
    captured=token(captured)
    if type(before_pinned) is not bool:raise ValueError('Typed observed pin intent required')
    if type(receipt) is not dict or receipt.get('ok') is not True or receipt.get('phase')!='complete' or receipt.get('actionsInvoked') is not True or receipt.get('possiblePartialOutcome') is not False or token(receipt.get('captured'))!=captured:raise ValueError('Actual complete typed native receipt required')
    before=projected(receipt.get('before'),captured);after=projected(receipt.get('after'),captured)
    if before['pinned'] is not before_pinned or after['pinned'] is not (not before_pinned) or receipt.get('desiredPinned') is not (not before_pinned):raise ValueError('Actual one-toggle latest native state required')
    if not before['live'] or not before['normal'] or before['fullscreen'] or not after['live'] or not after['normal'] or not after['floating'] or after['fullscreen']:raise ValueError('Actual eligible complete pin state required')
    return True

def integer_point(box,width,height):
    if len(box)!=4 or type(width) is not int or type(height) is not int or width<=0 or height<=0:raise ValueError('Exact output/box required')
    if any(type(v) not in (str,int,float) or isinstance(v,bool) for v in box):raise ValueError('Finite represented box required')
    values=[Decimal(str(v)) for v in box]
    if not all(v.is_finite() for v in values):raise ValueError('Nonfinite box')
    x,y,w,h=values
    if w<=0 or h<=0 or x<0 or y<0 or x+w>width or y+h>height:raise ValueError('Witnessed box outside exact private output')
    result=[]
    for start,size,extent in ((x,w,width),(y,h,height)):
        lo=int(start.to_integral_value(rounding=ROUND_FLOOR))+1
        hi=int((start+size).to_integral_value(rounding=ROUND_CEILING))-1
        if lo>hi:raise ValueError('No integer point strictly inside witnessed box')
        point=(lo+hi)//2
        if not 0<=point<extent or not start<point<start+size:raise ValueError('Integer interior representation failed')
        result.append(point)
    return result

def move_command(point,width,height):
    if type(point) not in (list,tuple) or len(point)!=2 or any(type(x) is not int for x in point) or not 0<=point[0]<width or not 0<=point[1]<height:raise ValueError('Both bounded exact integer tokens required before writing')
    return 'move %d %d\n'%tuple(point)

def input_safe(native):
    names=('sessionLocked','constrained','heldButtons','seatGrab','captured','dnd','dragTarget')
    if any(native.get(k) is not False for k in names) or type(native.get('exclusiveLayers')) is not int or native['exclusiveLayers']!=0 or type(native.get('clickMode')) is not int or native['clickMode']!=0:raise ValueError('Actual private input availability required')
    return True

def cursor_owner(native,point,captured):
    input_safe(native)
    coordinates=native.get('cursor')
    if type(coordinates) is not list or len(coordinates)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in coordinates) or coordinates!=point or not matches(native.get('hitOwner'),captured):raise ValueError('Actual exact native cursor and captured hit owner required')
    return True

def protected_order(stack):
    if type(stack) is not dict or stack.get('planValid') is not True or stack.get('satisfied') is not True:raise ValueError('Actual protected-band verification required')
    rows=stack.get('order')
    if type(rows) is not list or len(rows)>512 or len({r.get('address') for r in rows})!=len(rows):raise ValueError('Bounded unique owning-core order required')
    by={r['address']:r for r in rows};protected=set()
    for row in rows:
        for name in ('eligible','pinned','floating','modal','x11','fullscreen'):
            if type(row.get(name)) is not bool:raise ValueError('Typed native stacking state required')
        if row['eligible'] and row['pinned'] and row['floating'] and not row['fullscreen']:protected.add(row['address'])
    for _ in rows:
        for row in rows:
            parent=by.get(row['parent'])
            if parent and parent['address'] in protected and row['eligible'] and row['workspace']==parent['workspace'] and row['monitor']==parent['monitor'] and (row['modal'] or row['x11'] and parent['x11']):protected.add(row['address'])
    order=[r['address'] for r in rows];band=[a for a in order if a in protected]
    if band and order[-len(band):]!=band:raise ValueError('Independent actual core order lacks protected suffix')
    for address in band:
        parent=by[address]['parent']
        if parent in protected and order.index(parent)>=order.index(address):raise ValueError('Actual modal/transient order reversed')
    return band

class Case:
    def __init__(self,captured):self.captured=token(captured);self.pressed=False;self.released=False;self.current=True;self.receipt=False;self.observed=False
    def press(self,actual,owner):
        if actual is not True or owner is not True or not self.current:raise ValueError('Actual same-owner input required')
        self.pressed=True;self.released=False
    def release(self,actual):
        if actual is not True or not self.pressed or not self.current:raise ValueError('Actual same-episode release required')
        self.released=True
    def invalidate(self):self.current=False;self.receipt=False;self.observed=False
    def accept(self):
        if not(self.current and self.pressed and self.released and self.receipt and self.observed):raise ValueError('No feature authority before actual input/release/receipt/current observation')
        return True
