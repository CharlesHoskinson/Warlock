"""Native desktop point to measured current Qt input locals; no effect authority."""
from geometry import point,rectangle,identity,surface_translation
from journal import Refused,integer

def input_coordinates(binding,global_point):
 if type(binding) is not dict or type(binding.get('qt')) is not dict:raise Refused('current Qt binding')
 qt=binding['qt'];actual=identity(qt);captured=binding.get('identity')
 if type(captured) is not dict or any(captured.get(k)!=v or type(captured.get(k))!=type(v) for k,v in actual.items()):raise Refused('input translation identity mismatch')
 if qt.get('visible') is not True:raise Refused('visible current Qt input target')
 rx,ry,rw,rh=rectangle([*binding['native']['at'],*binding['native']['size']]);gx,gy,gw,gh=rectangle(binding['wire']['windowGeometry'])
 if [rw,rh]!=[gw,gh]:raise Refused('Q1 current input geometry')
 global_point=point(global_point);mapped=surface_translation(qt)
 surface=[global_point[i]-[rx,ry][i]+[gx,gy][i] for i in (0,1)]
 window=[surface[i]+mapped[i] for i in (0,1)]
 ww=integer(qt.get('windowWidth'),1,2**23);wh=integer(qt.get('windowHeight'),1,2**23)
 if not 0<=window[0]<ww or not 0<=window[1]<wh:raise Refused('input outside actual QWindow')
 position=point([qt.get('windowPositionX'),qt.get('windowPositionY')])
 return {'surface':surface,'window':window,'toolkitGlobal':[position[i]+window[i] for i in (0,1)],'surfaceToWindow':mapped,'identity':actual}
