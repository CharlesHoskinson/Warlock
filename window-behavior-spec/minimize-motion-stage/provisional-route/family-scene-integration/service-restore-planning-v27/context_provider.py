"""Read-only native desktop fingerprint; output presentation authority is separate.

The supplied desktop must use the explicit compositor session selected by the
service launcher. No native calls occur on import. This does not identify output
object lifetimes: the producer's exact Wayland generation ledger does that.
"""
import math
from scene_controller import key

def monitor_fingerprint(monitors):
    names=set();result=[]
    for m in monitors:
        name=m['name']
        if not isinstance(name,str) or not name or name in names:raise ValueError('duplicate/invalid native output name')
        names.add(name)
        values=[m[n] for n in ('id','x','y','width','height','scale','transform')]
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in values):raise ValueError('nonfinite native output metadata')
        if m['width']<=0 or m['height']<=0 or m['scale']<=0 or m['transform'] not in range(8):raise ValueError('invalid native output extent/transform')
        workspace=m['activeWorkspace']
        if not isinstance(workspace.get('id'),int) or not isinstance(workspace.get('name'),str):raise ValueError('invalid active workspace')
        result.append((name,*values,workspace['id'],workspace['name']))
    if not result:raise ValueError('native outputs missing')
    return tuple(sorted(result))

class NativeContextProvider:
    def __init__(self,desktop,*,session):
        if not isinstance(session,str) or not session:raise ValueError('explicit compositor session required')
        self.desktop=desktop;self.session=session
    def __call__(self,request):
        captured=(request['address'],str(request['stableId']),request['pid'])
        def observe_window():
            matches=[w for w in self.desktop.clients() if key(w)==captured and w.get('mapped',True)]
            if len(matches)!=1:raise ValueError('captured context identity missing/reused')
            w=matches[0]
            return (w.get('monitor'),w.get('workspace',{}).get('id'),w.get('workspace',{}).get('name'))
        window_before=observe_window()
        before=monitor_fingerprint(self.desktop.monitors())
        after=monitor_fingerprint(self.desktop.monitors())
        window_after=observe_window()
        if before!=after or window_before!=window_after:raise ValueError('native context changed during observation')
        # Global current desktops must match before provisional expansion. Home
        # destination/complete family identity/geometry are still checked by the
        # controller before promotion. Monitor IDs alone are not generations.
        return (self.session,before)
