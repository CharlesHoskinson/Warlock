"""Buffer submission/presentation cadence; does not decode client pixel meaning."""
import statistics

def distribution(values):
    if not values:return {'count':0,'median':None,'p95':None,'maximum':None,'over33ms':0,'over100ms':0}
    ordered=sorted(values)
    return {'count':len(values),'median':statistics.median(values),
            'p95':ordered[min(len(ordered)-1,int(len(ordered)*.95))],
            'maximum':max(values),'over33ms':sum(v>33.4 for v in values),
            'over100ms':sum(v>100 for v in values)}

def analyze(raw):
    marks=dict(raw.get('marks',[]));begin=marks.get('begin',500);end=marks.get('end',20000)
    content=[c for c in raw['contentCommits'] if begin<=c[0]<=end]
    observed=[];seen=set();ages=[];hardware=True
    for p in raw['presentations']:
        if not p[6] or p[7]<0:continue
        frame=raw['frames'][p[7]]
        if not begin<=frame[0]<=end or not frame[15] or not frame[13]:continue
        hardware=hardware and (p[3]&7)==7
        if frame[13] not in seen:
            seen.add(frame[13]);observed.append(p[1])
            ages.append(p[1]-(raw['originMonotonicMs']+frame[14]))
    return {'bufferCommits':len(content),'distinctObservedEpochs':len(seen),
            'surfaceIDs':sorted({c[1] for c in content}),
            'clientBufferGapsMs':distribution([b[0]-a[0] for a,b in zip(content,content[1:])]),
            'observedContentGapsMs':distribution([b-a for a,b in zip(observed,observed[1:])]),
            'latestBufferAgeAtPresentationMs':distribution(ages),
            'allHardwareClockCompletion':hardware,'negativeAges':sum(a<-.2 for a in ages),
            'scope':'Latest observed surface-buffer epoch at output submission; visible disposable window; not per-pixel proof'}
