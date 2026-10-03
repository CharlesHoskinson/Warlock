#!/usr/bin/python3
"""Compare captured files and Git blobs with the immutable source inventory."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

REPO = Path(__file__).resolve().parents[1]

def hashes(path):
    sha256 = hashlib.sha256()
    oid = hashlib.sha1()
    oid.update(b'blob ' + str(path.stat().st_size).encode() + b'\0')
    with path.open('rb') as handle:
        while chunk := handle.read(1024 * 1024):
            sha256.update(chunk)
            oid.update(chunk)
    return sha256.hexdigest(), oid.hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', default='HEAD')
    parser.add_argument('--index', action='store_true')
    parser.add_argument('--write-report', action='store_true')
    parser.add_argument('--inventory', default='provenance/snapshot.jsonl')
    parser.add_argument('--report', default='provenance/verification.json')
    args = parser.parse_args()
    command = ['git', 'ls-files', '-s', '-z'] if args.index else ['git', 'ls-tree', '-r', '-z', args.revision]
    raw = subprocess.check_output(command, cwd=REPO)
    entries = {}
    for entry in raw.split(b'\0'):
        if not entry:
            continue
        header, name = entry.split(b'\t', 1)
        pieces = header.split()
        mode = pieces[0].decode()
        oid = pieces[1 if args.index else 2].decode()
        if args.index:
            assert pieces[2] == b'0', 'Unmerged index'
        else:
            assert pieces[1] == b'blob', 'Embedded Git repository in snapshot'
        entries[os.fsdecode(name)] = (mode, oid)
    counts = {'files': 0, 'symlinks': 0, 'upstreamGitArchives': 0, 'specialFilesRecordedOnly': 0}
    with (REPO / args.inventory).open() as handle:
        for line in handle:
            row = json.loads(line)
            kind = row['kind']
            if kind == 'file':
                path = REPO / row['path']
                digest, oid = hashes(path)
                assert digest == row['sha256'], f'Inventory mismatch: {row["path"]}'
                assert path.stat().st_size == row['size']
                assert stat.S_IMODE(path.stat().st_mode) == row['mode']
                mode = '100755' if row['mode'] & 0o111 else '100644'
                assert entries.get(row['path']) == (mode, oid), f'Git blob mismatch: {row["path"]}'
                counts['files'] += 1
            elif kind == 'symlink':
                path = REPO / row['path']
                assert path.is_symlink() and os.readlink(path) == row['target']
                data = os.fsencode(row['target'])
                oid = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                assert entries.get(row['path']) == ('120000', oid)
                counts['symlinks'] += 1
            elif kind == 'upstream-git-archive':
                digest, oid = hashes(REPO / row['archive'])
                assert digest == row['sha256']
                assert entries.get(row['archive']) == ('100644', oid)
                counts['upstreamGitArchives'] += 1
            elif kind == 'special-file-not-copied':
                assert row['path'] not in entries
                counts['specialFilesRecordedOnly'] += 1
    assert subprocess.run(['git', 'fsck', '--no-dangling'], cwd=REPO, stdout=subprocess.DEVNULL).returncode == 0
    report = {'result': 'pass', 'verifiedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'target': 'index' if args.index else args.revision, 'counts': counts,
              'trackedFiles': len(entries), 'inventory': args.inventory, 'inventorySHA256': hashes(REPO / args.inventory)[0],
              'allCapturedFilesMatchInventoryAndGitBlobs': True, 'gitObjectIntegrity': True,
              'sourceTreesModified': False, 'deploymentPerformed': False}
    if args.write_report:
        with (REPO / args.report).open('x') as handle:
            json.dump(report, handle, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
    print(json.dumps(report))

if __name__ == '__main__':
    main()
