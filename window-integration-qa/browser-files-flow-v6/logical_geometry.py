"""Exact single untransformed output extents; no desktop or input access."""
from decimal import Decimal

def logical_output(monitors):
 assert len(monitors)==1,'Fixture supports one output only'
 monitor=monitors[0];assert monitor['x']==monitor['y']==0 and monitor['transform']==0,'Fixture requires untransformed output at origin'
 scale=Decimal(str(monitor['scale']));assert scale.is_finite() and scale>0,'Positive finite output scale required'
 sizes=[]
 for field in ('width','height'):
  extent=Decimal(str(monitor[field]))/scale
  assert extent.is_finite() and extent==extent.to_integral_value() and extent>0,'Exact integer logical output extent required'
  sizes.append(int(extent))
 assert sizes[0]>=1500 and sizes[1]>=900,'Fixture rectangles require logical output at least1500x900'
 return {'monitor':{field:monitor.get(field) for field in ('name','x','y','width','height','scale','transform')},'logicalWidth':sizes[0],'logicalHeight':sizes[1],'derivation':'exact decimal physical-size / scale','preButtonCursorToleranceLogicalPx':0.5}
