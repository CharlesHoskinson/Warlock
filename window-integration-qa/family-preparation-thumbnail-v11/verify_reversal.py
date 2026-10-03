"""Independent actual-event origin/texture verifier; contains no launch code."""
import math
import re


def token(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{12}-[1-9][0-9]{0,14}', value):
        raise ValueError('Invalid scene token')
    prefix, serial = value.split('-')
    return prefix, int(serial)


def verify(events, expected_identities, required_reversals=2):
    if not isinstance(events, list) or not events or len(events) > 1024:
        raise ValueError('Complete bounded actor event stream required')
    if len(expected_identities) != 3 or len({(str(r['stableId']), r['pid']) for r in expected_identities}) != 3:
        raise ValueError('Exact three distinct family identities required')
    swaps = {}
    for row in events:
        if row.get('event') == 'swap' and row.get('success') is True:
            key = (row['output'], row['generation'], row['sequence'])
            if key in swaps:
                raise ValueError('Duplicate successful swap identity')
            swaps[key] = row
    seeded = [r for r in events if r.get('event') == 'seeded']
    if len(seeded) != 1:
        raise ValueError('Retained reversal requires exactly one seed')
    seed = seeded[0]
    if seed['identities'] != expected_identities:
        raise ValueError('Seed family identity/order mismatch')
    sources = seed['sourceDigests']
    if [{k: r[k] for k in ('stableId', 'pid')} for r in sources] != expected_identities:
        raise ValueError('Source identity/order mismatch')
    if any(not re.fullmatch('[0-9a-f]{64}', r['digest']) for r in sources):
        raise ValueError('Invalid source digest')
    current = seed['token']
    token(current)
    latest = {}
    accepted = {}
    applied = set()
    retargets = []
    upload_count = sum(r.get('event') == 'uploaded' for r in events)
    if upload_count != 3:
        raise ValueError('Sources must upload exactly once per family member')
    if sorted(r['digest'] for r in events if r.get('event') == 'uploaded') != sorted(r['digest'] for r in sources):
        raise ValueError('Actual uploaded digests differ from immutable sources')
    for index, row in enumerate(events):
        kind = row.get('event')
        if kind in ('fatal', 'rejected'):
            raise ValueError('Actual renderer refused or failed')
        if kind == 'presented' and row.get('accepted') is True:
            if row['token'] != seed['token'] and row['token'] not in accepted:
                raise ValueError('Presentation has unknown receipt token')
            key = (row['output'], row['generation'], row['sequence'])
            swap = swaps.get(key)
            fields = ('token', 'sequence', 'output', 'generation', 'members', 'rectangle', 'progress')
            if swap is None or any(row[k] != swap[k] for k in fields):
                raise ValueError('Presentation lacks exact successful immutable swap')
            if [{k: m[k] for k in ('stableId', 'pid', 'digest')} for m in row['members']] != sources:
                raise ValueError('Presented sources/order changed')
            progress = row['progress']
            if isinstance(progress, bool) or not isinstance(progress, (int, float)) or not math.isfinite(progress) or not 0 <= progress <= 1:
                raise ValueError('Invalid actual progress')
            output = (row['output'], row['generation'])
            previous = latest.get(output)
            if previous and (int(row['sequence']) <= int(previous['sequence']) or int(row['timestampNs']) <= int(previous['timestampNs'])):
                raise ValueError('Accepted presentation sequence/time regressed')
            latest[output] = row
        elif kind == 'retargetAccepted':
            prefix, serial = token(row['token'])
            old_prefix, old_serial = token(current)
            if prefix != old_prefix or serial <= old_serial or row['token'] in accepted:
                raise ValueError('Retarget receipt must strictly advance')
            if row['identities'] != expected_identities or row['sourceDigests'] != sources or row.get('nativeAuthority') is not False:
                raise ValueError('Provisional retarget gained authority or changed sources')
            current = row['token']
            accepted[current] = index
        elif kind == 'retargeted':
            if row['token'] != current or current not in accepted or current in applied or row.get('sourceReused') is not True or row.get('nativeAuthority') is not False:
                raise ValueError('Retarget must apply exact accepted provisional receipt')
            if row['identities'] != expected_identities or row['sourceDigests'] != sources or row['uploadCount'] != 3:
                raise ValueError('Retarget recaptured, reuploaded or reordered sources')
            origins = row['origins']
            outputs = [(r['output'], r['generation']) for r in origins]
            if not origins or len(outputs) != len(set(outputs)) or set(outputs) != set(latest):
                raise ValueError('Every actual output requires one presented origin')
            proofs = []
            for origin in origins:
                previous = latest[(origin['output'], origin['generation'])]
                if any(origin[k] != previous[k] for k in ('sequence', 'timestampNs', 'rectangle', 'members')):
                    raise ValueError('Retarget origin differs from latest displayed frame')
                if not 0 < previous['progress'] < 1:
                    raise ValueError('Reversal must begin from an actual interior presentation')
                proofs.append({'origin': origin, 'actualPresentedToken': previous['token']})
            retargets.append({'token': current, 'origins': proofs, 'sourceReused': True})
            applied.add(current)
        elif kind in ('ready', 'endpoint'):
            if row['token'] != current or row.get('servicePromoted') is not True or row['identities'] != expected_identities or row['sourceDigests'] != sources:
                raise ValueError('Stale or unbound native authority event')
            if not latest or any(p['token'] != current or (kind == 'endpoint' and not p.get('endpoint')) for p in latest.values()):
                raise ValueError('Authority lacks complete current presented family')
    if len(retargets) != required_reversals:
        raise ValueError('Required actual interior reversals missing')
    if not any(r.get('event') == 'endpoint' and r.get('token') == current for r in events):
        raise ValueError('Final current-token endpoint missing')
    return {'reversals': retargets, 'sourceUploads': upload_count,
            'displayedOriginsBound': True, 'rendererEvidenceAccepted': True,
            'nativeCommitAccepted': False, 'physicalCadenceAccepted': False,
            'fullWindowsParityAccepted': False}
