"""Exact owned root-browser writable tmpfs data, bounded metadata witnesses only.

No process launch/input. Mutable file data/timestamps/FD position are recorded
but excluded from authority. Every fresh proof invalidates earlier partial state.
"""
from pathlib import Path
import base64
import os
import re
import stat
from owned_shared_data import bounded, digest, identity, maps, no_exec

SIZE = 4194304
MAX_FDS = 4096


def raw_record(raw):
    return {'base64': base64.b64encode(raw).decode(), 'bytes': len(raw),
            'sha256': digest(raw)}


def error_record(error):
    return {'type': type(error).__name__, 'errno': getattr(error, 'errno', None),
            'error': str(error)}


def directory(path):
    path = Path(path)
    current = path.lstat()
    if path.resolve() != path or not stat.S_ISDIR(current.st_mode):
        raise RuntimeError('Metrics directory must be canonical nonsymlink directory')
    if current.st_uid != os.getuid() or stat.S_IMODE(current.st_mode) != 0o700:
        raise RuntimeError('Metrics directory must be owned full mode0700')
    return {'path': str(path), 'device': current.st_dev, 'inode': current.st_ino,
            'uid': current.st_uid, 'mode': current.st_mode}


def anchors(runtime, profile):
    """Capture freshly created runtime/profile before browser launch."""
    runtime, profile = Path(runtime), Path(profile)
    if profile.parent != runtime or profile.name != 'browser-profile':
        raise RuntimeError('Exact fresh private browser profile required')
    return {'runtime': directory(runtime), 'profile': directory(profile)}


def stat_record(current):
    return {k: getattr(current, k) for k in
            ('st_mode', 'st_dev', 'st_ino', 'st_uid', 'st_gid', 'st_nlink',
             'st_size', 'st_mtime_ns', 'st_ctime_ns')}


def directory_token(current, path):
    if (not stat.S_ISDIR(current.st_mode) or current.st_uid != os.getuid() or
        stat.S_IMODE(current.st_mode) != 0o700):
        raise RuntimeError('Metrics directory must be owned full mode0700')
    return {'path': str(path), 'device': current.st_dev, 'inode': current.st_ino,
            'uid': current.st_uid, 'mode': current.st_mode}


def parent_observation(profile, profile_anchor, evidence):
    """Observe one child relative to a pinned exact current profile directory.

    Genuine absent ENOENT is a separate namespace state, never a historical
    parent inode/mode assertion. Attach raw diagnostics before predicate checks.
    """
    profile = Path(profile); component = 'BrowserMetrics'; path = profile / component
    evidence.update(requestedPath=str(path), component=component,
                    followSymlinks=False, errors={})
    parent_fd = child_fd = None
    try:
        evidence['profilePathBefore'] = directory(profile)
        parent_fd = os.open(profile, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        evidence['profileFDNumber'] = parent_fd
        before = os.fstat(parent_fd); evidence['profileFDRawBefore'] = stat_record(before)
        slots = []
        for phase in ('Before', 'After'):
            observation = {}; evidence['lookup' + phase] = observation
            try:
                slot = os.stat(component, dir_fd=parent_fd, follow_symlinks=False)
                observation.update(state='present', stat=stat_record(slot)); slots.append(slot)
                if phase == 'Before' and stat.S_ISDIR(slot.st_mode):
                    child_fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent_fd)
                    evidence['childFDRaw'] = stat_record(os.fstat(child_fd))
            except FileNotFoundError as error:
                observation.update(state='absentENOENT', error=error_record(error),
                                   actualFilename=error.filename, requestedPath=str(path))
                if error.errno != 2 or error.filename != component:
                    raise RuntimeError('Metrics absence must be exact component ENOENT') from error
                slots.append(None)
        after = os.fstat(parent_fd); evidence['profileFDRawAfter'] = stat_record(after)
        evidence['profilePathAfter'] = directory(profile)
        tokens = [directory_token(before, profile), directory_token(after, profile),
                  evidence['profilePathBefore'], evidence['profilePathAfter']]
        if any(token != profile_anchor for token in tokens):
            raise RuntimeError('Metrics pinned profile FD/named anchor changed')
        if (slots[0] is None) != (slots[1] is None):
            raise RuntimeError('Metrics parent state changed during descriptor lookup')
        if slots[0] is None:
            evidence['stable'] = {'state': 'absentENOENT', 'path': str(path),
                                  'component': component, 'errno': 2,
                                  'profileIdentity': profile_anchor}
        else:
            first = directory_token(slots[0], path); last = directory_token(slots[1], path)
            if first != last or child_fd is None or directory_token(os.fstat(child_fd), path) != first:
                raise RuntimeError('Metrics present parent directory replaced')
            evidence['stable'] = {**first, 'state': 'present', 'profileIdentity': profile_anchor}
        return evidence['stable']
    except Exception as error:
        evidence['errors']['observation'] = error_record(error)
        raise
    finally:
        if child_fd is not None:os.close(child_fd)
        if parent_fd is not None:os.close(parent_fd)


def parse_mount(raw, runtime):
    eligible = []
    for line in raw.decode().splitlines():
        head, tail = line.split(' - ')
        fields, fs = head.split(), tail.split()
        if len(fields) < 6 or len(fs) < 3:
            raise RuntimeError('Incomplete metrics mount metadata')
        # Escapes/relative routes are not authority for this exact private path.
        route = fields[4]
        if '\\' in route or '\\' in fields[3] or not route.startswith('/'):
            continue
        mountpoint = Path(route)
        if runtime == mountpoint or runtime.is_relative_to(mountpoint):
            major, minor = map(int, fields[2].split(':'))
            eligible.append({'id': int(fields[0]), 'device': os.makedev(major, minor),
                             'root': fields[3], 'path': route, 'type': fs[0],
                             'source': fs[1], 'line': line})
    if not eligible:
        raise RuntimeError('No metrics runtime mount')
    depth = max(len(Path(r['path']).parts) for r in eligible)
    selected = [r for r in eligible if len(Path(r['path']).parts) == depth]
    if len(selected) != 1 or selected[0]['type'] != 'tmpfs' or selected[0]['root'] != '/':
        raise RuntimeError('Metrics runtime tmpfs mount ambiguous')
    if selected[0]['device'] != runtime.stat().st_dev:
        raise RuntimeError('Metrics runtime mount device differs')
    return selected[0]


def parse_fdinfo(raw):
    fields = {}
    for line in raw.decode().splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            if key in fields:
                raise RuntimeError('Duplicate metrics fdinfo field')
            fields[key] = value.strip()
    return {k: int(fields[k], 8 if k == 'flags' else 10)
            for k in ('flags', 'mnt_id', 'ino')}


def fd_metadata(pid, number, evidence):
    evidence.update(number=number, errors={})
    def read(key, fn):
        try:
            evidence[key] = fn()
        except Exception as error:
            evidence['errors'][key] = error_record(error)
    path = Path('/proc') / str(pid) / 'fd' / str(number)
    def stat_record():
        current = path.stat()
        return {k: getattr(current, k) for k in
                ('st_mode', 'st_dev', 'st_ino', 'st_uid', 'st_gid',
                 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns')}
    read('stat', stat_record)
    read('target', lambda: os.readlink(path))
    read('rawFdinfo', lambda: raw_record(bounded(path.parent.parent / 'fdinfo' / str(number), 16384)))
    if 'rawFdinfo' in evidence:
        read('fdinfo', lambda: parse_fdinfo(base64.b64decode(evidence['rawFdinfo']['base64'], validate=True)))


def sample(evidence, browser, compositor, runtime, profile, candidate, frozen,
           guard, read_maps, initial_anchors):
    """Attach all raw/error observations before any metadata acceptance check."""
    evidence.update(errors={}, directories={}, matchingFDs=[], inventory=[])
    def read(key, fn):
        try:
            evidence[key] = fn()
        except Exception as error:
            evidence['errors'][key] = error_record(error)
    read('guardBefore', lambda: (guard(), True)[1])
    read('rootBefore', lambda: identity(browser, frozen))
    read('compositorBefore', lambda: identity(compositor, frozen))
    for key, path in [('runtime', runtime), ('profile', profile)]:
        try:
            evidence['directories'][key] = directory(path)
        except Exception as error:
            evidence['errors']['directory:' + key] = error_record(error)
    parent = {}; evidence['parentObservation'] = parent
    try:
        evidence['directories']['parent'] = parent_observation(profile, initial_anchors['profile'], parent)
    except Exception as error:
        evidence['errors']['directory:parent'] = error_record(error)
    proc = Path('/proc') / str(browser['pid'])
    read('rawMountinfo', lambda: raw_record(bounded(proc / 'mountinfo', 1024 * 1024)))
    if 'rawMountinfo' in evidence:
        read('mount', lambda: parse_mount(base64.b64decode(evidence['rawMountinfo']['base64'], validate=True), runtime))
    read('rootMaps', lambda: raw_record(read_maps(browser['pid'])))
    read('compositorMaps', lambda: raw_record(read_maps(compositor['pid'])))
    try:
        inventory = sorted(int(p.name) for p in (proc / 'fd').iterdir())
        if len(inventory) > MAX_FDS:
            raise RuntimeError('Metrics FD inventory exceeds bound')
        for number in inventory:
            row = {'number': number}; evidence['inventory'].append(row)
            try:
                current = (proc / 'fd' / str(number)).stat()
                row.update(device=current.st_dev, inode=current.st_ino)
                if (current.st_dev, current.st_ino) == (candidate['device'], candidate['inode']):
                    fd = {}; evidence['matchingFDs'].append(fd)
                    fd_metadata(browser['pid'], number, fd)
            except Exception as error:
                row['error'] = error_record(error)
                evidence['errors']['inventory:' + str(number)] = row['error']
    except Exception as error:
        evidence['errors']['inventory'] = error_record(error)
    read('rootAfter', lambda: identity(browser, frozen))
    read('compositorAfter', lambda: identity(compositor, frozen))
    read('guardAfter', lambda: (guard(), True)[1])


def stable_sample(evidence, candidate, initial_anchors):
    if evidence['errors']:
        raise RuntimeError('Metrics witness observation unavailable:' + str(evidence['errors']))
    if evidence['rootBefore'] != evidence['rootAfter'] or evidence['compositorBefore'] != evidence['compositorAfter']:
        raise RuntimeError('Metrics root/compositor lifetime changed')
    dirs = evidence['directories']
    if any(dirs[k] != initial_anchors[k] for k in ('runtime', 'profile')):
        raise RuntimeError('Metrics runtime/profile anchor changed')
    if 'parent' in initial_anchors and dirs['parent'] != initial_anchors['parent']:
        raise RuntimeError('Metrics BrowserMetrics parent anchor changed')
    if dirs['parent']['state'] == 'present' and dirs['parent']['device'] != dirs['runtime']['device']:
        raise RuntimeError('Metrics parent mount route differs')
    if len(evidence['matchingFDs']) != 1:
        raise RuntimeError('Exactly one matching root metrics FD required')
    fd = evidence['matchingFDs'][0]
    if fd['errors']:
        raise RuntimeError('Metrics FD metadata unavailable:' + str(fd['errors']))
    st, info = fd['stat'], fd['fdinfo']
    if (not stat.S_ISREG(st['st_mode']) or stat.S_IMODE(st['st_mode']) != 0o600 or
        st['st_uid'] != os.getuid() or st['st_nlink'] != 0 or st['st_size'] != SIZE):
        raise RuntimeError('Metrics FD regular/fullmode/UID/unlink/size differs')
    if fd['target'] != candidate['path'] or (st['st_dev'], st['st_ino']) != (candidate['device'], candidate['inode']):
        raise RuntimeError('Metrics FD target/device/inode differs')
    if (info['flags'] & os.O_ACCMODE) != os.O_RDWR or info['flags'] & os.O_PATH:
        raise RuntimeError('Metrics FD must be O_RDWR without O_PATH')
    mount = evidence['mount']
    if st['st_dev'] != mount['device'] or info['mnt_id'] != mount['id'] or info['ino'] != st['st_ino']:
        raise RuntimeError('Metrics FD mount/device/inode differs')
    page = os.sysconf('SC_PAGE_SIZE')
    if (candidate['permissions'] != 'rw-s' or candidate['offset'] != 0 or
        candidate['begin'] % page or candidate['end'] - candidate['begin'] != SIZE):
        raise RuntimeError('Metrics VMA must be aligned rw-s fullsize offset0')
    fresh_root = base64.b64decode(evidence['rootMaps']['base64'], validate=True)
    fresh_host = base64.b64decode(evidence['compositorMaps']['base64'], validate=True)
    if candidate not in maps(fresh_root):
        raise RuntimeError('Metrics root VMA changed')
    no_exec(candidate, [fresh_root, fresh_host])
    # Stable projection deliberately excludes mutable timestamps/content/FD pos.
    selected = {k: st[k] for k in ('st_mode', 'st_dev', 'st_ino', 'st_uid',
                                  'st_gid', 'st_nlink', 'st_size')}
    return {'root': evidence['rootBefore'], 'compositor': evidence['compositorBefore'],
            'directories': dirs, 'mount': mount, 'fd': fd['number'],
            'target': fd['target'], 'stat': selected, 'fdinfo': info,
            'mapping': candidate}


def revoke(proof):
    proof.update(accepted=False, usableForInput=False, confirmedAfterDiskValidation=False)
    for row in proof.get('observations', []):
        row['accepted'] = False


def observe(proof, batch, browser, compositor, runtime, profile, initial_anchors,
            frozen, guard, read_maps=None):
    revoke(proof)
    proof.update(mappings={}, observations=[], originalRoot=dict(browser),
                 scope='Exact captured root batch plus fresh root/compositor maps; not global or continuous')
    runtime, profile = Path(runtime), Path(profile)
    read_maps = read_maps or (lambda pid: bounded(Path('/proc') / str(pid) / 'maps'))
    try:
        guard()
        if browser['pid'] == compositor['pid']:
            raise RuntimeError('Metrics root and compositor roles must differ')
        if profile.parent != runtime or profile.name != 'browser-profile':
            raise RuntimeError('Exact private browser profile required')
        exact = [r for r in batch['processes'] if r['identity']['pid'] == browser['pid']
                 and str(r['identity']['start']) == str(browser['start'])]
        if len(exact) != 1 or exact[0].get('readError') or not exact[0].get('lifetimeBefore') or not exact[0].get('lifetimeAfter'):
            raise RuntimeError('One exact live readable captured browser maps row required')
        row = exact[0]; raw = base64.b64decode(row['rawMapsBase64'], validate=True)
        if raw.decode() != row['maps'] or len(raw) != row['rawMapsBytes'] or digest(raw) != row['rawMapsSHA256']:
            raise RuntimeError('Metrics captured raw snapshot binding differs')
        proof['rootRawMapsSHA256'] = digest(raw)
        prefix = str(profile / 'BrowserMetrics') + '/'
        candidates = [r for r in maps(raw) if r['path'].startswith(prefix) and r['path'].endswith(' (deleted)')]
        observed_raws = []
        for observed in batch['processes']:
            if observed.get('exitedBeforeObservation') or observed.get('exitedDuringObservation'):
                continue
            if observed.get('readError') or not observed.get('lifetimeBefore') or not observed.get('lifetimeAfter'):
                raise RuntimeError('Metrics owned batch alias observation unavailable')
            captured = base64.b64decode(observed['rawMapsBase64'], validate=True)
            if digest(captured) != observed['rawMapsSHA256'] or captured.decode() != observed['maps']:
                raise RuntimeError('Metrics owned batch raw binding differs')
            observed_raws.append(captured)
        if not candidates:
            # Absence is also refreshed after strict disk checking. An old empty
            # batch must not hide a newly appearing metrics VMA before input.
            proof['absenceSamples'] = []
            for _ in range(2):
                absence = {'errors': {}}; proof['absenceSamples'].append(absence)
                for key, fn in (
                    ('root', lambda: identity(browser, frozen)),
                    ('compositor', lambda: identity(compositor, frozen)),
                    ('runtime', lambda: directory(runtime)),
                    ('profile', lambda: directory(profile)),
                    ('rootMaps', lambda: raw_record(read_maps(browser['pid']))),
                    ('compositorMaps', lambda: raw_record(read_maps(compositor['pid'])))):
                    try:
                        absence[key] = fn()
                    except Exception as error:
                        absence['errors'][key] = error_record(error)
                guard()
            first, last = proof['absenceSamples']
            for absence in proof['absenceSamples']:
                if absence['errors']:
                    raise RuntimeError('Metrics absence observation unavailable')
                if any(absence[key] != initial_anchors[key] for key in ('runtime', 'profile')):
                    raise RuntimeError('Metrics absence runtime/profile anchor changed')
                if any(r['path'].startswith(prefix) and r['path'].endswith(' (deleted)')
                       for r in maps(base64.b64decode(absence['rootMaps']['base64'], validate=True))):
                    raise RuntimeError('New metrics mapping absent from captured root snapshot')
            if first['root'] != last['root'] or first['compositor'] != last['compositor']:
                raise RuntimeError('Metrics absence root/compositor lifetime changed')
            proof['absenceStable'] = {key: first[key] for key in ('root', 'compositor', 'runtime', 'profile')}
        for candidate in candidates:
            observation = {'mapping': candidate, 'accepted': False, 'before': {}, 'after': {}}
            proof['observations'].append(observation)
            # Both full observations precede assertions, including failing predicates.
            sample(observation['before'], browser, compositor, runtime, profile, candidate, frozen, guard, read_maps, initial_anchors)
            sample(observation['after'], browser, compositor, runtime, profile, candidate, frozen, guard, read_maps, initial_anchors)
            name = candidate['path'].removeprefix(prefix).removesuffix(' (deleted)')
            if not re.fullmatch(r'BrowserMetrics-[0-9A-F]+-' + format(browser['pid'], 'X') + r'\.pma', name):
                raise RuntimeError('Metrics canonical PID filename differs')
            no_exec(candidate, observed_raws)
            before = stable_sample(observation['before'], candidate, initial_anchors)
            after = stable_sample(observation['after'], candidate, initial_anchors)
            observation.update(stableBefore=before, stableAfter=after)
            if before != after:
                raise RuntimeError('Metrics immutable witness changed between snapshots')
            observation['accepted'] = True; proof['mappings'][candidate['line']] = observation
        guard()
        proof.update(accepted=True, noCandidate=not candidates)
        return proof
    except Exception as error:
        revoke(proof); proof['error'] = error_record(error)
        raise


def confirm(proof, batch, browser, compositor, runtime, profile, initial_anchors,
            frozen, guard, read_maps=None):
    prior = {line: row['stableBefore'] for line, row in proof.get('mappings', {}).items()}
    was_accepted = proof.get('accepted') is True
    revoke(proof)
    followup = {}; proof['afterDiskValidation'] = followup
    try:
        if not was_accepted:
            raise RuntimeError('Metrics partial or invalidated proof cannot confirm')
        observe(followup, batch, browser, compositor, runtime, profile, initial_anchors, frozen, guard, read_maps)
        if (not followup['accepted'] or proof['rootRawMapsSHA256'] != followup['rootRawMapsSHA256'] or
            proof['originalRoot'] != followup['originalRoot'] or
            proof.get('absenceStable') != followup.get('absenceStable') or
            prior != {line: row['stableBefore'] for line, row in followup['mappings'].items()}):
            raise RuntimeError('Metrics witness changed during strict disk validation')
        for row in proof['observations']:
            row['accepted'] = True
        if prior and 'parent' not in initial_anchors:
            initial_anchors['parent'] = next(iter(prior.values()))['directories']['parent']
        proof.update(accepted=True, usableForInput=True, confirmedAfterDiskValidation=True)
    except Exception as error:
        revoke(proof); proof['confirmationError'] = error_record(error)
        raise


def classification(proof, raw, line, observed_identity, runtime):
    """Only the original exact root row can consume this bounded witness."""
    if not proof or proof.get('accepted') is not True or observed_identity is None:
        return None
    original = proof.get('originalRoot', {})
    if (observed_identity.get('pid') != original.get('pid') or
        str(observed_identity.get('start')) != str(original.get('start')) or
        proof.get('rootRawMapsSHA256') != digest(raw.encode())):
        return None
    observation = proof.get('mappings', {}).get(line)
    if not observation or observation.get('accepted') is not True:
        return None
    mapping = observation.get('mapping', {})
    profile = Path(runtime) / 'browser-profile'
    name = mapping.get('path', '')
    prefix = str(profile / 'BrowserMetrics') + '/'
    if (mapping.get('line') != line or mapping.get('permissions') != 'rw-s' or
        mapping.get('offset') != 0 or mapping.get('end', 0) - mapping.get('begin', 0) != SIZE or
        not name.startswith(prefix) or not name.endswith(' (deleted)') or
        not re.fullmatch(r'BrowserMetrics-[0-9A-F]+-' + format(original['pid'], 'X') + r'\.pma',
                         name.removeprefix(prefix).removesuffix(' (deleted)'))):
        return None
    before, after = observation.get('stableBefore'), observation.get('stableAfter')
    if not before or before != after or before.get('mapping') != mapping:
        return None
    return {'path': name, 'permissions': 'rw-s', 'inode': mapping['inode'],
            'classification': 'Exact owned root-browser mutable unlinked tmpfs data; bounded observed snapshots, not disk code',
            'producerProof': observation}
