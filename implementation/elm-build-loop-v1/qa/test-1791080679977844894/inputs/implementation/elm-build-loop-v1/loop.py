#!/usr/bin/env python3
"""Durable checkpoints and serialized QA launches; host goals drive AI turns.

Journal entries describe progress, never accepted requirements. Failed evidence
may be referenced. This is append-only by convention, not a tamper-proof store.
The native lock covers adopters of this coordinator. A conservative /proc check
also refuses visible existing protected QA scopes, including CPU-only scopes;
uncoordinated launches after that check cannot be ruled out by this lock.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import uuid

PROTECTED_LAUNCHER = Path('/home/hoskinson/window-integration-qa/qa_run.py')
EVENTS = Path('docs/elm-roadmap/delivery/build-loop-events')
STATUSES = frozenset({'active', 'progress', 'blocked'})


class BusyError(RuntimeError):
    pass


def repository(repo: Path) -> Path:
    resolved = Path(repo).resolve(strict=True)
    if not resolved.is_dir():
        raise ValueError('Repository must be a directory')
    return resolved


def contained(repo: Path, candidate: Path, *, exists: bool = True) -> Path:
    """Reject traversal and every symlink component, not just the final file."""
    root = repository(repo)
    path = Path(candidate)
    if not path.is_absolute():
        path = root / path
    if '..' in path.parts:
        raise ValueError('Parent traversal is forbidden')
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise ValueError('Path must reside in the repository') from error
    current = root
    for component in relative.parts:
        current /= component
        if current.is_symlink():
            raise ValueError('Symlink paths are forbidden')
    resolved = path.resolve(strict=exists)
    if not resolved.is_relative_to(root):
        raise ValueError('Path escapes repository')
    return resolved


def validate_runner(repo: Path, runner: Path) -> Path:
    path = Path(runner)
    if not path.is_absolute():
        raise ValueError('Native runner must be an absolute path')
    path = contained(repo, path)
    if path.suffix != '.py' or not path.is_file():
        raise ValueError('Native runner must be a regular Python source file')
    return path


def text_field(value: str, name: str, limit: int = 4096) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f'Invalid {name}')
    return value


def write_checkpoint(repo: Path, thread: str, current_slice: str,
                     next_work: list[str], status: str,
                     evidence=()) -> Path:
    root = repository(repo)
    if not isinstance(thread, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', thread):
        raise ValueError('Invalid thread identifier')
    if status not in STATUSES:
        raise ValueError('Checkpoint status cannot certify completion')
    text_field(current_slice, 'slice', 512)
    if Path(current_slice).is_absolute():
        raise ValueError('Slice must be repository-relative')
    slice_path = contained(root, Path(current_slice))
    if not slice_path.is_dir():
        raise ValueError('Slice must be an existing source directory')
    if not isinstance(next_work, list) or len(next_work) > 100:
        raise ValueError('Invalid next work')
    next_work = [text_field(item, 'next work') for item in next_work]
    if not isinstance(evidence, (list, tuple)) or len(evidence) > 100:
        raise ValueError('Invalid evidence list')
    references = []
    for item in evidence:
        text_field(item, 'evidence path', 1024)
        if Path(item).is_absolute():
            raise ValueError('Evidence must be repository-relative')
        path = contained(root, Path(item))
        if not path.is_file():
            raise ValueError('Evidence must be a regular file')
        references.append({'path': str(path.relative_to(root)),
                           'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                           'size': path.stat().st_size})
    directory = contained(root, EVENTS, exists=False)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    # Recheck after creation. These directories are user-controlled, not an
    # authorization boundary against another process running as the same user.
    contained(root, directory)
    now = datetime.now(timezone.utc)
    event_id = uuid.uuid4().hex
    name = now.strftime('%Y%m%dT%H%M%S.%fZ') + '--' + thread + '--' + event_id + '.json'
    event = {'schema': 1, 'eventId': event_id, 'thread': thread,
             'observedUTC': now.isoformat(), 'status': status,
             'currentSlice': str(slice_path.relative_to(root)),
             'nextWork': next_work, 'evidence': references,
             'acceptance': 'No requirement or cycle completion is asserted.'}
    payload = (json.dumps(event, indent=2, ensure_ascii=True) + '\n').encode()
    temporary = directory / ('.pending-' + event_id)
    destination = directory / name
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o444)
        # Atomic, exclusive publication: status never sees half a JSON event.
        os.link(temporary, destination, follow_symlinks=False)
        directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def lock_path(repo: Path, state_root: Path | None = None) -> Path:
    root = Path(state_root) if state_root is not None else Path.home() / '.local/state/elm-build-loop'
    # A user-owned directory and regular lock prevent symlink lock substitution.
    current = root.absolute()
    for ancestor in [*reversed(current.parents), current]:
        if ancestor.is_symlink():
            raise ValueError('Symlink state directory is forbidden')
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = root.stat()
    if info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError('State directory must be private and owned by this user')
    key = hashlib.sha256(str(repository(repo)).encode()).hexdigest()
    return root / (key + '.native.lock')


@contextmanager
def native_lock(repo: Path, state_root: Path | None = None):
    path = lock_path(repo, state_root)
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError('Unsafe native lock file')
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise BusyError('Another coordinated native campaign is running') from error
        yield path
    finally:
        os.close(descriptor)


def find_qa_conflicts() -> list[dict]:
    conflicts = []
    for directory in Path('/proc').iterdir():
        if not directory.name.isdigit() or int(directory.name) == os.getpid():
            continue
        try:
            if directory.stat().st_uid != os.getuid():
                continue
            arguments = (directory / 'cmdline').read_bytes().split(b'\0')
            protected = any(argument.endswith(b'/qa_run.py') or argument == b'qa_run.py'
                            for argument in arguments)
            cgroup = (directory / 'cgroup').read_text()
            if protected or 'qa-harness-' in cgroup or 'qa-harness.slice' in cgroup:
                conflicts.append({'pid': int(directory.name),
                                  'reason': 'protected QA launcher' if protected else 'protected QA scope'})
        except (FileNotFoundError, ProcessLookupError):
            continue
        except PermissionError as error:
            raise BusyError('Cannot establish whether an existing QA process is safe') from error
    return conflicts


def run_native(repo: Path, runner: Path, arguments=(), state_root: Path | None = None,
               conflict_probe=None, launch=None) -> int:
    path = validate_runner(repo, runner)
    if not all(isinstance(argument, str) for argument in arguments):
        raise ValueError('Invalid runner arguments')
    probe = find_qa_conflicts if conflict_probe is None else conflict_probe
    invoke = subprocess.run if launch is None else launch
    with native_lock(repo, state_root):
        conflicts = probe()
        if conflicts:
            raise BusyError('Existing protected QA processes: ' + ', '.join(str(item['pid']) for item in conflicts))
        # Check again after acquiring the lock; no source path can be swapped to
        # a symlink between the preliminary check and this metadata check.
        path = validate_runner(repo, path)
        env = dict(os.environ)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        command = ['/usr/bin/python3', '-B', str(PROTECTED_LAUNCHER), '--',
                   '/usr/bin/python3', '-B', str(path), *arguments]
        return invoke(command, env=env).returncode


def coordinator_status(repo: Path, state_root: Path | None = None,
                       thread: str | None = None) -> dict:
    root = repository(repo)
    result = {'repository': str(root), 'continuation': 'Host goal mechanism supplies automatic AI turns.',
              'completionAuthority': 'Acceptance review and host goal state; never this checkpoint CLI.',
              'nativeSerialization': 'Nonblocking coordinator lock plus conservative visible QA process check; unadopted races remain possible.'}
    for key, relative in [('backlog', 'docs/elm-roadmap/delivery/sprint-backlog.json'),
                          ('primaryLoopState', 'docs/elm-roadmap/delivery/loop-state.json')]:
        path = contained(root, Path(relative), exists=False)
        if path.exists():
            result[key] = json.loads(path.read_text())
        else:
            result[key] = None
    roadmap = contained(root, Path('docs/elm-roadmap/SPRINTS.md'), exists=False)
    result['roadmap'] = {'path': str(roadmap.relative_to(root)), 'exists': roadmap.is_file()}
    if roadmap.is_file():
        result['roadmap']['sha256'] = hashlib.sha256(roadmap.read_bytes()).hexdigest()
    events = contained(root, EVENTS, exists=False)
    checkpoints = []
    if events.exists():
        for path in sorted(events.glob('*.json')):
            contained(root, path)
            value = json.loads(path.read_text())
            if thread is None or value.get('thread') == thread:
                checkpoints.append(value)
    result['checkpoints'] = checkpoints
    result['latestCheckpoint'] = checkpoints[-1] if checkpoints else None
    path = lock_path(root, state_root)
    result['nativeLock'] = {'path': str(path), 'busy': False}
    try:
        with native_lock(root, state_root):
            pass
    except BusyError:
        result['nativeLock']['busy'] = True
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    commands = parser.add_subparsers(dest='command', required=True)
    status_parser = commands.add_parser('status')
    status_parser.add_argument('--thread')
    checkpoint = commands.add_parser('checkpoint')
    checkpoint.add_argument('--thread', required=True)
    checkpoint.add_argument('--slice', '--current-slice', dest='current_slice', required=True)
    checkpoint.add_argument('--next', '--next-work', dest='next_work', action='append', default=[])
    checkpoint.add_argument('--status', choices=sorted(STATUSES), default='progress')
    checkpoint.add_argument('--evidence', action='append', default=[])
    native = commands.add_parser('native')
    native.add_argument('--runner', type=Path, required=True)
    native.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    try:
        if args.command == 'status':
            print(json.dumps(coordinator_status(args.repo, thread=args.thread), indent=2))
        elif args.command == 'checkpoint':
            path = write_checkpoint(args.repo, args.thread, args.current_slice,
                                    args.next_work, args.status, args.evidence)
            print(path)
        else:
            arguments = args.arguments[1:] if args.arguments[:1] == ['--'] else args.arguments
            code = run_native(args.repo, args.runner, arguments)
            return 128 - code if code < 0 else code
    except BusyError as error:
        print(str(error), file=sys.stderr)
        return 75
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
