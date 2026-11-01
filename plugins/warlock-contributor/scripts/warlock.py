#!/usr/bin/env python3
"""Offline contribution checks and explicit plugin regressions; no GUI acceptance/builds."""
import argparse
import base64
import fcntl
import os
import datetime as dt
import hashlib
import importlib.util
import json
import pathlib
import re
import shutil
import shlex
import secrets
import stat
import subprocess
import sys

BASE = 'docs/elm-roadmap/requirements.json'
STATE = 'docs/warlock-build-loop/v2/STATE.json'
LEDGER = 'docs/warlock-build-loop/v2/requirement-ledger.json'
TASKS = 'openspec/changes/elm-desktop-pivot/tasks.md'
TRACEABILITY = 'docs/elm-roadmap/TRACEABILITY.md'
EXPECTED = 'a0c2093cc7769e05b70cc81aa3c001dbcbffe936cc17d1c494d7ab2fdc8b3b1b'
LANGUAGE_BASELINE = 'docs/elm-roadmap/baselines/requirements-pre-language-20261030.json'
LANGUAGE_REVISION = 'docs/elm-roadmap/language-revision.json'
LANGUAGE_HELPER = 'docs/elm-roadmap/tools/language_revision.py'
APPROVED_LANGUAGE_REVISION = 'd405ed8b8fd7e47420f108ed5692970734e341913a029a894b971397849b216c'
APPROVED_LANGUAGE_HELPER = 'a792ed03d3bc7eeed978b387ee5dda8474af0738844c29caaa39cafe1d5c7e4a'
BOUNDARY = 'Structural compliance only; physical presentation, native input, AT/IME, scenario and release acceptance require external evidence and independent review.'
AUTHORED_JAVASCRIPT = frozenset('assets/' + name for name in (
    'adapter.js', 'activation.js', 'bar-adapter.js', 'context.js',
    'controlled-popup-adapter.js', 'native-preview-proposals.js',
    'native-preview-control-outbox.js', 'popup-adapter.js',
    'retained-preview-controls.js', 'recovered-native-preview-control-outbox.js'))


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def safe(root, name):
    p = pathlib.Path(name)
    if p.is_absolute() or '..' in p.parts or not p.parts:
        raise ValueError('Expected safe repository-relative path: ' + str(name))
    result = root / p
    cursor = root
    for part in p.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError('Symlink path is not allowed: ' + str(name))
    if not result.resolve().is_relative_to(root.resolve()):
        raise ValueError('Path escapes repository: ' + str(name))
    return result


def open_parent(path, create=False):
    """Pin directory components without following concurrent symlink swaps."""
    absolute = pathlib.Path(path).absolute()
    if '..' in absolute.parts or not absolute.name:
        raise ValueError('Unsafe filesystem path')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        for component in absolute.parts[1:-1]:
            if create:
                try:
                    os.mkdir(component, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            following = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
            os.close(fd)
            fd = following
        return fd, absolute.name
    except BaseException:
        os.close(fd)
        raise


def regular_bytes_at(parent, name):
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK, dir_fd=parent)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise ValueError('Expected regular file: ' + name)
        body = stream.read()
        after = os.fstat(stream.fileno())
        signature = lambda st: (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)
        if signature(before) != signature(after):
            raise ValueError('File changed during read: ' + name)
        return body


def regular_bytes(path):
    parent, name = open_parent(path)
    try:
        return regular_bytes_at(parent, name)
    finally:
        os.close(parent)


def digest(path):
    try:
        return hashlib.sha256(regular_bytes(path)).hexdigest()
    except FileNotFoundError:
        return None


def read(path):
    return json.loads(regular_bytes(path))


def json_snapshot(path):
    body = regular_bytes(path)
    return json.loads(body), hashlib.sha256(body).hexdigest()


def git_run(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_TERMINAL_PROMPT='0')
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True, env=env)


def git(root, *args):
    r = git_run(root, *args)
    if r.returncode:
        raise ValueError('Git operation failed: ' + r.stderr.decode(errors='replace').strip())
    return r.stdout


def fingerprint(root, name):
    p = pathlib.Path(name)
    if p.is_absolute() or '..' in p.parts or not p.parts:
        raise ValueError('Unsafe foreign path: ' + name)
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        for index, component in enumerate(p.parts):
            try:
                status = os.stat(component, dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError:
                return None
            if stat.S_ISLNK(status.st_mode):
                return 'symlink:' + hashlib.sha256(os.fsencode(os.readlink(component, dir_fd=fd))).hexdigest()
            if index == len(p.parts) - 1:
                if stat.S_ISDIR(status.st_mode):
                    return 'directory'
                return hashlib.sha256(regular_bytes_at(fd, component)).hexdigest()
            following = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
            os.close(fd)
            fd = following
    finally:
        os.close(fd)


def dirty_names(root):
    names = set(git(root, 'diff', '--no-renames', '--name-only', '-z').decode().split('\0'))
    names.update(git(root, 'diff', '--cached', '--no-renames', '--name-only', '-z').decode().split('\0'))
    names.update(git(root, 'ls-files', '--others', '--exclude-standard', '-z', '--', 'implementation/warlock', 'plugins/warlock-contributor', '.warlock-contributor').decode().split('\0'))
    return sorted(n for n in names if n)


def dirty(root):
    return {n: fingerprint(root, n) for n in dirty_names(root)}


def write_record(path, value, exclusive=False, parent_fd=None, expected_sha=None):
    """Replace inside a held directory; never re-resolve a pathname at commit."""
    value = {k: v for k, v in value.items() if k != '_recordPath'}
    own_parent = parent_fd is None
    parent, name = open_parent(path) if own_parent else (parent_fd, pathlib.Path(path).name)
    temporary = '.' + name + '.' + secrets.token_hex(16)
    created = False
    temporary_identity = None
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent)
        created = True
        with os.fdopen(fd, 'w') as stream:
            temporary_status = os.fstat(stream.fileno())
            temporary_identity = (temporary_status.st_dev, temporary_status.st_ino)
            json.dump(value, stream, indent=2)
            stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
        if expected_sha is not None:
            try:
                actual = hashlib.sha256(regular_bytes_at(parent, name)).hexdigest()
            except FileNotFoundError:
                actual = 'absent'
            if actual != expected_sha:
                raise ValueError('Record changed during reconciliation')
        current_temporary = os.stat(temporary, dir_fd=parent, follow_symlinks=False)
        if (not stat.S_ISREG(current_temporary.st_mode)
                or (current_temporary.st_dev, current_temporary.st_ino) != temporary_identity):
            raise ValueError('Temporary record entry changed before replacement')
        if exclusive or expected_sha == 'absent':
            os.link(temporary, name, src_dir_fd=parent, dst_dir_fd=parent, follow_symlinks=False)
        else:
            os.replace(temporary, name, src_dir_fd=parent, dst_dir_fd=parent)
        os.fsync(parent)
    finally:
        if created:
            try:
                status = os.stat(temporary, dir_fd=parent, follow_symlinks=False)
                if (status.st_dev, status.st_ino) == temporary_identity:
                    os.unlink(temporary, dir_fd=parent)
            except FileNotFoundError:
                pass
        if own_parent:
            os.close(parent)


def json_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def record_identity(record, record_path):
    selected = record.get('slice', {})
    identity = {
        'schema': record.get('schema'),
        'owner': record.get('owner'),
        'recordPath': record_path,
        'slice': {key: selected.get(key) for key in ('id', 'requirements', 'scenarios', 'before', 'after', 'verification')},
        'baseline': record.get('baseline'),
        'startedUTC': record.get('startedUTC'),
        'sourceRevision': record.get('sourceRevision'),
        'sourceHashes': record.get('sourceHashes'),
        'foreignDirty': record.get('foreignDirty'),
        'adoptedDirty': record.get('adoptedDirty'),
    }
    return json_sha256(identity)


def reconciliation_path(root, record):
    # Locate by immutable participant fields; custody is separately pinned and
    # replay-validated in the sidecar, not discarded from its review identity.
    locator_record = dict(record, foreignDirty=None, adoptedDirty=None)
    locator = record_identity(locator_record, record.get('_recordPath', '.warlock-contributor/slice.json'))
    return safe(root, '.warlock-contributor/foreign-reconciliations/' + locator + '.json')


def latest_recorded_source_hash(record, name):
    """Resolve current owner binding, not historical claim/evidence citations."""
    latest = record.get('sourceHashes', {}).get(name)
    iterations = record.get('iterations', [])
    extensions = record.get('pathExtensions', [])
    for index in range(len(iterations) + 1):
        for extension in extensions:
            if extension.get('afterIteration') == index and name in extension.get('sourceHashes', {}):
                latest = extension['sourceHashes'][name]
        if index < len(iterations) and name in iterations[index].get('sourceHashes', {}):
            latest = iterations[index]['sourceHashes'][name]
    return latest


def canonical_source_path(root, name):
    """Return a safe repository-relative POSIX spelling or fail closed."""
    if not isinstance(name, str) or not name or '\\' in name:
        raise ValueError('Owned source path must use a canonical POSIX spelling')
    parsed = pathlib.PurePosixPath(name)
    if (parsed.is_absolute() or parsed.as_posix() != name
            or any(part in ('', '.', '..') for part in parsed.parts)):
        raise ValueError('Owned source path must use a canonical POSIX spelling: ' + name)
    safe(root, name)
    return parsed.as_posix()


def validate_reconciliation_event(root, record, identity, event, previous_events, errors):
    required = ('path', 'fromSha256', 'toSha256', 'sourceRecordSnapshot', 'sourceRecordSnapshotSha256',
                'reviewFile', 'reviewFileSha256', 'reason', 'reviewer', 'sourceOwner', 'atUTC',
                'previousEventSha256', 'eventSha256')
    version = event.get('eventSchema', 1) if isinstance(event, dict) else None
    if isinstance(event, dict) and 'eventSchema' in event and type(version) is not int:
        errors.append('Foreign reconciliation event schema must be an integer')
        return None
    if version == 2:
        required += ('sourceRecordPath', 'ownerCensusSnapshot', 'ownerCensusSnapshotSha256')
    elif version != 1:
        errors.append('Foreign reconciliation event has an unsupported schema')
        return None
    if not isinstance(event, dict) or any(key not in event for key in required):
        errors.append('Foreign reconciliation event has an incomplete schema')
        return None
    content = {key: value for key, value in event.items() if key != 'eventSha256'}
    if event.get('eventSha256') != json_sha256(content):
        errors.append('Foreign reconciliation event hash differs')
    if not isinstance(event.get('reason'), str) or not event['reason'].strip():
        errors.append('Foreign reconciliation event requires a reason')
    try:
        dt.datetime.fromisoformat(event['atUTC'])
    except (ValueError, TypeError):
        errors.append('Foreign reconciliation event timestamp is invalid')
    previous_hash = previous_events[-1].get('eventSha256') if previous_events else None
    if event.get('previousEventSha256') != previous_hash:
        errors.append('Foreign reconciliation event chain is broken')
    name = event.get('path')
    if not isinstance(name, str) or name not in record.get('foreignDirty', {}):
        errors.append('Foreign reconciliation path is invalid')
        return None
    try:
        safe(root, name)
    except ValueError:
        errors.append('Foreign reconciliation path is unsafe: ' + str(name))
        return None
    selected = set(record.get('slice', {}).get('paths', []))
    adopted = set(record.get('adoptedDirty', {}).get('paths', []))
    if name in selected or name in adopted:
        errors.append('Foreign reconciliation cannot change selected or adopted ownership: ' + name)
        return None
    old = event.get('fromSha256')
    if name in record.get('foreignDirty', {}):
        expected = record['foreignDirty'][name]
    else:
        expected = None
    for prior in previous_events:
        if prior.get('path') == name:
            expected = prior.get('toSha256')
    if old != expected:
        errors.append('Foreign reconciliation does not continue the captured hash chain: ' + name)
    new = event.get('toSha256')
    if not isinstance(new, str) or re.fullmatch(r'[0-9a-f]{64}', new) is None:
        errors.append('Foreign reconciliation target must be a regular-file SHA-256: ' + name)
        return None
    if old == new:
        errors.append('Foreign reconciliation event must record a changed source hash: ' + name)

    snapshot_path = event.get('sourceRecordSnapshot')
    review_path = event.get('reviewFile')
    if not isinstance(snapshot_path, str) or not snapshot_path.startswith('.warlock-contributor/evidence/foreign-reconciliation-snapshots/'):
        errors.append('Foreign reconciliation needs a frozen owner-record snapshot')
        return None
    if not isinstance(review_path, str) or not review_path.startswith('.warlock-contributor/evidence/foreign-reconciliations/'):
        errors.append('Foreign reconciliation needs a retained independent review artifact')
        return None
    try:
        snapshot_file = safe(root, snapshot_path)
        review_file = safe(root, review_path)
        snapshot, snapshot_hash = json_snapshot(snapshot_file)
        review, review_hash = json_snapshot(review_file)
    except (OSError, ValueError, json.JSONDecodeError):
        errors.append('Foreign reconciliation evidence cannot be read')
        return None
    if snapshot_hash != event.get('sourceRecordSnapshotSha256') or not isinstance(snapshot, dict):
        errors.append('Foreign reconciliation owner snapshot hash differs')
        return None
    source_record_path = None
    census_path = None
    census_hash = None
    if version == 2:
        try:
            if canonical_source_path(root, name) != name:
                raise ValueError('Reconciled path is not canonical')
        except ValueError as exc:
            errors.append('Foreign reconciliation path is not canonical: ' + str(exc))
            return None
        source_record_path = event.get('sourceRecordPath')
        census_path = event.get('ownerCensusSnapshot')
        census_hash = event.get('ownerCensusSnapshotSha256')
        try:
            census, actual_census_hash, census_records = decode_owner_census(root, census_path)
            snapshot_raw = regular_bytes(snapshot_file)
            if actual_census_hash != census_hash:
                raise ValueError('Owner census snapshot hash differs')
            if source_record_path not in census_records:
                raise ValueError('Source record path is not in the frozen participant index')
            source_raw, census_record = census_records[source_record_path]
            if source_raw != snapshot_raw or census_record != snapshot:
                raise ValueError('Source record snapshot does not match the exact indexed record bytes')
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            errors.append('Foreign reconciliation source owner is not bound to the exact indexed record: ' + str(exc))
            return None
    source_owner = snapshot.get('owner')
    source_paths = set(snapshot.get('slice', {}).get('paths', []))
    source_paths.update(snapshot.get('adoptedDirty', {}).get('paths', []))
    if name not in source_paths or name in snapshot.get('foreignDirty', {}):
        errors.append('Frozen owner record does not own the reconciled path: ' + name)
    if event.get('sourceOwner') != source_owner or not source_owner:
        errors.append('Foreign reconciliation source owner differs from its frozen record')
    if new != latest_recorded_source_hash(snapshot, name):
        errors.append('Frozen owner record current binding does not pin the reconciled source hash: ' + name)
    if version == 2:
        if (not isinstance(source_owner, str) or not source_owner.strip()
                or source_owner.strip().casefold() == str(record.get('owner', '')).strip().casefold()):
            errors.append('Foreign source owner must differ from the target participant owner')
        census_claimants = []
        for candidate_path, (_, candidate_record) in census_records.items():
            selected_paths = candidate_record.get('slice', {}).get('paths', [])
            adopted_paths = candidate_record.get('adoptedDirty', {}).get('paths', [])
            foreign_paths = candidate_record.get('foreignDirty', {})
            if (not isinstance(selected_paths, list) or not isinstance(adopted_paths, list)
                    or not isinstance(foreign_paths, dict)):
                errors.append('Owner census participant has invalid path ownership fields')
                continue
            try:
                selected_canonical = {canonical_source_path(root, item) for item in selected_paths}
                adopted_canonical = {canonical_source_path(root, item) for item in adopted_paths}
                foreign_canonical = {canonical_source_path(root, item) for item in foreign_paths}
            except ValueError as exc:
                errors.append('Owner census contains a noncanonical source path: ' + str(exc))
                continue
            if (name in selected_canonical | adopted_canonical) and name not in foreign_canonical:
                census_claimants.append((candidate_path, latest_recorded_source_hash(candidate_record, name)))
        if (len(census_claimants) != 1 or census_claimants[0][0] != source_record_path
                or census_claimants[0][1] != new):
            errors.append('Owner census does not establish one unique current owner with the exact source hash')
    if review_hash != event.get('reviewFileSha256') or not isinstance(review, dict):
        errors.append('Foreign reconciliation review artifact hash differs')
        return None
    reviewer = review.get('reviewer')
    expected_review = {
        'schema': 1,
        'scope': 'foreign-provenance-only',
        'scenarioAcceptance': False,
        'recordIdentitySha256': identity,
        'recordPath': record.get('_recordPath', '.warlock-contributor/slice.json'),
        'path': name,
        'previousSha256': old,
        'currentSha256': new,
        'sourceRecordSnapshot': snapshot_path,
        'sourceRecordSnapshotSha256': snapshot_hash,
        'sourceOwner': source_owner,
        'reason': event.get('reason'),
    }
    if version == 2:
        expected_review.update(sourceRecordPath=source_record_path,
                               ownerCensusSnapshot=census_path,
                               ownerCensusSnapshotSha256=census_hash)
    if any(review.get(key) != value for key, value in expected_review.items()):
        errors.append('Independent review does not cover this exact foreign-path transition')
    if not isinstance(reviewer, str) or not reviewer.strip() or review.get('independent') is not True:
        errors.append('Foreign reconciliation requires an explicitly independent reviewer')
        return None
    if reviewer.strip().casefold() in {str(record.get('owner', '')).strip().casefold(), str(source_owner).strip().casefold()}:
        errors.append('Foreign reconciliation reviewer must differ from target and source owners')
    if event.get('reviewer') != reviewer:
        errors.append('Foreign reconciliation reviewer differs from retained review')
    return new


def empty_reconciliation(record):
    return {'schema': 1,
            'recordIdentitySha256': record_identity(record, record.get('_recordPath', '.warlock-contributor/slice.json')),
            'events': [], 'custodyBaseline': {
                'foreignDirty': record.get('foreignDirty', {}),
                'adoptedDirty': record.get('adoptedDirty', {}),
                'pathExtensions': record.get('pathExtensions', []),
                'ownershipAdoptions': record.get('ownershipAdoptions', []),
                'selectedPaths': record.get('slice', {}).get('paths', [])}}


def foreign_reconciliations(root, record, override=None, check_current=True):
    errors = []
    identity = record_identity(record, record.get('_recordPath', '.warlock-contributor/slice.json'))
    path = reconciliation_path(root, record)
    data = override
    if data is None:
        if not path.exists():
            data = empty_reconciliation(record)
        else:
            try:
                data = read(path)
            except (OSError, json.JSONDecodeError):
                return {}, ['Foreign reconciliation sidecar is unreadable: ' + str(path)], None
    if not isinstance(data, dict) or data.get('schema') != 1 or not isinstance(data.get('events'), list):
        return {}, ['Foreign reconciliation sidecar has invalid schema'], None
    baseline = data.get('custodyBaseline')
    if (not isinstance(baseline, dict) or not isinstance(baseline.get('foreignDirty'), dict)
            or not isinstance(baseline.get('adoptedDirty'), dict)
            or not isinstance(baseline.get('pathExtensions'), list)
            or not isinstance(baseline.get('selectedPaths'), list)
            or not isinstance(baseline.get('ownershipAdoptions'), list)):
        return {}, ['Foreign reconciliation custody baseline is invalid'], None
    original_record = dict(record, foreignDirty=baseline['foreignDirty'], adoptedDirty=baseline['adoptedDirty'],
                           slice=dict(record.get('slice', {}), paths=baseline['selectedPaths']))
    identity = record_identity(original_record, record.get('_recordPath', '.warlock-contributor/slice.json'))
    if data.get('recordIdentitySha256') != identity:
        return {}, ['Foreign reconciliation sidecar does not match the immutable participant record identity'], None
    prefix = baseline['pathExtensions']
    extensions = record.get('pathExtensions', [])
    if extensions[:len(prefix)] != prefix:
        return {}, ['Foreign reconciliation custody extension history changed'], None
    expected_foreign = dict(baseline['foreignDirty'])
    expected_selected = set(baseline['selectedPaths'])
    for extension in extensions[len(prefix):]:
        expected_selected.update(extension.get('sourceHashes', {}))
        for name in extension.get('adoptedDirty', {}).get('paths', []):
            expected_foreign.pop(name, None)
    ownership_prefix = baseline['ownershipAdoptions']
    ownership = record.get('ownershipAdoptions', [])
    if ownership[:len(ownership_prefix)] != ownership_prefix:
        return {}, ['Foreign reconciliation custody adoption history changed'], None
    expected_adopted = baseline['adoptedDirty']
    for event in ownership[len(ownership_prefix):]:
        if event.get('adoptedDirtyBefore') != expected_adopted:
            return {}, ['Foreign reconciliation custody adoption chain differs'], None
        expected_adopted = event.get('adoptedDirtyAfter')
        for name in event.get('paths', []):
            expected_foreign.pop(name, None)
    if (record.get('foreignDirty') != expected_foreign or record.get('adoptedDirty', {}) != expected_adopted
            or set(record.get('slice', {}).get('paths', [])) != expected_selected):
        return {}, ['Foreign reconciliation custody differs without an authorized extension'], None
    result = {}
    prior = []
    saw_schema2 = False
    for event in data['events']:
        version = event.get('eventSchema', 1) if isinstance(event, dict) else None
        if saw_schema2 and version != 2:
            errors.append('Foreign reconciliation event schema cannot downgrade after schema 2')
        if version == 2 and type(version) is int:
            saw_schema2 = True
        value = validate_reconciliation_event(root, original_record, identity, event, prior, errors)
        if value is not None:
            result[event['path']] = value
        prior.append(event)
    if check_current:
        for name, expected in result.items():
            if name in record.get('foreignDirty', {}) and fingerprint(root, name) != expected:
                errors.append('Reconciled foreign path changed: ' + name)
    return result, errors, data


def reconcile_foreign(root, record, reqs, state, args):
    sidecar = reconciliation_path(root, record)
    parent, leaf = open_parent(sidecar, create=True)
    try:
        try:
            body = regular_bytes_at(parent, leaf)
            data, before_sha = json.loads(body), hashlib.sha256(body).hexdigest()
        except FileNotFoundError:
            data, before_sha = empty_reconciliation(record), 'absent'
        return reconcile_foreign_at(root, record, reqs, state, args, parent, data, before_sha)
    finally:
        os.close(parent)


def reconcile_foreign_at(root, record, reqs, state, args, parent_fd, prior_data, before_sha):
    """Append an atomic, independently reviewed batch; never alter participant custody."""
    if (not args.transition_file.startswith('.warlock-contributor/')
            or git_run(root, 'check-ignore', '-q', '--', args.transition_file).returncode != 0):
        raise ValueError('Transition file must be untracked Git-ignored scratch')
    transitions = read(safe(root, args.transition_file))
    if not isinstance(transitions, list) or not transitions:
        raise ValueError('Transition file must contain a nonempty array')
    names = []
    for item in transitions:
        if not isinstance(item, dict) or set(item) != {
                'path', 'sourceRecordPath', 'ownerCensusSnapshot',
                'sourceRecordSnapshot', 'reviewFile', 'reason'}:
            raise ValueError('Transition needs exact path, sourceRecordPath, ownerCensusSnapshot, sourceRecordSnapshot, reviewFile and reason')
        name = item['path']
        if not isinstance(name, str) or name not in record.get('foreignDirty', {}):
            raise ValueError('Only captured protected foreign paths may be reconciled')
        if name in names or name in record['slice']['paths'] or name in record.get('adoptedDirty', {}).get('paths', []):
            raise ValueError('Duplicate, selected or adopted reconciliation path')
        safe(root, name)
        if not isinstance(item['reason'], str) or not item['reason'].strip():
            raise ValueError('Transition requires a concrete reason')
        names.append(name)
    existing, errors, data = foreign_reconciliations(root, record, override=prior_data, check_current=False)
    if errors:
        raise ValueError('; '.join(errors))
    base_errors, _ = validate(root, record, reqs, state)
    allowed = {prefix + name for name in names for prefix in
               ('Protected foreign-dirty path changed: ', 'Reconciled foreign path changed: ')}
    unrelated = [error for error in base_errors if error not in allowed]
    if unrelated:
        raise ValueError('Reconcile only after unrelated participant-check findings are resolved: ' + '; '.join(unrelated))
    identity = data['recordIdentitySha256']
    candidate = dict(data, events=list(data['events']))
    for item in transitions:
        name = item['path']
        before = existing.get(name, record['foreignDirty'][name])
        after = fingerprint(root, name)
        if after is None or re.fullmatch(r'[0-9a-f]{64}', after) is None:
            raise ValueError('Only an existing regular file with a SHA-256 may be reconciled')
        if before == after:
            raise ValueError('Foreign path matches its captured fingerprint; no reconciliation is needed')
        snapshot_path, review_path = item['sourceRecordSnapshot'], item['reviewFile']
        census_path = item['ownerCensusSnapshot']
        for value, prefix in ((snapshot_path, '.warlock-contributor/evidence/foreign-reconciliation-snapshots/'),
                              (review_path, '.warlock-contributor/evidence/foreign-reconciliations/'),
                              (census_path, '.warlock-contributor/evidence/foreign-owner-censuses/')):
            if not isinstance(value, str) or not value.startswith(prefix):
                raise ValueError('Evidence must be stored under ' + prefix)
            evidence = safe(root, value)
            if fingerprint(root, value) is None or not evidence.is_file() or evidence.is_symlink():
                raise ValueError('Frozen owner-record snapshot and review must be regular files')
            if git_run(root, 'check-ignore', '-q', '--', value).returncode != 0:
                raise ValueError('Reconciliation evidence must remain in ignored scratch')
        snapshot, snapshot_sha = json_snapshot(safe(root, snapshot_path))
        review, review_sha = json_snapshot(safe(root, review_path))
        census, census_sha, census_records = decode_owner_census(root, census_path)
        verify_current_owner_census(root, census)
        source_record_path = item['sourceRecordPath']
        if source_record_path not in census_records:
            raise ValueError('Source record path is not present in the frozen participant index')
        source_raw, _ = census_records[source_record_path]
        if source_raw != regular_bytes(safe(root, snapshot_path)):
            raise ValueError('Source record snapshot differs from the exact indexed record bytes')
        event = dict(eventSchema=2, path=name, fromSha256=before, toSha256=after,
                     sourceRecordSnapshot=snapshot_path, sourceRecordSnapshotSha256=snapshot_sha,
                     sourceRecordPath=source_record_path,
                     ownerCensusSnapshot=census_path, ownerCensusSnapshotSha256=census_sha,
                     reviewFile=review_path, reviewFileSha256=review_sha,
                     reason=item['reason'], reviewer=review.get('reviewer') if isinstance(review, dict) else None,
                     sourceOwner=snapshot.get('owner') if isinstance(snapshot, dict) else None,
                     atUTC=now(), previousEventSha256=candidate['events'][-1]['eventSha256'] if candidate['events'] else None)
        event['eventSha256'] = json_sha256(event)
        candidate['events'].append(event)
    reconciled, errors, _ = foreign_reconciliations(root, record, override=candidate)
    if errors or any(reconciled.get(name) != fingerprint(root, name) for name in names):
        raise ValueError('Provenance evidence is insufficient: ' + '; '.join(errors))
    path = reconciliation_path(root, record)
    if git_run(root, 'check-ignore', '-q', '--', str(path.relative_to(root))).returncode != 0:
        raise ValueError('Reconciliation sidecar must remain in ignored scratch')
    write_record(path, candidate, parent_fd=parent_fd, expected_sha=before_sha)
    return dict(record=record.get('_recordPath'), recordIdentitySha256=identity,
                sidecar=str(path.relative_to(root)), sidecarSha256=hashlib.sha256(regular_bytes_at(parent_fd, path.name)).hexdigest(), paths=names,
                foreignOwnershipRetained=True, scenarioAcceptanceInferred=False)


def discover_repo():
    for parent in (pathlib.Path.cwd(), *pathlib.Path.cwd().parents):
        if (parent / BASE).is_file() and (parent / STATE).is_file():
            return str(parent)
    return str(pathlib.Path(__file__).resolve().parents[3])


def requirement_document(root):
    """Retain the frozen original or reproduce its exact governed revision."""
    path = safe(root, BASE)
    data = read(path)
    if digest(path) == EXPECTED:
        return data
    try:
        baseline = safe(root, LANGUAGE_BASELINE)
        revision = safe(root, LANGUAGE_REVISION)
        if digest(baseline) != EXPECTED or digest(revision) != APPROVED_LANGUAGE_REVISION:
            raise ValueError('Unapproved original or language revision')
        helper = safe(root, LANGUAGE_HELPER)
        if digest(helper) != APPROVED_LANGUAGE_HELPER:
            raise ValueError('Unapproved language revision helper')
        spec = importlib.util.spec_from_file_location('warlock_governed_language_revision', helper)
        if spec is None or spec.loader is None:
            raise ValueError('Language revision helper is unavailable')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        approved = module.apply_language_revision(read(baseline), revision.parent)
        if data != approved:
            raise ValueError('Requirement document differs from approved language revision')
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ImportError) as exc:
        raise ValueError('Frozen original 242/417 baseline changed: ' + str(exc)) from exc
    return data


def validate_registry_admission(root, requirements):
    """Check the live assignment bijections without mutating admission state.

    This verifies explicit role labels and mappings, not a reviewer's identity
    or any implementation/native acceptance. Frozen-source guards still apply.
    """
    def fail(message):
        raise ValueError('Registry admission: ' + message)

    def text(row, key, identity):
        value = row.get(key)
        if not isinstance(value, str) or not value.strip():
            fail(identity + ' missing nonempty ' + key + ' mapping')
        return value.strip()

    def document(name):
        try:
            return safe(root, name).read_text(encoding='utf-8')
        except (OSError, UnicodeError) as exc:
            fail(name + ' mapping is unavailable: ' + str(exc))

    def bijection(actual, expected, name):
        missing, foreign = sorted(set(expected) - set(actual)), sorted(set(actual) - set(expected))
        if missing or foreign:
            fail(name + ' mapping identities differ; missing=' + repr(missing) + '; foreign=' + repr(foreign))

    registry, task_ids = {}, {}
    if not isinstance(requirements, list) or len(requirements) != 242:
        fail('registry must assign all 242 requirements')
    for row in requirements:
        if not isinstance(row, dict):
            fail('registry row must be an object')
        identity = text(row, 'id', 'registry row')
        if identity in registry:
            fail('duplicate registry requirement mapping: ' + identity)
        owner = text(row, 'accountableOwnerRole', identity)
        verifier = text(row, 'verifierRole', identity)
        if owner.casefold() == verifier.casefold() or not re.search(r'\bindependent\b', verifier, re.IGNORECASE):
            fail(identity + ' needs a distinct independent verifierRole mapping')
        phase = text(row, 'phase', identity)
        task = text(row, 'taskId', identity)
        text(row, 'task', identity)
        if not re.fullmatch(r'P[0-8]', phase) or task != phase + '-' + identity:
            fail(identity + ' phase/taskId mapping differs')
        if task in task_ids:
            fail('duplicate registry task mapping: ' + task)
        scenarios = row.get('scenarios')
        if not isinstance(scenarios, list) or not scenarios:
            fail(identity + ' missing named acceptance scenario mapping')
        names = []
        for scenario in scenarios:
            if not isinstance(scenario, dict):
                fail(identity + ' acceptance scenario must be an object')
            names.append(text(scenario, 'name', identity + ' acceptance scenario'))
        if len(set(names)) != len(names):
            fail(identity + ' duplicate named acceptance scenario mapping')
        registry[identity], task_ids[task] = row, identity

    tasks, phase = {}, None
    for line_number, raw in enumerate(document(TASKS).splitlines(), 1):
        line = raw.strip()
        heading = re.fullmatch(r'##\s+(P[0-8])(?:\s+.*)?', line)
        if heading:
            phase = heading[1]
        if not line.startswith('- ['):
            continue
        item = re.fullmatch(r'-\s+\[[ xX]\]\s+([^:\s]+):\s*(.*?)\s+Verify:\s*(.+)', line)
        if not item:
            fail(TASKS + ':' + str(line_number) + ' malformed task mapping')
        task, description, verification = item.groups()
        if task in tasks:
            fail(TASKS + ' duplicate task mapping: ' + task)
        tasks[task] = (phase, description.strip(), verification.strip())
    bijection(tasks, task_ids, TASKS)
    for task, (phase, description, verification) in tasks.items():
        row = registry[task_ids[task]]
        if phase != row['phase'] or description != row['task'] or verification != row['verification']:
            fail(TASKS + ' phase/task/verification mapping differs: ' + task)

    # Split only unescaped Markdown separators; escaped pipes remain text.
    def cells(line):
        return [value.strip().replace(r'\|', '|') for value in re.split(r'(?<!\\)\|', line.strip())[1:-1]]

    columns = ['Requirement', 'Phase', 'Priority', 'OpenSpec requirement/scenarios',
               'Task', 'Owner / verifier', 'Verification', 'Legacy/new evidence']
    traces, in_table, found_table = {}, False, False
    for line_number, raw in enumerate(document(TRACEABILITY).splitlines(), 1):
        line = raw.strip()
        if not (line.startswith('|') and line.endswith('|')):
            in_table = False
            continue
        values = cells(line)
        if values and values[0] == 'Requirement':
            if values != columns:
                fail(TRACEABILITY + ':' + str(line_number) + ' requirement mapping columns differ')
            in_table, found_table = True, True
            continue
        if not in_table or all(re.fullmatch(r':?-+:?', value) for value in values):
            continue
        if len(values) != len(columns):
            fail(TRACEABILITY + ':' + str(line_number) + ' malformed requirement mapping')
        identity = values[0]
        if identity in traces:
            fail(TRACEABILITY + ' duplicate requirement mapping: ' + identity)
        traces[identity] = dict(zip(columns, values))
    if not found_table:
        fail(TRACEABILITY + ' requirement mapping table is missing')
    bijection(traces, registry, TRACEABILITY)
    for identity, trace in traces.items():
        row = registry[identity]
        roles = re.split(r'\s*/\s*', trace['Owner / verifier'])
        expected_link = '../../openspec/changes/elm-desktop-pivot/specs/' + row['capability'] + '/spec.md#requirement-' + identity.lower()
        scenarios = re.fullmatch(r'\[([0-9]+) scenario\(s\)\]\(([^)]+)\)', trace['OpenSpec requirement/scenarios'])
        if trace['Phase'] != row['phase'] or trace['Task'] != row['taskId']:
            fail(TRACEABILITY + ' phase/task mapping differs: ' + identity)
        if roles != [row['accountableOwnerRole'], row['verifierRole']]:
            fail(TRACEABILITY + ' owner/verifier role mapping differs: ' + identity)
        if not scenarios or int(scenarios[1]) != len(row['scenarios']) or scenarios[2] != expected_link:
            fail(TRACEABILITY + ' named scenario count/capability requirement link mapping differs: ' + identity)
        if trace['Priority'] != row['priority'] or trace['Verification'] != row['verification']:
            fail(TRACEABILITY + ' priority/verification mapping differs: ' + identity)


def context(root):
    data = requirement_document(root)
    reqs = {r['id']: r for r in data['requirements']}
    if len(reqs) != 242 or sum(len(r['scenarios']) for r in reqs.values()) != 417:
        raise ValueError('Frozen original 242/417 baseline changed')
    ledger = read(safe(root, LEDGER))
    if ledger['baseline']['sha256'] != EXPECTED:
        raise ValueError('Ledger baseline hash differs')
    entries = ledger.get('requirements', [])
    if len(entries) != 242 or {r['id'] for r in entries} != set(reqs):
        raise ValueError('Ledger requirement identities differ from original')
    count = 0
    for row in entries:
        scenarios = row.get('scenarios', [])
        original = {x['name']: x['then'] for x in reqs[row['id']]['scenarios']}
        if len(scenarios) != len(original) or {x['name']: x['oracle'] for x in scenarios} != original:
            raise ValueError('Ledger scenario identities/oracles differ: ' + row['id'])
        count += len(scenarios)
    if count != 417:
        raise ValueError('Ledger must preserve all 417 scenarios')
    validate_registry_admission(root, data['requirements'])
    return reqs, read(safe(root, STATE))


def normalize_slice(root, s, reqs):
    s = dict(s)
    for k in ('id', 'before', 'after'):
        if not isinstance(s.get(k), str) or not s[k].strip():
            raise ValueError('Slice needs ' + k)
    ids = s.get('requirements', [])
    if not 1 <= len(ids) <= 3 or len(set(ids)) != len(ids) or any(x not in reqs for x in ids):
        raise ValueError('Slice requires 1–3 exact original requirement IDs')
    names = s.get('scenarios', [])
    available = {x['name'] for i in ids for x in reqs[i]['scenarios']}
    if not names or len(set(names)) != len(names) or not set(names) <= available:
        raise ValueError('Slice needs exact original scenario names under selected requirements')
    if any(not any(x['name'] in names for x in reqs[i]['scenarios']) for i in ids):
        raise ValueError('Each requirement needs a selected original scenario')
    paths = s.get('paths', [])
    if not paths or len(set(paths)) != len(paths):
        raise ValueError('Slice needs unique product source paths')
    normalized = []
    for name in paths:
        safe(root, name)  # Reject absolute/escaping inputs before adding the product prefix.
        name = str(pathlib.Path(name))
        name = name if name.startswith('implementation/warlock/') else 'implementation/warlock/' + name
        p = safe(root, name)
        if not name.startswith('implementation/warlock/') or name.endswith('/') or p.is_dir():
            raise ValueError('Product paths must be files in incremental implementation/warlock')
        normalized.append(name)
    if len(set(normalized)) != len(normalized):
        raise ValueError('Slice paths must be unique after normalization')
    s['paths'] = normalized
    if not isinstance(s.get('verification'), list) or not s['verification'] or any(not isinstance(x, str) or not x.strip() for x in s['verification']):
        raise ValueError('Slice needs proportional decisive verification')
    return s


def slice_originals(s, reqs):
    return [{'requirement': i, 'verification': reqs[i]['verification'],
             'scenarios': [x for x in reqs[i]['scenarios'] if x['name'] in s['scenarios']]}
            for i in s['requirements']]


def load_slice(root, name, reqs):
    """Accept bare slices or unchanged plan packets; never trust copied oracles."""
    selection = read(safe(root, name))
    if not isinstance(selection, dict):
        raise ValueError('Slice file must contain a bare slice or planSchema=1 packet')
    if 'planSchema' in selection:
        if type(selection['planSchema']) is not int or selection['planSchema'] != 1:
            raise ValueError('Unsupported planSchema; expected 1')
        s = normalize_slice(root, selection['slice'], reqs)
        if selection.get('originals') != slice_originals(s, reqs):
            raise ValueError('Saved plan originals differ from the selected frozen scenarios or verification; regenerate the plan')
        return s
    return normalize_slice(root, selection, reqs)


def preflight(root, record_path, slice_file, reqs):
    """Preview a prospective start without adopting drafts or writing records."""
    s = load_slice(root, slice_file, reqs)
    prior = stopped_record_overlaps(root, s, reqs, record_path)
    snapshot = dirty(root)
    selected_dirty = {n: snapshot[n] for n in s['paths'] if n in snapshot}
    ignored = git_run(root, 'check-ignore', '-q', '--', record_path).returncode == 0
    path = safe(root, record_path)
    errors, warnings = [], []
    if path.exists():
        errors.append('Record already exists; use handoff to resume it or choose a new --record. Preflight never replaces records.')
    if not ignored:
        errors.append('Record must be Git-ignored before start; add its narrow directory to the ignore or choose an ignored --record.')
    location_error = participant_record_location_error(record_path)
    if location_error:
        errors.append(location_error)
    if prior['records']:
        errors.append('A prior participant record for the same original requirement/scenario has reached its no-progress stop; do not reset that history by starting a new record.')
    if prior['inventoryErrors']:
        errors.extend(prior['inventoryErrors'])
    if prior['unreadablePaths']:
        warnings.append('Unreadable JSON entries were excluded from participant matching; inspect these paths before resuming any scenario whose history they may contain: ' + ', '.join(prior['unreadablePaths']))
    for parent in path.parents:
        if parent == root:
            break
        if parent.exists() and not parent.is_dir():
            errors.append('Record parent is not a directory: ' + str(parent.relative_to(root)))
            break
    if selected_dirty:
        warnings.append('Selected dirty paths are not owned by this preview. start protects them unless you explicitly assert actual ownership with --adopt-dirty and --ownership-note; never adopt another contributor\'s draft.')
    missing = [n for n in s['paths'] if not safe(root, n).exists()]
    if missing:
        warnings.append('Absent selected files are allowed for new implementation; they cannot support an evidence claim until created and verified.')
    return {'preflightSchema': 1, 'slice': s, 'originals': slice_originals(s, reqs),
            'sliceFile': slice_file, 'sliceFileSha256': digest(safe(root, slice_file)),
            'sourceRevision': git(root, 'rev-parse', 'HEAD').decode().strip(),
            'sourceHashes': {n: digest(safe(root, n)) for n in s['paths']},
            'record': record_path, 'recordExists': path.exists(), 'recordIgnored': ignored,
            'selectedDirtyPaths': selected_dirty,
            'otherDirtyPaths': {n: h for n, h in snapshot.items() if n not in selected_dirty},
            'newSourcePaths': missing, 'requiresOwnershipDecision': bool(selected_dirty),
            'priorStoppedRecords': prior['records'], 'historyWarnings': prior['unreadablePaths'],
            'participantInventoryCount': len(prior['participantInventory']['records']),
            'historyErrors': prior['inventoryErrors'],
            'canStartCleanDraft': not errors and not selected_dirty,
            'errors': errors, 'warnings': warnings,
            'writesPerformed': False, 'acceptanceInferred': False,
            'snapshotLimit': 'Read-only snapshot, not reserved ownership. start rechecks paths and Git state; concurrent edits can change these findings.'}


def authored(name, include_cpp=True, include_js=True):
    prefix = 'implementation/warlock/'
    if not name.startswith(prefix):
        return False
    relative = name[len(prefix):]
    if include_js and relative in AUTHORED_JAVASCRIPT:
        return True
    extensions = ('.elm', '.c', '.h', '.py', '.css', '.svg') + (('.cpp', '.hpp') if include_cpp else ())
    return relative.startswith(('src/', 'native/', 'adapter/', 'assets/')) and pathlib.Path(name).suffix in extensions


def authored_v5(name):
    # Policy 5 is frozen for historical iterations. New records use policy 6;
    # old records retain their authored-language classification semantics.
    prefix = 'implementation/warlock/'
    if not name.startswith(prefix):
        return False
    relative = name[len(prefix):]
    suffix = pathlib.Path(relative).suffix
    return ((suffix == '.elm' and relative.startswith(('src/', 'native/', 'adapter/', 'assets/')))
            or (suffix == '.hs' and relative.startswith(('src/', 'native/', 'adapter/'))))


def authored_v6(name):
    """Prospective classifier; historical policies never consult this function."""
    if authored_v5(name):
        return True
    parts = pathlib.PurePosixPath(name).parts
    if len(parts) < 6 or parts[:3] != ('implementation', 'warlock', 'haskell') or parts[4] != 'src':
        return False
    # One Cabal package segment, not arbitrary files anywhere under haskell/.
    if re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', parts[3]) is None:
        return False
    support = {'test', 'tests', 'qa', 'formal', 'model', 'models', 'build',
               'dist', 'dist-newstyle', 'bench', 'benches', 'examples', 'generated'}
    if any(part in ('.', '..') or part.startswith('.') or part in support for part in parts[5:-1]):
        return False
    return not parts[-1].startswith('.') and pathlib.PurePosixPath(name).suffix in ('.hs', '.hsc')


def product_delta(current, previous, include_cpp=True, include_js=True, policy5=False, policy6=False):
    return any((authored_v6(n) if policy6 else authored_v5(n) if policy5 else authored(n, include_cpp, include_js))
               and current[n] != previous.get(n) for n in current)


def extension_baseline(record, previous, position):
    """Include new dependencies without presenting their existing bytes as a fix."""
    previous = dict(previous)
    for extension in record.get('pathExtensions', []):
        if extension['afterIteration'] == position:
            previous.update(extension['sourceHashes'])
    return previous


def extend_paths(root, record, reqs, state, args):
    """Explicitly add dependencies to the same behavior, retaining its delivery history."""
    if not args.reason.strip():
        raise ValueError('Extension requires a concrete --reason')
    old = normalize_slice(root, record['slice'], reqs)
    requested = normalize_slice(root, dict(old, paths=args.path), reqs)['paths']
    selected_adoption = any(n in old['paths'] for n in requested)
    adopted = list(dict.fromkeys(args.adopt_dirty))
    if any(n not in requested for n in adopted):
        raise ValueError('Dirty adoption is restricted to exact new product paths')
    if adopted and (not args.ownership_note or not args.ownership_note.strip()):
        raise ValueError('Dirty adoption requires an explicit --ownership-note')
    snapshot = dirty(root)
    if any(n not in snapshot for n in adopted):
        raise ValueError('Adopted path is not currently dirty')
    if any(n in snapshot and n not in adopted for n in requested):
        raise ValueError('New dirty dependencies require explicit --adopt-dirty and ownership note')
    # Check foreign custody before any adoption; an overwritten draft cannot be repaired here.
    reconciled, reconciliation_errors, _ = foreign_reconciliations(root, record)
    if reconciliation_errors or any(fingerprint(root, n) != reconciled.get(n, h) for n, h in record['foreignDirty'].items()):
        raise ValueError('Protected foreign-dirty path changed; extension cannot override custody')
    if selected_adoption:
        if (any(n not in old['paths'] for n in requested) or set(adopted) != set(requested)
                or any(n in record.get('adoptedDirty', {}).get('paths', []) for n in requested)):
            raise ValueError('Already-declared adoption requires exact selected paths and explicit --adopt-dirty')
        hashes = {n: digest(safe(root, n)) for n in requested}
        if any(hashes[n] is None or hashes[n] != latest_recorded_source_hash(record, n)
               or (n in record['foreignDirty'] and hashes[n] != record['foreignDirty'][n]) for n in requested):
            raise ValueError('Already-declared adoption cannot override changed captured or latest recorded source')
        before = dict(record.get('adoptedDirty', {}))
        after = {'paths': list(dict.fromkeys(before.get('paths', []) + adopted)), 'ownershipNote': args.ownership_note}
        event = {'atUTC': now(), 'afterIteration': len(record['iterations']), 'reason': args.reason,
                 'paths': requested, 'sourceHashes': hashes,
                 'foreignHashes': {n: record['foreignDirty'][n] for n in requested if n in record['foreignDirty']},
                 'adoptedDirtyBefore': before, 'adoptedDirtyAfter': after}
        record.setdefault('ownershipAdoptions', []).append(event)
        record['adoptedDirty'] = after
        for name in requested:
            record['foreignDirty'].pop(name, None)
        errors, warnings = validate(root, record, reqs, state)
        if errors:
            raise ValueError('Cannot adopt declared source: ' + '; '.join(errors))
        return {'ownershipAdoption': event, 'slice': record['slice'], 'warnings': warnings, 'progress': progress_status(record)}
    hashes = {n: digest(safe(root, n)) for n in requested}
    event = {'atUTC': now(), 'afterIteration': len(record['iterations']),
             'reason': args.reason, 'sourceHashes': hashes,
             'adoptedDirty': {'paths': adopted, 'ownershipNote': args.ownership_note}}
    record['slice']['paths'] = old['paths'] + requested
    record.setdefault('pathExtensions', []).append(event)
    for n in adopted:
        record['foreignDirty'].pop(n, None)
    for iteration in record['iterations']:
        for claim in iteration.get('claims', []):
            claim['historicalAfterSliceExtension'] = True
    mark_historical(root, record)
    errors, warnings = validate(root, record, reqs, state)
    if errors:
        raise ValueError('Cannot extend slice: ' + '; '.join(errors))
    return {'extension': event, 'slice': record['slice'], 'warnings': warnings,
            'progress': progress_status(record)}


def verdict_key(claim, policy=4):
    identity = [claim.get('requirement'), claim.get('scenario'), claim.get('disposition')]
    if policy < 4:
        identity += [claim.get('scope'), sorted(claim.get('missingObservations', []))]
    return json.dumps(identity, sort_keys=True)


def mark_historical(root, record):
    for iteration in record.get('iterations', []):
        for claim in iteration.get('claims', []):
            if any(digest(safe(root, n)) != h for n, h in claim.get('sourceHashes', {}).items()):
                claim['historicalAfterSourceChange'] = True


def scaffold_claim(root, record, reqs, state, args):
    """Print a self-attested observation packet; never write or grant acceptance."""
    mark_historical(root, record)  # Only the in-memory copy; same freshness rules as record.
    errors, warnings = validate(root, record, reqs, state)
    if errors:
        raise ValueError('Cannot scaffold claim: ' + '; '.join(errors))
    s = normalize_slice(root, record['slice'], reqs)
    if args.requirement not in s['requirements'] or args.scenario not in s['scenarios']:
        raise ValueError('Claim outside selected slice')
    original = reqs[args.requirement]
    scenario = next((x for x in original['scenarios'] if x['name'] == args.scenario), None)
    if scenario is None:
        raise ValueError('Scenario does not belong to selected original requirement')
    if not args.scope.strip() or any(not x.strip() for x in args.missing):
        raise ValueError('Evidence scope and missing observations must contain text')
    if args.disposition in ('partial', 'blocked') and not args.missing:
        raise ValueError('Partial/blocked observations require --missing')
    evidence = []
    for name in dict.fromkeys(args.evidence):
        h = digest(safe(root, name))
        if h is None:
            raise ValueError('Missing evidence file: ' + name)
        evidence.append({'path': name, 'sha256': h})
    hashes = {n: digest(safe(root, n)) for n in s['paths']}
    if any(h is None for h in hashes.values()):
        raise ValueError('Every selected source must exist before a claim is scaffolded')
    claim = {'requirement': args.requirement, 'scenario': args.scenario,
             'oracle': scenario['then'], 'verificationScope': original['verification'],
             'scope': args.scope, 'evidence': evidence, 'sourceHashes': hashes,
             'reviewer': record['owner'], 'disposition': args.disposition,
             'missingObservations': args.missing}
    return {'claimSchema': 1, 'claims': [claim],
            'sourceRevision': git(root, 'rev-parse', 'HEAD').decode().strip(),
            'warnings': warnings + ['Contributor observation only. This scaffold neither reviews evidence contents '
                                    'nor updates the original ledger; accepted claims require external review.']}


def handoff(root, record, reqs, state):
    """Read-only resume packet. Current hashes never upgrade recorded observations."""
    errors, warnings = validate(root, record, reqs, state)
    s = normalize_slice(root, record['slice'], reqs)
    _, _, foreign_data = foreign_reconciliations(root, record)
    retained_identity = foreign_data['recordIdentitySha256'] if foreign_data else record_identity(record, record.get('_recordPath', '.warlock-contributor/slice.json'))
    iterations = record.get('iterations', [])
    last = iterations[-1] if iterations else None
    previous = extension_baseline(record, last['sourceHashes'] if last else record['sourceHashes'], len(iterations))
    current = {n: digest(safe(root, n)) for n in s['paths']}
    latest = {}
    for iteration in iterations:
        for claim in iteration.get('claims', []):
            latest[(claim['requirement'], claim['scenario'])] = claim
    observations = []
    for requirement in s['requirements']:
        for scenario in reqs[requirement]['scenarios']:
            if scenario['name'] not in s['scenarios']:
                continue
            claim = latest.get((requirement, scenario['name']))
            observations.append({
                'requirement': requirement, 'scenario': scenario['name'],
                'oracle': scenario['then'], 'verificationScope': reqs[requirement]['verification'],
                'recordedDisposition': claim['disposition'] if claim else None,
                'scope': claim['scope'] if claim else None,
                'evidenceMatchesCurrentSources': bool(claim) and not claim.get('historicalAfterSourceChange', False)
                    and not claim.get('historicalAfterSliceExtension', False)
                    and claim['sourceHashes'] == current
                    and all(digest(safe(root, e['path'])) == e['sha256'] for e in claim['evidence']),
                'missingObservations': claim['missingObservations'] if claim else
                    ['No observation recorded in this participant record; inspect the original ledger and retained evidence.'],
                'evidence': claim['evidence'] if claim else []})
    return {
        'owner': record['owner'], 'slice': s,
        'sourceRevision': git(root, 'rev-parse', 'HEAD').decode().strip(),
        'sourceHashes': current,
        'changedSinceLastRecord': [n for n in current if current[n] != previous.get(n)],
        'protectedForeignPaths': sorted(record['foreignDirty']),
        'recordIdentitySha256': retained_identity,
        'foreignReconciliationSidecar': str(reconciliation_path(root, record).relative_to(root)),
        'pathExtensions': record.get('pathExtensions', []),
        'lastIteration': {k: last[k] for k in ('atUTC', 'outcome', 'summary', 'meaningfulProgress')} if last else None,
        'observations': observations, 'errors': errors, 'warnings': warnings,
        'progress': progress_status(record),
        'nextAction': 'Resolve structural errors before claims.' if errors else
            'Read the observations and implement the next source change, or record the decisive original-scenario observation. '
            'Follow any no-progress warning; do not rerun unchanged qualification by default.'}


def progress_status(record, clock=None):
    """Recorded progress is a self-attestation, never an observed feature count."""
    iterations = record.get('iterations', [])
    qualifying = 0
    for item in reversed(iterations):
        if item['meaningfulProgress']:
            break
        qualifying += 1
    since = record['startedUTC']
    for item in iterations:
        if item['meaningfulProgress']:
            since = item['atUTC']
    clock = clock or dt.datetime.now(dt.timezone.utc)
    elapsed = max(0, (clock - dt.datetime.fromisoformat(since)).total_seconds())
    reasons = []
    if qualifying >= 2:
        reasons.append('two-iterations-without-progress')
    if elapsed >= 2700:
        reasons.append('45-minutes-without-recorded-progress')
    return {'iterationsWithoutProgress': qualifying, 'lastRecordedProgressUTC': since,
            'secondsSinceRecordedProgress': int(elapsed),
            'limits': {'iterations': 2, 'seconds': 2700},
            'investigationNeedsChange': bool(reasons), 'reasons': reasons,
            'action': 'Record the missing observation and select another bounded mandatory slice; '
                      'do not block independent work or bypass safety.' if reasons else
                      'Continue the selected behavior with proportional verification.',
            'basis': 'Participant record; unrecorded work and oracle truth are not inferred.'}


def slice_scenario_pairs(slice_record, reqs):
    """Return only requirement/scenario pairs that exist in the frozen originals."""
    pairs = set()
    for requirement in slice_record.get('requirements', []):
        original = reqs.get(requirement)
        if original is None:
            continue
        scenario_names = {scenario['name'] for scenario in original['scenarios']}
        pairs.update((requirement, scenario) for scenario in slice_record.get('scenarios', [])
                     if scenario in scenario_names)
    return pairs


def participant_record_location_error(record_path):
    parts = pathlib.PurePosixPath(record_path).parts
    if len(parts) != 2 or parts[0] != '.warlock-contributor' or pathlib.PurePosixPath(parts[-1]).suffix != '.json':
        return 'Participant records must be direct .json children of .warlock-contributor so stop history has one complete inventory.'
    return None


def participant_index_path_error(record_path):
    parts = pathlib.PurePosixPath(record_path).parts
    if (len(parts) < 2 or parts[0] != '.warlock-contributor'
            or pathlib.PurePosixPath(parts[-1]).suffix != '.json'
            or '..' in parts or record_path == PARTICIPANT_INDEX):
        return 'Indexed participant paths must remain JSON files under .warlock-contributor.'
    return None


PARTICIPANT_INDEX = '.warlock-contributor/participant-index.json'
BOOTSTRAP_CLASSIFICATIONS = '.warlock-contributor/participant-bootstrap-classifications.json'


def bootstrap_json(body):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate bootstrap field: ' + key)
            result[key] = value
        return result
    return json.loads(body, object_pairs_hook=unique)


def bootstrap_artifact(root, name):
    """Snapshot an exact leaf; a symlink's raw target is never dereferenced."""
    parent, leaf = open_parent(root / name)
    try:
        before = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        if stat.S_ISLNK(before.st_mode):
            target = os.fsencode(os.readlink(leaf, dir_fd=parent))
            after = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
            signature = lambda item: (item.st_dev, item.st_ino, item.st_mtime_ns, item.st_ctime_ns)
            if signature(before) != signature(after) or not stat.S_ISLNK(after.st_mode):
                raise ValueError('Bootstrap symlink changed: ' + name)
            return 'symlink', 'symlink:' + hashlib.sha256(target).hexdigest(), None
        body = regular_bytes_at(parent, leaf)
        try:
            record = json.loads(body)
        except (ValueError, UnicodeError):
            record = None
        return 'file', hashlib.sha256(body).hexdigest(), record
    finally:
        os.close(parent)


def bootstrap_classifications(root, indexed, bound):
    """Reviewed provenance exclusions, never a participant/history verdict."""
    if bound is not None:
        if (not isinstance(bound, dict) or set(bound) != {'path', 'sha256'}
                or bound['path'] != BOOTSTRAP_CLASSIFICATIONS
                or not isinstance(bound['sha256'], str)
                or re.fullmatch(r'[0-9a-f]{64}', bound['sha256']) is None):
            raise ValueError('Invalid indexed bootstrap classification binding')
    path = root / BOOTSTRAP_CLASSIFICATIONS
    if not os.path.lexists(path):
        if bound is not None:
            raise ValueError('Indexed bootstrap classification manifest is missing')
        return {}, None
    body = regular_bytes(path)
    source_sha = hashlib.sha256(body).hexdigest()
    if bound is not None and bound['sha256'] != source_sha:
        raise ValueError('Indexed bootstrap classification manifest bytes changed')
    manifest = bootstrap_json(body)
    if (not isinstance(manifest, dict)
            or set(manifest) != {'schema', 'owner', 'reviewer', 'entries', 'review'}
            or manifest['schema'] != 1 or not isinstance(manifest['entries'], dict)):
        raise ValueError('Unsupported bootstrap classification manifest shape')
    owner, reviewer = manifest['owner'], manifest['reviewer']
    if (not isinstance(owner, str) or not owner.strip()
            or not isinstance(reviewer, str) or not reviewer.strip()
            or owner.strip().casefold() == reviewer.strip().casefold()):
        raise ValueError('Bootstrap classification requires distinct owner and reviewer')
    review = manifest['review']
    if (not isinstance(review, dict) or set(review) != {'path', 'sha256'}
            or not isinstance(review['path'], str)
            or participant_index_path_error(review['path'])
            or review['path'] != pathlib.PurePosixPath(review['path']).as_posix()
            or review['path'] == BOOTSTRAP_CLASSIFICATIONS
            or not isinstance(review['sha256'], str)
            or re.fullmatch(r'[0-9a-f]{64}', review['sha256']) is None):
        raise ValueError('Invalid bootstrap review artifact reference')
    review_body = regular_bytes(safe(root, review['path']))
    if hashlib.sha256(review_body).hexdigest() != review['sha256']:
        raise ValueError('Bootstrap review artifact bytes changed')
    reviewed = bootstrap_json(review_body)
    payload = {key: manifest[key] for key in ('schema', 'owner', 'reviewer', 'entries')}
    if (not isinstance(reviewed, dict) or reviewed.get('schema') != 1
            or reviewed.get('disposition') != 'accepted'
            or reviewed.get('scope') != 'participant-inventory-bootstrap-only'
            or reviewed.get('scenarioAcceptance') is not False
            or reviewed.get('independent') is not True
            or reviewed.get('owner') != owner or reviewed.get('reviewer') != reviewer
            or reviewed.get('classificationsSha256') != json_sha256(payload)):
        raise ValueError('Bootstrap review does not bind this exact provenance-only payload')
    entries = manifest['entries']
    for name, entry in entries.items():
        if (not isinstance(name, str) or participant_index_path_error(name)
                or name != pathlib.PurePosixPath(name).as_posix()
                or name in (BOOTSTRAP_CLASSIFICATIONS, review['path']) or name in indexed):
            raise ValueError('Bootstrap classification cannot exclude indexed/control path: ' + str(name))
        if (not isinstance(entry, dict)
                or set(entry) != {'kind', 'fingerprint', 'reason', 'producer'}
                or entry['kind'] not in ('file', 'symlink')
                or any(not isinstance(entry[key], str) or not entry[key].strip()
                       for key in ('fingerprint', 'reason', 'producer'))):
            raise ValueError('Invalid bootstrap classification entry: ' + name)
        kind, actual, record = bootstrap_artifact(root, name)
        if kind != entry['kind'] or actual != entry['fingerprint']:
            raise ValueError('Bootstrap classification artifact fingerprint differs: ' + name)
        if isinstance(record, dict):
            if 'startedUTC' in record or 'iterations' in record:
                raise ValueError('Bootstrap classification cannot exclude participant or possible history: ' + name)
            try:
                participant_entry(record)
            except (ValueError, TypeError):
                pass
            else:
                raise ValueError('Bootstrap classification cannot exclude a genuine participant: ' + name)
    return entries, {'path': BOOTSTRAP_CLASSIFICATIONS, 'sha256': source_sha}


def participant_index_payload(entries, classification_binding=None):
    payload = {'schema': 1, 'records': dict(sorted(entries.items()))}
    if classification_binding is not None:
        payload['bootstrapClassifications'] = classification_binding
    return payload


def participant_identity(record):
    """Stable identity fields; iterations and verification extensions stay mutable."""
    if not isinstance(record, dict) or not isinstance(record.get('slice'), dict):
        raise ValueError('Participant record identity is unreadable')
    slice_record = record['slice']
    payload = {'owner': record.get('owner'), 'baseline': record.get('baseline'),
               'startedUTC': record.get('startedUTC'),
               'requirements': slice_record.get('requirements'),
               'scenarios': slice_record.get('scenarios')}
    if (not isinstance(payload['owner'], str) or not payload['owner']
            or not isinstance(payload['baseline'], str)
            or not isinstance(payload['startedUTC'], str)
            or not isinstance(payload['requirements'], list)
            or not isinstance(payload['scenarios'], list)
            or any(not isinstance(item, str) or not item for item in payload['requirements'])
            or any(not isinstance(item, str) or not item for item in payload['scenarios'])
            or not isinstance(record.get('iterations'), list)):
        raise ValueError('Participant record identity is incomplete')
    return payload


def participant_entry(record, source_sha256=None):
    identity = participant_identity(record)
    value = {key: item for key, item in record.items() if key != '_recordPath'}
    record_sha256 = source_sha256 or hashlib.sha256((json.dumps(value, indent=2) + '\n').encode('utf-8')).hexdigest()
    return {'identitySha256': json_sha256(identity), 'owner': identity['owner'],
            'baseline': identity['baseline'], 'startedUTC': identity['startedUTC'],
            'requirements': identity['requirements'], 'scenarios': identity['scenarios'],
            'recordSha256': record_sha256}


def owner_census_bytes(root):
    """Capture the exact participant index and every indexed record byte."""
    index_raw = regular_bytes(root / PARTICIPANT_INDEX)
    index = json.loads(index_raw)
    if not isinstance(index, dict) or index.get('schema') != 1 or not isinstance(index.get('records'), dict):
        raise ValueError('Participant index has an unsupported shape')
    payload = {'schema': 1, 'records': index['records']}
    if index.get('indexSha256') != json_sha256(payload):
        raise ValueError('Participant index digest does not match its contents')
    records = []
    for name in sorted(index['records']):
        location_error = participant_index_path_error(name)
        if location_error:
            raise ValueError(location_error)
        raw = regular_bytes(safe(root, name))
        record = json.loads(raw)
        entry = participant_entry(record, hashlib.sha256(raw).hexdigest())
        if entry != index['records'][name]:
            raise ValueError('Participant record differs from exact index binding: ' + name)
        records.append({'path': name, 'recordSha256': entry['recordSha256'],
                        'recordBase64': base64.b64encode(raw).decode('ascii')})
    return {'schema': 1, 'participantIndexPath': PARTICIPANT_INDEX,
            'participantIndexSha256': hashlib.sha256(index_raw).hexdigest(),
            'participantIndexBase64': base64.b64encode(index_raw).decode('ascii'),
            'records': records}


def decode_owner_census(root, relative_path):
    if not isinstance(relative_path, str) or not relative_path.startswith(
            '.warlock-contributor/evidence/foreign-owner-censuses/'):
        raise ValueError('Foreign reconciliation needs a frozen owner census')
    census, census_sha = json_snapshot(safe(root, relative_path))
    if not isinstance(census, dict) or census.get('schema') != 1:
        raise ValueError('Owner census has an unsupported shape')
    if census.get('participantIndexPath') != PARTICIPANT_INDEX:
        raise ValueError('Owner census names an unsupported participant index')
    try:
        index_raw = base64.b64decode(census['participantIndexBase64'], validate=True)
        index = json.loads(index_raw)
    except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError('Owner census participant index bytes are invalid') from exc
    if hashlib.sha256(index_raw).hexdigest() != census.get('participantIndexSha256'):
        raise ValueError('Owner census participant index hash differs')
    if (not isinstance(index, dict) or index.get('schema') != 1
            or not isinstance(index.get('records'), dict)
            or index.get('indexSha256') != json_sha256({'schema': 1, 'records': index['records']})):
        raise ValueError('Owner census participant index is invalid')
    supplied = census.get('records')
    if not isinstance(supplied, list) or len(supplied) != len(index['records']):
        raise ValueError('Owner census does not contain every indexed participant')
    by_path = {}
    for item in supplied:
        if not isinstance(item, dict) or set(item) != {'path', 'recordSha256', 'recordBase64'}:
            raise ValueError('Owner census participant entry is invalid')
        name = item['path']
        if not isinstance(name, str) or name in by_path or name not in index['records']:
            raise ValueError('Owner census participant paths are duplicate or unindexed')
        location_error = participant_index_path_error(name)
        if location_error:
            raise ValueError(location_error)
        try:
            raw = base64.b64decode(item['recordBase64'], validate=True)
            record = json.loads(raw)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError('Owner census record bytes are invalid: ' + name) from exc
        entry = participant_entry(record, hashlib.sha256(raw).hexdigest())
        if item['recordSha256'] != entry['recordSha256'] or index['records'][name] != entry:
            raise ValueError('Owner census record differs from indexed identity or bytes: ' + name)
        by_path[name] = (raw, record)
    if set(by_path) != set(index['records']):
        raise ValueError('Owner census participant path set differs from its index')
    return census, census_sha, by_path


def verify_current_owner_census(root, census):
    """Require event-time evidence to match the locked, current inventory."""
    inventory = participant_inventory(root)
    if inventory['errors']:
        raise ValueError('Participant inventory is incomplete: ' + '; '.join(inventory['errors']))
    if inventory['warnings']:
        raise ValueError('Participant inventory has unclassified JSON paths: ' + ', '.join(inventory['warnings']))
    if set(inventory['records']) != {item['path'] for item in census.get('records', [])}:
        raise ValueError('Owner census omits an inventoried participant-shaped record')
    current = owner_census_bytes(root)
    if current != census:
        raise ValueError('Owner census is stale; capture a new census under the participant lock')


def participant_inventory(root):
    """Load indexed participants and discover valid legacy records recursively.

    An indexed participant that goes missing, changes identity, or becomes
    unreadable is fatal to new starts because its scenario history is unknown.
    Unrelated malformed scratch JSON is only a warning after the initial index
    exists. Before bootstrap, malformed JSON prevents a complete inventory.
    """
    directory = root / '.warlock-contributor'
    index_path = root / PARTICIPANT_INDEX
    errors, warnings = [], []
    indexed = {}
    has_index = index_path.exists()
    if has_index:
        try:
            index, _ = json_snapshot(root / PARTICIPANT_INDEX)
            if not isinstance(index, dict) or index.get('schema') != 1 or not isinstance(index.get('records'), dict):
                raise ValueError('Participant index has an unsupported shape')
            if 'bootstrapClassifications' in index and index['bootstrapClassifications'] is None:
                raise ValueError('Participant index has an empty bootstrap classification binding')
            supplied = index.get('indexSha256')
            payload = participant_index_payload(index['records'], index.get('bootstrapClassifications'))
            if supplied != json_sha256(payload):
                raise ValueError('Participant index digest does not match its contents')
            indexed = dict(index['records'])
        except (OSError, ValueError, TypeError) as exc:
            errors.append('Participant history index is unreadable: ' + str(exc))
            return {'records': {}, 'entries': {}, 'errors': errors, 'warnings': warnings,
                    'hasIndex': True}

    try:
        classified, classification_binding = bootstrap_classifications(
            root, indexed, index.get('bootstrapClassifications') if has_index else None)
    except (OSError, ValueError, TypeError) as exc:
        errors.append('Participant bootstrap classifications are invalid: ' + str(exc))
        return {'records': {}, 'entries': indexed, 'errors': errors, 'warnings': warnings,
                'hasIndex': has_index}
    participants = {}
    missing_indexed = {}
    for name, entry in indexed.items():
        location_error = participant_index_path_error(name)
        if location_error or not isinstance(entry, dict):
            errors.append('Participant history index contains an invalid record path: ' + str(name))
            continue
        if not isinstance(entry.get('recordSha256'), str) or re.fullmatch(r'[0-9a-f]{64}', entry['recordSha256']) is None:
            errors.append('Participant history index lacks an exact-byte binding at ' + str(name) +
                          '; preserve the legacy record and reconcile its provenance before migration')
            continue
        path = root / name
        try:
            record, source_sha256 = json_snapshot(path)
            actual = participant_entry(record, source_sha256)
            prior_identity = {key: value for key, value in entry.items() if key != 'recordSha256'}
            if prior_identity != {key: value for key, value in actual.items() if key != 'recordSha256'}:
                raise ValueError('immutable participant identity differs from index')
            if entry.get('recordSha256') is not None and entry['recordSha256'] != source_sha256:
                raise ValueError('participant bytes differ from indexed history')
            indexed[name] = actual
            participants[name] = record
        except FileNotFoundError:
            missing_indexed[name] = entry
        except (OSError, ValueError, TypeError, KeyError) as exc:
            errors.append('Indexed participant history is unreadable at ' + name + ': ' + str(exc))

    if not directory.is_dir():
        return {'records': participants, 'entries': indexed, 'errors': errors,
                'warnings': warnings, 'hasIndex': has_index, 'bootstrapClassifications': classification_binding}
    for path in sorted(directory.rglob('*.json')):
        relative = path.relative_to(root).as_posix()
        if relative == PARTICIPANT_INDEX:
            continue
        if relative.startswith('.warlock-contributor/evidence/') and relative not in indexed:
            continue
        if relative in classified:
            try:
                kind, actual, _ = bootstrap_artifact(root, relative)
                if kind != classified[relative]['kind'] or actual != classified[relative]['fingerprint']:
                    raise ValueError('artifact fingerprint differs')
            except (OSError, ValueError, TypeError) as exc:
                errors.append('Reviewed bootstrap artifact changed at ' + relative + ': ' + str(exc))
            continue
        try:
            record, source_sha256 = json_snapshot(root / relative)
        except (OSError, ValueError, TypeError) as exc:
            if relative in indexed or not has_index:
                errors.append('Participant history inventory cannot classify ' + relative + ': ' + str(exc))
            else:
                warnings.append(relative)
            continue
        if not isinstance(record, dict):
            if relative in indexed:
                errors.append('Indexed participant history has invalid JSON shape: ' + relative)
            continue
        signature = {'owner', 'slice', 'startedUTC', 'iterations'}
        if signature <= record.keys():
            try:
                entry = participant_entry(record, source_sha256)
            except (ValueError, TypeError):
                errors.append('Participant-shaped JSON has incomplete identity: ' + relative)
                continue
            if relative in indexed and indexed[relative] != entry:
                errors.append('Participant identity differs from its index: ' + relative)
            else:
                participants[relative] = record
                indexed[relative] = entry
        elif relative in indexed:
            errors.append('Indexed participant history has invalid record shape: ' + relative)
        elif (len(pathlib.PurePosixPath(relative).parts) == 2 and
              (('owner' in record and 'slice' in record) or ('startedUTC' in record and 'iterations' in record))):
            errors.append('Participant-shaped JSON has incomplete identity: ' + relative)
    unindexed = {name: indexed[name] for name in participants
                 if name not in (index.get('records', {}) if has_index else {})}
    relocation_candidates = {}
    relocation_destinations = {}
    for old_name, old_entry in missing_indexed.items():
        expected_identity = old_entry.get('identitySha256')
        matches = [name for name, entry in unindexed.items()
                   if entry.get('identitySha256') == expected_identity
                   and entry.get('recordSha256') == old_entry.get('recordSha256')]
        relocation_candidates[old_name] = matches
        if len(matches) == 1:
            relocation_destinations[matches[0]] = relocation_destinations.get(matches[0], 0) + 1
    for old_name, matches in relocation_candidates.items():
        if len(matches) == 1 and relocation_destinations[matches[0]] == 1:
            new_name = matches[0]
            indexed.pop(old_name, None)
            indexed[new_name] = unindexed[new_name]
            warnings.append('Relocated participant path reconciled by exact indexed identity: ' + old_name + ' -> ' + new_name)
        else:
            errors.append('Indexed participant history is missing at ' + old_name +
                          (' and has no unique exact relocation' if not matches or (len(matches) == 1 and relocation_destinations[matches[0]] > 1)
                           else ' and has ambiguous exact relocations'))
    return {'records': participants, 'entries': indexed, 'errors': errors,
            'warnings': warnings, 'hasIndex': has_index, 'bootstrapClassifications': classification_binding}


def write_participant_index(root, inventory, record_path, record, parent_fd):
    """Append immutable participant identity after the record write succeeds."""
    entries = dict(inventory['entries'])
    entries[record_path] = participant_entry(record)
    payload = participant_index_payload(entries, inventory.get('bootstrapClassifications'))
    index = dict(payload, indexSha256=json_sha256(payload))
    write_record(root / PARTICIPANT_INDEX, index, parent_fd=parent_fd)


def write_participant_inventory_index(root, inventory, parent_fd):
    payload = participant_index_payload(inventory['entries'], inventory.get('bootstrapClassifications'))
    index = dict(payload, indexSha256=json_sha256(payload))
    write_record(root / PARTICIPANT_INDEX, index, parent_fd=parent_fd)


def stopped_record_overlaps(root, candidate_slice, reqs, exclude_record=None, inventory=None):
    """Find prior same-scenario records whose own progress threshold has fired.

    This read-only inventory prevents a new record from silently restarting the
    no-progress clock. Independent original scenarios remain available.
    """
    candidate_pairs = slice_scenario_pairs(candidate_slice, reqs)
    if not candidate_pairs:
        return {'records': [], 'unreadablePaths': [], 'inventoryErrors': []}
    blocked = []
    inventory = inventory or participant_inventory(root)
    for relative, data in sorted(inventory['records'].items()):
        if exclude_record and relative == exclude_record:
            continue
        source_hash = hashlib.sha256(regular_bytes(root / relative)).hexdigest()
        try:
            prior_pairs = slice_scenario_pairs(data['slice'], reqs)
        except (AttributeError, KeyError, TypeError):
            inventory['errors'].append('Participant scenario identity is invalid: ' + relative)
            continue
        overlap = sorted(candidate_pairs & prior_pairs)
        if not overlap:
            continue
        try:
            progress = progress_status(data)
        except (KeyError, TypeError, ValueError):
            progress = {'investigationNeedsChange': True,
                        'reasons': ['participant-record-progress-unreadable'],
                        'lastRecordedProgressUTC': None, 'secondsSinceRecordedProgress': None}
        if not progress['investigationNeedsChange']:
            continue
        blocked.append({'record': relative, 'recordSha256': source_hash,
                        'owner': data['owner'], 'sliceId': data['slice'].get('id'),
                        'overlappingOriginals': [{'requirement': requirement, 'scenario': scenario}
                                                 for requirement, scenario in overlap],
                        'stopReasons': progress['reasons'],
                        'lastRecordedProgressUTC': progress['lastRecordedProgressUTC'],
                        'secondsSinceRecordedProgress': progress['secondsSinceRecordedProgress']})
    return {'records': blocked, 'unreadablePaths': inventory['warnings'],
            'inventoryErrors': inventory['errors'], 'participantInventory': inventory}


def verification_plan(root, record, reqs, state, selected=False):
    """Suggest existing protected runners. Never run or certify their contents."""
    packet = handoff(root, record, reqs, state)
    paths = packet['slice']['paths'] if selected else packet['changedSinceLastRecord']
    product = [n for n in paths if authored(n) or authored_v6(n)]
    requirements = set(packet['slice']['requirements'])
    scenarios = set(packet['slice']['scenarios'])
    primary = bool(scenarios & {'taskbar-inactive', 'taskbar-active', 'taskbar-minimized'})
    reflow = bool(requirements & {'ELM-UI-008'} and 'overflow-resize' in scenarios)
    dense = bool(requirements & {'ELM-UI-008'} and scenarios & {'overflow-first-last', 'overflow-resize'})
    menus = bool(requirements & {'ELM-UI-008'} and 'menu-invocation' in scenarios)
    previews = bool('ELM-UX-006' in requirements and 'ux-006' in scenarios)
    cpu, mapped = [], set()

    def add(name, arguments, sources, reason):
        runner = 'implementation/warlock/qa/' + name
        key = (runner, tuple(arguments))
        for target in cpu:
            if (target['runner'], tuple(target['arguments'])) == key:
                target['triggerPaths'] = sorted(set(target['triggerPaths']) | set(sources))
                return
        exists = safe(root, runner).is_file()
        launcher = safe(root, 'window-integration-qa/qa_run.py')
        qa_support = safe(root, 'window-integration-qa')
        can_run = exists and launcher.is_file() and qa_support.is_dir()
        argv = ['/usr/bin/python3', '-B', str(launcher), '--', '/usr/bin/python3',
                '-B', str(safe(root, runner)), *arguments] if can_run else None
        environment = {'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONPATH': str(qa_support)} if can_run else None
        command = ('PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=' + shlex.quote(str(qa_support)) +
                   ' ' + shlex.join(argv)) if argv else None
        cpu.append({'runner': runner, 'runnerSha256': digest(safe(root, runner)),
                    'arguments': arguments, 'triggerPaths': sorted(sources), 'reason': reason,
                    'runnerAvailable': exists, 'protectedLauncherAvailable': launcher.is_file(),
                    'environment': environment, 'argv': argv, 'command': command})

    for name in product:
        relative = name.removeprefix('implementation/warlock/')
        if relative.startswith('native/core/'):
            if relative == 'native/core/SeatManager.cpp':
                add('check-focus-core.py', [], [name], 'Compile the changed owning core unit and relink the exact archive.')
                add('check-native-authority.py', [], [name], 'After the core build, rebuild authority against the same owning headers/provider.')
            else:
                continue
        elif relative in ('native/host.c', 'native/shared-host.c', 'native/surface.h'):
            add('check-search.py', ['--popup-reflow'] if reflow else ['--native-popup'], [name],
                'Changed host compile, relink and popup lifecycle checks; retain the selected reflow mode.')
        elif relative.startswith('native/'):
            add('check-native-authority.py', [], [name], 'Compile changed authority units against the owning core tuple.')
        elif relative in ('adapter/taskbar_preferences.py', 'adapter/taskbar_projection.py'):
            add('check-pin-storage.py', [], [name], 'Pin persistence/component behavior; inspect scope for non-pin projection changes.')
        elif relative in ('src/Catalog.elm', 'src/Launch.elm', 'adapter/catalog_authority.py'):
            add('check-search.py', [], [name], 'Compile search views and catalog/launch replays.')
        elif relative in ('src/TaskView.elm', 'src/Taskbar.elm', 'src/TaskbarShell.elm',
                          'src/Surface.elm', 'src/Desktop.elm', 'src/Main.elm',
                          'src/SurfaceRenderer.elm', 'src/SurfaceController.elm', 'src/Popup.elm',
                          'src/Bar.elm', 'src/ActionProjection.elm', 'src/PreviewPresenter.elm',
                          'src/PreviewVisual.elm', 'src/NativePreviewReceiver.elm',
                          'assets/adapter.js', 'assets/activation.js', 'assets/bar-adapter.js',
                          'assets/context.js', 'assets/popup-adapter.js', 'assets/shell.css'):
            if requirements & {'ELM-UI-007'}:
                add('check-feedback.py', [], [name], 'Changed feedback views and state projection.')
            else:
                flags = ['--preview-states'] if previews else \
                        ['--popup-reflow'] if reflow else \
                        ['--dense-taskbar'] if dense else \
                        ['--pinned-menus'] if menus else \
                        ['--taskbar-primary'] if primary else \
                        ['--workspace-navigation'] if requirements & {'ELM-UI-002', 'ELM-UX-008'} else \
                        ['--task-view'] if requirements & {'ELM-UI-006', 'ELM-UX-017'} else \
                        ['--pins'] if requirements & {'ELM-UX-004'} else []
                add('check-search.py', flags, [name], 'Compile the affected shell/view route; review the selected runner mode.')
        elif relative in ('src/Effects.elm', 'src/NativeOutcome.elm', 'adapter/effect_endpoint.py'):
            add('check-feedback.py', [], [name], 'Outcome/state projection; select additional replay/model cases for changed invariants.')
        else:
            continue
        mapped.add(name)

    modes = []
    if product:
        if reflow:
            modes += [['--popup-reflow']]
        elif dense:
            modes += [['--dense-taskbar']]
        elif menus:
            modes += [['--pinned-menus']]
        if requirements & {'ELM-UI-006', 'ELM-UX-017'}:
            modes += [['--task-view'], ['--task-view-retired-opener']]
        if requirements & {'ELM-UI-002', 'ELM-UX-008'}:
            modes += [['--workspace-navigation']]
        if requirements & {'ELM-UI-005', 'ELM-UX-029'}:
            modes += [['--launcher-search']]
        if requirements & {'ELM-UX-004'}:
            modes += [['--taskbar-pins']]
        if primary:
            modes += [['--taskbar-primary']]
        if 'taskbar-group' in scenarios or requirements & {'ELM-UX-005', 'ELM-UX-024'}:
            modes += [['--taskbar-focus']]
        if requirements & {'ELM-UI-007'}:
            modes += [[]]
    native = []
    runner = 'implementation/warlock/qa/native-window-feedback.py'
    for arguments in modes:
        exists = safe(root, runner).is_file()
        argv = ['python3', '-B', 'docs/warlock-build-loop/v2/loop.py', '--record',
                record.get('_recordPath', '.warlock-contributor/slice.json'),
                'native', '--runner', str(safe(root, runner)), '--', *arguments] if exists else None
        native.append({'runner': runner, 'runnerSha256': digest(safe(root, runner)),
                       'arguments': arguments, 'runnerAvailable': exists,
                       'argv': argv, 'command': shlex.join(argv) if argv else None})
    unplanned = []
    if previews:
        original = next(item for item in reqs['ELM-UX-006']['scenarios'] if item['name'] == 'ux-006')
        unplanned.append({'requirement': 'ELM-UX-006', 'scenario': 'ux-006',
                          'requiredVerification': reqs['ELM-UX-006']['verification'],
                          'scenarioOracle': original['then'],
                          'missingObservation': 'Isolated current-source native recording',
                          'reason': 'No qualified current-source UX-006 native runner is mapped; do not use the historical preview wrapper.'})
    packet.update(verificationPlanSchema=2, executionPerformed=False, acceptanceInferred=False,
                  mode='selected-paths' if selected else 'changes-since-last-record',
                  consideredPaths=paths, cpuTargets=cpu, nativeCandidates=native,
                  unplannedOriginalObservations=unplanned,
                  unmappedProductPaths=sorted(set(product) - mapped),
                  supportPaths=[n for n in paths if n not in product],
                  instructions=[
                      'Suggestions only: inspect runners, prerequisites and source tuple before execution; run nothing automatically.',
                      'Choose the smallest decisive behavior plus a meaningful negative/lifecycle case. Native candidates run serially.',
                      'Add Quint/fuzz only for changed reducer, concurrency or authority invariants; this map is not complete coverage.',
                      'Unmapped product/support changes need an explicit proportional check chosen by the contributor.',
                      'Original verification and missing observations below still apply; suggested runner passes do not accept scenarios.',
                      'No changed sources means no default rerun. Use --selected to plan before edits, not to infer new evidence.'])
    return packet


def doctor(root, record_path):
    """Inspect local availability without running client binaries, builds or installs."""
    plugin = 'plugins/warlock-contributor/'
    required = ['scripts/warlock.py', 'scripts/session_hook.py',
                'skills/warlock-contribute/SKILL.md', '.claude-plugin/plugin.json',
                '.codex-plugin/plugin.json', 'hooks/hooks.json', 'hooks/codex.json']
    missing = [plugin + n for n in required if not safe(root, plugin + n).is_file()]
    errors = ['Missing package file: ' + n for n in missing]
    manifests = {}
    for name in ('.claude-plugin/plugin.json', '.codex-plugin/plugin.json'):
        path = safe(root, plugin + name)
        if not path.is_file():
            continue
        try:
            manifest = read(path)
            if not isinstance(manifest, dict) or manifest.get('name') != 'warlock-contributor':
                raise ValueError('Expected warlock-contributor manifest object')
            version = manifest.get('version')
            if not isinstance(version, str) or not version.strip():
                raise ValueError('Missing package version')
            manifests[name] = version
            if name.startswith('.codex-plugin/'):
                for field, directory in (('skills', True), ('hooks', False)):
                    target = manifest.get(field)
                    if not isinstance(target, str) or not target.startswith('./'):
                        raise ValueError(field + ' must be an explicit plugin-relative path')
                    destination = safe(root, plugin + target)
                    if not (destination.is_dir() if directory else destination.is_file()):
                        raise ValueError('Missing ' + field + ' target: ' + target)
        except (ValueError, OSError, TypeError) as exc:
            errors.append('Invalid package metadata ' + name + ': ' + str(exc))
    if len(set(manifests.values())) > 1:
        errors.append('Claude and Codex package versions differ')
    for name in ('hooks/hooks.json', 'hooks/codex.json'):
        path = safe(root, plugin + name)
        if not path.is_file():
            continue
        try:
            data = read(path)
            hooks = data.get('hooks') if isinstance(data, dict) else None
            if not isinstance(hooks, dict):
                raise ValueError('Expected hooks object')
            for event in ('SessionStart', 'UserPromptSubmit'):
                entries = hooks.get(event)
                if not isinstance(entries, list) or not entries:
                    raise ValueError('Missing hook entries for ' + event)
                for entry in entries:
                    commands = entry.get('hooks') if isinstance(entry, dict) else None
                    if not isinstance(commands, list) or not commands:
                        raise ValueError('Missing commands for ' + event)
                    for command in commands:
                        if not isinstance(command, dict) or command.get('type') != 'command' \
                                or not isinstance(command.get('command'), str) or not command['command'].strip():
                            raise ValueError('Expected nonempty command hook for ' + event)
                        timeout = command.get('timeout')
                        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 60:
                            raise ValueError('Expected bounded positive hook timeout for ' + event)
        except (ValueError, OSError, TypeError) as exc:
            errors.append('Invalid package metadata ' + name + ': ' + str(exc))
    ignored = git_run(root, 'check-ignore', '-q', '--', record_path).returncode == 0
    warnings = ['Client executable availability does not establish installation, enabled hooks or trust. '
                'Product toolchain and native runtime are checked by their protected runners.']
    if not ignored:
        warnings.append('Scratch record is not ignored; start will refuse to write it. Add a narrow ignore or select an ignored --record path.')
    return {
        'python': {'version': list(sys.version_info[:3]), 'minimum': '3.9'},
        'git': shutil.which('git'),
        'clientExecutables': {name: shutil.which(name) for name in ('claude', 'codex', 'grok')},
        'recordIgnored': ignored,
        'recordExists': safe(root, record_path).exists(),
        'missingPackageFiles': missing,
        'manifestVersions': manifests,
        'metadataValidation': 'Local manifest identity, version agreement, referenced paths and reminder-hook shape only; no client loading or trust inferred.',
        'errors': errors,
        'warnings': warnings}


def self_test(root):
    """Explicit plugin-only regression run; no product build or native campaign."""
    qa = safe(root, 'plugins/warlock-contributor/qa')
    tests = sorted(qa.glob('test_*.py'))
    if not tests:
        raise ValueError('Plugin regression tests are missing; use a complete repository checkout')
    for test in tests:
        if not safe(root, str(test.relative_to(root))).is_file():
            raise ValueError('Expected regular plugin test file: ' + test.name)
    argv = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(qa),
            '-t', str(qa), '-p', 'test_*.py']
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(('GIT_', 'GROK_', 'CLAUDE_', 'PLUGIN_'))
           and key not in ('PYTHONPATH', 'PYTHONHOME')}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    try:
        result = subprocess.run(argv, cwd=root, env=env, capture_output=True,
                                text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {'selfTestSchema': 1, 'executionPerformed': True, 'acceptanceInferred': False,
                'argv': argv, 'errors': ['Plugin regression suite exceeded its 300-second limit']}
    errors = ['Plugin regression suite failed'] if result.returncode else []
    if '\nRan 0 tests in ' in result.stderr:
        errors = ['Plugin regression suite discovered zero tests']
    return {'selfTestSchema': 1, 'executionPerformed': True, 'acceptanceInferred': False,
            'scope': 'Plugin contribution-policy regressions; no GUI build, native/AT oracle or client installation.',
            'argv': argv, 'returnCode': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr,
            'errors': errors}


def contribution_report(root, record, reqs, state):
    """Prepare a delivery note from recorded observations, without inventing results."""
    packet = handoff(root, record, reqs, state)
    current = packet['sourceHashes']
    selected_dirty = set(dirty_names(root)) & set(current)
    initial = dict(record['sourceHashes'])
    for extension in record.get('pathExtensions', []):
        initial.update(extension['sourceHashes'])
    packet.update(
        reportSchema=1, releaseAccepted=False,
        intendedBehavior=record['slice']['after'],
        observedResult=packet['lastIteration']['summary'] if packet['lastIteration'] else None,
        selectedChanges=[{'path': name, 'initialSha256': initial.get(name),
                         'currentSha256': sha, 'uncommitted': name in selected_dirty}
                        for name, sha in current.items()
                        if sha != initial.get(name) or name in selected_dirty],
        reportBoundary='Contributor self-attestation for review. Intended behavior is not an observation; '
                       'matching hashes do not establish oracle truth, independent review or release acceptance.')
    return packet


def markdown_literal(value):
    """Keep contributor text literal, without HTML, links or injected headings."""
    text = ' '.join(str(value).splitlines())
    for character in ('\\', '`', '*', '_', '[', ']', '<', '>', '#', '|'):
        text = text.replace(character, '\\' + character)
    return text


def report_markdown(packet):
    literal = markdown_literal

    lines = ['Warlock contribution: ' + literal(packet['slice']['id']), '',
             'Owner: ' + literal(packet['owner']),
             'Source HEAD: ' + literal(packet['sourceRevision']) + ' (see uncommitted paths below).', '',
             'Before: ' + literal(packet['slice']['before']),
             'Intended result: ' + literal(packet['intendedBehavior']),
             'Recorded observation: ' + literal(packet['observedResult'] or 'No iteration recorded.'), '',
             'Recorded progress: ' + str(packet['progress']['iterationsWithoutProgress']) +
             ' consecutive iterations without progress; ' + str(packet['progress']['secondsSinceRecordedProgress']) +
             ' seconds since the recorded progress baseline.',
             'Investigation action: ' + literal(packet['progress']['action']), '',
             packet['reportBoundary'], '', 'Selected source changes:', '']
    for change in packet['selectedChanges']:
        lines.append('- ' + literal(change['path']) +
                     (' — uncommitted' if change['uncommitted'] else ' — committed') +
                     '; current SHA-256: ' + literal(change['currentSha256'] or 'deleted'))
    if not packet['selectedChanges']:
        lines.append('No selected source changes since this record began.')
    lines.extend(['', 'Original scenario observations:', ''])
    for observation in packet['observations']:
        lines.extend(['- ' + literal(observation['requirement']) + ' / ' + literal(observation['scenario']) +
                      ': recorded disposition ' + literal(observation['recordedDisposition'] or 'none') + '.',
                      '  Original oracle: ' + literal(observation['oracle']),
                      '  Verification obligations: ' + literal(observation['verificationScope']),
                      '  Source/evidence hashes: ' + ('current' if observation['evidenceMatchesCurrentSources']
                                                    else 'not current or no observation') + '.'])
        if observation.get('scope'):
            lines.append('  Recorded evidence scope: ' + literal(observation['scope']))
        for evidence in observation['evidence']:
            lines.append('  Evidence: ' + literal(evidence['path']) + '; SHA-256: ' + literal(evidence['sha256']))
        for missing in observation['missingObservations']:
            lines.append('  Remaining observation: ' + literal(missing))
    lines.extend(['', 'Planned verification (execution is not inferred):', ''])
    lines.extend('- ' + literal(item) for item in packet['slice']['verification'])
    if packet['errors'] or packet['warnings']:
        lines.extend(['', 'Structural findings:', ''])
        lines.extend('- Error: ' + literal(item) for item in packet['errors'])
        lines.extend('- Advisory: ' + literal(item) for item in packet['warnings'])
    lines.extend(['', 'Full release acceptance is not established by this report.', ''])
    return '\n'.join(lines)


def capabilities(root, reqs):
    """Discover original capability identities without selecting contributor work."""
    ledger = read(safe(root, LEDGER))
    groups = {}
    for row in ledger['requirements']:
        capability = reqs[row['id']]['capability']
        group = groups.setdefault(capability, {'capability': capability,
            'requirements': [], 'scenarioCountsByRecordedStatus': {}})
        group['requirements'].append(row['id'])
        for scenario in row['scenarios']:
            status = scenario['status']
            counts = group['scenarioCountsByRecordedStatus']
            counts[status] = counts.get(status, 0) + 1
    rows = [groups[name] for name in sorted(groups)]
    for row in rows:
        row['requirementCount'] = len(row['requirements'])
        row['scenarioCount'] = sum(row['scenarioCountsByRecordedStatus'].values())
    return {'capabilities': rows, 'ledgerSha256': digest(safe(root, LEDGER)),
            'recordedOnly': True, 'releaseAccepted': False,
            'warnings': ['Capability counts describe the frozen baseline and recorded dispositions only; '
                         'they do not establish implementation, evidence freshness or release acceptance.']}


def inspect_requirements(root, reqs, requirements, scenarios):
    if not 1 <= len(requirements) <= 3 or len(set(requirements)) != len(requirements) or any(i not in reqs for i in requirements):
        raise ValueError('Inspect needs 1–3 unique original requirement IDs')
    available = {s['name'] for i in requirements for s in reqs[i]['scenarios']}
    if len(set(scenarios)) != len(scenarios) or not set(scenarios) <= available:
        raise ValueError('Inspect needs unique exact scenario names under the selected requirements')
    if scenarios and any(not any(s['name'] in scenarios for s in reqs[i]['scenarios']) for i in requirements):
        raise ValueError('Each inspected requirement needs a selected original scenario')
    rows = {r['id']: r for r in read(safe(root, LEDGER))['requirements']}
    result = []
    for identity in requirements:
        original, row = dict(reqs[identity]), dict(rows[identity])
        total = len(original['scenarios'])
        if scenarios:
            original['scenarios'] = [s for s in original['scenarios'] if s['name'] in scenarios]
            row['scenarios'] = [s for s in row['scenarios'] if s['name'] in scenarios]
        result.append({'original': original, 'ledger': row,
            'originalScenarioCount': total, 'omittedScenarios': total - len(original['scenarios']),
            'pointers': {'original': BASE, 'ledger': LEDGER, 'contribution': original.get('source'),
                'openSpec': [str(p.relative_to(root)) for p in (root / 'openspec' / 'changes').glob(
                    '*/specs/' + original['capability'] + '/spec.md')]}})
    return {'requirements': result, 'scenarioFilter': scenarios,
            'ledgerSha256': digest(safe(root, LEDGER))}


def remaining(root, reqs, requirements, statuses, summary_only, limit=None, offset=0, selected_capabilities=()):
    """Report recorded backlog, without inferring implementation or acceptance."""
    if len(set(requirements)) != len(requirements) or any(i not in reqs for i in requirements):
        raise ValueError('Remaining needs unique original requirement IDs')
    available = {r['capability'] for r in reqs.values()}
    if len(set(selected_capabilities)) != len(selected_capabilities) or not set(selected_capabilities) <= available:
        raise ValueError('Remaining needs unique exact capabilities; use capabilities to list them')
    ledger = read(safe(root, LEDGER))
    counts, rows = {}, []
    requirement_count = 0
    for requirement in ledger['requirements']:
        identity = requirement['id']
        if requirements and identity not in requirements:
            continue
        original = reqs[identity]
        if selected_capabilities and original['capability'] not in selected_capabilities:
            continue
        requirement_count += 1
        scenarios = {s['name']: s for s in original['scenarios']}
        for scenario in requirement['scenarios']:
            status = scenario['status']
            counts[status] = counts.get(status, 0) + 1
            if status not in statuses:
                continue
            rows.append({'requirement': identity, 'capability': original['capability'],
                         'original': scenarios[scenario['name']],
                         'verificationScope': original['verification'], 'ledger': scenario})
    matching = len(rows)
    shown = [] if summary_only else rows[offset:None if limit is None else offset + limit]
    omitted_before = 0 if summary_only else min(offset, matching)
    omitted_after = matching - omitted_before - len(shown)
    return {'ledgerSha256': digest(safe(root, LEDGER)), 'recordedOnly': True,
            'filters': {'requirements': requirements, 'capabilities': list(selected_capabilities), 'statuses': statuses},
            'requirementsConsidered': requirement_count, 'scenarioCountsByRecordedStatus': counts,
            'matchingScenarios': matching, 'scenarios': shown,
            'offset': offset, 'limit': limit, 'shownScenarios': len(shown),
            'omittedBefore': omitted_before, 'omittedAfter': omitted_after,
            'nextOffset': offset + len(shown) if omitted_after and not summary_only else None,
            'summaryOnly': summary_only, 'releaseAccepted': False,
            'warnings': ['Recorded dispositions are not revalidated here. Unadjudicated does not mean unimplemented; '
                         'accepted rows still require current evidence and independent review. '
                         'The frozen 242/417 baseline is only part of the full release scope.']}


def remaining_markdown(packet):
    literal = markdown_literal
    lines = ['Warlock recorded scenario checklist', '',
             'Ledger SHA-256: ' + literal(packet['ledgerSha256']), '',
             str(packet['requirementsConsidered']) + ' requirements considered; ' +
             str(packet['matchingScenarios']) + ' scenarios match the selected statuses.',
             'Recorded counts: ' + ', '.join(literal(status) + '=' + str(count)
                 for status, count in sorted(packet['scenarioCountsByRecordedStatus'].items())) + '.', '',
             'Showing ' + str(packet['shownScenarios']) + ' scenarios; ' +
             str(packet['omittedBefore']) + ' omitted before and ' + str(packet['omittedAfter']) + ' after.', '']
    for row in packet['scenarios']:
        original, observation = row['original'], row['ledger']
        # Never render a checked box: recorded acceptance has not been revalidated.
        marker = '- ' if observation['status'] == 'accepted' else '- [ ] '
        lines.extend([marker + literal(row['requirement']) + ' / ' + literal(original['name']) +
                      ' (recorded ' + literal(observation['status']) + ')', '',
                      '  Given: ' + literal(original['given']), '',
                      '  When: ' + literal(original['when']), '',
                      '  Original oracle: ' + literal(original['then']), '',
                      '  Verification obligations: ' + literal(row['verificationScope']), ''])
        if observation.get('missingObservation'):
            lines.extend(['  Missing observation: ' + literal(observation['missingObservation']), ''])
        for evidence in observation.get('evidence', []):
            if evidence.get('scope'):
                lines.extend(['  Recorded evidence scope: ' + literal(evidence['scope']), ''])
    if packet['nextOffset'] is not None:
        lines.extend(['Next page: repeat the same filters and limit with --offset ' +
                      str(packet['nextOffset']) + '; compare the ledger hash before combining pages.', ''])
    if not packet['scenarios'] and not packet['summaryOnly']:
        lines.extend(['No rows on this page; this does not establish release completion.', ''])
    lines.extend(packet['warnings'])
    lines.extend(['', 'Full release acceptance is not established by this checklist.', ''])
    return '\n'.join(lines)


def review(root, record, reqs, state, includes):
    """Read-only staging review; explicit support paths do not override foreign ownership."""
    packet = handoff(root, record, reqs, state)
    allowed = set(record['slice']['paths'])
    for name in includes:
        path = safe(root, name)
        if path.is_dir() or name.startswith(('.git/', '.warlock-contributor/')):
            raise ValueError('Review includes must be publishable repository files: ' + name)
        if name.startswith('implementation/') and not name.startswith('implementation/warlock/'):
            raise ValueError('Review cannot include archival implementation: ' + name)
        allowed.add(name)
    for iteration in record['iterations']:
        for claim in iteration.get('claims', []):
            allowed.update(e['path'] for e in claim['evidence'])
    staged = []
    for name in git(root, 'diff', '--cached', '--no-renames', '--name-only', '-z', '--').decode().split('\0'):
        if not name:
            continue
        if name in record['foreignDirty']:
            packet['errors'].append('Staged protected foreign path: ' + name)
        elif name not in allowed:
            packet['errors'].append('Staged path needs explicit contribution scope (--include for owned support files): ' + name)
        path = safe(root, name)
        entries = git(root, 'ls-files', '--stage', '-z', '--', ':(literal)' + name).split(b'\0')
        index_hash = None
        for entry in entries:
            if not entry:
                continue
            metadata, _ = entry.split(b'\t', 1)
            mode, blob, stage = metadata.decode().split()
            if stage != '0' or mode not in ('100644', '100755'):
                raise ValueError('Staged path must be a resolved regular file: ' + name)
            index_hash = hashlib.sha256(git(root, 'cat-file', 'blob', blob)).hexdigest()
        current_hash = digest(path)
        matches = index_hash == current_hash
        if not matches:
            packet['errors'].append('Staged bytes differ from current source/evidence: ' + name)
        staged.append({'path': name, 'stagedSha256': index_hash, 'workingSha256': current_hash,
                       'matchesWorkingTree': matches})
    if not staged:
        packet['warnings'].append('Nothing is staged; this review has no commit contents to check.')
    packet.update(staged=staged, explicitSupportPaths=includes,
                  reviewBoundary='Read-only scope and byte comparison. Does not stage, commit, push, run QA or certify observations.')
    return packet


def accepted_revision(root, claim, cache):
    """Bind accepted source hashes to immutable regular Git blobs, without checkout."""
    source_tuple = claim.get('sourceTuple', {})
    if not isinstance(source_tuple, dict) or any(not source_tuple.get(k) for k in ('sourceRevision', 'core', 'plugin', 'toolchain')):
        return ['Accepted claim needs reproducible source/core/plugin/toolchain tuple']
    revision = source_tuple['sourceRevision']
    if not isinstance(revision, str):
        return ['Accepted sourceRevision must be a full immutable commit hash']
    resolved = git_run(root, 'rev-parse', '--verify', '--end-of-options', revision + '^{commit}')
    if resolved.returncode:
        return ['Accepted sourceRevision is not a commit in this repository']
    if resolved.stdout.decode().strip() != revision:
        return ['Accepted sourceRevision must be a full immutable commit hash, not a ref or abbreviation']
    errors = []
    for name, expected in claim['sourceHashes'].items():
        safe(root, name)
        key = (revision, name)
        if key not in cache:
            tree = git(root, '--literal-pathspecs', 'ls-tree', '-z', revision, '--', name)
            entry = tree.rstrip(b'\0').split(b'\t', 1)
            metadata = entry[0].split() if tree else []
            if len(entry) != 2 or len(metadata) != 3 or metadata[0] not in (b'100644', b'100755') or metadata[1] != b'blob':
                cache[key] = None
            else:
                blob = git(root, 'cat-file', 'blob', metadata[2].decode())
                cache[key] = hashlib.sha256(blob).hexdigest()
        if cache[key] is None:
            errors.append('Accepted sourceRevision lacks a regular source file: ' + name)
        elif cache[key] != expected:
            errors.append('Accepted sourceRevision bytes differ from claimed source: ' + name)
    return errors


def validate_ownership_adoptions(record):
    previous = None
    for event in record.get('ownershipAdoptions', []):
        paths = event.get('paths')
        before, after = event.get('adoptedDirtyBefore'), event.get('adoptedDirtyAfter')
        count = event.get('afterIteration')
        if (not isinstance(paths, list) or not paths or len(set(paths)) != len(paths)
                or not isinstance(before, dict) or not isinstance(after, dict)
                or type(count) is not int or count < 0 or count > len(record.get('iterations', []))
                or not isinstance(event.get('reason'), str) or not event['reason'].strip()):
            raise ValueError('Invalid selected-source ownership adoption history')
        if previous is not None and before != previous:
            raise ValueError('Selected-source ownership adoption chain differs')
        dt.datetime.fromisoformat(event['atUTC'])
        if (not isinstance(after.get('ownershipNote'), str) or not after['ownershipNote'].strip()
                or after.get('paths') != list(dict.fromkeys(before.get('paths', []) + paths))):
            raise ValueError('Selected-source ownership adoption needs exact paths and ownership note')
        source_at_event = dict(record, iterations=record.get('iterations', [])[:count],
                               pathExtensions=[e for e in record.get('pathExtensions', []) if e['afterIteration'] <= count])
        for name in paths:
            binding = latest_recorded_source_hash(source_at_event, name)
            if (name not in record['slice']['paths'] or binding is None
                    or name in record['foreignDirty'] or name in before.get('paths', [])
                    or event.get('sourceHashes', {}).get(name) != binding
                    or (name in event.get('foreignHashes', {}) and event['foreignHashes'][name] != binding)):
                raise ValueError('Selected-source ownership adoption does not match captured source')
        previous = after
    if previous is not None and record.get('adoptedDirty') != previous:
        raise ValueError('Selected-source ownership adoption does not match current custody')


def validate(root, record, reqs, state):
    validate_ownership_adoptions(record)
    errors, warnings = [], []
    revision_cache = {}
    if record.get('schema') != 1 or not record.get('owner'):
        raise ValueError('Invalid record schema/owner')
    s = normalize_slice(root, record['slice'], reqs)
    adoption = record.get('adoptedDirty', {'paths': [], 'ownershipNote': None})
    if not isinstance(adoption, dict) or not isinstance(adoption.get('paths'), list):
        raise ValueError('Invalid dirty adoption metadata')
    if adoption['paths'] and (not isinstance(adoption.get('ownershipNote'), str) or not adoption['ownershipNote'].strip()):
        errors.append('Dirty adoption lacks explicit ownership note')
    if any(n not in s['paths'] for n in adoption['paths']):
        errors.append('Dirty adoption exceeds declared product paths')
    if record.get('baseline') != EXPECTED:
        errors.append('Record baseline differs')
    extensions = record.get('pathExtensions', [])
    known_paths = set(record['sourceHashes'])
    last_position = 0
    for extension in extensions:
        position = extension.get('afterIteration')
        if type(position) is not int or not last_position <= position <= len(record.get('iterations', [])):
            raise ValueError('Invalid extension iteration position')
        last_position = position
        hashes = extension.get('sourceHashes')
        if not isinstance(hashes, dict) or not hashes or known_paths.intersection(hashes):
            raise ValueError('Extension must identify unique new source paths')
        if any(n not in s['paths'] or (h is not None and (not isinstance(h, str) or len(h) != 64)) for n, h in hashes.items()):
            raise ValueError('Invalid extension source baseline')
        if not isinstance(extension.get('reason'), str) or not extension['reason'].strip():
            raise ValueError('Extension needs its reason')
        dt.datetime.fromisoformat(extension['atUTC'])
        adoption = extension.get('adoptedDirty', {})
        if not isinstance(adoption.get('paths'), list) or any(n not in hashes for n in adoption['paths']):
            raise ValueError('Invalid extension dirty adoption')
        if adoption['paths'] and (not isinstance(adoption.get('ownershipNote'), str) or not adoption['ownershipNote'].strip()):
            raise ValueError('Extension dirty adoption needs ownership note')
        known_paths.update(hashes)
    if extensions and known_paths != set(s['paths']):
        errors.append('Extension history does not cover declared source paths')
    if not record.get('explicitSliceOverride') and s['id'] != state['activeSlice']['id']:
        errors.append('Live selected slice changed; restart deliberately or explicitly select a slice')
    reconciled, reconciliation_errors, _ = foreign_reconciliations(root, record)
    errors.extend(reconciliation_errors)
    for name, old in record['foreignDirty'].items():
        if fingerprint(root, name) != reconciled.get(name, old):
            errors.append('Protected foreign-dirty path changed: ' + name)
    for name in dirty_names(root):
        if name in record['foreignDirty'] or name in s['paths'] or name.startswith(('plugins/warlock-contributor/', '.warlock-contributor/', 'docs/', 'implementation/warlock/qa/evidence/')):
            continue
        if name.startswith('implementation/'):
            errors.append('Unowned or archival implementation change: ' + name)
    for index, item in enumerate(record.get('iterations', [])):
        for c in item.get('claims', []):
            if c.get('disposition') not in ('unadjudicated', 'missing', 'implemented-unverified', 'partial', 'failed', 'blocked', 'accepted'):
                errors.append('Unknown scenario disposition')
            if not isinstance(c.get('missingObservations'), list) or any(not isinstance(x, str) or not x.strip() for x in c['missingObservations']):
                errors.append('Missing observations must be an array of nonempty strings')
            if c.get('disposition') in ('partial', 'blocked') and not c.get('missingObservations'):
                errors.append('Partial/blocked verdict requires a missing observation')
            if c.get('disposition') == 'accepted':
                if c.get('missingObservations'):
                    errors.append('Accepted claim contradicts remaining missing observations')
                reviewer = c.get('reviewer')
                if not isinstance(reviewer, dict) or not reviewer.get('name') or reviewer.get('independent') is not True or reviewer.get('disposition') != 'accepted':
                    errors.append('Accepted claim needs independent external reviewer identity/disposition')
                if isinstance(reviewer, dict) and str(reviewer.get('name', '')).strip().casefold() == str(record['owner']).strip().casefold():
                    errors.append('Accepted external reviewer must differ from contributor owner')
                for evidence in c.get('evidence', []):
                    evidence_path = evidence.get('path', '')
                    ignored = git_run(root, 'check-ignore', '--', evidence_path).returncode == 0
                    if evidence_path in s['paths'] or authored(evidence_path) or (item.get('progressPolicy', 1) == 5 and authored_v5(evidence_path)) or (item.get('progressPolicy', 1) >= 6 and authored_v6(evidence_path)) or evidence_path.startswith('.warlock-contributor/') or ignored:
                        errors.append('Accepted evidence cannot be product source or ignored scratch')
                if not c.get('evidence'):
                    errors.append('Accepted claim needs retained evidence')
                errors.extend(accepted_revision(root, c, revision_cache))
            if c['requirement'] not in s['requirements'] or c['scenario'] not in s['scenarios']:
                errors.append('Claim outside selected slice')
                continue
            original = reqs[c['requirement']]
            scenarios = {x['name']: x for x in original['scenarios']}
            if c['scenario'] not in scenarios or c['oracle'] != scenarios[c['scenario']]['then'] or c['verificationScope'] != original['verification']:
                errors.append('Claim oracle/verification differs from original')
            for e in c['evidence']:
                if not isinstance(e.get('sha256'), str) or len(e['sha256']) != 64 or digest(safe(root, e['path'])) != e['sha256']:
                    errors.append('Missing or changed evidence: ' + e['path'])
            for name, h in c['sourceHashes'].items():
                if not isinstance(h, str) or len(h) != 64 or name not in s['paths'] or digest(safe(root, name)) != h:
                    if c.get('historicalAfterSourceChange') and isinstance(h, str) and len(h) == 64 and name in s['paths']:
                        warnings.append('Historical evidence source changed; current acceptance invalidated: ' + name)
                    else:
                        errors.append('Stale or irrelevant claim source: ' + name)
            later_paths = {n for e in extensions if e['afterIteration'] > index for n in e['sourceHashes']}
            historical_scope = bool(later_paths) and c.get('historicalAfterSliceExtension') is True
            expected_sources = set(s['paths']) - later_paths if historical_scope else set(s['paths'])
            if set(c['sourceHashes']) != expected_sources:
                errors.append('Claim must identify all selected relevant sources')
            if historical_scope:
                warnings.append('Historical evidence predates added dependencies; current acceptance invalidated.')
            elif c.get('historicalAfterSliceExtension'):
                errors.append('Claim extension marker lacks a later source extension')
    iterations = record.get('iterations', [])
    previous = record['sourceHashes']
    seen_claims = []
    for index, item in enumerate(iterations):
        previous = extension_baseline(record, previous, index)
        policy = item.get('progressPolicy', 1)
        if policy not in (1, 2, 3, 4, 5, 6):
            errors.append('Unknown iteration progress policy')
        seen_verdicts = {verdict_key(c, policy) for c in seen_claims}
        expected_progress = (item['outcome'] == 'production-fix' and product_delta(item['sourceHashes'], previous, policy in (2, 3, 4), policy in (3, 4), policy == 5, policy == 6)) or (item['outcome'] == 'scenario-verdict' and any(verdict_key(c, policy) not in seen_verdicts for c in item.get('claims', [])))
        if item['meaningfulProgress'] != expected_progress:
            errors.append('Iteration progress assertion differs from source hashes/recorded verdict')
        previous = item['sourceHashes']
        seen_claims.extend(item.get('claims', []))
    if progress_status(record)['investigationNeedsChange']:
        warnings.append('Stop expanding this investigation; record missing observation and choose another bounded mandatory slice. Independent work remains allowed.')
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default=None)
    parser.add_argument('--record', default='.warlock-contributor/slice.json')
    parser.add_argument('--json', action='store_true')
    subs = parser.add_subparsers(dest='command', required=True)
    inspect = subs.add_parser('inspect')
    inspect.add_argument('--requirement', action='append', required=True)
    inspect.add_argument('--scenario', action='append', default=[], help='Exact original scenario name; repeat to narrow inspection')
    subs.add_parser('capabilities', help='Read-only original capability IDs and recorded counts; does not select work')
    subs.add_parser('status'); check = subs.add_parser('check')
    subs.add_parser('doctor')
    subs.add_parser('self-test', help='Run plugin regression tests in isolated fixtures; no GUI campaigns')
    subs.add_parser('index-participants', help='Freeze the complete local participant path/identity inventory without editing participant records')
    subs.add_parser('owner-census', help='Freeze exact indexed participant record bytes for reviewed foreign ownership provenance')
    preview = subs.add_parser('preflight', help='Read-only saved-plan and prospective-record checks; no ownership or writes')
    preview.add_argument('--slice-file', required=True)
    subs.add_parser('handoff')
    reconciliation = subs.add_parser('reconcile-foreign', help='Append reviewed foreign provenance without adopting files or changing participant history')
    reconciliation.add_argument('--transition-file', required=True, help='Ignored scratch JSON array of exact reviewed foreign-path transitions')
    extension = subs.add_parser('extend', help='Add dependencies to the same owned slice without resetting its history or timer')
    extension.add_argument('--path', action='append', required=True)
    extension.add_argument('--reason', required=True)
    extension.add_argument('--adopt-dirty', action='append', default=[], metavar='PATH')
    extension.add_argument('--ownership-note')
    verification = subs.add_parser('verify-plan', help='Read-only suggestions for proportional protected checks; never executes QA')
    verification.add_argument('--selected', action='store_true', help='Plan declared paths before edits; default considers only changes since last record')
    report = subs.add_parser('report', help='Read-only delivery note from the participant record; no acceptance inferred')
    report.add_argument('--markdown', action='store_true', help='Print a reviewable Markdown note instead of the JSON packet')
    backlog = subs.add_parser('remaining', help='Read-only original scenario checklist from recorded ledger dispositions')
    backlog.add_argument('--requirement', action='append', default=[])
    backlog.add_argument('--capability', action='append', default=[], help='Exact original capability; intersects requirement filters')
    backlog.add_argument('--status', action='append', choices=['unadjudicated', 'missing', 'implemented-unverified', 'partial', 'failed', 'blocked', 'accepted'])
    backlog.add_argument('--summary', action='store_true', help='Counts only; omit scenario details')
    backlog.add_argument('--limit', type=int, help='Maximum matching scenarios to show; positive integer')
    backlog.add_argument('--offset', type=int, default=0, help='Skip this many matching scenarios in ledger order')
    backlog.add_argument('--markdown', action='store_true', help='Print a readable checklist instead of the JSON packet')
    staging = subs.add_parser('review', help='Read-only participant handoff and staged contribution review')
    staging.add_argument('--include', action='append', default=[], help='Explicitly owned supporting file; cannot override protected foreign paths')
    claim = subs.add_parser('claim', help='Print a record-compatible observation scaffold; does not write or accept')
    claim.add_argument('--requirement', required=True)
    claim.add_argument('--scenario', required=True)
    claim.add_argument('--evidence', action='append', required=True)
    claim.add_argument('--scope', required=True)
    claim.add_argument('--disposition', required=True,
                       choices=['unadjudicated', 'missing', 'implemented-unverified', 'partial', 'failed', 'blocked'])
    claim.add_argument('--missing', action='append', default=[])
    plan = subs.add_parser('plan', help='Print a start-compatible slice scaffold; does not write or select work')
    plan.add_argument('--id', required=True)
    plan.add_argument('--requirement', action='append', required=True)
    plan.add_argument('--scenario', action='append', required=True)
    plan.add_argument('--path', action='append', required=True)
    plan.add_argument('--before', required=True)
    plan.add_argument('--after', required=True)
    plan.add_argument('--verify', action='append', required=True)
    check.add_argument('--project-only', action='store_true', help='Check project/baseline without reading a participant record')
    check.add_argument('--require-record', action='store_true', help='Fail if the participant slice record is absent')
    check.add_argument('--base-ref', help='Check changed implementation paths since this Git revision')
    start = subs.add_parser('start')
    start.add_argument('--owner', required=True); start.add_argument('--slice-file')
    start.add_argument('--adopt-dirty', action='append', default=[], metavar='PATH', help='Explicitly assert ownership of an already dirty declared product path')
    start.add_argument('--ownership-note', help='Explain authorization/ownership for adopting dirty product paths')
    rec = subs.add_parser('record')
    rec.add_argument('--outcome', choices=['qualification', 'production-fix', 'scenario-verdict'], required=True)
    rec.add_argument('--summary', required=True); rec.add_argument('--claim-file')
    args = parser.parse_args()
    result = {'acceptanceBoundary': BOUNDARY, 'checkerSha256': digest(pathlib.Path(__file__))}
    lock = None
    lock_parent = None
    records_lock = None
    records_parent = None
    history_inventory = None
    try:
        root = pathlib.Path(args.repo or discover_repo()).resolve()
        owned_checker = safe(root, 'plugins/warlock-contributor/scripts/warlock.py')
        if digest(owned_checker) != result['checkerSha256']:
            raise ValueError('Installed checker differs from repository-owned checker; use the reviewed repository copy')
        if args.command == 'check' and args.project_only and args.require_record:
            raise ValueError('--project-only is incompatible with --require-record')
        if args.command in ('report', 'remaining') and args.markdown and args.json:
            raise ValueError('--markdown is incompatible with --json')
        if args.command == 'remaining':
            if args.limit is not None and args.limit < 1 or args.offset < 0:
                raise ValueError('--limit must be positive and --offset must be nonnegative')
            if args.summary and (args.limit is not None or args.offset):
                raise ValueError('--summary is incompatible with pagination')
        reqs, state = context(root)
        if args.command == 'check' and args.base_ref:
            args.base_ref = git(root, 'rev-parse', '--verify', '--end-of-options', args.base_ref + '^{commit}').decode().strip()
        path = safe(root, args.record)
        def read_target():
            record = json.loads(regular_bytes_at(lock_parent, path.name)) if lock_parent is not None else read(path)
            record['_recordPath'] = args.record
            return record
        if args.command in ('start', 'record', 'extend', 'reconcile-foreign', 'index-participants', 'owner-census'):
            records_parent, records_name = open_parent(safe(root, '.warlock-contributor/.records.lock'), create=True)
            records_lock = os.fdopen(os.open(records_name, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC,
                                             0o600, dir_fd=records_parent), 'w')
            fcntl.flock(records_lock, fcntl.LOCK_EX)
            if git_run(root, 'check-ignore', '-q', '--', args.record).returncode != 0:
                raise ValueError('Record must be Git-ignored; add its directory to .gitignore or local .git/info/exclude')
            if args.command == 'start':
                location_error = participant_record_location_error(args.record)
                if location_error:
                    raise ValueError(location_error)
            history_inventory = participant_inventory(root)
            if history_inventory['errors']:
                raise ValueError('Participant history inventory is incomplete: ' + '; '.join(history_inventory['errors']))
            if (args.command not in ('start', 'index-participants', 'owner-census')
                    and args.record not in history_inventory['records']):
                raise ValueError('Existing participant record is absent from the inventoried .warlock-contributor history; run index-participants after reviewing its exact legacy path.')
            lock_path = safe(root, args.record + '.lock')
            lock_parent, lock_name = open_parent(lock_path, create=True)
            lock = os.fdopen(os.open(lock_name, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=lock_parent), 'w')
            fcntl.flock(lock, fcntl.LOCK_EX)
        if args.command == 'doctor':
            result.update(doctor(root, args.record))
        elif args.command == 'self-test':
            result.update(self_test(root))
        elif args.command == 'index-participants':
            write_participant_inventory_index(root, history_inventory, records_parent)
            result.update(indexPath=PARTICIPANT_INDEX,
                          participantCount=len(history_inventory['records']),
                          recordPaths=sorted(history_inventory['records']),
                          historyWarnings=history_inventory['warnings'],
                          recordsSha256=digest(safe(root, PARTICIPANT_INDEX)))
        elif args.command == 'owner-census':
            if set(history_inventory['records']) != set(history_inventory['entries']):
                raise ValueError('Owner census requires the participant index to cover every discovered participant record')
            if history_inventory['warnings']:
                raise ValueError('Owner census requires an inventory without unclassified JSON paths: ' +
                                 ', '.join(history_inventory['warnings']))
            census = owner_census_bytes(root)
            body = (json.dumps(census, indent=2) + '\n').encode('utf-8')
            census_sha = hashlib.sha256(body).hexdigest()
            relative = '.warlock-contributor/evidence/foreign-owner-censuses/' + census_sha + '.json'
            if git_run(root, 'check-ignore', '-q', '--', relative).returncode != 0:
                raise ValueError('Owner census must remain in Git-ignored evidence scratch')
            target = safe(root, relative)
            if target.exists():
                if regular_bytes(target) != body:
                    raise ValueError('Content-addressed owner census path contains different bytes')
            else:
                census_parent, _ = open_parent(target, create=True)
                try:
                    write_record(target, census, exclusive=True, parent_fd=census_parent)
                finally:
                    os.close(census_parent)
            result.update(ownerCensusSnapshot=relative, ownerCensusSnapshotSha256=census_sha,
                          participantIndexSha256=census['participantIndexSha256'],
                          participantCount=len(census['records']), scenarioAcceptanceInferred=False)
        elif args.command == 'capabilities':
            result.update(capabilities(root, reqs))
        elif args.command == 'remaining':
            result.update(remaining(root, reqs, args.requirement,
                args.status or ['unadjudicated', 'missing', 'implemented-unverified', 'partial', 'failed', 'blocked'],
                args.summary, args.limit, args.offset, args.capability))
        elif args.command == 'plan':
            s = normalize_slice(root, {'id': args.id, 'requirements': args.requirement,
                'scenarios': args.scenario, 'paths': args.path, 'before': args.before,
                'after': args.after, 'verification': args.verify}, reqs)
            result.update(planSchema=1, slice=s, originals=slice_originals(s, reqs))
        elif args.command == 'preflight':
            result.update(preflight(root, args.record, args.slice_file, reqs))
        elif args.command in ('handoff', 'claim', 'review', 'report', 'verify-plan', 'extend', 'reconcile-foreign'):
            if not path.exists():
                raise ValueError('No participant record to resume; inspect status and start an owned slice first')
            if args.command == 'reconcile-foreign':
                result.update(reconcile_foreign(root, read_target(), reqs, state, args))
            elif args.command == 'extend':
                record = read_target()
                result.update(extend_paths(root, record, reqs, state, args))
                write_record(path, record, parent_fd=lock_parent)
                write_participant_index(root, history_inventory, args.record, record, records_parent)
                result['record'] = args.record
            elif args.command == 'verify-plan':
                record = read_target()
                record['_recordPath'] = args.record
                result.update(verification_plan(root, record, reqs, state, args.selected))
            elif args.command == 'claim':
                result.update(scaffold_claim(root, read_target(), reqs, state, args))
            elif args.command == 'review':
                result.update(review(root, read_target(), reqs, state, args.include))
            elif args.command == 'report':
                result.update(contribution_report(root, read_target(), reqs, state))
            else:
                result.update(handoff(root, read_target(), reqs, state))
        elif args.command == 'inspect':
            result.update(inspect_requirements(root, reqs, args.requirement, args.scenario))
        elif args.command == 'status':
            result.update(activeSlice=state['activeSlice'], baseline=EXPECTED, recordExists=path.exists(), releaseAccepted=False)
            if path.exists():
                record = read_target()
                errors, warnings = validate(root, record, reqs, state)
                result.update(errors=errors, warnings=warnings, progress=progress_status(record))
        elif args.command == 'start':
            if path.exists():
                raise ValueError('Record already exists; retain it and choose a new --record for a new slice')
            s = load_slice(root, args.slice_file, reqs) if args.slice_file else normalize_slice(root, state['activeSlice'], reqs)
            prior = stopped_record_overlaps(root, s, reqs, args.record, history_inventory)
            if prior['inventoryErrors']:
                raise ValueError('Participant history inventory is incomplete: ' + '; '.join(prior['inventoryErrors']))
            if prior['records']:
                paths = ', '.join(item['record'] for item in prior['records'])
                raise ValueError('Start refused: same original requirement/scenario has a prior stopped record (' + paths + '). Preserve and resume that participant history or select a different mandatory scenario; do not reset its no-progress clock.')
            adopted = list(dict.fromkeys(args.adopt_dirty))
            if adopted and (not args.ownership_note or not args.ownership_note.strip()):
                raise ValueError('Dirty adoption requires an explicit --ownership-note')
            if any(n not in s['paths'] for n in adopted):
                raise ValueError('Dirty adoption is restricted to exact declared product paths')
            dirty_snapshot = dirty(root)
            if any(n not in dirty_snapshot for n in adopted):
                raise ValueError('Adopted path is not currently dirty')
            record = {'schema': 1, 'owner': args.owner, 'slice': s, 'explicitSliceOverride': bool(args.slice_file), 'baseline': EXPECTED, 'startedUTC': now(), 'sourceRevision': git(root, 'rev-parse', 'HEAD').decode().strip(), 'sourceHashes': {n: digest(safe(root,n)) for n in s['paths']}, 'foreignDirty': {n: h for n, h in dirty_snapshot.items() if n not in adopted}, 'adoptedDirty': {'paths': adopted, 'ownershipNote': args.ownership_note}, 'iterations': []}
            # Reserve the exact participant identity in the index first. If
            # record creation is interrupted, later starts fail closed on the
            # missing indexed record instead of overlooking its history.
            write_participant_index(root, history_inventory, args.record, record, records_parent)
            write_record(path, record, exclusive=True, parent_fd=lock_parent)
            result.update(record=args.record, slice=s, historyWarnings=prior['unreadablePaths'])
            if prior['unreadablePaths']:
                result['warnings'] = ['Unreadable JSON entries were excluded from participant matching; inspect before resuming possibly overlapping histories: ' + ', '.join(prior['unreadablePaths'])]
        elif args.command == 'check' and (args.project_only or not path.exists()):
            if args.require_record:
                raise ValueError('Continuation requires a participant slice record; run start first')
            changed = {}
            if args.base_ref:
                changed.update({n: None for n in git(root, 'diff', '--no-renames', '--name-only', '-z', args.base_ref, '--').decode().split('\0') if n})
            errors = ['Archival implementation change: ' + n for n in changed if n.startswith('implementation/') and not n.startswith('implementation/warlock/')]
            result.update(errors=errors, warnings=['No participant slice record; baseline/project checks only. No contributor source ownership or evidence claim checked.'])
        else:
            record = read_target()
            if args.command == 'record':
                mark_historical(root, record)
            errors, warnings = validate(root, record, reqs, state)
            if args.command == 'record' and not errors:
                claims = read(safe(root, args.claim_file)) if args.claim_file else []
                if isinstance(claims, dict) and claims.get('claimSchema') == 1:
                    claims = claims['claims']
                if not isinstance(claims, list):
                    raise ValueError('Claim file must contain an array or claimSchema=1 packet')
                for c in claims:
                    for key in ('requirement','scenario','oracle','verificationScope','scope','evidence','sourceHashes','reviewer','disposition','missingObservations'):
                        if key not in c:
                            raise ValueError('Claim missing ' + key)
                    if not isinstance(c['evidence'], list) or not isinstance(c['sourceHashes'], dict) or not isinstance(c['missingObservations'], list):
                        raise ValueError('Claim evidence/missingObservations must be arrays; sourceHashes must be an object')
                    if not c['evidence'] or not c['reviewer'] or not c['scope'] or not c['disposition']:
                        raise ValueError('Claims require evidence, scope, reviewer and disposition')
                hashes = {n: digest(safe(root,n)) for n in record['slice']['paths']}
                previous = extension_baseline(record, record['iterations'][-1]['sourceHashes'] if record['iterations'] else record['sourceHashes'], len(record['iterations']))
                seen_verdicts = {verdict_key(c) for i in record['iterations'] for c in i.get('claims', [])}
                progress = (args.outcome == 'production-fix' and product_delta(hashes, previous, policy6=True)) or (args.outcome == 'scenario-verdict' and any(verdict_key(c) not in seen_verdicts for c in claims))
                record['iterations'].append({'atUTC': now(), 'outcome': args.outcome, 'summary': args.summary, 'sourceHashes': hashes, 'meaningfulProgress': progress, 'progressPolicy': 6, 'claims': claims, 'sourceRevision': git(root, 'rev-parse', 'HEAD').decode().strip()})
                errors, warnings = validate(root, record, reqs, state)
                if not errors:
                    write_record(path, record, parent_fd=lock_parent)
                    write_participant_index(root, history_inventory, args.record, record, records_parent)
            result.update(errors=errors, warnings=warnings, record=args.record, progress=progress_status(record))
        if args.command == 'check' and args.base_ref and path.exists() and not args.project_only:
            names = git(root, 'diff', '--no-renames', '--name-only', '-z', args.base_ref, '--').decode().split('\0')
            result.setdefault('errors', []).extend('Archival implementation change: ' + n for n in names if n.startswith('implementation/') and not n.startswith('implementation/warlock/'))
        result['ok'] = not result.get('errors')
        code = 0 if result['ok'] else 1
    except (ValueError, OSError, KeyError, TypeError, AttributeError, IndexError) as exc:
        result.update(ok=False, errors=[str(exc)])
        code = 2
    finally:
        if records_lock is not None:
            records_lock.close()
        if records_parent is not None:
            os.close(records_parent)
        if lock is not None:
            lock.close()
        if lock_parent is not None:
            os.close(lock_parent)
    if args.command == 'report' and args.markdown and 'reportSchema' in result:
        print(report_markdown(result))
    elif args.command == 'remaining' and args.markdown and 'matchingScenarios' in result:
        print(remaining_markdown(result))
    else:
        print(json.dumps(result, indent=2) if args.json else '\n'.join([BOUNDARY, json.dumps(result, indent=2)]))
    return code


if __name__ == '__main__':
    sys.exit(main())
