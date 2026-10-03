"""Causal immutable frame/analytic derivative audit; no execution authority."""
import math
import re
from verify_reversal import verify as verify_original

FIELDS = ('token', 'sequence', 'output', 'generation', 'epoch', 'sampleNs',
          'startNs', 'elapsedSeconds', 'durationSeconds', 'progress', 'endpoint', 'members')
AXES = ('x', 'y', 'width', 'height')

def natural(value, zero=False):
    if not isinstance(value, str) or not re.fullmatch(r'0|[1-9][0-9]*', value):
        raise ValueError('Canonical exact integer string required')
    number = int(value)
    if number < (0 if zero else 1) or number > 2**64 - 1:
        raise ValueError('Bounded integer required')
    return number

def finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Finite numeric sample required')
    return float(value)

def vector(rect):
    if not isinstance(rect, dict) or set(rect) != set(AXES):
        raise ValueError('Complete rectangle required')
    values = [finite(rect[k]) for k in AXES]
    if any(abs(v) > 400000 for v in values) or min(values[2:]) <= 0:
        raise ValueError('Rectangle leaves admitted bounds')
    return values

def close(actual, expected, scale):
    # Independent Bernstein evaluation vs de Casteljau: 128 rounding ULPs of
    # bounded control magnitudes plus1e-9. Never used for origin pair identity.
    return abs(actual - expected) <= 128 * math.ulp(max(1.0, abs(scale), abs(actual), abs(expected))) + 1e-9

def sample(a, v, b, duration, elapsed):
    control = [x + duration * speed / 3 for x, speed in zip(a, v)]
    tangent = [3 * (end - c) / duration for end, c in zip(b, control)]
    if any(abs(x) > 400000 or (i >= 2 and x <= 0) for i, x in enumerate(control)) or any(abs(x) > 1e9 for x in tangent):
        raise ValueError('Trajectory control leaves admitted bounds')
    if elapsed == 0:
        return a, v
    if elapsed >= duration:
        return b, [0.0] * 4
    t = elapsed / duration
    u = 1 - t
    position = [u**3*x + 3*u*u*t*c + (3*u*t*t+t**3)*end for x,c,end in zip(a,control,b)]
    velocity = [u*u*speed + 2*u*t*middle for speed,middle in zip(v,tangent)]
    return position, velocity

def payload(record):
    if record.get('nativeAuthority') is not False:
        raise ValueError('Kinematics gained effect authority')
    return {k: record[k] for k in FIELDS}

def verify(events, identities, captured_sources, required_reversals=2,
           nominal_seconds=.22, original=True):
    old = verify_original(events, identities, required_reversals) if original else {}
    if not isinstance(events, list) or not events or len(events) > 1024:
        raise ValueError('Complete bounded event stream required')
    if len(captured_sources) != len(identities) or [{k:s[k] for k in ('stableId','pid')} for s in captured_sources] != identities:
        raise ValueError('Exact captured source order required')
    sources = [{k:s[k] for k in ('stableId','pid','digest')} for s in captured_sources]
    for source in captured_sources:
        vector(source['atlasRect']); vector(source['iconRect'])
    swaps = {}
    for index, row in enumerate(events):
        if row.get('event') == 'swap' and row.get('success') is True:
            key = (row['token'],row['output'],row['generation'],row['sequence'])
            if key in swaps or index+1 >= len(events):
                raise ValueError('Duplicate or incomplete swap evidence')
            kin = events[index+1]
            if kin.get('event')!='frameKinematics' or kin.get('phase')!='swap' or kin.get('accepted') is not True:
                raise ValueError('Successful swap lacks adjacent immutable kinematics')
            swaps[key] = payload(kin)
    latest = {}; plans = {}; token_epoch = {}; operation = {}; origins = {}; proofs = []
    consumed_origins=set(); current_token=None
    counts = {}; cadence = {}; accepted_count = 0; t0_count = 0
    for index, row in enumerate(events):
        kind = row.get('event')
        if kind == 'seeded':
            if plans or operation:
                raise ValueError('Exactly one seed required')
            operation[row['token']] = 'minimize'
            origins[row['token']] = None
            current_token=row['token']
        elif kind == 'retargeted':
            if not latest:
                raise ValueError('Retarget requires accepted frame')
            token = row['token']
            if token in operation:
                raise ValueError('Duplicate retarget token')
            operation[token] = 'restore' if len(operation)%2 else 'minimize'
            current_token=token
            origin_rows = row['origins']
            if {(r['output'],r['generation']) for r in origin_rows} != set(latest):
                raise ValueError('Incomplete retarget output set')
            selected = {}
            for j, origin in enumerate(sorted(origin_rows,key=lambda r:r['output'])):
                kin = events[index+1+j] if index+1+j < len(events) else {}
                output = (origin['output'],origin['generation'])
                expected = latest[output]
                if kin.get('event')!='frameKinematics' or kin.get('phase')!='retargetOrigin' or kin.get('accepted') is not True or payload(kin)!=expected:
                    raise ValueError('Origin position/velocity differs from latest actual accepted frame')
                if natural(kin['sampleNs']) > natural(row['startNs']):
                    raise ValueError('Retarget clock precedes origin sample')
                selected[output] = expected
                consumed_origins.add(index+1+j)
                if not any(any(v != 0 for v in m['velocity']) for m in expected['members']):
                    raise ValueError('Reversal origin needs actual nonzero velocity')
                proofs.append(dict(newToken=token,actualPresentedToken=kin['token'],
                    output=origin['output'],generation=origin['generation'],
                    sequence=kin['sequence'],originKinematics=expected,
                    exactOriginPositionAndVelocity=True,analyticT0PairEqual=True,
                    t0ActuallyPresentedClaimed=False))
                t0_count += 1
            origins[token] = selected
            plans[token] = dict(start=natural(row['startNs']),duration=None,epoch=None)
        elif kind == 'presented' and row.get('accepted') is True:
            if index+1 >= len(events):
                raise ValueError('Presented frame lacks kinematics')
            kin = events[index+1]
            if kin.get('event')!='frameKinematics' or kin.get('phase')!='presented' or kin.get('accepted') is not True:
                raise ValueError('Accepted presentation lacks adjacent kinematics')
            record = payload(kin)
            key = (row['token'],row['output'],row['generation'],row['sequence'])
            if swaps.get(key) != record:
                raise ValueError('Presented immutable sample differs from successful swap')
            if any(kin[k] != row[k] for k in ('token','sequence','output','generation','progress','endpoint')):
                raise ValueError('Presentation kinematics identity differs')
            if [{k:m[k] for k in ('stableId','pid','digest','rectangle')} for m in kin['members']] != row['members']:
                raise ValueError('Drawn and presented ordered members differ')
            if [{k:m[k] for k in ('stableId','pid','digest')} for m in kin['members']] != sources:
                raise ValueError('Captured ordered sources differ')
            token = kin['token']; output = (kin['output'],kin['generation'])
            if token not in operation or token!=current_token:
                raise ValueError('Unknown or superseded trajectory token')
            epoch = natural(kin['epoch']); start = natural(kin['startNs'],zero=True)
            ns = natural(kin['sampleNs']); natural(kin['sequence'])
            elapsed = finite(kin['elapsedSeconds']); duration = finite(kin['durationSeconds'])
            if not 0 < duration <= nominal_seconds or elapsed < 0 or (start and (ns<start or ns-start>2**53-1)):
                raise ValueError('Unrepresentable duration/sample clock')
            expected_elapsed = (ns-start)/1e9 if start else 0
            if elapsed != expected_elapsed:
                raise ValueError('Elapsed seconds differs from exact shared clock')
            plan = plans.setdefault(token,dict(start=start,duration=duration,epoch=epoch))
            if plan['duration'] is None:
                plan['duration']=duration;plan['epoch']=epoch
            if plan['duration']!=duration or plan['epoch']!=epoch:
                raise ValueError('Common output duration/epoch changed')
            if plan['start']==0 and start:
                plan['start']=start
            elif plan['start']!=start:
                raise ValueError('One-shot/shared output clock changed')
            if token not in token_epoch:
                if epoch != len(token_epoch)+1:
                    raise ValueError('Trajectory epoch not monotonic')
                token_epoch[token]=epoch
            if finite(kin['progress']) != min(1,elapsed/duration) or kin['endpoint'] is not (elapsed>=duration):
                raise ValueError('Progress/endpoint does not match trajectory')
            for i, (member,source) in enumerate(zip(kin['members'],captured_sources)):
                position = vector(member['rectangle'])
                velocity = [finite(v) for v in member['velocity']]
                if len(velocity)!=4 or any(abs(v)>1e9 for v in velocity):
                    raise ValueError('Invalid analytic velocity')
                target = vector(source['iconRect'] if operation[token]=='minimize' else source['atlasRect'])
                if origins[token] is None:
                    a=vector(source['atlasRect']);v=[0.0]*4
                else:
                    origin=origins[token][output]['members'][i]
                    a=vector(origin['rectangle']);v=origin['velocity']
                expected_pos, expected_vel = sample(a,v,target,duration,elapsed)
                if any(not close(x,y,max(map(abs,a+target))) for x,y in zip(position,expected_pos)) or any(not close(x,y,1e9) for x,y in zip(velocity,expected_vel)):
                    raise ValueError('Actual sample differs from analytic origin-preserving trajectory')
            previous = latest.get(output)
            if previous and natural(kin['sequence']) <= natural(previous['sequence']):
                raise ValueError('Displayed sequence regressed')
            latest[output]=record;accepted_count += 1
            cadence.setdefault(kin['output'],[]).append(natural(row['timestampNs']))
            counts[token]=counts.get(token,0)+1
    for index,row in enumerate(events):
        if row.get('event')!='frameKinematics':continue
        phase=row.get('phase'); previous=events[index-1] if index else {}
        if phase=='retargetOrigin':
            if index not in consumed_origins:raise ValueError('Orphan or duplicate origin telemetry')
        elif phase in ('swap','presented','presentationObservedBeforeSwap'):
            if previous.get('event')!=phase or any(previous.get(k)!=row.get(k) for k in ('token','output','generation','sequence')):
                raise ValueError('Orphan or reordered frame telemetry')
            expected_accepted=previous.get('success') if phase=='swap' else previous.get('accepted')
            if row.get('accepted') is not expected_accepted:raise ValueError('Telemetry acceptance differs from actual event')
        else:raise ValueError('Unknown kinematics phase')
    if len(origins)-1!=required_reversals or any(counts.get(t,0)==0 for t in origins):
        raise ValueError('Required presented epochs missing')
    return dict(original=old,exactDisplayedOriginPairs=proofs,analyticT0Pairs=t0_count,
        acceptedAnalyticSamples=accepted_count,commonPlans=plans,
        cadence={name:dict(timestampNs=times,gapsNs=[b-a for a,b in zip(times,times[1:])]) for name,times in cadence.items()},
        exactOriginPositionVelocityAccepted=True,analyticVelocityAccepted=True,
        nativeAuthorityGranted=False,physicalCadenceAccepted=False)
