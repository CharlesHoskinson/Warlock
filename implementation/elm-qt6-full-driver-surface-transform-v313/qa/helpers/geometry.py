"""Qt measured logical-window conversion; no Qt global desktop authority."""
import math
from journal import Refused,integer

def number(v):
 if type(v) not in (int,float) or abs(v)>2**23 or (type(v) is float and not math.isfinite(v)):raise Refused('finite bounded logical coordinate')
 return v

def point(v):
 if type(v) not in (list,tuple) or len(v)!=2:raise Refused('point shape')
 return [number(x) for x in v]

def extent(v):
 r=point(v)
 if any(x<=0 for x in r):raise Refused('positive measured extent')
 return r

def rectangle(v):
 if type(v) not in (list,tuple) or len(v)!=4:raise Refused('rectangle shape')
 return point(v[:2])+extent(v[2:])

def identity(role):
 if type(role) is not dict or role.get('role') not in ('A','B','C','D','P'):raise Refused('Qt role identity')
 return {'role':role['role'],**{k:integer(role.get(k),1,2**32-1) for k in ('instance','mapGeneration','surfaceId')}}

def surface_translation(role):
 if role.get('surfaceTransformAvailable') is not True:raise Refused('actual Qt surface translation unavailable')
 resource=integer(role.get('surfaceTransformResourceId'),1,2**32-1)
 if resource!=integer(role.get('surfaceId'),1,2**32-1):raise Refused('surface translation resource mismatch')
 margins=[integer(role.get('clientMargin'+name),0,2**23) for name in ('Left','Top','Right','Bottom')]
 mapped=point([role.get('surfaceToWindowX'),role.get('surfaceToWindowY')])
 if mapped!=[-margins[0],-margins[1]]:raise Refused('actual Qt map/margins disagreement')
 return mapped


def marker(role,*,identity,native_real,window_geometry,local=(8,8),popup=False):
 if globals()['identity'](role)!=identity or role.get('visible') is not True:raise Refused('visible exact Qt identity')
 rx,ry,rw,rh=rectangle(native_real);gx,gy,gw,gh=rectangle(window_geometry)
 if [rw,rh]!=[gw,gh]:raise Refused('Q1 native/window geometry equality required')
 ww=integer(role.get('windowWidth'),1,2**23);wh=integer(role.get('windowHeight'),1,2**23)
 extent([role.get('devicePixelRatio'),role.get('devicePixelRatio')])
 if popup:
  if role.get('popupMarkerBoundsAvailable') is not True:raise Refused('measured popup marker absent')
  offset=point([role.get('popupMarkerWindowX'),role.get('popupMarkerWindowY')]);size=extent([role.get('popupMarkerWidth'),role.get('popupMarkerHeight')]);local=point(local)
 else:
  offset=point([role.get('landmarkWindowX'),role.get('landmarkWindowY')]);size=extent([role.get('landmarkWidth'),role.get('landmarkHeight')]);local=point(local)
 if not all(0<=local[i]<size[i] for i in range(2)):raise Refused('marker outside measured allocation')
 window=[offset[i]+local[i] for i in range(2)]
 if not 0<=window[0]<ww or not 0<=window[1]<wh:raise Refused('marker outside current QWindow')
 mapped=surface_translation(role)
 surface=[window[i]-mapped[i] for i in range(2)]
 global_point=[rx+surface[0]-gx,ry+surface[1]-gy]
 return {'window':window,'surface':surface,'global':global_point,'surfaceToWindow':mapped,'clientMargins':[role['clientMargin'+n] for n in ('Left','Top','Right','Bottom')],'nativeReal':[rx,ry,rw,rh],'windowGeometry':[gx,gy,gw,gh],'identity':identity,'presentationProved':False}

def action_region(role,*,native_real,window_geometry):
 if role.get('role')!='P' or any(role.get(k) is not True for k in ('actionBoundsAvailable','popupActionEnabled','popupActionVisible')):raise Refused('current enabled visible QAction measured rectangle')
 x,y=point([role.get('actionWindowX'),role.get('actionWindowY')]);w,h=extent([role.get('actionWidth'),role.get('actionHeight')])
 ww=integer(role.get('windowWidth'),1,2**23);wh=integer(role.get('windowHeight'),1,2**23)
 if x<0 or y<0 or x+w>ww or y+h>wh:raise Refused('whole QAction outside measured QWindow')
 rx,ry,rw,rh=rectangle(native_real);gx,gy,gw,gh=rectangle(window_geometry)
 if [rw,rh]!=[gw,gh]:raise Refused('Q1 popup geometry')
 mapped=surface_translation(role)
 sx,sy=x-mapped[0],y-mapped[1]
 return {'window':[x,y,w,h],'surface':[sx,sy,w,h],'global':[rx+sx-gx,ry+sy-gy,w,h],'point':[rx+sx+w/2-gx,ry+sy+h/2-gy],'surfaceToWindow':mapped,'identity':identity(role),'nativeActionAuthority':False}
