"""Read-only causal evidence, independent of desktop and renderer execution."""
import hashlib
import os
from pathlib import Path
import stat

def digest(path):
    path=Path(path);fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or before.st_mode&0o077 or before.st_size>268435456:
            raise ValueError('Unsafe retained cache/source file')
        with os.fdopen(fd,'rb',closefd=False) as stream:data=stream.read(268435457)
        after=os.fstat(fd);named=path.lstat()
        fields=lambda row:(row.st_dev,row.st_ino,row.st_size,row.st_mtime_ns,row.st_ctime_ns)
        if fields(before)!=fields(after) or fields(before)!=fields(named) or not stat.S_ISREG(named.st_mode) or len(data)!=before.st_size:
            raise ValueError('Retained cache/source file changed')
        return hashlib.sha256(data).hexdigest()
    finally:os.close(fd)

def captured_and_seeded(packet,operation,members):
    expected={(str(m['stableId']),m['pid']) for m in members}
    rows=packet['retainedEpochSources'];events=packet['rendererEvents']
    if len(rows)!=3 or {(str(r['source']['stableId']),r['source']['pid']) for r in rows}!=expected:
        raise ValueError('Three actual family captures required before cache acceptance')
    for row in rows:
        if (not row['captureCallbackDelegatedOnce'] or not row['sourceResultUnchanged']
                or row['sha256']!=row['source']['digest'] or digest(row['retainedPath'])!=row['sha256']):
            raise ValueError('Returned capture source evidence changed')
    matches=[]
    for record in packet['history']:
        if record['operation']!=operation:continue
        sources=record['sources'];token=record['token']
        if len(sources)!=3 or not all(any(row['source']==source for row in rows) for source in sources):continue
        digests=[{k:s[k] for k in ('stableId','pid','digest')} for s in sources]
        seeds=[e for e in events if e.get('event')=='seeded' and e.get('token')==token and e.get('sourceDigests')==digests]
        uploads=all(any(e.get('event')=='uploaded' and e.get('digest')==s['digest'] and e.get('pixels')==s['pixels'] for e in events) for s in sources)
        if seeds and uploads:matches.append(dict(token=token,seededEvents=seeds,matchedUploads=True))
    if not matches:raise ValueError('Actual family renderer seed and uploads required')
    return dict(actor=packet['retirement']['actor'],captures=rows,matches=matches)

def unchanged_pairs(packet,members,prior=None):
    expected={(m['address'],str(m['stableId']),m['pid']) for m in members}
    pairs=packet['cachePairsAtCapture']
    if len(pairs)!=3 or {tuple(p['identity']) for p in pairs}!=expected:
        raise ValueError('Three capture-time family cache pairs required')
    observed={}
    for pair in pairs:
        files=pair['files']
        if len(files)!=2 or {Path(r['source']).suffix for r in files}!={'.json','.png'}:
            raise ValueError('Complete immutable PNG/pointer pair required')
        for row in files:
            if digest(row['retainedPath'])!=row['sha256'] or digest(row['source'])!=row['sha256']:
                raise ValueError('Published cache bytes changed after actor disposal')
            if row['source'] in observed:raise ValueError('Duplicate cache publication path')
            observed[row['source']]=row['sha256']
    if prior is not None and observed!=prior:raise ValueError('Restore did not reuse exact published cache pairs')
    return observed
