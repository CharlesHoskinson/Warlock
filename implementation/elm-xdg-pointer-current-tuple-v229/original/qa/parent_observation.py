"""Closed V225 parent proof. No callback-derived transform or hardware claim."""
import math,re
class Refused(ValueError):pass

def keys(value,names):
 if type(value) is not dict or set(value)!=set(names):raise Refused('Exact observer fields')
def integer(v,lo,hi):
 if type(v) is not int or not lo<=v<=hi:raise Refused('Canonical observer integer')
 return v
def start(v):
 if type(v) is not str or not re.fullmatch(r'[1-9][0-9]{0,19}',v) or int(v)>2**64-1:raise Refused('Canonical process start')
 return v
def point(v):
 if type(v) is not list or len(v)!=2 or any(type(n) not in (int,float) or abs(n)>4096 or (type(n) is float and not math.isfinite(n)) for n in v):raise Refused('Bounded observer point')
 return v
def proof(value,*,sequence,parent_pid,parent_start,uid,controller_pid,controller_start,target_pid,target_start,global_point):
 keys(value,['schema','sequence','revision','parent','controller','target','viewId','surfaceId','surfaceExtent','corners','viewportDestination','output','pointer'])
 integer(value['schema'],1,1);integer(value['sequence'],sequence,sequence);integer(value['revision'],1,2**32-1)
 for name,pid,started in [('parent',parent_pid,parent_start),('controller',controller_pid,controller_start),('target',target_pid,target_start)]:
  keys(value[name],['pid','started','uid'] if name=='parent' else ['pid','started'])
  if integer(value[name]['pid'],2,2**31-1)!=pid or start(value[name]['started'])!=start(started):raise Refused('Observer owning process mismatch')
 if integer(value['parent']['uid'],0,2**32-1)!=uid:raise Refused('Observer UID')
 view=integer(value['viewId'],1,2**32-1);surface=integer(value['surfaceId'],1,2**32-1)
 extent=value['surfaceExtent']
 if type(extent) is not list or len(extent)!=2 or [integer(n,1,4096) for n in extent]!=[800,600]:raise Refused('Selected parent surface extent')
 destination=value['viewportDestination']
 if type(destination) is not list or len(destination)!=2 or any(type(n) is not int for n in destination) or destination not in ([800,600],[-1,-1]):raise Refused('Parent destination identity mapping')
 corners=value['corners']
 if type(corners) is not list or len(corners)!=4 or [point(c) for c in corners]!=[[0,0],[800,0],[0,600],[800,600]]:raise Refused('Actual parent surface placement/transform')
 output=value['output'];keys(output,['id','name','origin','logicalExtent','modeExtent','scale'])
 integer(output['id'],0,2**32-1)
 if type(output['name']) is not str or not 1<=len(output['name'])<=128 or any(ord(c)<32 or ord(c)==127 for c in output['name']):raise Refused('Parent output name')
 if point(output['origin'])!=[0,0]:raise Refused('Parent output origin')
 for name in ['logicalExtent','modeExtent']:
  if type(output[name]) is not list or len(output[name])!=2 or [integer(n,1,4096) for n in output[name]]!=[800,600]:raise Refused('Parent output extent')
 integer(output['scale'],1,1)
 pointer=value['pointer'];keys(pointer,['global','focusedPid','focusedStarted','focusedViewId','focusedSurfaceId'])
 if point(pointer['global'])!=point(global_point):raise Refused('Parent pointer actual point')
 if integer(pointer['focusedPid'],2,2**31-1)!=target_pid or start(pointer['focusedStarted'])!=target_start or integer(pointer['focusedViewId'],1,2**32-1)!=view or integer(pointer['focusedSurfaceId'],1,2**32-1)!=surface:raise Refused('Exact parent focused nested root')
 return {'revision':value['revision'],'viewId':view,'surfaceId':surface,'output':output,'corners':corners,'destination':destination,'physicalHardwareAccepted':False}
