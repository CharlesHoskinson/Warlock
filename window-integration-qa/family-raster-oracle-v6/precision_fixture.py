"""Read-only gate over actual producer diagnostic rows; never establishes pixels."""
def require_explicit_high_precision(rows):
    event=next((r for r in rows if r.get('event')=='shaderPrecision'),None)
    if not event or event.get('supported') is not True or event.get('error')!=0:
        raise AssertionError('actual high shader precision is unproved: '+repr(event))
    records=event.get('observed',[])
    if len(records)!=6 or {(r['stage'],r['kind']) for r in records}!={(s,k) for s in ('vertex','fragment') for k in ('low','medium','high')}:
        raise AssertionError('complete actual shader precision vector missing')
    if any(r['precisionBits']<23 or r['rangeMin']<127 or r['rangeMax']<127 for r in records if r['kind']=='high'):
        raise AssertionError('required actual float precision/range missing')
    return event
