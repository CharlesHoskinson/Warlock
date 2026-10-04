"""Bounded RGB screenshot oracle; caller owns capture/lifetime/deadline binding."""
import math
class Refused(ValueError):pass

def integer(value,minimum,maximum):
    if type(value) is not int or not minimum<=value<=maximum:raise Refused('integer domain')
    return value

def center_rgb(serial):
    integer(serial,0,2**32-1)
    return (0x28^(serial&63),0x71^((serial>>6)&63),0xc8^((serial>>12)&63))

def inspect(rgb,width,height,monitor_origin,monitor_scale,real,geometry,serial,*,observed_serials,diagnostic_nonzero=False):
    integer(width,1,8192);integer(height,1,8192);integer(monitor_scale,1,2)
    if type(diagnostic_nonzero) is not bool:raise Refused('diagnostic option domain')
    if type(rgb) is not bytes or len(rgb)!=width*height*3 or len(rgb)>128*1024*1024:raise Refused('RGB extent')
    if len(real)!=4 or len(geometry)!=4 or len(monitor_origin)!=2:raise Refused('coordinate shape')
    if any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>2**31-1 for v in [*real,*monitor_origin]):raise Refused('coordinate domain')
    integer(serial,0,2**32-1)
    if type(observed_serials) not in (list,tuple) or not 1<=len(observed_serials)<=8192:raise Refused('serial observation history')
    if serial not in observed_serials:raise Refused('serial observation history')
    selected=center_rgb(serial)
    for previous in observed_serials:
        if previous!=serial and center_rgb(previous)==selected:raise Refused('serial color alias')
    x,y,w,h=geometry
    for v in (x,y):integer(v,0,256)
    for v in (w,h):integer(v,32,4096)
    if real[2:]!=[w,h] and tuple(real[2:])!=(w,h):raise Refused('native/committed extent mismatch')
    if (x or y) and not diagnostic_nonzero:raise Refused('nonzero rendering remains unqualified')
    local=[(x+4,y+4),(x+w-4,y+4),(x+4,y+h-4),(x+w-4,y+h-4),(x+w//2,y+h//2)]
    colors=[(255,48,48),(48,255,48),(48,48,255),(255,255,48),center_rgb(serial)]
    records=[]
    for (lx,ly),expected in zip(local,colors):
        # Proposed surface transform puts committed geometry origin at real origin.
        sx=(real[0]+lx-x-monitor_origin[0])*monitor_scale
        sy=(real[1]+ly-y-monitor_origin[1])*monitor_scale
        px,py=math.floor(sx),math.floor(sy)
        if px<1 or py<1 or px+1>=width or py+1>=height:raise Refused('clipped landmark')
        measured=[]
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                off=((py+dy)*width+px+dx)*3;measured.append(tuple(rgb[off:off+3]))
        if any(c!=expected for c in measured):raise Refused('presented landmark mismatch')
        records.append({'surfaceLocal':[lx,ly],'screenshotPixel':[px,py],'rgb':expected})
    return {'samples':records,'serial':serial,'diagnosticNonzero':bool(x or y),'nonzeroCapabilityAccepted':False}
