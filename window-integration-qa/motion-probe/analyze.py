"""Pure analysis of the native observer's raw captures."""
import statistics

def difference(a,b): return max(abs(x-y) for x,y in zip(a,b))
def percentile(values,q):
    values=sorted(values)
    return values[min(len(values)-1,int((len(values)-1)*q))] if values else None
def analyze(raw):
    pairs=[(p,raw['frames'][p[7]]) for p in raw['presentations']
           if p[6] and p[7]>=0 and p[1]>=0]
    errors=[difference(f[1:5],f[5:9]) for p,f in pairs]
    active={i for i,error in enumerate(errors) if error>1}
    changed={i for i in range(1,len(pairs))
             if difference(pairs[i][1][1:5],pairs[i-1][1][1:5])>.05}
    indices=sorted(active|changed)
    span=pairs[max(0,min(indices)-1):max(indices)+1] if indices else []
    # Include every presentation across the movement, including repeats.
    gaps=[b[0][1]-a[0][1] for a,b in zip(span,span[1:])]
    refresh=statistics.median([p[4]/1e6 for p,f in pairs if p[4]>0]) if pairs else None
    # For animated movement, assess geometry update cadence while its error is
    # still >1 logical pixel. A spring's subpixel tail ending exactly at goal
    # is deliberately excluded, and reported through finalGoalError instead.
    updates=sorted(changed & active if active else changed)
    # Separate transitions may contain intentional settled pauses. Preserve
    # unchanged frames while away from the target (a real stall), but reset
    # cadence after a presentation reaches the target within one pixel.
    update_gaps=[]
    previous_update=None
    update_set=set(updates)
    for i in range(len(pairs)):
        if active and i not in active:
            previous_update=None
        if i in update_set:
            if previous_update is not None:
                update_gaps.append(pairs[i][0][1]-pairs[previous_update][0][1])
            previous_update=i
    # Drag can briefly animate during its first motion. Use the entire pointer
    # motion span for direct-drag analysis, not only that initial spring frame.
    if len(raw['inputs'])>2:
        start,end=raw['inputs'][1][0],raw['inputs'][-1][0]
        updates=sorted(i for i in changed if start<=pairs[i][1][0]<=end+25)
        update_gaps=[pairs[b][0][1]-pairs[a][0][1] for a,b in zip(updates,updates[1:])]
    result={
        'submissions':len(raw['frames']),'presentations':len(raw['presentations']),
        'paired':len(pairs),'unmatched':raw['unmatched'],'ambiguous':raw['ambiguous'],
        'refreshMs':refresh,'movingIntervals':len(gaps),
        'medianGapMs':statistics.median(gaps) if gaps else None,
        'p95GapMs':percentile(gaps,.95),'maxGapMs':max(gaps) if gaps else None,
        'gapsOverTwoRefreshes':sum(g>refresh*2+.5 for g in gaps) if refresh else None,
        'gapsOver33ms':sum(g>33.4 for g in gaps),
        'geometryUpdates':len(updates),
        'medianGeometryGapMs':statistics.median(update_gaps) if update_gaps else None,
        'p95GeometryGapMs':percentile(update_gaps,.95),
        'maxGeometryGapMs':max(update_gaps) if update_gaps else None,
        'geometryGapsOver33ms':sum(g>33.4 for g in update_gaps),
        'intermediateFrames':sum(e>1 for e in errors),'inputEvents':len(raw['inputs']),
        'finalGoalError':errors[-1] if errors else None,
    }
    if indices: result['movingSpanMs']=span[-1][0][1]-span[0][0][1]
    goals={tuple(pairs[i][1][5:9]) for i in active}
    result['goalChanges']=max(0,len(goals)-1)
    if active and len(raw['inputs'])<3 and len(goals)==1:
        first=next((f for p,f in pairs),None)
        goal=pairs[-1][1][5:9]
        overshoot=0
        for p,f in pairs:
            for initial,current,target in zip(first[1:5],f[1:5],goal):
                if target>initial: overshoot=max(overshoot,current-target)
                elif target<initial: overshoot=max(overshoot,target-current)
        result['maxOvershootPixels']=overshoot
    return result
