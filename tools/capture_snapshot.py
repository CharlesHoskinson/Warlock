#!/usr/bin/python3
"""Capture the existing workspace without editing it; preserve provenance."""
import collections
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tarfile

REPO = Path(__file__).resolve().parents[1]
HOME_ROOT = Path('/home/hoskinson')
FICLONE = 0x40049409

def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

def signature(st):
    return (st.st_dev, st.st_ino, st.st_mode, st.st_size, st.st_mtime_ns, st.st_ctime_ns)

def plan():
    entries = [
        ('window-behavior-spec', 'window-behavior-spec'),
        ('window-integration-qa', 'window-integration-qa'),
        ('.local/share/hypr-window-controls', 'installed/home/.local/share/hypr-window-controls'),
        ('.local/share/omarchy-files', 'installed/home/.local/share/omarchy-files'),
        ('.local/share/omarchy-files-native', 'installed/home/.local/share/omarchy-files-native'),
        ('.config/hypr', 'installed/home/.config/hypr'),
        ('.config/omarchy/shell.json', 'installed/home/.config/omarchy/shell.json'),
        ('Documents/crash-noise', 'docs/crash-noise'),
        ('.codex/skills/omarchy', 'docs/skills/omarchy'),
    ]
    for name in ['hoskinson.windows', 'hoskinson.taskview', 'hoskinson.files']:
        entries.append((f'.config/omarchy/plugins/{name}', f'installed/home/.config/omarchy/plugins/{name}'))
    for name in ['hyprbars-dragend', 'hyprbars-dragend-initfix', 'hyprland-motion-audit',
                 'hyprland-plugins-upstream', 'qtdeclarative-accessibility',
                 'quickshell-accessibility', 'window-accessibility-bridge',
                 'window-accessibility-bridge-reader', 'xdph-pr429']:
        entries.append((f'src/{name}', f'src/{name}'))
    for directory, pattern in [('.local/bin', 'hypr-*'), ('.local/lib', 'libhyprbars*'),
                               ('.config/systemd/user', 'omarchy-taskbar*')]:
        for source in sorted((HOME_ROOT / directory).glob(pattern)):
            entries.append((str(source.relative_to(HOME_ROOT)), 'installed/home/' + str(source.relative_to(HOME_ROOT))))
    for relative in ['.local/bin/omarchy-files', '.local/bin/omarchy-crash-watch-filtered',
                     '.config/systemd/user/omarchy-crash-watch.service.d']:
        entries.append((relative, 'installed/home/' + relative))
    result = [(HOME_ROOT / source, REPO / destination) for source, destination in entries]
    for source in [Path('/usr/local/lib/omarchy-files'), Path('/usr/bin/Hyprland'), Path('/usr/bin/qs')]:
        if source.exists():
            result.append((source, REPO / 'installed/system' / str(source).lstrip('/')))
    return result

def main():
    provenance = REPO / 'provenance'
    provenance.mkdir(exist_ok=True)
    archive_dir = provenance / 'upstream-git'
    archive_dir.mkdir(exist_ok=True)
    inventory = provenance / 'snapshot.jsonl'
    counts = collections.Counter()
    byte_count = 0
    mappings = []
    omitted = []
    missing = []
    with inventory.open('x') as manifest:
        def record(row):
            manifest.write(json.dumps(row, sort_keys=True) + '\n')

        def capture(source, destination):
            nonlocal byte_count
            before = source.lstat()
            row = {'source': str(source), 'path': str(destination.relative_to(REPO)),
                   'mode': stat.S_IMODE(before.st_mode), 'uid': before.st_uid,
                   'gid': before.st_gid, 'mtime_ns': before.st_mtime_ns}
            if source.name == '.git':
                archive = archive_dir / (hashlib.sha256(str(source).encode()).hexdigest()[:20] + '.tar.gz')
                with tarfile.open(archive, 'x:gz', dereference=False) as tar:
                    tar.add(source, arcname='.git', recursive=True)
                row.update(kind='upstream-git-archive', archive=str(archive.relative_to(REPO)), sha256=digest(archive))
                counts['upstreamGitArchives'] += 1
                record(row)
                return
            if stat.S_ISLNK(before.st_mode):
                destination.parent.mkdir(parents=True, exist_ok=True)
                target = os.readlink(source)
                destination.symlink_to(target)
                row.update(kind='symlink', target=target)
                counts['symlinks'] += 1
            elif stat.S_ISDIR(before.st_mode):
                destination.mkdir(parents=True, exist_ok=False)
                for child in sorted(source.iterdir()):
                    capture(child, destination / child.name)
                shutil.copystat(source, destination, follow_symlinks=False)
                row.update(kind='directory')
                counts['directories'] += 1
            elif stat.S_ISREG(before.st_mode):
                destination.parent.mkdir(parents=True, exist_ok=True)
                with source.open('rb') as original, destination.open('xb') as copy:
                    try:
                        fcntl.ioctl(copy.fileno(), FICLONE, original.fileno())
                    except OSError:
                        shutil.copyfileobj(original, copy, 1024 * 1024)
                shutil.copystat(source, destination, follow_symlinks=False)
                copied_hash = digest(destination)
                assert digest(source) == copied_hash, f'Changed source: {source}'
                row.update(kind='file', size=before.st_size, sha256=copied_hash)
                byte_count += before.st_size
                counts['files'] += 1
            else:
                row.update(kind='special-file-not-copied', reason='Git stores regular files and symlinks; runtime sockets/devices/FIFOs are not source artifacts.')
                omitted.append(row)
                counts['specialFilesRecordedOnly'] += 1
            assert signature(before) == signature(source.lstat()), f'Changed during capture: {source}'
            record(row)

        for source, destination in plan():
            if not source.exists() and not source.is_symlink():
                missing.append(str(source))
                continue
            mappings.append({'source': str(source), 'destination': str(destination.relative_to(REPO))})
            print(json.dumps({'capturing': str(source)}), flush=True)
            capture(source, destination)
        manifest.flush()
        os.fsync(manifest.fileno())
    assert not missing, f'Missing requested roots: {missing}'
    summary = {'capturedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'mappings': mappings, 'counts': dict(counts), 'regularFileBytes': byte_count,
               'manifestSHA256': digest(inventory), 'allCopiedFileHashesMatchSource': True,
               'sourceFilesModified': False, 'specialFiles': omitted,
               'absolutePathsPreserved': True, 'deploymentPerformed': False,
               'fullWindowsParityAccepted': False}
    with (provenance / 'snapshot-summary.json').open('x') as handle:
        json.dump(summary, handle, indent=2)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    print(json.dumps({'result': 'captured', 'counts': dict(counts), 'bytes': byte_count}), flush=True)

if __name__ == '__main__':
    main()
