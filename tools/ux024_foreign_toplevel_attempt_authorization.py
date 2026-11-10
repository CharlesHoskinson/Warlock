#!/usr/bin/env python3
"""Read-only current authorization and sealed per-attempt effect guards.

The caller pins this module and the core, supplies the freshly read canonical
record, and retains the separate live goal/stop/claim checks. No authority is
created here. Historical helpers are never mutated or given new globals.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import struct
import time

ROOT = Path('/home/hoskinson/Projects/Warlock')
RECORD = '.warlock-contributor/ux024-menu-tab-focus-root-20261109.json'
CORE = ROOT / 'plugins/warlock-contributor/scripts/warlock.py'
BASE = ROOT / 'tools/run_arm_gl_foundation_renewed_20261108_0623.py'
BASE_SHA = '769f48e13990909a88b588e3e145775b5ee16571a81817fac17eede1252bcdd2'
CAP = 65536
ATTEMPT_NS = 28_000_000_000
CLEANUP_NS = 2_000_000_000
_SEAL = object()


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate authorization field')
        result[key] = value
    return result


def _read_ref(ref):
    if not isinstance(ref, dict) or set(ref) != {'path', 'sha256'}:
        raise ValueError('exact authorization reference required')
    path = Path(ref['path'])
    if not path.is_absolute() or '..' in path.parts or path.resolve() != path:
        raise ValueError('canonical authorization path required')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > CAP or before.st_mode & 0o022:
            raise ValueError('bounded unwritable authorization file required')
        raw = stream.read(CAP + 1)
        after = os.fstat(stream.fileno())
    if (len(raw) > CAP or len(raw) != before.st_size
            or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) !=
               (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            or hashlib.sha256(raw).hexdigest() != ref['sha256']):
        raise ValueError('authorization bytes changed or hash differs')
    return json.loads(raw.decode('utf-8', errors='strict'), object_pairs_hook=_unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite authorization')))


def _utc_ns(value):
    if not isinstance(value, str) or not value.endswith('Z'):
        raise ValueError('explicit UTC authorization required')
    parsed = datetime.fromisoformat(value[:-1] + '+00:00')
    delta = parsed - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (delta.days * 86400 + delta.seconds) * 1_000_000_000 + delta.microseconds * 1000


@dataclass(frozen=True, slots=True)
class AttemptAuthorization:
    expires_utc: str
    expires_ns: int
    evidence_sha256: str
    record_identity: str
    selection: int
    event_sha256: str
    goal_definition: tuple
    participant_started_utc: str
    _seal: object


def resolve_authorization(ref, record, identity, selection, core):
    data = _read_ref(ref)
    fields = {'schema', 'kind', 'recordPath', 'recordIdentitySha256', 'selectionGeneration',
              'authorizationExpiresUTC', 'authorizationEventSha256', 'coreSha256',
              'goalDefinition', 'participantStartedUTC'}
    if (not isinstance(data, dict) or set(data) not in (fields,fields|{'goalObservation'}) or type(data['schema']) is not int
            or data['schema'] != 1 or data['kind'] != 'ux003-current-attempt-authorization'
            or data['recordPath'] != RECORD or data['recordIdentitySha256'] != identity
            or type(selection) is not int or type(data['selectionGeneration']) is not int
            or data['selectionGeneration'] != selection):
        raise ValueError('authorization record or selection differs')
    if Path(core.__file__) != CORE or hashlib.sha256(CORE.read_bytes()).hexdigest() != data['coreSha256']:
        raise ValueError('authorization core source differs')
    if core.record_identity(record, RECORD) != identity:
        raise ValueError('current canonical record identity differs')
    expiry = core.effective_delivery_authorization(record)
    events = [event for event in record['delivery']['events'] if event.get('kind') == 'authorization-renewed']
    if (not events or data['authorizationExpiresUTC'] != expiry
            or core.json_sha256(events[-1]) != data['authorizationEventSha256']):
        raise ValueError('authorization differs from latest canonical renewal')
    evidence = json.loads(core.delivery_ref(ROOT, events[-1]['evidence']), object_pairs_hook=_unique)
    goal_receipt = json.loads(core.delivery_ref(ROOT, evidence['goalObservation']), object_pairs_hook=_unique)
    if 'goalObservation' in data:
        actual = _read_ref(data['goalObservation'])
        response = actual.get('actualToolResponse') if isinstance(actual,dict) else None
        goal = response.get('goal') if isinstance(response,dict) else None
        if (not isinstance(goal,dict) or goal_receipt.get('status') != 'active'
                or goal_receipt.get('thread') != goal.get('threadId')
                or goal_receipt.get('objective') != goal.get('objective')):
            raise ValueError('actual tool goal differs from immutable canonical renewal observation')
        goal_thread = goal_receipt.get('thread')
    else:
        goal = goal_receipt.get('actualRPC', {}).get('goalResponse', {}).get('result', {}).get('goal')
        goal_thread = goal_receipt.get('threadId')
    if (not isinstance(goal, dict) or goal_receipt.get('status') != 'active'
            or goal.get('status') != 'active' or type(goal.get('createdAt')) is not int
            or not isinstance(goal.get('objective'), str) or not goal['objective']
            or not isinstance(goal.get('threadId'), str) or not goal['threadId']
            or goal_thread != goal['threadId']):
        raise ValueError('canonical renewal lacks the actual stable active-goal definition')
    definition = {'threadId': goal['threadId'], 'createdAt': goal['createdAt'],
                  'objectiveSha256': hashlib.sha256(goal['objective'].encode('utf-8')).hexdigest()}
    if (data['goalDefinition'] != definition
            or type(data['goalDefinition'].get('createdAt')) is not int
            or not isinstance(record.get('startedUTC'), str)
            or data['participantStartedUTC'] != record['startedUTC']
            or evidence.get('startedUTC') != record['startedUTC']):
        raise ValueError('stable goal definition or participant start differs')
    horizon = _utc_ns(expiry)
    if time.time_ns() + ATTEMPT_NS + CLEANUP_NS >= horizon:
        raise TimeoutError('insufficient canonical authorization for original28+cleanup2')
    return AttemptAuthorization(expiry, horizon, ref['sha256'], identity, selection,
                                data['authorizationEventSha256'], tuple(sorted(definition.items())),
                                record['startedUTC'], _SEAL)


def authorization_deadline_ns(authority):
    if isinstance(authority, SealedClock):
        return clock_authorization_deadline_ns(authority)
    if not isinstance(authority, AttemptAuthorization) or authority._seal is not _SEAL:
        raise ValueError('resolved attempt authority required')
    return authority.expires_ns


class SealedClock(dict):
    """The issued horizon and original clock tuple cannot be replaced by a renewal."""
    __slots__ = ('_authority', '_issued')

    def __init__(self, clock, authority):
        authorization_deadline_ns(authority)
        for field in ('origin', 'deadline', 'last'):
            if type(clock.get(field)) is not int:
                raise ValueError('exact original clock integers required')
        if (not isinstance(clock.get('boot'), str) or not clock['boot']
                or clock['deadline'] - clock['origin'] != ATTEMPT_NS
                or not clock['origin'] <= clock['last'] < clock['deadline']):
            raise ValueError('original28 clock required')
        dict.__init__(self, clock)
        dict.__setitem__(self, 'authorizationExpiresNs', authority.expires_ns)
        dict.__setitem__(self, 'authorizationEvidenceSha256', authority.evidence_sha256)
        object.__setattr__(self, '_authority', authority)
        object.__setattr__(self, '_issued', (clock['origin'], clock['deadline'], clock['boot']))

    def __setattr__(self, name, value):
        raise AttributeError('issued clock seal is immutable')

    def copy(self):
        clock_authorization_deadline_ns(self)
        # Do not reissue or reject an expired D during cleanup copying.
        other = dict.__new__(SealedClock)
        dict.__init__(other, self)
        object.__setattr__(other, '_authority', self._authority)
        object.__setattr__(other, '_issued', self._issued)
        return other


def seal_clock(clock, authority):
    if isinstance(clock, SealedClock):
        clock_authorization_deadline_ns(clock)
        if clock._authority != authority:
            raise ValueError('an issued attempt cannot be resealed to a renewal')
        return clock.copy()
    return SealedClock(clock, authority)


def clock_authorization_deadline_ns(clock):
    if not isinstance(clock, SealedClock):
        raise ValueError('sealed original attempt clock required')
    horizon = authorization_deadline_ns(clock._authority)
    if ((clock.get('origin'), clock.get('deadline'), clock.get('boot')) != clock._issued
            or clock.get('authorizationExpiresNs') != horizon
            or clock.get('authorizationEvidenceSha256') != clock._authority.evidence_sha256):
        raise ValueError('issued clock or authorization was changed')
    return horizon


def _boot():
    return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


# These fixed delegates have no reachable dependency on the old wall-expiry
# constant. registry has its own explicit implementation below; main is absent.
_DELEGATES = frozenset({'sha', 'unique', 'regular', 'remaining', 'cleanup_ceiling',
    'clean_environment', 'device_identity', 'graphics_shape', 'verify_graphics',
    'graphics_environment', 'graphics_fds', 'missing_protocols', 'parse_registry',
    'process_birth', 'check_process', 'mapped', 'private_soname', 'bound_output',
    'GRAPHICS', 'REQUIRED', 'CAP'})


class _EffectBase:
    __slots__ = ('_base', '_authority')

    def __init__(self, base, authority):
        authorization_deadline_ns(authority)
        if Path(base.__file__) != BASE or hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA:
            raise ValueError('fixed historical effect primitives required')
        object.__setattr__(self, '_base', base)
        object.__setattr__(self, '_authority', authority)

    def __setattr__(self, name, value):
        raise AttributeError('effect authority is immutable')

    def __getattr__(self, name):
        if name not in _DELEGATES:
            raise AttributeError(name)
        return getattr(self._base, name)

    def left(self, clock):
        horizon = clock_authorization_deadline_ns(clock)
        if clock._authority != self._authority:
            raise ValueError('effect clock belongs to another authorization')
        if time.time_ns() >= horizon:
            raise TimeoutError('issued authorization expired')
        return self._base.remaining(clock, time.monotonic_ns(), _boot()) / 1e9

    def registry(self, path, proc, birth, image, clock):
        before = path.lstat()
        if not stat.S_ISSOCK(before.st_mode) or before.st_uid != os.getuid():
            raise ValueError('owned private Wayland socket required')
        self.check_process(proc, birth, image)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(self.left(clock))
            client.connect(str(path))
            pid, uid, _ = struct.unpack('3i', client.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
            if pid != proc.pid or uid != os.getuid():
                raise ValueError('foreign Wayland peer')
            client.sendall(struct.pack('<IIIIII', 1, (12 << 16) | 1, 2, 1, 12 << 16, 3))
            data = bytearray()
            while True:
                client.settimeout(self.left(clock))
                block = client.recv(min(4096, CAP + 1 - len(data)))
                if not block or len(data) + len(block) > CAP:
                    raise ValueError('registry EOF/output cap')
                data.extend(block)
                cursor = 0
                while cursor + 8 <= len(data):
                    packed = struct.unpack_from('<I', data, cursor + 4)[0]
                    size = packed >> 16
                    if size < 8 or size % 4:
                        raise ValueError('malformed Wayland frame')
                    if cursor + size > len(data):
                        break
                    cursor += size
                if cursor == len(data):
                    globals_, done = self.parse_registry(data)
                    if done:
                        break
        after = path.lstat()
        if (before.st_dev, before.st_ino, before.st_uid) != (after.st_dev, after.st_ino, after.st_uid):
            raise ValueError('Wayland socket replaced')
        self.check_process(proc, birth, image)
        return {'path': str(path), 'device': before.st_dev, 'inode': before.st_ino, 'pid': proc.pid,
                'startTicks': birth, 'globals': globals_}


def effect_base(base, authority):
    return _EffectBase(base, authority)
