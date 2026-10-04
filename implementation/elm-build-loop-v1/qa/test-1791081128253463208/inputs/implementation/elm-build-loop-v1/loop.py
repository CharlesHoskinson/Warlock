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
import signal
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
    repository(repo)
    return root / 'global.native.lock'


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
        yield descriptor
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


def supervise_native(command, *, env, pass_fds) -> subprocess.CompletedProcess:
    """Hold the coordinator alive, forwarding cancellation until child exit.

    The descriptor also enters the protected launcher. Scope/exec programs may
    close inherited descriptors; our supervising process holds it throughout
    normal cancellation. SIGKILL or unadopted launch races remain outside that
    guarantee, so the conservative process check is still required.
    """
    child = subprocess.Popen(command, env=env, pass_fds=pass_fds, start_new_session=True)
    previous = {}
    cancelled_by = None
    def forward(signum, _frame=None):
        nonlocal cancelled_by
        if cancelled_by is None:
            cancelled_by = signum
        try:
            os.killpg(child.pid, signum)
        except ProcessLookupError:
            pass
    try:
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous[signum] = signal.signal(signum, forward)
        while True:
            try:
                code = child.wait()
                break
            except KeyboardInterrupt:
                forward(signal.SIGINT)
        # A child may clean up gracefully and exit zero after cancellation.
        # Preserve the cancellation outcome instead of reporting QA success.
        if code == 0 and cancelled_by is not None:
            code = -cancelled_by
        return subprocess.CompletedProcess(command, code)
    finally:
        # Unexpected supervision errors must not let a still-running launcher
        # escape our lock. Cancellation signals do not use this error branch.
        if child.poll() is None:
            forward(signal.SIGTERM)
            child.wait()
        for signum, handler in previous.items():
            signal.signal(signum, handler)


def run_native(repo: Path, runner: Path, arguments=(), state_root: Path | None = None,
               conflict_probe=None, launch=None) -> int:
    path = validate_runner(repo, runner)
    if not all(isinstance(argument, str) for argument in arguments):
        raise ValueError('Invalid runner arguments')
    probe = find_qa_conflicts if conflict_probe is None else conflict_probe
    invoke = supervise_native if launch is None else launch
    with native_lock(repo, state_root) as descriptor:
        conflicts = probe()
        if conflicts:
            raise BusyError('Existing protected QA processes: ' + ', '.join(str(item['pid']) for item in conflicts))
        # Revalidate after taking the lock. This is not an authorization boundary
        # against another process changing source files as the same desktop user.
        path = validate_runner(repo, path)
        env = dict(os.environ)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        command = ['/usr/bin/python3', '-B', str(PROTECTED_LAUNCHER), '--',
                   '/usr/bin/python3', '-B', str(path), *arguments]
        return invoke(command, env=env, pass_fds=(descriptor,)).returncode


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
    configuration = contained(root, Path('implementation/elm-build-loop-v1/config.json'), exists=False)
    result['baselineVerification'] = None
    if configuration.is_file():
        config = json.loads(configuration.read_text())
        requirements_path = contained(root, Path(config['requirements']))
        requirements_bytes = requirements_path.read_bytes()
        digest = hashlib.sha256(requirements_bytes).hexdigest()
        requirements = json.loads(requirements_bytes)['requirements']
        count = len(requirements)
        scenarios = sum(len(item['scenarios']) for item in requirements)
        if (digest != config['baselineRequirementsSHA256']
                or count != config['baselineRequirementCount']
                or scenarios != config['baselineScenarioCount']
                or len({item['id'] for item in requirements}) != count
                or result['backlog']['requirementsSHA256'] != digest):
            raise ValueError('Baseline requirements hash or counts do not match the frozen backlog')
        contract_path = contained(root, Path(config['rightClickContract']))
        contract = contract_path.read_text()
        rc_requirements = re.findall(r'^### Requirement: (ELM-RC-\d+)\b', contract, re.MULTILINE)
        rc_scenarios = re.findall(r'^#### Scenario: (ELM-RC-\d+ [^\n]+)', contract, re.MULTILINE)
        validation_path = contained(root, Path(config['rightClickValidation']))
        validation = json.loads(validation_path.read_text())
        if (len(rc_requirements) != config['rightClickRequirementCount']
                or len(set(rc_requirements)) != len(rc_requirements)
                or len(rc_scenarios) != config['rightClickScenarioCount']
                or len(set(rc_scenarios)) != len(rc_scenarios)
                or validation['requirements'] != len(rc_requirements)
                or validation['acceptanceScenarios'] != len(rc_scenarios)
                or validation['baselineLedgerModified'] is not False):
            raise ValueError('Right-click amendment counts do not match its separate planning evidence')
        result['baselineVerification'] = {'sha256': digest, 'requirements': count,
                                          'scenarios': scenarios, 'verified': True}
        result['rightClickAmendment'] = {'requirements': len(rc_requirements),
                                        'scenarios': len(rc_scenarios),
                                        'separateFromBaseline': True,
                                        'implementationAcceptanceAsserted': False}
    events = contained(root, EVENTS, exists=False)
    checkpoints = []
    latest_per_thread = {}
    if events.exists():
        for path in sorted(events.glob('*.json')):
            contained(root, path)
            value = json.loads(path.read_text())
            latest_per_thread[value['thread']] = value
            if thread is None or value.get('thread') == thread:
                checkpoints.append(value)
    result['checkpoints'] = checkpoints
    result['latestCheckpoint'] = checkpoints[-1] if checkpoints else None
    result['latestPerThread'] = latest_per_thread
    path = lock_path(root, state_root)
    result['nativeLock'] = {'path': str(path), 'busy': False,
                            'repositoryKey': hashlib.sha256(str(root).encode()).hexdigest()}
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
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
