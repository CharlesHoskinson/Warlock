#!/usr/bin/python3
"""Root read-only review of the exact B01–B12 source component packet."""
import datetime
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat

B = Path('/home/hoskinson/window-behavior-spec/pin-max-campaign-b-controller-v1-proposal')
QA = Path('/home/hoskinson/window-integration-qa')

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify(packet):
    assert set(packet['inputs']) == set(packet['inputModes'])
    for name, wanted in packet['inputs'].items():
        path = Path(name)
        assert digest(path) == wanted, name
        assert stat.S_IMODE(path.stat().st_mode) == packet['inputModes'][name], name
    for name, wanted in packet['symlinks'].items():
        assert Path(name).is_symlink() and os.readlink(name) == wanted, name
    for name, wanted in packet['directoryModes'].items():
        path = Path(name)
        assert path.is_dir() and not path.is_symlink(), name
        assert stat.S_IMODE(path.stat().st_mode) == wanted, name

def contains(parent, child):
    for field in ['inputs', 'inputModes', 'symlinks', 'directoryModes']:
        assert all(parent[field].get(k) == v for k, v in child[field].items()), field

def main():
    from qa_launch import require_qa_scope
    scope = require_qa_scope()
    path = B / 'SOURCE_INPUTS.json'
    packet = json.loads(path.read_bytes())
    ready = json.loads((B / 'SOURCE_READY.json').read_bytes())
    assert ready['sourceInputsSHA256'] == digest(path)
    assert ready['pairSHA256'] == digest(B / 'PAIR_READY.json')
    assert ready['nativeAuthorized'] is False and ready['fullCampaignBAccepted'] is False
    verify(packet)
    a = json.loads((QA / 'pin-maximized-native-v2/frozen-inputs.json').read_bytes())
    contains(packet, a)
    observer_root = Path('/home/hoskinson/window-behavior-spec/pin-max-campaign-b-observer-v2-build')
    observer = json.loads((observer_root / 'SOURCE_READY_INPUTS.json').read_bytes())
    contains(packet, dict(inputs=observer['inputs'], inputModes=observer['inputModes'],
                          symlinks=observer['links'], directoryModes=observer['directoryModes']))
    design_root = Path('/home/hoskinson/window-behavior-spec/pin-maximized-native-policy-v1-design')
    design = json.loads((design_root / 'DESIGN_INPUTS.json').read_bytes())
    for relative, record in design['files'].items():
        name = str(design_root / relative)
        assert packet['inputs'][name] == record['sha256']
        assert packet['inputModes'][name] == record['mode']
    inverses = json.loads((B / 'SOURCE_INVERSES.json').read_bytes())
    assert inverses['productDeltas'] == []
    assert inverses['original14BodiesPredicatesDeadlinesUnchanged'] is True
    for row in inverses['originalA3SourceConservation']:
        path = Path(row['path'])
        assert digest(path) == row['sha256']
        assert stat.S_IMODE(path.stat().st_mode) == row['mode']
    for row in inverses['wholePreReviewInverses']:
        before, after = Path(row['preimage']), Path(row['final'])
        assert digest(before) == row['beforeSHA256']
        assert digest(after) == row['afterSHA256']
        diff = ''.join(difflib.unified_diff(before.read_text().splitlines(True),
                    after.read_text().splitlines(True), fromfile=str(before), tofile=str(after)))
        assert Path(row['wholeFileDiff']).read_text() == diff
        assert digest(row['wholeFileDiff']) == row['diffSHA256']
    pair = json.loads((B / 'PAIR_READY.json').read_bytes())
    assert pair['buildComplete'] is True and pair['observerBuildComplete'] is True
    assert pair['sourceProposalOnly'] is False
    for name, wanted in pair['inputs'].items():
        assert packet['inputs'][name] == wanted
        assert packet['inputModes'][name] == pair['inputModes'][name]
    for name, wanted in pair['directoryModes'].items():
        assert packet['directoryModes'][name] == wanted
    result = dict(schema='root-pin-campaign-b-controller-review-v1', scope=scope,
        observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        sourceReadySHA256=digest(B / 'SOURCE_READY.json'), sourceInputsSHA256=digest(path),
        pairSHA256=digest(B / 'PAIR_READY.json'), files=len(packet['inputs']),
        links=len(packet['symlinks']), directories=len(packet['directoryModes']),
        allBytesModesLinksDirectoriesMatch=True, fullAAncestorConserved=len(a['inputs']),
        wholeObserverConserved=len(observer['inputs']), fullDesignConserved=len(design['files']),
        originalA3Conserved=len(inverses['originalA3SourceConservation']), productDeltas=[],
        reviewed='Complete controller and all final deltas; runner/freezer/host/producer classifier and actual focused CPU cases; fourteen-case closure model and prior B design; source/ABI observer reviews.',
        approved='Freeze exact packet, then one root serial private B01–B12 component attempt after exact frozen/pair grant.',
        nativeExecuted=False, fullCampaignBAccepted=False, fullParityAccepted=False)
    output = QA / 'pin-max-campaign-b-controller-root-source-review-v1.json'
    raw = (json.dumps(result, indent=2) + '\n').encode()
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps(dict(report=str(output), sha256=hashlib.sha256(raw).hexdigest(),
                         files=result['files'], links=result['links'], result='pass')))

if __name__ == '__main__':
    main()
