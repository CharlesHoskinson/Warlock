#!/usr/bin/env python3
"""Exercise release review against independent package mutations in QA scope."""
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


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    require_qa_scope()
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp); payload = root / 'payload'; payload.mkdir()
        source = root / 'source'; candidate = source / 'implementation/warlock'
        notice = candidate / 'release/notices/license.txt'; notice.parent.mkdir(parents=True)
        notice.write_bytes(b'license evidence\n')
        (source / 'provenance').write_bytes(b'upstream source\n')
        (payload / 'release/notices').mkdir(parents=True)
        (payload / 'release/notices/license.txt').write_bytes(notice.read_bytes())
        (payload / 'program').write_bytes(b'candidate\n')
        (payload / 'alias').symlink_to('program')
        prov = [{'path': 'provenance', 'sha256': digest(b'upstream source\n')}]
        notices = [{'path': 'release/notices/license.txt', 'sha256': digest(notice.read_bytes())}]
        def component(name, category, scope='build'):
            return {'id': name, 'scope': scope, 'category': category, 'provenance': prov,
                    'notices': notices, 'disposition': {'status': 'reviewed', 'evidence': 'review record'}, 'files': []}
        components = [component('compiler', 'compiler'), component('package', 'package', 'shipped'),
                      component('host', 'host', 'shipped'), component('native', 'native-library'),
                      component('asset', 'asset')]
        components[2]['contains'] = ['package']
        components[2]['files'] = [{'path': 'program', 'type': 'file', 'sha256': digest(b'candidate\n')},
                                  {'path': 'alias', 'type': 'symlink', 'target': 'program'},
                                  {'path': 'release/notices/license.txt', 'type': 'file', 'sha256': digest(notice.read_bytes())}]
        catalog = root / 'catalog.json'
        def run(rows=components):
            catalog.write_text(json.dumps({'schema': 1, 'components': rows}))
            return review(payload, [catalog], source)
        first = run()
        assert first['ok'], first
        assert first == run(), 'review should be deterministic'
        bad = copy.deepcopy(components); bad[0]['disposition']['status'] = 'unknown'
        assert not run(bad)['ok'], 'unknown disposition must block'
        bad = copy.deepcopy(components); bad[0]['notices'] = []
        assert not run(bad)['ok'], 'undetermined notice applicability must block'
        bad = copy.deepcopy(components); bad[2].pop('contains')
        assert not run(bad)['ok'], 'unconnected embedded component must block'
        bad = copy.deepcopy(components); bad[3]['files'] = [copy.deepcopy(components[2]['files'][0])]; bad[3]['scope'] = 'shipped'
        assert not run(bad)['ok'], 'duplicate ownership must block'
        bad = copy.deepcopy(components); bad[2]['files'][0]['path'] = '../program'
        assert not run(bad)['ok'], 'traversal must block'
        bad = copy.deepcopy(components); bad[0]['provenance'][0]['sha256'] = '0' * 64
        assert not run(bad)['ok'], 'stale provenance must block'
        for value in (None, [], {}, 1, True):
            bad = copy.deepcopy(components); bad[0]['category'] = value
            assert not run(bad)['ok'], 'malformed category must return a blocker'
            bad = copy.deepcopy(components); bad[0]['contains'] = [value]
            assert not run(bad)['ok'], 'malformed relation must return a blocker'
        bad = copy.deepcopy(components); bad[2].pop('contains'); bad[1]['contains'] = ['package']
        assert not run(bad)['ok'], 'self-referencing attribution must block'
        bad = copy.deepcopy(components); bad[0]['provenance'][0]['path'] = '/private/example'
        result = run(bad)
        assert not result['ok'] and '/private/example' not in json.dumps(result), 'absolute paths must not leak'
        def inaccessible(_root, *, followlinks, onerror):
            onerror(PermissionError('unreadable subtree'))
            return iter(())
        with patch('release_compliance.os.walk', inaccessible):
            assert 'payload traversal failed' in run()['errors'], 'walk errors must block'
        (payload / 'extra').write_text('unexpected')
        assert not run()['ok'], 'unexpected payload must block'
        (payload / 'extra').unlink()
        (payload / 'release/notices/license.txt').write_text('tampered')
        assert not run()['ok'], 'notice tampering must block'
        (payload / 'release/notices/license.txt').write_bytes(notice.read_bytes())
        (payload / 'alias').unlink(); (payload / 'alias').symlink_to('../provenance')
        assert not run()['ok'], 'escaping symlink must block'
        (payload / 'alias').unlink(); (payload / 'alias').symlink_to('./program')
        assert not run()['ok'], 'different symlink spelling must block'
        catalog.write_text('{"schema":1,"schema":1,"components":[]}')
        assert not review(payload, [catalog], source)['ok'], 'duplicate JSON keys must block'
        print('release compliance positive and mutation checks passed; no release acceptance inferred')


if __name__ == '__main__':
    main()
