"""Verify every real address-reuse attempt before cross-run fixed-gate comparison."""
import re

ATTEMPT = re.compile(r'^reuseAttempt([1-9][0-9]*)(OneFreshNativeIncarnation|OriginalClockBeforeExpiry|UnreusedSourceNormalExit)$')

def validate_attempts(proof):
    attempts = proof['addressReuseAttempts']
    assert 1 <= len(attempts) <= 12
    evidence = proof['addressReuseEvidence']
    assert evidence['actualAddressReuse'] and evidence['oldAddress'] == evidence['replacementAddress']
    assert evidence['oldSubject'] != evidence['replacementSubject']
    frame = evidence['originalFrame']
    expected = []
    previous = int(evidence['oldSubject'])
    for ordinal, attempt in enumerate(attempts, 1):
        assert attempt['attempt'] == ordinal
        assert attempt['oldAddress'] == evidence['oldAddress'] and attempt['oldSubject'] == evidence['oldSubject']
        assert int(attempt['newSubject']) > previous
        previous = int(attempt['newSubject'])
        scope = attempt['scope']
        assert scope['context']['incarnation'] == attempt['newSubject']
        assert scope['clock'] == frame['job']['clock']
        assert int(scope['now']) < int(frame['expires'])
        expected.extend(['reuseAttempt'+str(ordinal)+'OneFreshNativeIncarnation',
                         'reuseAttempt'+str(ordinal)+'OriginalClockBeforeExpiry'])
        if ordinal < len(attempts):
            assert attempt['newAddress'] != evidence['oldAddress']
            expected.append('reuseAttempt'+str(ordinal)+'UnreusedSourceNormalExit')
        else:
            assert attempt['newAddress'] == evidence['oldAddress']
            assert attempt['newSubject'] == evidence['replacementSubject']
        exits = [row for row in proof['ownedExitCodes'] if row['name'] == 'reuse-replacement-'+str(ordinal)]
        assert len(exits) == 1 and exits[0]['exitCode'] == 0
    actual = [row for row in proof['checks'] if ATTEMPT.fullmatch(row['name'])]
    assert [row['name'] for row in actual] == expected
    assert all(row['passed'] for row in actual)
    return {'attempts': len(attempts), 'actualAttemptChecks': len(actual),
            'originalExpiryUnchanged': True, 'allOwnedAttemptExitsNormal': True}

def compare(prior, current, stable_names):
    previous_attempts = validate_attempts(prior)
    current_attempts = validate_attempts(current)
    previous = [name for name in stable_names(prior['checks']) if not ATTEMPT.fullmatch(name)]
    names = set(previous)
    actual = [name for name in stable_names(current['checks']) if name in names]
    assert actual == previous
    assert all(row['passed'] for row in prior['checks'] if row['name'] in names)
    assert all(row['passed'] for row in current['checks'] if row['name'] in names)
    return {'passed': True, 'fixedOrderedControls': len(previous),
            'prior': previous_attempts, 'current': current_attempts,
            'scope': 'Conditional allocator trials each verified against their actual native evidence; unchanged fixed ordered oracles, physical/receipt/clock/pixel/deadline gates remain required.'}
