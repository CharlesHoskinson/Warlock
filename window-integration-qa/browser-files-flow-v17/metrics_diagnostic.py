"""Read-only owned browser data observations; never grants mapping authority."""
from pathlib import Path
import base64
import hashlib
import os
import re
import stat
from owned_shared_data import bounded, identity, maps

def raw_record(raw):
    return {'base64': base64.b64encode(raw).decode(), 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest()}

def observe(proof, batch, browser, profile, frozen, guard):
    proof.update(authorityGranted=False, observations=[], errors={}, completed=False)
    guard()
    proof['before'] = identity(browser, frozen)
    profile = Path(profile)
    st = profile.stat()
    proof['profile'] = {'path': str(profile), 'device': st.st_dev,
                        'inode': st.st_ino, 'uid': st.st_uid,
                        'fullMode': stat.S_IMODE(st.st_mode)}
    if not profile.is_dir() or st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) != 0o700:
        raise RuntimeError('Exact owned private browser profile required')
    rows = [r for r in batch['processes'] if r['identity']['pid'] == browser['pid']
            and str(r['identity']['start']) == str(browser['start'])]
    if len(rows) != 1 or rows[0].get('readError'):
        raise RuntimeError('One exact readable browser map snapshot required')
    raw = base64.b64decode(rows[0]['rawMapsBase64'], validate=True)
    proof['capturedMaps'] = raw_record(raw)
    prefix = str(profile / 'BrowserMetrics') + '/'
    candidates = [r for r in maps(raw) if r['path'].startswith(prefix)]
    proc = Path('/proc') / str(browser['pid'])
    fds = list((proc / 'fd').iterdir())
    if len(fds) > 4096:
        raise RuntimeError('Browser diagnostic FD inventory exceeds bound')
    proof['fdInventoryCount'] = len(fds)
    mount_raw = bounded(proc / 'mountinfo', 1024 * 1024)
    proof['rawMountinfo'] = raw_record(mount_raw)
    for mapping in candidates:
        result = {'mapping': mapping, 'matchingFDs': [], 'fdScanErrors': []}
        proof['observations'].append(result)
        name = mapping['path'].removesuffix(' (deleted)').removeprefix(prefix)
        result['filenamePIDMatches'] = bool(re.fullmatch(
            r'BrowserMetrics-[0-9A-F]+-' + format(browser['pid'], 'X') + r'\.pma', name))
        for path in fds:
            try:
                current = path.stat()
            except OSError as error:
                result['fdScanErrors'].append({'fd': path.name, 'errno': error.errno,
                                               'error': str(error)})
                continue
            if (current.st_dev, current.st_ino) != (mapping['device'], mapping['inode']):
                continue
            fd = {'number': int(path.name), 'errors': {}, 'stat': {
                key: getattr(current, key) for key in
                ('st_mode', 'st_dev', 'st_ino', 'st_nlink', 'st_uid', 'st_gid',
                 'st_size', 'st_mtime_ns', 'st_ctime_ns')}}
            result['matchingFDs'].append(fd)
            fd['stat'].update(regular=stat.S_ISREG(current.st_mode),
                              fullMode=stat.S_IMODE(current.st_mode))
            try:
                fd['target'] = os.readlink(path)
            except OSError as error:
                fd['errors']['target'] = {'errno': error.errno, 'error': str(error)}
            try:
                fd_raw = bounded(proc / 'fdinfo' / path.name, 16384)
                fd['rawFdinfo'] = raw_record(fd_raw)
                fields = {}
                for line in fd_raw.decode().splitlines():
                    if ':' in line:
                        key, value = line.split(':', 1)
                        if key in fields:
                            raise ValueError('Duplicate diagnostic fdinfo field')
                        fields[key] = value.strip()
                fd['fdinfo'] = {key: int(fields[key], 8 if key == 'flags' else 10)
                                for key in ('flags', 'mnt_id', 'ino')}
            except (OSError, ValueError, KeyError) as error:
                fd['errors']['fdinfo'] = {'errno': getattr(error, 'errno', None),
                                          'type': type(error).__name__, 'error': str(error)}
    guard()
    proof['freshMaps'] = raw_record(bounded(proc / 'maps'))
    proof['after'] = identity(browser, frozen)
    if proof['before'] != proof['after']:
        raise RuntimeError('Exact browser diagnostic lifetime changed')
    proof['completed'] = True
