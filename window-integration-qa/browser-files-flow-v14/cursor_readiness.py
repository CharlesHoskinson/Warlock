"""Unrounded native cursor arrival; integer IPC is diagnostic only."""
import math
TOLERANCE_LOGICAL_PX=0.5

def native_delta(snapshot,requested):
 position=snapshot['cursor']
 if len(position)!=2 or len(requested)!=2:raise AssertionError('Two actual native/requested coordinates required')
 if not all(isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) for value in (*position,*requested)):raise AssertionError('Finite native/requested coordinates required')
 return [position[axis]-requested[axis] for axis in (0,1)]

def native_arrived(snapshot,requested):
 return all(abs(delta)<=TOLERANCE_LOGICAL_PX for delta in native_delta(snapshot,requested))
