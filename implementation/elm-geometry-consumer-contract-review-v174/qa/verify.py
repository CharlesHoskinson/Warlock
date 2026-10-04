#!/usr/bin/env python3
"""Integrity-only verification of an independent read-only review capture."""
from pathlib import Path
import hashlib, json, time
ROOT = Path(__file__).resolve().parents[1]
def main():
    out = ROOT / 'qa' / ('review-' + str(time.time_ns()))
    out.mkdir(mode=0o700)
    files = {}
    checks = []
    manifest = json.loads((ROOT / 'source-snapshot.json').read_text())
    for original, row in manifest['sources'].items():
        path = ROOT / row['capture']
        data = path.read_bytes()
        checks.append({'name': original, 'passed': not path.is_symlink() and len(data) == row['size'] and hashlib.sha256(data).hexdigest() == row['sha256']})
        files[row['capture']] = {'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data)}
    for relative in ['CONTRACT.md', 'source-snapshot.json', 'qa/verify.py', 'qa/source-capture-failure.txt']:
        data = (ROOT / relative).read_bytes()
        files[relative] = {'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data)}
    checks.append({'name': 'capture explicitly makes no behavioral/native acceptance claim', 'passed': manifest['nativeAcceptance'] is False and manifest['behavioralAcceptance'] is False})
    report = {'schema': 1, 'passed': all(c['passed'] for c in checks), 'kind': 'read-only-source-review-integrity', 'checks': checks, 'files': files, 'behavioralAcceptance': False, 'nativeAcceptance': False, 'scope': 'Captured bytes and contract review only; no consumer tests or GUI ran.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'checks': len(checks), 'report': str(out / 'report.json')}))
    return 0 if report['passed'] else 1
if __name__ == '__main__':
    raise SystemExit(main())
