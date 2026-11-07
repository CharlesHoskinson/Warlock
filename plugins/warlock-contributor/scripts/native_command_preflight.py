#!/usr/bin/env python3
"""Advisory fixed metadata argv check; never imports or executes native sources."""
import argparse
import json
from pathlib import Path
import sys

from owner_route_preflight import Refused, SHA, _read, _sha, _unique

NATIVE_GUARDS = {
    'implementation/elm-build-loop-v1/loop.py': '13216f4226f4fdb2e439604459e860763ce351fa77cec0f6082c30195372dbd6',
    'window-integration-qa/qa_run.py': '656f118c268e9f762f2d62c859d146043d74c83b72cd5457b779f1e30cb183a1',
    'window-integration-qa/qa_launch.py': '6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23',
}
PORTABLE_WRAPPER = 'docs/warlock-build-loop/v2/loop.py'
PORTABLE_WRAPPER_SHA256 = 'f565ce4c667eef25d087750b8dc95bff02e73d0e7d998ef623362448b0ce0a9e'
RUNNER = 'tools/run_webkit_provider_probe.py'
PACKET = '.warlock-contributor/evidence/nextloop-20261106/native-provider-probe/probe-packet.json'


def inspect(root, candidate_relative, expected_sha256):
    """Check only this fixed command/binding; actual admission remains separate."""
    root = Path(root)
    if not root.is_absolute() or root.resolve() != root:
        raise Refused('Expected canonical absolute repository root')
    if not isinstance(expected_sha256, str) or not SHA.fullmatch(expected_sha256):
        raise Refused('Candidate digest must be exact SHA256')
    observed = {}

    def read(name):
        data = _read(root, name, 8 * 1024 * 1024)
        observed[name] = data
        return data

    body = read(candidate_relative)
    if _sha(body) != expected_sha256:
        raise Refused('Candidate file digest differs')
    try:
        candidate = json.loads(body, object_pairs_hook=_unique)
    except (ValueError, UnicodeError) as error:
        raise Refused('Candidate JSON invalid') from error
    if not isinstance(candidate, dict) or candidate.get('scope') != 'native':
        raise Refused('Only fixed native metadata candidate is supported')
    manifest = candidate.get('manifest')
    if (not isinstance(manifest, dict) or not isinstance(manifest.get('runners'), dict)
            or not isinstance(manifest.get('profiles'), dict)):
        raise Refused('Candidate runner/profile bindings missing')
    packet_sha = manifest['profiles'].get(PACKET)
    runner_sha = manifest['runners'].get(RUNNER)
    if any(not isinstance(value, str) or not SHA.fullmatch(value)
           for value in (packet_sha, runner_sha)):
        raise Refused('Fixed packet or runner hash missing')
    expected = ['/usr/bin/python3', '-B', str(root / 'window-integration-qa/qa_run.py'),
                '--', '/usr/bin/python3', '-B', str(root / RUNNER), '--sha256', packet_sha]
    if candidate.get('argv') != expected:
        raise Refused('Fixed portable native command differs')
    pins = dict(NATIVE_GUARDS, **{PORTABLE_WRAPPER: PORTABLE_WRAPPER_SHA256,
                                RUNNER: runner_sha, PACKET: packet_sha})
    for name, pin in pins.items():
        if _sha(read(name)) != pin:
            raise Refused('Current native command binding differs: ' + name)
    for name, data in observed.items():
        if _read(root, name, 8 * 1024 * 1024) != data:
            raise Refused('Input changed during advisory observation: ' + name)
    return {'schema': 1, 'status': 'consistent-advisory-only',
            'candidateFileSha256': expected_sha256,
            'candidateSha256': _sha(json.dumps(candidate, sort_keys=True,
                separators=(',', ':'), ensure_ascii=False).encode()),
            'fixedMode': 'webkit-metadata-only', 'bindings': pins,
            'executionAuthorized': False, 'executionPerformed': False,
            'nativeAuthority': False, 'sourceReady': False,
            'fullCandidateValidationAndAllAdmissionGuardsStillRequired': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    try:
        relative = str(args.candidate.absolute().relative_to(args.root))
        result = inspect(args.root, relative, args.sha256)
    except (ValueError, OSError) as error:
        print(json.dumps({'schema': 1, 'status': 'refused', 'error': str(error),
                          'executionAuthorized': False, 'executionPerformed': False,
                          'nativeAuthority': False, 'sourceReady': False}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
