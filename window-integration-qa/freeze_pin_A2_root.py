"""Freeze reviewed A2 sources while retaining the entire original A1 closure."""
from pathlib import Path
import hashlib
import json
import os
import stat

QA = Path('/home/hoskinson/window-integration-qa')
B = QA / 'pin-native-qa-v2'
A1 = QA / 'pin-native-qa-v1/source-ready-inputs.json'
A1_SHA = '7f8f54910c2f3a260856e419c1f094e6ed6dbab84807368be3c874ae33967f57'
COMPONENT = QA / 'pin-input-episode-v2-component-handoff-v1.json'
COMPONENT_SHA = '9ae5080c2e740edf642056713b031c2e143d6baddf4838d3eed36ee2f8cf942b'
REVIEW = QA / 'pin-v25-A2-root-source-review-v1.json'
REVIEW_SHA = 'f298623f89f79e0ca017df80bcd5f3aec8d608a47a5d9cb3802f9acad0436599'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def verify(row):
    if set(row['inputs']) != set(row['inputModes']):
        raise ValueError('Complete source byte and mode pairs required')
    for name, digest in row['inputs'].items():
        p = Path(name)
        if p.is_symlink() or sha(p) != digest or stat.S_IMODE(p.stat().st_mode) != row['inputModes'][name]:
            raise ValueError('Frozen source changed: ' + name)
    for name, target in row['symlinks'].items():
        if not Path(name).is_symlink() or os.readlink(name) != target:
            raise ValueError('Frozen link changed: ' + name)


def inventory():
    for p, expected in ((A1, A1_SHA), (COMPONENT, COMPONENT_SHA), (REVIEW, REVIEW_SHA)):
        if sha(p) != expected:
            raise ValueError('Reviewed source packet changed')
    original = json.loads(A1.read_text())
    verify(original)
    row = {**original, 'inputs': dict(original['inputs']),
           'inputModes': dict(original['inputModes']), 'symlinks': dict(original['symlinks'])}

    def add(p, expected=None, mode=None):
        p = Path(p).absolute()
        actual = sha(p)
        actual_mode = stat.S_IMODE(p.stat().st_mode)
        if p.is_symlink() or (expected is not None and expected != actual) or (mode is not None and mode != actual_mode):
            raise ValueError('Reviewed source changed: ' + str(p))
        for alias in (p, p.resolve()):
            name = str(alias)
            if name in row['inputs'] and (row['inputs'][name] != actual or row['inputModes'][name] != actual_mode):
                raise ValueError('Conflicting source alias: ' + name)
            row['inputs'][name] = actual
            row['inputModes'][name] = actual_mode
        for alias in (p, *p.parents):
            if alias.is_symlink():
                target = os.readlink(alias)
                if str(alias) in row['symlinks'] and row['symlinks'][str(alias)] != target:
                    raise ValueError('Conflicting source link')
                row['symlinks'][str(alias)] = target

    component = json.loads(COMPONENT.read_text())
    for name, w in component['componentSources'].items():
        add(name, w['sha256'], w['mode'])
    for folder in (QA / 'pin-input-episode-v2-design', QA / 'pin-input-episode-v2-cpu-v1',
                   QA / 'pin-input-episode-v2-cpu-v2'):
        for p in sorted(folder.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                add(p)
    for p in (A1, A1.parent / 'source-ready.json', COMPONENT, REVIEW,
              Path(__file__).resolve(), Path('/home/hoskinson/Documents/crash-noise/HANDOFF-codex-window-qa.md')):
        add(p)
    row.update(version='pin-native-A2-reviewed', sourceComponent=str(COMPONENT),
               sourceComponentSHA256=COMPONENT_SHA, productReview=str(REVIEW), productReviewSHA256=REVIEW_SHA,
               nativeLaunch=False, nativeAccepted=False, mainChanges=False,
               fullWindowsParityAccepted=False, sourceOnly=False, originalFeatureCases=14)
    row['candidate'] = {**original['candidate'], 'moduleSourceReviewPending': False}
    row['inputs'] = dict(sorted(row['inputs'].items()))
    row['inputModes'] = dict(sorted(row['inputModes'].items()))
    row['symlinks'] = dict(sorted(row['symlinks'].items()))
    verify(row)
    return row


def main():
    packet = inventory()
    destination = B / 'frozen-inputs.json'
    with os.fdopen(os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600), 'w') as f:
        json.dump(packet, f, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    directory = os.open(B, os.O_DIRECTORY | os.O_RDONLY | os.O_CLOEXEC)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    print(json.dumps({'result': 'pass', 'manifest': str(destination), 'sha256': sha(destination),
                      'inputs': len(packet['inputs']), 'modes': len(packet['inputModes']),
                      'links': len(packet['symlinks']), 'nativeAccepted': False}))


if __name__ == '__main__':
    main()
