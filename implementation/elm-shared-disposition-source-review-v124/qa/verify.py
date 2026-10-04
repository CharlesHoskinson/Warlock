"""Independent held-packet integrity check; no GUI or acceptance inference."""
import hashlib
import json
import stat
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PACKETS = {
    'elm-shared-batch-disposition-v104': '5e120bdb350c664897f14ff0ebdf25e857fe37aa2cd8819d3be02ef2f7bfd21e',
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(path, row):
    assert not path.is_symlink(), str(path)
    assert digest(path) == row['sha256'], str(path)
    if 'size' in row:
        assert path.stat().st_size == row['size'], str(path)
    if 'mode' in row:
        mode = row['mode']
        expected = int(mode, 8) if isinstance(mode, str) else mode
        assert stat.S_IMODE(path.stat().st_mode) == expected, str(path)

def main():
    output = ROOT / 'qa' / ('verify-' + str(time.time_ns()))
    output.mkdir()
    report = {'passed': False, 'nativeAcceptance': False, 'fullRoadmapAccepted': False,
              'scope': 'Independent hash, size and recorded mode verification of held packets', 'packets': {}}
    try:
        for name, expected in PACKETS.items():
            packet_root = REPO / 'implementation' / name
            manifest = packet_root / 'qa/held-source-manifest.json'
            assert digest(manifest) == expected, str(manifest)
            packet = json.loads(manifest.read_text())
            assert packet['sourceHeld'] and packet['evidenceIntegrityPassed']
            for relative, row in packet['files'].items():
                path = packet_root / relative
                assert path.resolve().is_relative_to(packet_root.resolve()), str(path)
                verify(path, row)
            for absolute, row in packet.get('externalFiles', {}).items():
                verify(Path(absolute), row)
            report['packets'][name] = {'manifestSHA256': expected, 'files': len(packet['files']),
                                      'externalFiles': len(packet.get('externalFiles', {}))}
        report['passed'] = True
    except Exception as error:
        report['error'] = repr(error)
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'report': str(output / 'report.json'), 'error': report.get('error')}))
    return not report['passed']

if __name__ == '__main__':
    raise SystemExit(main())
