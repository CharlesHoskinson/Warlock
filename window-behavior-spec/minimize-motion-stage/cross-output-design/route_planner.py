#!/usr/bin/env python3
"""Offline global-coordinate route/fragment design; no desktop calls."""
from dataclasses import dataclass
import math
@dataclass(frozen=True)
class Rect:
 x:float;y:float;width:float;height:float
 def __post_init__(self):
  if not all(math.isfinite(v) for v in (self.x,self.y,self.width,self.height)) or self.width<=0 or self.height<=0:raise ValueError('invalid rectangle')
 @property
 def right(self):return self.x+self.width
 @property
 def bottom(self):return self.y+self.height
 def clip(self,other):
  x,y=max(self.x,other.x),max(self.y,other.y);r,b=min(self.right,other.right),min(self.bottom,other.bottom)
  return Rect(x,y,r-x,b-y) if r>x and b>y else None
 def lerp(self,end,p):
  if not 0<=p<=1:raise ValueError('invalid progress')
  return Rect(*(a+(b-a)*p for a,b in zip((self.x,self.y,self.width,self.height),(end.x,end.y,end.width,end.height))))
@dataclass(frozen=True)
class Output:
 name:str;x:float;y:float;width:int;height:int;scale:float=1;transform:int=0
 @property
 def bounds(self):
  if not isinstance(self.name,str) or not self.name or not all(math.isfinite(v) for v in (self.x,self.y,self.width,self.height,self.scale)) or self.width<=0 or self.height<=0 or self.scale<=0 or isinstance(self.transform,bool) or not isinstance(self.transform,int) or self.transform not in range(8):raise ValueError('invalid output identity/geometry/scale/transform')
  w,h=(self.height,self.width) if self.transform%2 else (self.width,self.height)
  return Rect(self.x,self.y,w/self.scale,h/self.scale)
@dataclass(frozen=True)
class Fragment:
 output:str;global_clip:Rect;local_clip:Rect;uv:Rect

def validate_outputs(outputs):
 outputs=list(outputs)
 names=set()
 for out in outputs:
  out.bounds # Validate every output even when it does not intersect the route.
  if out.name in names:raise ValueError('duplicate output name')
  names.add(out.name)
 return outputs

def fragments(global_rect,outputs):
 outputs=validate_outputs(outputs)
 result=[]
 for out in outputs:
  clipped=global_rect.clip(out.bounds)
  if clipped:
   result.append(Fragment(out.name,clipped,Rect(clipped.x-out.x,clipped.y-out.y,clipped.width,clipped.height),
     Rect((clipped.x-global_rect.x)/global_rect.width,(clipped.y-global_rect.y)/global_rect.height,clipped.width/global_rect.width,clipped.height/global_rect.height)))
 return result

def required_outputs(start,end,outputs):
 outputs=validate_outputs(outputs)
 # Lerp rectangles cannot leave this enclosing bound; readiness may safely
 # include extra intersecting outputs instead of discovering them mid-route.
 swept=Rect(min(start.x,end.x),min(start.y,end.y),max(start.right,end.right)-min(start.x,end.x),max(start.bottom,end.bottom)-min(start.y,end.y))
 return [o.name for o in outputs if swept.clip(o.bounds)]
