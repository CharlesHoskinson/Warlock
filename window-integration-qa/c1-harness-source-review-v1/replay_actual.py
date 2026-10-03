"""Read-only independent causal/numeric replay of root's actual C1 campaign."""
from pathlib import Path
import copy
import hashlib
import json
import math
import os
import stat
import sys
sys.dont_write_bytecode=True
QA=Path('/home/hoskinson/window-integration-qa')
STAGE=QA/'family-continuous-c1-v4'
ACTUAL=STAGE/'attempt-1'
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(STAGE))
from verify_reversal import verify as original_reversal
from verify_c1 import verify as c1_verify
import c1_pairing
sys.path.insert(0,str(c1_pairing.PRODUCER))
from verify_production_pipeline import verify_selection

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def exact_file(path,expected=None,size=None):
    path=Path(path)
    if not path.is_relative_to(ACTUAL):raise ValueError('Retained source outside exact actual attempt')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        before=os.fstat(fd)
        assert stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and not before.st_mode&0o077 and before.st_size<=268435456
        with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(268435457)
        after=os.fstat(fd);named=path.lstat()
        projection=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        assert projection(before)==projection(after)==projection(named)
        assert len(raw)==before.st_size and (size is None or len(raw)==size)
        digest=hashlib.sha256(raw).hexdigest();assert expected is None or digest==expected
        return raw,digest
    finally:os.close(fd)

def frozen():
    packet=json.loads((STAGE/'frozen-inputs.json').read_text())
    assert sha(STAGE/'frozen-inputs.json')=='585f38c248a43775da64dc3136ec831c65a1df31e08b57c5b9827d1373dc8134'
    for name,value in packet['inputs'].items():assert sha(name)==value and stat.S_IMODE(Path(name).stat().st_mode)==packet['inputModes'][name]
    for name,value in packet['symlinks'].items():assert Path(name).is_symlink() and os.readlink(name)==value
    c1_pairing.verified_packet()
    return packet

def polynomial(a,v,b,d,e):
    if e==0:return a,v
    if e>=d:return b,[0.0]*4
    t=e/d
    return ([x+d*s*t+(3*(y-x)-2*d*s)*t*t+(2*(x-y)+d*s)*t*t*t for x,s,y in zip(a,v,b)],
            [s+(6*(y-x)/d-4*s)*t+(6*(x-y)/d+3*s)*t*t for x,s,y in zip(a,v,b)])

def main():
    packet=frozen()
    artifact_names=['report.json','service-evidence.json','c1-continuous-audit.json']+[f'service-retirement-{i}.json' for i in range(1,5)]
    hashes_before={name:sha(ACTUAL/name) for name in artifact_names}
    report=json.loads((ACTUAL/'report.json').read_text());evidence=json.loads((ACTUAL/'service-evidence.json').read_text())
    assert report['result']=='pass' and len(report['checks'])==39 and all(r['passed'] for r in report['checks'])
    old_report=json.loads((QA/'family-continuous-reversal-v3/attempt-1/report.json').read_text())
    assert [r['name'] for r in report['checks'] if not r['name'].startswith('C1 actual')]==[r['name'] for r in old_report['checks']]
    names=('owner','child','nested');windows=[report['originalWindows'][n] for n in names]
    identities=[dict(stableId=str(w['stableId']),pid=w['pid']) for w in windows]
    triples=[(w['address'],str(w['stableId']),w['pid']) for w in windows]
    assert evidence['observerBindingActors']==[1,2,3,4] and len(evidence['transports'])==4
    assert not evidence['nativeTargetOverrides'] and not evidence['failure'] and not evidence['serviceFailure']
    selections=[verify_selection(t['events'],'production-default') for t in evidence['transports']]
    captures=[]
    for row in evidence['retainedEpochSources']:
        assert row['captureCallbackDelegatedOnce'] and row['sourceResultUnchanged'] and row['sha256']==row['source']['digest']
        _,digest=exact_file(row['retainedPath'],row['sha256'],row['bytes'])
        captures.append(dict(actor=row['actor'],path=row['retainedPath'],sha256=digest))
    assert len(captures)==12
    assert len(evidence['records'])==4
    commits=[];analytic_checks=0;accepted_frames=0;pair_maps={};pair_checks=[]
    for actor_index,actor in enumerate(evidence['records']):
        number=actor_index+1;assert actor['actor']==number and len(actor['history'])==1
        record=actor['history'][0];events=evidence['transports'][actor_index]['events']
        assert record['validated'] and record['ready'] and not record['profile'].get('failure') and not record['profile'].get('settlementFailure') and record['profile']['settlementReason']=='native handover complete'
        assert [(m['address'],str(m['stableId']),m['pid']) for m in record['members']]==triples
        sources=record['sources'];ordered=[{k:s[k] for k in ('stableId','pid','digest')} for s in sources]
        assert [{k:s[k] for k in ('stableId','pid')} for s in sources]==identities
        actor_captures=[c for c in evidence['retainedEpochSources'] if c['actor']==number]
        assert len(actor_captures)==3 and all(any(c['source']==s for c in actor_captures) for s in sources)
        uploaded=[e for e in events if e.get('event')=='uploaded'];seeded=[e for e in events if e.get('event')=='seeded']
        assert len(uploaded)==3 and len(seeded)==1 and seeded[0]['sourceDigests']==ordered and seeded[0]['identities']==identities
        assert sorted(e['digest'] for e in uploaded)==sorted(s['digest'] for s in sources)
        assert all(any(u['digest']==s['digest'] and u['pixels']==s['pixels'] for u in uploaded) for s in sources)
        operation=record['operation'];reason='presented ready' if operation=='minimize' else 'presented endpoint'
        authority=[e for e in events if e.get('event')==('ready' if operation=='minimize' else 'endpoint') and e.get('token')==record['token']]
        assert len(authority)==1 and authority[0]['servicePromoted'] and authority[0]['identities']==identities and authority[0]['sourceDigests']==ordered
        assert len(record['results'])==3 and [tuple(r['identity']) for r in record['results']]==triples
        bound=[]
        for i,p in enumerate(events):
            if p.get('event')!='presented' or p.get('accepted') is not True:continue
            matching=[s for s in events if s.get('event')=='swap' and s.get('success') is True and all(s.get(k)==p.get(k) for k in ('token','sequence','output','generation','members','rectangle','progress'))]
            assert len(matching)==1
            if p['token']==record['token'] and (operation=='minimize' or p['endpoint']):bound.append((p,matching[0]))
        assert bound
        for result in record['results']:
            assert result['operation']==operation and result['reason']==reason
            assert any(int(p['timestampNs'])<=result['committedNs'] and int(p['feedbackDeliveredNs'])<=result['committedNs'] and int(s['swapReturnedNs'])<=result['committedNs'] for p,s in bound)
        commits.append(dict(actor=number,token=record['token'],operation=operation,exactThreeNativeResults=record['results'],matchingActualPresentedFrames=len(bound),sourceUploadCount=3))
        # Independent Hermite polynomial/derivative evaluation on every actor,
        # including restore-only actors whose initial state is the icon endpoint.
        token_operations={seeded[0]['token']:'minimize' if number in (1,3) else 'restore'}
        origin_pairs={seeded[0]['token']:None};latest={};plans={}
        for i,row in enumerate(events):
            if row.get('event')=='retargeted':
                current=row['token'];token_operations[current]='restore' if len(token_operations)%2 else 'minimize'
                selected={}
                for j,o in enumerate(sorted(row['origins'],key=lambda r:r['output'])):
                    k=events[i+1+j];key=(o['output'],o['generation'])
                    assert k['phase']=='retargetOrigin'
                    immutable={f:k[f] for f in ('token','sequence','output','generation','epoch','sampleNs','startNs','elapsedSeconds','durationSeconds','progress','endpoint','members')}
                    assert immutable==latest[key];selected[key]=immutable
                origin_pairs[current]=selected
            if row.get('event')!='presented' or row.get('accepted') is not True:continue
            k=events[i+1];assert k['event']=='frameKinematics' and k['phase']=='presented' and k['accepted'] is True and k['nativeAuthority'] is False
            token=k['token'];d=k['durationSeconds'];elapsed=k['elapsedSeconds'];start=int(k['startNs']);ns=int(k['sampleNs'])
            assert elapsed==((ns-start)/1e9 if start else 0) and 0<d<=.22
            immutable={f:k[f] for f in ('token','sequence','output','generation','epoch','sampleNs','startNs','elapsedSeconds','durationSeconds','progress','endpoint','members')}
            swapkin=[e for e in events if e.get('event')=='frameKinematics' and e.get('phase')=='swap' and e.get('accepted') is True and all(e.get(f)==k.get(f) for f in ('token','sequence','output','generation'))]
            assert len(swapkin)==1 and {f:swapkin[0][f] for f in immutable}==immutable
            selected=origin_pairs[token]
            for member_index,(member,source) in enumerate(zip(k['members'],sources)):
                axes=('x','y','width','height');target_key='iconRect' if token_operations[token]=='minimize' else 'atlasRect'
                target=[source[target_key][a] for a in axes]
                if selected is None:
                    initial_key='atlasRect' if token_operations[token]=='minimize' else 'iconRect'
                    a=[source[initial_key][axis] for axis in axes];v=[0.0]*4
                else:
                    old=selected[(k['output'],k['generation'])]['members'][member_index];a=[old['rectangle'][axis] for axis in axes];v=old['velocity']
                expected_position,expected_velocity=polynomial(a,v,target,d,elapsed)
                for actual,expected in zip([member['rectangle'][axis] for axis in axes],expected_position):assert math.isfinite(actual) and abs(actual-expected)<=128*math.ulp(400000.0)+1e-9;analytic_checks+=1
                for actual,expected in zip(member['velocity'],expected_velocity):assert math.isfinite(actual) and abs(actual-expected)<=128*math.ulp(1e9)+1e-9;analytic_checks+=1
            latest[(k['output'],k['generation'])]=immutable;accepted_frames+=1
        actor_pairs=[p for p in evidence['cachePairsAtCapture'] if p['actor']==number]
        assert len(actor_pairs)==3 and [tuple(p['identity']) for p in actor_pairs]==triples
        published={}
        for pair in actor_pairs:
            assert len(pair['files'])==2
            pointer_file=next(f for f in pair['files'] if f['source'].endswith('.json'))
            png_file=next(f for f in pair['files'] if f['source'].endswith('.png'))
            pointer=json.loads(exact_file(pointer_file['retainedPath'],pointer_file['sha256'],pointer_file['bytes'])[0])
            _,pngsha=exact_file(png_file['retainedPath'],png_file['sha256'],png_file['bytes'])
            assert pointer['identity']==pair['identity'] and pointer['stableId']==pair['identity'][1] and pointer['pid']==pair['identity'][2]
            assert pointer['cacheDigest']==pair['cacheDigest']==pngsha and pointer['cacheFile']==Path(png_file['source']).name
            assert pointer['ok'] and pointer['whole'] and pointer['canonical']
            for f in pair['files']:published[f['source']]=f['sha256']
            pair_checks.append(dict(actor=number,identity=pair['identity'],pointerSHA256=pointer_file['sha256'],pngSHA256=pngsha,completeExactPublishedPair=True))
        pair_maps[number]=published
    assert pair_maps[1]==pair_maps[2] and pair_maps[3]==pair_maps[4]
    actual_events=evidence['transports'][2]['events'];strict=original_reversal(actual_events,identities)
    c1=c1_verify(actual_events,identities,evidence['records'][2]['history'][0]['sources'])
    assert c1==json.loads((ACTUAL/'c1-continuous-audit.json').read_text())
    assert c1['analyticT0Pairs']==2 and all(p['exactOriginPositionAndVelocity'] for p in c1['exactDisplayedOriginPairs'])
    requests=report['continuousRequests'];assert len(requests)==4 and len({r['answer']['actor'] for r in requests[:3]})==1 and requests[3]['answer']['actor']!=requests[2]['answer']['actor']
    assert all(r['answer']['ok'] and r['answer']['accepted'] and not r['answer']['completed'] and r['journalAfterACK']['serial']>=r['answer']['receipt'] for r in requests+report['requests'])
    hashes_after={name:sha(ACTUAL/name) for name in artifact_names};assert hashes_before==hashes_after
    frozen()
    result=dict(result='accepted-private-C1-family-causal-numeric-replay',artifactSHA256=hashes_before,all39Gates=True,allOriginal38NamesAndGatesPreserved=True,ordinaryDefaultSelections=selections,originalStrictReversal=strict,C1Replay=c1,independentHermiteComponentChecks=analytic_checks,allFourActorsAcceptedFrames=accepted_frames,exactCurrentNativeCommits=commits,retainedSourceChecks=captures,immutablePairChecks=pair_checks,baselineRestorePairsExact=True,continuousRestorePairsExact=True,actualRequestLatenciesMs=[(r['afterNs']-r['beforeNs'])/1e6 for r in requests],frozenInputs=len(packet['inputs']),frozenLinks=len(packet['symlinks']),allEvidenceUnchanged=True,mainPreservationGeneralAuditOwner='root',genuineWidgetPreviewAccepted=False,physicalCadenceAccepted=False,velocityContinuityAccepted=True,fullWindowsParityAccepted=False,productionDeployed=False,nativeExecutedByReviewer=False,mainWrites=False)
    with (OUT/'actual-c1-independent-replay.json').open('x') as output:json.dump(result,output,indent=2);output.write('\n')
    print(json.dumps(dict(result=result['result'],sha256=sha(OUT/'actual-c1-independent-replay.json'),acceptedFrames=accepted_frames,componentChecks=analytic_checks,exactOrigins=c1['analyticT0Pairs'],captures=len(captures),pairChecks=len(pair_checks))))
if __name__=='__main__':main()
