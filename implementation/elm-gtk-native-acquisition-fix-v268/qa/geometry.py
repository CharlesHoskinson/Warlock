"""Measured GTK native/widget/surface conversion; inputs are independent facts."""
import math
from journal import Refused,integer

def number(value):
 if type(value) not in (int,float) or abs(value)>2**23 or (type(value) is float and not math.isfinite(value)):raise Refused('finite bounded geometry')
 return value
def point(value):
 if type(value) not in (list,tuple) or len(value)!=2:raise Refused('coordinate pair shape')
 return [number(v) for v in value]
def extent(value):
 values=point(value)
 if any(v<=0 for v in values):raise Refused('positive extent')
 return values

def marker(role,*,identity,native_real,window_geometry,local=(8,8)):
 if type(role) is not dict or type(identity) is not dict or set(identity)!={'role','instance','mapGeneration','surfaceId'}:raise Refused('bound landmark role identity')
 if role.get('role')!=identity['role']:raise Refused('landmark role changed')
 for key in ('instance','mapGeneration','surfaceId'):
  if integer(role.get(key),1,2**32-1)!=integer(identity[key],1,2**32-1):raise Refused('landmark lifetime/resource/map changed')
 if role.get('mapped') is not True or role.get('landmarkBoundsAvailable') is not True:raise Refused('actual mapped GTK landmark bounds absent')
 if type(native_real) is not list or len(native_real)!=4 or type(window_geometry) is not list or len(window_geometry)!=4:raise Refused('measured rectangles')
 rx,ry=point(native_real[:2]);rw,rh=extent(native_real[2:]);gx,gy=point(window_geometry[:2]);gw,gh=extent(window_geometry[2:]);local=point(local)
 if [rw,rh]!=[gw,gh]:raise Refused('Q1 equal native/window geometry extent unqualified')
 width=number(role.get('landmarkWidth'));height=number(role.get('landmarkHeight'))
 if not 0<=local[0]<width or not 0<=local[1]<height:raise Refused('local marker outside actual allocation')
 widget=[number(role.get('landmarkNativeX'))+local[0],number(role.get('landmarkNativeY'))+local[1]]
 transform=[number(role.get('nativeSurfaceTransformX')),number(role.get('nativeSurfaceTransformY'))]
 # Official GtkNative transform translates surface into widget, so invert once.
 surface=[widget[i]-transform[i] for i in range(2)]
 sw=integer(role.get('surfaceWidth'),1,2**23);sh=integer(role.get('surfaceHeight'),1,2**23)
 if not 0<=surface[0]<sw or not 0<=surface[1]<sh:raise Refused('landmark outside actual GDK surface')
 global_point=[rx+surface[0]-gx,ry+surface[1]-gy]
 if any(v!=int(v) or not 0<=v<bound for v,bound in zip(global_point,(800,600))):raise Refused('integer current private-output marker point required')
 return {'widget':widget,'surface':surface,'global':[int(v) for v in global_point],'nativeReal':native_real,'windowGeometry':window_geometry,'identity':identity}


def attribution(selected,other):
 p=selected['marker']['global'];x,y=point(p);rx,ry=point(selected['native']['at']);rw,rh=extent(selected['native']['size'])
 if not (rx<=x-1 and ry<=y-1 and x+2<=rx+rw and y+2<=ry+rh):raise Refused('all selected3x3 pixels must lie within selected native real rect')
 ox,oy=point(other['native']['at']);gx,gy=point(other['wire']['windowGeometry'][:2]);sw=integer(other['gtk'].get('surfaceWidth'),1,2**23);sh=integer(other['gtk'].get('surfaceHeight'),1,2**23)
 surface=[ox-gx,oy-gy,sw,sh]
 if not (x+2<=surface[0] or surface[0]+sw<=x-1 or y+2<=surface[1] or surface[1]+sh<=y-1):raise Refused('other entire GTKsurface/CSD/shadow intersects selected3x3 pixels')
 return {'selectedSampleRect':[x-1,y-1,3,3],'selectedRealRect':[rx,ry,rw,rh],'excludedOtherSurfaceRect':surface}
