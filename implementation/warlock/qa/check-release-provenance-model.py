#!/usr/bin/env python3
"""Model-derived review mutations; this is not release acceptance."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope
sys.path.insert(0, str(REPO / 'implementation/warlock/adapter'))
from release_compliance import review


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    require_qa_scope()
    with tempfile.TemporaryDirectory() as d:
        root = Path(d); source = root / 'source'; source.mkdir()
        candidate = source / 'implementation/warlock'; candidate.mkdir(parents=True)
        payload = root / 'payload'; payload.mkdir()
        src = source / 'source.txt'; src.write_bytes(b'source')
        notice = candidate / 'notice.txt'; notice.write_bytes(b'notice')
        (payload / 'notice.txt').write_bytes(b'notice')
        components = []
        for category in ('compiler', 'package', 'host', 'native-library', 'asset'):
            components.append({'id': category, 'category': category, 'scope': 'build',
                'provenance': [{'path': 'source.txt', 'sha256': digest(b'source')}],
                'notices': [{'path': 'notice.txt', 'sha256': digest(b'notice')}],
                'disposition': {'status': 'reviewed', 'evidence': 'record'}, 'files': []})
        components[-1]['scope'] = 'shipped'
        components[-1]['files'] = [{'path': 'notice.txt', 'type': 'file', 'sha256': digest(b'notice')}]
        catalog = root / 'catalog.json'
        def check(rows=components):
            catalog.write_text(json.dumps({'schema': 1, 'components': rows}))
            return review(payload, [catalog], source)
        def expect(ok, label, rows=components):
            result = check(rows)
            assert result['ok'] == ok, (label, result['errors'])
            print(label, 'accepted' if ok else 'refused')
        expect(True, 'complete')
        src.write_bytes(b'changed'); expect(False, 'source mismatch')
        src.unlink(); expect(False, 'source missing')
        src.write_bytes(b'source'); expect(True, 'source restored')
        notice.write_bytes(b'changed'); expect(False, 'notice mismatch')
        notice.unlink(); expect(False, 'notice missing')
        notice.write_bytes(b'notice'); expect(True, 'notice restored')
        (payload / 'notice.txt').write_bytes(b'changed'); expect(False, 'payload notice mismatch')
        (payload / 'notice.txt').write_bytes(b'notice')
        bad = copy.deepcopy(components); bad[0]['disposition']['status'] = 'unknown'; expect(False, 'unknown disposition', bad)
        bad[0]['disposition'] = {'status': 'reviewed', 'evidence': ''}; expect(False, 'empty review evidence', bad)
        bad = copy.deepcopy(components); bad[0]['notices'] = []; expect(False, 'missing applicability', bad)
        bad[0]['notice_disposition'] = {'status': 'reviewed', 'evidence': 'record'}; expect(True, 'reviewed no notice', bad)
        expect(True, 'recovered')
    print('API checks only; no release acceptance inferred')


if __name__ == '__main__':
    main()
