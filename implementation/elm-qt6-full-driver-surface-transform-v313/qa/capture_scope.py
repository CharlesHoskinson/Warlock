"""Whole selected Qt SHM surface extent; never substitute QWindow client size."""
import re
from journal import Refused,integer
from protocol import Trace

def surface_extent(raw,binding):
 trace=Trace(raw);wire=binding['wire'];bid=integer(wire['bufferId'],1,2**32-1);sid=integer(binding['identity']['surfaceId'],1,2**32-1);commit=integer(wire['lastCommitIndex'],0,2**63-1)
 buffers=[];scale=1
 for row in trace.calls:
  if row['index']>=commit:break
  if row['direction']!='request':continue
  if row['iface']=='wl_surface' and row['id']==sid and row['method']=='set_buffer_scale':
   if not re.fullmatch('[1-9][0-9]*',row['args']):raise Refused('canonical surface buffer scale')
   scale=integer(int(row['args']),1,2)
  if row['iface']=='wl_shm_pool' and row['method']=='create_buffer':
   m=re.fullmatch(r'new id wl_buffer[@#]([1-9][0-9]*), ([0-9]+), ([1-9][0-9]*), ([1-9][0-9]*), ([1-9][0-9]*), ([0-9]+)',row['args'])
   if m and int(m[1])==bid:buffers.append((row['index'],[int(m[i]) for i in range(2,7)]))
  if row['iface']=='wl_buffer' and row['id']==bid and row['method']=='destroy':buffers=[]
 if len(buffers)!=1:raise Refused('one current selected actual SHM buffer allocation')
 offset,width,height,stride,fmt=buffers[0][1]
 if not 0<width<=4096 or not 0<height<=4096 or not width*4<=stride<=65536 or stride*height>64*1024*1024 or fmt not in (0,1):raise Refused('qualified raster buffer bounds/format')
 if width%scale or height%scale:raise Refused('integer logical full surface extent')
 return {'logical':[width//scale,height//scale],'physical':[width,height],'scale':scale,'allocationIndex':buffers[0][0],'commitIndex':commit,'bufferId':bid,'source':'actual selected SHM buffer wire'}

def attribution(raw,selected,other):
 p=selected['marker']['global'];x,y=p;rx,ry=selected['native']['at'];rw,rh=selected['native']['size']
 if not(rx<=x-1 and ry<=y-1 and x+2<=rx+rw and y+2<=ry+rh):raise Refused('selected complete3x3 inside current real rect')
 extent=surface_extent(raw,other);ox,oy=other['native']['at'];gx,gy=other['wire']['windowGeometry'][:2];sw,sh=extent['logical'];rect=[ox-gx,oy-gy,sw,sh]
 if not(x+2<=rect[0] or rect[0]+sw<=x-1 or y+2<=rect[1] or rect[1]+sh<=y-1):raise Refused('whole other Qt surface/CSD intersects sampled marker')
 return {'selectedSampleRect':[x-1,y-1,3,3],'excludedOtherSurfaceRect':rect,'actualExtent':extent}
