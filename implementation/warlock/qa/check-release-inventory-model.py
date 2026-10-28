#!/usr/bin/env python3
"""Model-derived review cases; requires the protected CPU QA scope."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope
sys.path.insert(0, str(REPO / 'implementation/warlock/adapter'))
from release_compliance import review


def main():
    require_qa_scope()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp); source = root / 'source'; source.mkdir()
        payload = root / 'payload'; payload.mkdir()
        (source / 'proof').write_bytes(b'proof')
        (payload / 'program').write_bytes(b'program')
        digest = lambda b: hashlib.sha256(b).hexdigest()
        def component(name, category, scope='build'):
            return {'id': name, 'category': category, 'scope': scope,
                    'provenance': [{'path': 'proof', 'sha256': digest(b'proof')}],
                    'notices': [], 'notice_disposition': {'status': 'reviewed', 'evidence': 'none applicable'},
                    'disposition': {'status': 'reviewed', 'evidence': 'review'}, 'files': []}
        rows = [component('root', 'host', 'shipped'), component('child', 'package', 'shipped'),
                component('compiler', 'compiler'), component('native', 'native-library'), component('asset', 'asset')]
        rows[0]['files'] = [{'path': 'program', 'type': 'file', 'sha256': digest(b'program')}]
        rows[0]['contains'] = ['child']
        catalog = root / 'catalog.json'
        def run(value):
            catalog.write_text(json.dumps({'schema': 1, 'components': value}))
            return review(payload, [catalog], source)
        assert run(rows)['ok']
        (payload / 'extra').write_bytes(b'extra')
        assert any('unaccounted' in x for x in run(rows)['errors'])
        (payload / 'extra').unlink()
        bad = copy.deepcopy(rows); bad[1]['files'] = copy.deepcopy(rows[0]['files'])
        assert any('duplicate owner' in x for x in run(bad)['errors'])
        bad = copy.deepcopy(rows); bad[0]['contains'] = []; bad[1]['contains'] = ['child']
        assert any('disconnected shipped' in x for x in run(bad)['errors'])
        bad[0]['contains'] = ['child']
        assert run(bad)['ok'], 'rooted self-cycle is reachable'
        def broken_walk(_root, *, followlinks, onerror):
            onerror(PermissionError('inaccessible'))
            return iter(())
        with patch('release_compliance.os.walk', broken_walk):
            assert 'payload traversal failed' in run(rows)['errors']
        assert run(rows)['ok'], 'restoration'
    print('six review correspondence cases passed; no release acceptance inferred')


if __name__ == '__main__':
    main()
