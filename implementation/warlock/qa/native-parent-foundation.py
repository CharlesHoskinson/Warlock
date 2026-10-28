#!/usr/bin/env python3
"""In-repository entry for the reviewed, hash-pinned private parent probe."""
import hashlib
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[3]
TARGET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/parent-host/foundation.py')
EXPECTED_SHA256 = 'a490b8cf45aa8593c96138d4820481d3f03397ede62d9f075aa6a1f6e1205cdc'


def checked_payload():
    path = Path(TARGET.anchor)
    for component in TARGET.parts[1:]:
        path /= component
        if path.is_symlink():
            raise RuntimeError('Foundation source symlink refused')
    if not path.is_file():
        raise RuntimeError('Reviewed foundation source unavailable')
    body = path.read_bytes()
    if hashlib.sha256(body).hexdigest() != EXPECTED_SHA256:
        raise RuntimeError('Reviewed foundation source changed')
    return body


def main():
    sys.path.insert(0, str(REPO / 'window-integration-qa'))
    from qa_launch import require_qa_scope
    require_qa_scope()
    body = checked_payload()
    sys.path.insert(0, str(TARGET.parent))
    sys.argv[0] = str(TARGET)
    # Run precisely the bytes checked above; no second path read after hashing.
    namespace = {'__name__': '__main__', '__file__': str(TARGET),
                 '__package__': None, '__cached__': None}
    exec(compile(body, str(TARGET), 'exec'), namespace)


if __name__ == '__main__':
    main()
