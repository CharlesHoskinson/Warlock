#!/usr/bin/python3
"""Audit source coverage and extract external references without dumping packets."""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import stat

REPO = Path(__file__).resolve().parents[1]
HOME_ROOT = Path('/home/hoskinson')

def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

def main():
    output = REPO / 'provenance' / 'coverage-audit-v1'
    output.mkdir(exist_ok=False)
    summary = json.loads((REPO / 'provenance/snapshot-summary.json').read_text())
    rows = {}
    with (REPO / 'provenance/snapshot.jsonl').open() as handle:
        for line in handle:
            row = json.loads(line)
            rows[row['source']] = row
    changes = []
    new_files = []
    checked = collections.Counter()
    for row in rows.values():
        source = Path(row['source'])
        if row['kind'] == 'file':
            if not source.is_file():
                changes.append({'source': str(source), 'reason': 'missing'})
            elif digest(source) != row['sha256'] or stat.S_IMODE(source.stat().st_mode) != row['mode']:
                changes.append({'source': str(source), 'reason': 'content-or-mode-change'})
            checked['files'] += 1
        elif row['kind'] == 'symlink':
            if not source.is_symlink() or os.readlink(source) != row['target']:
                changes.append({'source': str(source), 'reason': 'symlink-change'})
            checked['symlinks'] += 1
    descriptors = []
    for mapping in summary['mappings']:
        source = Path(mapping['source'])
        if source.is_dir() and not source.is_symlink():
            for folder, dirs, files in os.walk(source, followlinks=False):
                dirs[:] = [d for d in dirs if d != '.git']
                for name in dirs + files:
                    path = Path(folder) / name
                    if name == '.git':
                        continue
                    if str(path) not in rows:
                        new_files.append(str(path))
                    lower = name.lower()
                    if path.is_file() and lower.endswith('.json') and any(token in lower for token in ['source-ready', 'frozen-input', 'source-input', 'source_input']):
                        descriptors.append(path)
    paths = set()
    pattern = re.compile(rb'"(/home/hoskinson/[^"\\\n]{1,4096})"')
    for descriptor in descriptors:
        overlap = b''
        with descriptor.open('rb') as handle:
            while chunk := handle.read(1024 * 1024):
                data = overlap + chunk
                for match in pattern.finditer(data):
                    paths.add(os.fsdecode(match.group(1)))
                overlap = data[-8192:]
    roots = [Path(m['source']) for m in summary['mappings']]
    external = []
    group_counts = collections.Counter()
    for name in sorted(paths):
        path = Path(name)
        if any(path == root or root in path.parents for root in roots):
            continue
        if not path.exists() and not path.is_symlink():
            state = 'historical-path-no-longer-present'
        elif path.is_symlink():
            state = 'existing-symlink'
        elif path.is_file():
            state = 'existing-file'
        else:
            state = 'existing-directory-or-special'
        relative = path.relative_to(HOME_ROOT)
        group = '/'.join(relative.parts[:3]) if relative.parts[0].startswith('.') else '/'.join(relative.parts[:2])
        group_counts[group] += 1
        external.append({'path': name, 'state': state, 'group': group})
    details = {'changesSinceCapture': changes, 'newFilesInMappedRoots': new_files,
               'externalHomeReferences': external}
    with (output / 'details.json').open('x') as handle:
        json.dump(details, handle, indent=2)
        handle.write('\n')
    report = {'auditedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'originalCapturedFilesChecked': dict(checked), 'changesSinceCapture': len(changes),
              'newFilesInMappedRoots': len(new_files), 'descriptorsScanned': len(descriptors),
              'uniqueReferencedHomePaths': len(paths), 'externalHomeReferences': len(external),
              'externalGroups': dict(group_counts), 'details': str((output / 'details.json').relative_to(REPO))}
    with (output / 'report.json').open('x') as handle:
        json.dump(report, handle, indent=2)
        handle.write('\n')
    print(json.dumps(report))

if __name__ == '__main__':
    main()
