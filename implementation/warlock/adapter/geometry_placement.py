"""Strict syntax for the negotiated snap intent; no geometry or effect policy."""
import math
from endpoint import Refused, canonical, exact

REGIONS = {'left-half','right-half','top-left','top-right','bottom-left','bottom-right'}
FIELDS = ['region','geometry','monitor','outputOwnershipGeneration','workAreaRevision','workspaceGeneration']

def validate(placement):
 exact(placement,FIELDS)
 if type(placement['region']) is not str or placement['region'] not in REGIONS:raise Refused('Snap region')
 values=placement['geometry']
 if type(values) is not list or len(values)!=4 or any(type(n) not in [int,float] or not math.isfinite(n) or abs(n)>2147483647 for n in values) or values[2]<=0 or values[3]<=0:raise Refused('Snap geometry')
 canonical(placement['monitor'],True)
 for field in FIELDS[3:]:canonical(placement[field])
 return placement
