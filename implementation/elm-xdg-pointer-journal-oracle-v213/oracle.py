"""Strict selected pointer-pair decoder, independent of native injection."""
import math
class Refused(ValueError):pass

def integer(v,lo,hi):
    if type(v) is not int or not lo<=v<=hi:raise Refused('canonical integer')
    return v

def fixed(v):
    if type(v) not in (int,float) or abs(v)>2**23 or (type(v) is float and not math.isfinite(v)):raise Refused('finite coordinate')
    scaled=v*256
    if not math.isfinite(scaled) or scaled!=int(scaled):raise Refused('fixed coordinate lattice')
    return integer(int(scaled),-2**31,2**31-1)

def validate_pair(events,*,pid,after_sequence,button,expected_local):
    integer(pid,1,2**31-1);integer(after_sequence,0,2**64-1);integer(button,1,2**32-1)
    if type(events) not in (list,tuple) or len(events)!=2:raise Refused('exact press/release pair')
    if type(expected_local) not in (list,tuple) or len(expected_local)!=2:raise Refused('expected coordinate shape')
    expected=[fixed(v) for v in expected_local];previous=after_sequence;selected=[]
    for row,state in zip(events,(1,0)):
        if type(row) is not dict or row.get('event')!='pointer-button' or row.get('ownedSurface') is not True:raise Refused('owned pointer recipient')
        if integer(row.get('pid'),1,2**31-1)!=pid:raise Refused('foreign process')
        sequence=integer(row.get('sequence'),1,2**64-1)
        if sequence<=previous:raise Refused('stale/reordered sequence')
        previous=sequence
        if integer(row.get('button'),1,2**32-1)!=button or integer(row.get('buttonState'),0,1)!=state:raise Refused('button chronology')
        integer(row.get('pointerSerial'),0,2**32-1);integer(row.get('pointerTime'),0,2**32-1)
        local=row.get('local');encoded=row.get('localFixed')
        if type(local) is not list or len(local)!=2 or type(encoded) is not list or len(encoded)!=2:raise Refused('pointer coordinate shape')
        actual=[integer(v,-2**31,2**31-1) for v in encoded]
        if actual!=expected or [fixed(v) for v in local]!=actual:raise Refused('pointer coordinate mismatch')
        selected.append({'sequence':sequence,'localFixed':actual,'buttonState':state})
    return {'pid':pid,'button':button,'events':selected,'physicalHardwareAccepted':False}
