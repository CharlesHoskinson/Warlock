"""Explicit private-session read-only fixture gate. No connection on import."""
def require_invisible_private_cursor(session):
    observed=session.data('getoption','cursor:invisible')
    if observed.get('bool') is not True or observed.get('set') is not True:
        raise AssertionError('private cursor:invisible not actually enabled: '+repr(observed))
    return observed

def require_deterministic_owned_raster(rows):
    state=next((r for r in rows if r.get('event')=='rasterState'),None)
    if state is None or state.get('ditherAfter') is not False or state.get('error')!=0:
        raise AssertionError('actual owned GL dithering state unproved: '+repr(state))
    return state
