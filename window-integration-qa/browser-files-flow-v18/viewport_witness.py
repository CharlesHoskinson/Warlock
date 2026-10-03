"""Exact bounded coordinate proof. Pure validation; no desktop/process/input access."""
from fractions import Fraction
import math,re

WIDTH,HEIGHT=1600,1000

def number(value):
 if type(value) not in (int,float) or not math.isfinite(value):raise ValueError('Finite nonboolean coordinate required')
 return Fraction(value)

def vector(value,length):
 if not isinstance(value,list) or len(value)!=length:raise ValueError('Exact coordinate vector shape required')
 return tuple(number(x) for x in value)

def move_command(point):
 if not isinstance(point,list) or len(point)!=2 or any(type(x)is not int for x in point):raise ValueError('Two exact integer pointer tokens required')
 if not (0<=point[0]<WIDTH and 0<=point[1]<HEIGHT):raise ValueError('Pointer tokens outside private output')
 command=f'move {point[0]} {point[1]}\n'
 if re.fullmatch(r'move [0-9]+ [0-9]+\n',command)is None:raise ValueError('Exact complete integer move grammar required')
 return command

def integer_interior(rect,margin):
 x,y,w,h=vector(rect,4);m=number(margin)
 if m<0 or w<=2*m or h<=2*m:raise ValueError('Nonempty interior rectangle required')
 point=[math.floor(x+w/2),math.floor(y+h/2)]
 if not (x+m<point[0]<x+w-m and y+m<point[1]<y+h-m):raise ValueError('No selected exact integer strictly inside rectangle')
 move_command(point)
 return point

def round_half_away(value):
 value=number(value)
 return math.floor(value+Fraction(1,2)) if value>=0 else -math.floor(-value+Fraction(1,2))

def wire_point(cursor,surface):
 vector(cursor,2);s=vector(surface,4);result=[]
 for axis in (0,1):
  # Match the actual binary64 local subtraction and power-of-two scaling.
  local=float(cursor[axis])-float(surface[axis])
  if not 1<local<float(surface[axis+2])-1:raise ValueError('Pointer must avoid protocol edge clipping')
  result.append(s[axis]+Fraction(round_half_away(local*256.0),256))
 return tuple(result)

def exact_float(value):
 result=float(value)
 if not math.isfinite(result) or Fraction(result)!=value:raise ValueError('Coordinate not exactly representable as binary64')
 return result

def key(dom,surface,identity,session):
 s=vector(surface,4);inner=vector(dom['inner'],2);outer=vector(dom['outer'],2);rect=vector(dom['rect'],4)
 if not (s[0]>=0 and s[1]>=0 and s[2]>0 and s[3]>0 and s[0]+s[2]<=WIDTH and s[1]+s[3]<=HEIGHT):raise ValueError('Exact native surface outside private output')
 if outer!=s[2:] or any(x<=0 for x in inner) or inner[0]>s[2] or inner[1]>s[3] or number(dom['ratio'])!=1:raise ValueError('Exact native outer/positive unscaled DOM viewport required')
 if rect[0]<0 or rect[1]<0 or rect[2]<=20 or rect[3]<=20 or rect[0]+rect[2]>inner[0] or rect[1]+rect[3]>inner[1]:raise ValueError('Textarea rectangle outside exact positive viewport')
 vv=dom['viewport']
 if vector(vv,5)!=(inner[0],inner[1],Fraction(1),Fraction(0),Fraction(0)) or vector(dom['scroll'],2)!=(0,0):raise ValueError('Exact visual viewport/no scroll basis required')
 if number(dom['timeOrigin'])<=0 or not isinstance(session,str) or not session:raise ValueError('Exact live page timeOrigin/session required')
 if set(identity)!={'address','stableId','pid','start'} or type(identity['pid'])is not int or identity['pid']<=0 or not all(identity[k]for k in ('address','stableId','start')):raise ValueError('Exact browser lifetime required')
 return {'identity':dict(identity),'session':session,'surfaceBox':list(surface),'inner':list(dom['inner']),'outer':list(dom['outer']),'rect':list(dom['rect']),'ratio':dom['ratio'],'viewport':list(vv),'scroll':list(dom['scroll']),'timeOrigin':dom['timeOrigin'],'url':dom['url'],'title':dom['title']}

def unchanged(before,after):
 return all(before[k]==after[k]for k in ('value','selection','active','clicks','events'))

def clear(snapshot):
 return not any(snapshot[k]for k in ('sessionLocked','exclusiveLayers','constrained','heldButtons','seatGrab','captured','dnd','dragTarget')) and snapshot['clickMode']==0

def selected_event(before,after):
 if type(before['pointerSequence'])is not int or type(after['pointerSequence'])is not int or not 0<=before['pointerSequence']<after['pointerSequence']<=65536:raise ValueError('Fresh bounded pointer event sequence required')
 rows=[r for r in after['pointerMoves']if r['sequence']>before['pointerSequence']]
 if not rows or rows[-1]['sequence']!=after['pointerSequence']:raise ValueError('Latest event sequence not retained')
 if len(rows)!=after['pointerSequence']-before['pointerSequence']:raise ValueError('Pointer event gap or bound truncation')
 coordinates=set()
 previous=before['pointerSequence']
 for row in rows:
  if type(row['sequence'])is not int or row['sequence']!=previous+1:raise ValueError('Serial event sequence required')
  previous=row['sequence']
  if row['trusted']is not True or row['type']!='pointermove' or row['pointerType']!='mouse' or row['primary']is not True or type(row['buttons'])is not int or row['buttons']!=0 or type(row['pointerId'])is not int or row['pointerId']<=0 or not isinstance(row['modifiers'],list) or len(row['modifiers'])!=4 or any(type(v)is not bool or v for v in row['modifiers']):raise ValueError('Trusted primary unmodified button-free mouse motion required')
  if not (number(before['now'])<=number(row['timestamp'])<=number(row['handled'])<=number(after['now'])):raise ValueError('Original event timestamp outside same-page selected move interval')
  coordinates.add(vector(row['client'],2))
 if len(coordinates)!=1 or len({r['pointerId']for r in rows})!=1:raise ValueError('Ambiguous intermediate/final DOM motion positions')
 return rows[-1]

def sample(before,after,native_before,native_after,surface,identity,session,expected_key,expected_focus):
 if key(before,surface,identity,session)!=expected_key or key(after,surface,identity,session)!=expected_key or not unchanged(before,after):raise ValueError('Page/layout/lifetime changed during coordinate observation')
 for native in (native_before,native_after):
  if not clear(native) or native['nativeFocus']!=expected_focus or not native['pointerSurfacePresent']:raise ValueError('Native input/focus state changed')
  for role in ('hitOwner','pointerOwner'):
   peer=native[role]
   if not peer or any(peer[k]!=identity[k]for k in ('address','stableId','pid')) or peer['surfaceBox']!=surface:raise ValueError('Exact native browser pointer and hit owner required')
 if vector(native_before['cursor'],2)!=vector(native_after['cursor'],2):raise ValueError('Native cursor changed while reading DOM event')
 event=selected_event(before,after);client=vector(event['client'],2);inner=vector(after['inner'],2)
 if not all(0<=client[i]<inner[i]for i in (0,1)):raise ValueError('Actual event outside DOM viewport')
 wire=wire_point(native_after['cursor'],surface)
 return {'key':expected_key,'event':event,'cursor':list(native_after['cursor']),'wire':wire,'offset':tuple(wire[i]-client[i]for i in (0,1))}

def pair(first,second):
 if first['key']!=second['key'] or second['event']['sequence']<=first['event']['sequence'] or first['event']['pointerId']!=second['event']['pointerId']:raise ValueError('Same exact current layout and serial samples required')
 if any(first['wire'][i]==second['wire'][i]for i in (0,1)) or first['offset']!=second['offset']:raise ValueError('Two distinct exact translations required')
 offset=first['offset'];k=first['key'];s=vector(k['surfaceBox'],4);inner=vector(k['inner'],2)
 insets=[offset[0]-s[0],offset[1]-s[1],s[0]+s[2]-offset[0]-inner[0],s[1]+s[3]-offset[1]-inner[1]]
 if any(x<0 for x in insets):raise ValueError('Derived viewport not contained in actual native surface')
 r=vector(k['rect'],4);global_rect=[exact_float(offset[0]+r[0]),exact_float(offset[1]+r[1]),exact_float(r[2]),exact_float(r[3])]
 point=integer_interior(global_rect,10)
 return {'key':k,'translation':[exact_float(x)for x in offset],'insets':[exact_float(x)for x in insets],'viewportBox':[exact_float(offset[0]),exact_float(offset[1]),*k['inner']],'textareaGlobalRect':global_rect,'integerPoint':point,'eventSequences':[first['event']['sequence'],second['event']['sequence']],'wireBasis':'surface origin + round(binary64(cursor-origin)*256)/256; half away, interior only','accepted':True,'originalFeatureAcceptance':False}
