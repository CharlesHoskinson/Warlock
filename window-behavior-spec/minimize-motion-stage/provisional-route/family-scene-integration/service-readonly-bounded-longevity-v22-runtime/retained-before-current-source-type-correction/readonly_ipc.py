"""Five owned read-only IPC requests; import creates no resources."""
from contextlib import nullcontext
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import socket
import stat
import struct
import subprocess
import threading
import time
import re

from recovery_resources import material_path, process_start
from readonly_archive import ArchiveStore, segment_chain
from readonly_current import CurrentReads, CurrentReadWitness
import readonly_current

MAX_REPLY = 1048576
MAX_HISTORY = 512
REQUESTS = {
    ('clients', '-j'): (b'j/clients', list),
    ('monitors', '-j'): (b'j/monitors', list),
    ('workspaces', '-j'): (b'j/workspaces', list),
    ('activewindow', '-j'): (b'j/activewindow', dict),
    ('repl', 'print(hl.plugin.hyprbars.window_families())'):
        (b'/repl print(hl.plugin.hyprbars.window_families())', list),
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


class ReadonlyIPC:
    def __init__(self, root, guard, lease_verify, record, *, reservation_lock=None, predecessor=None):
        from native_runtime import NativeSession
        from service_runtime import RuntimeLease
        lease = getattr(lease_verify, '__self__', None)
        if type(guard) is not NativeSession or type(lease) is not RuntimeLease or getattr(lease_verify, '__func__', None) is not RuntimeLease.verify:
            raise ValueError('actual bound NativeSession and RuntimeLease required')
        if Path(root) != lease.root or guard.session != lease.session:
            raise ValueError('selected read-only root/session differs')
        self.root = Path(root)
        self.guard = guard
        self.lease = lease
        self.record = record
        self.reservation_lock = reservation_lock or nullcontext()
        self.lock = threading.RLock()
        self.rows = {}
        self.serial = 0
        self.epoch = 0
        self.tip = None
        self.predecessor = deepcopy(predecessor)
        self.references = set()
        self.local = threading.local()
        self.rotation = threading.Lock()
        self.archive = ArchiveStore(self.root, lease.root_identity, create=True)
        self.fault = False
        self.source = material_path(__file__)
        self.session_source = material_path(Path(__file__).with_name('native_runtime.py'))
        self.archive_source = material_path(Path(__file__).with_name('readonly_archive.py'))
        self.current_source = material_path(readonly_current.__file__)
        selected = shutil.which('hyprctl', path=guard.env.get('PATH'))
        if selected is None:
            raise FileNotFoundError('selected hyprctl')
        self.executable = str(Path(selected).absolute())
        if Path(self.executable).resolve() != Path(self.executable):
            raise ValueError('canonical selected hyprctl required')
        self.executable_material = material_path(self.executable)
        self.socket_path = guard.sockets[0]
        info = self.socket_path.lstat()
        self.socket_identity = [info.st_dev, info.st_ino]
        self.issuer = {
            'pid': os.getpid(), 'start': process_start(os.getpid()),
            'uid': os.getuid(), 'root': str(self.root),
            'rootIdentity': list(lease.root_identity),
            'lockIdentity': list(lease.lock_identity), 'nonce': lease.nonce,
            'session': lease.session,
            'environment': {k: guard.env[k] for k in
                            ('XDG_RUNTIME_DIR', 'HYPRLAND_INSTANCE_SIGNATURE', 'WAYLAND_DISPLAY')},
            'compositorPID': guard.pid, 'compositorStart': guard.start,
            'socket': str(self.socket_path), 'socketIdentity': self.socket_identity,
            'adapter': self.source, 'sessionSource': self.session_source,
            'archiveSource': self.archive_source, 'currentSource': self.current_source,
            'executable': self.executable, 'executableMaterial': self.executable_material,
        }
        self.current = None
        self.authority()  # Full history before constructing any current-only proof.
        self.current = CurrentReads(self.archive, self.lease, self.issuer, self.predecessor)
        with self.reservation_lock, self.lock:
            self.publish()

    def snapshot(self):
        return {'version': 2, 'issuer': deepcopy(self.issuer),
                'history': deepcopy(list(self.rows.values())), 'fault': self.fault,
                'serial': self.serial, 'epoch': self.epoch, 'archiveTip': deepcopy(self.tip),
                'archiveDirectory': deepcopy(self.archive.directory),
                'predecessor': deepcopy(self.predecessor)}

    def assert_closed(self):
        if not self.rotation.acquire(blocking=False):
            raise ValueError('read-only append incomplete; normal shutdown refused')
        try:
            with self.reservation_lock,self.lock:
                if self.fault or self.references or any(r['closed'] is not True or r['published'] is not True or r['outcome'] not in ('complete','refused') for r in self.rows.values()):
                    raise ValueError('read-only connection closure incomplete; normal shutdown refused')
            self.audit_history()  # Older unborrowed mutation must refuse normal closure.
            self.current.close()
        finally:
            self.rotation.release()

    def publish(self):
        try:
            self.record(self.snapshot())
        except BaseException:
            self.fault = True
            raise

    def authority(self):
        if self.fault:
            raise ValueError('read-only journal failed; authority revoked')
        self.lease.verify()
        self.guard.verify()
        if (self.guard.pid,self.guard.start,self.guard.session)!=(self.issuer['compositorPID'],self.issuer['compositorStart'],self.issuer['session']) or any(self.guard.env.get(k)!=v for k,v in self.issuer['environment'].items()):
            raise ValueError('selected compositor/session identity changed')
        if self.lease.root!=self.root or list(self.lease.root_identity)!=self.issuer['rootIdentity'] or list(self.lease.lock_identity)!=self.issuer['lockIdentity'] or self.lease.nonce!=self.issuer['nonce'] or any(self.lease.owner.get(k)!=v for k,v in [('pid',self.issuer['pid']),('start',self.issuer['start']),('nonce',self.issuer['nonce']),('session',self.issuer['session'])]):
            raise ValueError('selected runtime lease identity changed')
        if os.getpid() != self.issuer['pid'] or process_start(os.getpid()) != self.issuer['start']:
            raise ValueError('read-only service lifetime changed')
        if self.socket_path.resolve() != self.socket_path.absolute():
            raise ValueError('selected control socket alias refused')
        info = self.socket_path.lstat()
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid() or [info.st_dev, info.st_ino] != self.socket_identity:
            raise ValueError('selected control socket identity changed')
        if material_path(__file__) != self.source or material_path(Path(__file__).with_name('native_runtime.py')) != self.session_source or material_path(Path(__file__).with_name('readonly_archive.py')) != self.archive_source:
            raise ValueError('reviewed read-only/session source changed')
        if shutil.which('hyprctl', path=self.guard.env.get('PATH')) != self.executable or material_path(self.executable) != self.executable_material:
            raise ValueError('selected hyprctl executable changed')
        try:
            self.archive.verify()
            with self.reservation_lock, self.lock:
                retained = self.snapshot()
            validate_storage(retained, root=self.root, environment=self.issuer['environment'], guard=self.guard)
        except BaseException:
            self.fault = True
            raise
        return digest(self.issuer)

    def _read_owner(self):
        if self.fault:
            raise ValueError('read-only journal failed; authority revoked')
        self.lease.verify()
        self.guard.verify()
        if (self.guard.pid,self.guard.start,self.guard.session)!=(self.issuer['compositorPID'],self.issuer['compositorStart'],self.issuer['session']) or any(self.guard.env.get(k)!=v for k,v in self.issuer['environment'].items()):
            raise ValueError('selected compositor/session identity changed')
        if self.lease.root!=self.root or list(self.lease.root_identity)!=self.issuer['rootIdentity'] or list(self.lease.lock_identity)!=self.issuer['lockIdentity'] or self.lease.nonce!=self.issuer['nonce'] or any(self.lease.owner.get(k)!=v for k,v in [('pid',self.issuer['pid']),('start',self.issuer['start']),('nonce',self.issuer['nonce']),('session',self.issuer['session'])]):
            raise ValueError('selected runtime lease identity changed')
        if os.getpid() != self.issuer['pid'] or process_start(os.getpid()) != self.issuer['start']:
            raise ValueError('read-only service lifetime changed')
        if self.socket_path.resolve() != self.socket_path.absolute():
            raise ValueError('selected control socket alias refused')
        info = self.socket_path.lstat()
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid() or [info.st_dev, info.st_ino] != self.socket_identity:
            raise ValueError('selected control socket identity changed')
        if material_path(__file__) != self.source or material_path(Path(__file__).with_name('native_runtime.py')) != self.session_source or material_path(Path(__file__).with_name('readonly_archive.py')) != self.archive_source or material_path(readonly_current.__file__) != self.current_source:
            raise ValueError('reviewed read-only/session source changed')
        if shutil.which('hyprctl', path=self.guard.env.get('PATH')) != self.executable or material_path(self.executable) != self.executable_material:
            raise ValueError('selected hyprctl executable changed')
        return digest(self.issuer)

    def audit_history(self):
        """Explicit full historical verification; current-data proofs never substitute."""
        return self.authority()

    def _current_authority(self, *, borrow=False):
        """Typed current-only result, exclusively fresh data/owned archive publication."""
        latest = None
        try:
            issuer = self._read_owner()
            self.current.verify_owner(self.lease, self.issuer, self.predecessor)
            with self.reservation_lock, self.lock:
                latest = self.current.acquire_latest(self.tip, self.epoch)
                snapshot = self.snapshot()
                fields = {'version', 'issuer', 'history', 'fault', 'serial', 'epoch',
                          'archiveTip', 'archiveDirectory', 'predecessor'}
                if (not isinstance(snapshot, dict) or set(snapshot) != fields or
                        type(snapshot['version']) is not int or snapshot['version'] != 2 or
                        snapshot['fault'] is not False or type(snapshot['serial']) is not int or
                        snapshot['serial'] < 0 or type(snapshot['epoch']) is not int or snapshot['epoch'] < 0 or
                        not isinstance(snapshot['issuer'], dict) or
                        not readonly_current.same_material(snapshot['issuer'], self.issuer) or
                        not readonly_current.same_material(snapshot['archiveDirectory'], self.archive.directory) or
                        not readonly_current.same_material(snapshot['predecessor'], self.predecessor) or
                        not readonly_current.same_material(snapshot['archiveTip'], self.tip)):
                    raise ValueError('complete unfaulted typed current archival dataset required')
                for pointer in (snapshot['archiveTip'], snapshot['predecessor']):
                    if pointer is not None: self.archive.check_pointer(pointer)
                frames = getattr(self.local, 'borrowed', None)
                if borrow and (not isinstance(frames, list) or not frames or
                               not getattr(self.local, 'frames', None)):
                    raise ValueError('current borrowing requires owned live query frame')
                borrowed = frames[-1] if frames else None
                if borrow and borrowed is None:
                    borrowed = self.current.acquire_latest(self.tip, self.epoch, borrow=True,limit=MAX_HISTORY)
                    frames[-1] = borrowed
            token = latest.token.verify()
            _validate_rows(snapshot['history'], self.issuer, root=self.root,
                           environment=self.issuer['environment'], guard=self.guard)
            if (token['issuerSHA256'] != issuer or token['archivedCount'] + len(snapshot['history']) != snapshot['serial'] or
                    any(row['serial'] > snapshot['serial'] for row in snapshot['history'])):
                raise ValueError('bounded current row/count/issuer binding changed')
            body = latest.verify(self.archive, self.current.directory_fd)
            if body is not None:
                fields = {'version','kind','issuerSHA256','epoch','previous','rows','first','last'}
                rows = body.get('rows')
                if set(body) != fields or not isinstance(rows,list) or not rows or len(rows)>MAX_HISTORY:
                    raise ValueError('complete bounded current segment required')
                _validate_rows(rows,self.issuer,root=self.root,environment=self.issuer['environment'],guard=self.guard)
                if (any(not(row['closed'] and row['published']) or row['outcome'] not in ('complete','refused') for row in rows) or
                        type(body['first']) is not int or type(body['last']) is not int or
                        body['first'] != rows[0]['serial'] or body['last'] != rows[-1]['serial'] or
                        {row['id'] for row in rows}.intersection(row['id'] for row in snapshot['history'])):
                    raise ValueError('bounded current segment interval/closure/rows differ')
            witness = self.current.witness(latest,borrowed or latest,self.issuer)
            if type(witness) is not CurrentReadWitness or witness.issuerSHA256 != issuer:
                raise ValueError('typed current-only witness required')
            self._read_owner()
            self.current.verify_owner(self.lease,self.issuer,self.predecessor)
            return witness
        except BaseException:
            self.fault = True
            raise
        finally:
            if latest is not None:self.current.release(latest)

    def ensure_capacity(self, remaining):
        with self.reservation_lock, self.lock:
            if self.fault: raise ValueError('read-only authority revoked')
            if len(self.rows) < MAX_HISTORY: return
        self.rotate_closed(remaining)

    def rotate_closed(self, remaining):
        # The same guarded rotation also supports proactive owned maintenance.
        if not self.rotation.acquire(timeout=remaining()):
            raise TimeoutError('read-only complete reply absolute deadline')
        prepared = None
        adopted = False
        try:
            before = self._current_authority().issuerSHA256
            remaining()
            with self.reservation_lock, self.lock:
                candidates = [deepcopy(row) for identifier, row in self.rows.items()
                              if identifier not in self.references and row['closed'] is True and
                              row['published'] is True and row['outcome'] in ('complete', 'refused')]
                if not candidates:
                    raise ValueError('complete bounded history has no reclaimable closed rows')
                old_tip = deepcopy(self.tip)
                old_epoch = self.epoch
            body = {'version': 1, 'kind': 'segment', 'issuerSHA256': before,
                    'epoch': old_epoch + 1, 'previous': old_tip, 'rows': candidates,
                    'first': candidates[0]['serial'], 'last': candidates[-1]['serial']}
            # All filesystem/source/peer observations precede the short publication lock.
            pointer = self.archive.write(body)
            if self._current_authority().issuerSHA256 != before: raise ValueError('archive issuer changed during write')
            old_token = self.current.latest.token.verify()
            prepared = self.current.prepare(pointer,old_tip,old_epoch+1,old_token['archivedCount']+len(candidates),self.issuer)
            remaining()
            with self.reservation_lock, self.lock:
                if (self.fault or self.tip != old_tip or self.epoch != old_epoch or
                        any(self.rows.get(row['id']) != row or row['id'] in self.references for row in candidates)):
                    raise ValueError('archive plan no longer bound to exact closed rows')
                compact = self.snapshot()
                compact['history'] = [r for r in compact['history'] if r['id'] not in {v['id'] for v in candidates}]
                compact['archiveTip'] = pointer
                compact['epoch'] = old_epoch + 1
                self.record(compact)  # Durable tip before any in-memory reclamation.
                self.current.adopt(prepared,old_tip)
                adopted = True
                self.tip = deepcopy(pointer)
                self.epoch = old_epoch + 1
                for row in candidates: del self.rows[row['id']]
            if self._current_authority().issuerSHA256 != before: raise ValueError('archive owner changed after publication')
            remaining()
        except BaseException:
            self.fault = True
            raise
        finally:
            if prepared is not None and not adopted: prepared.close()
            self.rotation.release()

    def register(self, row):
        with self.reservation_lock, self.lock:
            if self.fault or len(self.rows) >= MAX_HISTORY or row['id'] in self.rows:
                raise ValueError('complete bounded read-only history cannot register')
            if any(r['outcome'] == 'refused' and not(r['closed'] and r['published']) for r in self.rows.values()):
                raise ValueError('unfinished refusal blocks a new connection')
            if not getattr(self.local, 'frames', None):
                raise ValueError('registration requires owned live query reference')
            self.serial += 1
            row['serial'] = self.serial
            row['id'] = f'{self.serial:032x}'
            self.references.add(row['id'])
            self.local.frames[-1].add(row['id'])
            self.rows[row['id']] = deepcopy(row)
            self.publish()  # The owned descriptor is still unconnected.

    def finish(self, identifier, *, closed, outcome, evidence, error):
        with self.reservation_lock, self.lock:
            row = self.rows[identifier]
            if row['outcome'] == 'refused' and outcome == 'complete':
                raise ValueError('connection refusal is terminal')
            row.update(closed=closed, outcome=outcome, evidence=deepcopy(evidence),
                       error=error, finishedNs=time.monotonic_ns(), published=True)
            self.publish()

    def query(self, wire, shape, timeout, actor):
        frames = getattr(self.local, 'frames', None)
        if frames is None: self.local.frames = frames = []
        owned = set()
        frames.append(owned)
        borrowed = getattr(self.local,'borrowed',None)
        if borrowed is None:self.local.borrowed = borrowed = []
        borrowed.append(None)
        try:
            return self._query(wire, shape, timeout, actor)
        finally:
            with self.reservation_lock, self.lock:
                self.references.difference_update(owned)
            tip = borrowed.pop()
            if tip is not None:self.current.release(tip,borrow=True)
            if frames.pop() is not owned:
                self.fault = True
                raise ValueError('query reference stack changed')

    def _query(self, wire, shape, timeout, actor):
        if (wire, shape) not in REQUESTS.values() or type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('exact fixed request and positive absolute timeout required')
        if actor is not None and (type(actor) is not int or actor < 1):
            raise ValueError('typed caller actor or explicit service owner required')
        deadline = time.monotonic() + timeout
        def remaining():
            value = deadline - time.monotonic()
            if value <= 0:
                raise TimeoutError('read-only complete reply absolute deadline')
            return value
        before = self._current_authority(borrow=True).issuerSHA256
        remaining()
        self.ensure_capacity(remaining)
        remaining()
        connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        connection.set_inheritable(False)
        info = os.fstat(connection.fileno())
        identifier = None
        row = {'id': identifier, 'actor': actor,
               'thread': threading.get_native_id(), 'fd': connection.fileno(),
               'fdIdentity': [info.st_dev, info.st_ino],
               'issuerSHA256': before, 'request': wire.decode('ascii'),
               'requestSHA256': hashlib.sha256(wire).hexdigest(),
               'registeredNs': time.monotonic_ns(), 'closed': False,
               'published': True, 'outcome': 'pending', 'evidence': None, 'error': None}
        registered = False
        data = bytearray()
        evidence = {'completeServerEOF': False, 'replyBytes': 0, 'replySHA256': None,
                    'peer': None, 'socketIdentity': self.socket_identity}
        error = None
        try:
            self.register(row)
            identifier = row['id']
            registered = True
            connection.settimeout(remaining())
            connection.connect(str(self.socket_path))
            pid, uid, gid = struct.unpack('3i', connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
            evidence['peer'] = {'pid': pid, 'uid': uid, 'gid': gid}
            current = self.socket_path.lstat()
            if pid != self.guard.pid or uid != os.getuid() or [current.st_dev, current.st_ino] != self.socket_identity or process_start(pid) != self.guard.start:
                raise ValueError('read-only connection is not exact selected peer/socket/lifetime')
            connection.settimeout(remaining())
            connection.sendall(wire)
            while True:
                connection.settimeout(remaining())
                chunk = connection.recv(min(65536, MAX_REPLY + 1 - len(data)))
                if not chunk:
                    evidence['completeServerEOF'] = True
                    break
                data.extend(chunk)
                if len(data) > MAX_REPLY:
                    raise ValueError('read-only reply exceeds bound')
            text = data.decode('utf-8', errors='strict')
            decoded = json.loads(text)
            if type(decoded) is not shape or isinstance(decoded, dict) and 'error' in decoded:
                raise ValueError('read-only reply has wrong complete JSON shape')
            remaining()
        except BaseException as failure:
            error = failure
        finally:
            try:connection.close()
            except BaseException as failure:
                if error is None:error=failure
        evidence.update(replyBytes=len(data), replySHA256=hashlib.sha256(data).hexdigest())
        if not registered:
            # A failed registration publication is already latched; no send.
            if error is not None:
                raise error
            raise RuntimeError('unregistered read-only connection')
        try:
            if error is None and self._current_authority().issuerSHA256 != before:
                raise ValueError('read-only owner changed before confirmation')
            if error is None:
                remaining()
        except BaseException as failure:
            error = failure
        self.finish(identifier, closed=connection.fileno() == -1,
                    outcome='refused' if error else 'complete', evidence=evidence,
                    error=None if error is None else {'type': type(error).__name__, 'message': str(error)[:512]})
        if error is not None:
            raise error
        try:
            if self._current_authority().issuerSHA256 != before:
                raise ValueError('read-only owner changed after disk confirmation')
            remaining()
            with self.reservation_lock,self.lock:
                current=self.rows[identifier]
                if self.fault or current['outcome']!='complete' or current['closed'] is not True or current['published'] is not True or current['issuerSHA256']!=before or current['evidence']!=evidence:
                    raise ValueError('read-only result lacks exact durable closed confirmation')
        except BaseException as failure:
            self.finish(identifier, closed=True, outcome='refused', evidence=evidence,
                        error={'type': type(failure).__name__, 'message': str(failure)[:512]})
            raise
        return bytes(data)

    def run(self, args, *, actor, env, input, capture_output, timeout, check, options):
        selected = REQUESTS.get(tuple(args[1:]))
        if args[0] not in ('hyprctl', self.executable) or selected is None:
            return None
        if capture_output and ('stdout' in options or 'stderr' in options):
            raise ValueError('capture output conflicts')
        if input is not None or set(options) - {'stdout', 'stderr', 'text'} or options.get('stdout') != subprocess.PIPE and not capture_output:
            return None
        if any(env.get(k) != self.guard.env[k] for k in self.issuer['environment']):
            raise ValueError('read-only selected environment differs')
        raw = self.query(*selected, timeout, actor)
        stdout = raw.decode('utf-8') if options.get('text') else raw
        stderr = ('' if options.get('text') else b'') if capture_output or options.get('stderr') == subprocess.PIPE else None
        return subprocess.CompletedProcess(args, 0, stdout, stderr)


def _checked_active(value, *, root, environment, keeper, guard):
    """Validate old data provenance before inherited old-owner/group retirement.

    Pending rows supply no returned observation. Old service/whole Keeper and
    resource closure still belong to the unchanged recovery coordinator.
    """
    if not isinstance(value,dict) or set(value)!={'version','issuer','history','fault'} or type(value['version']) is not int or value['version']!=1 or value['fault'] is not False:
        raise ValueError('complete unfaulted retained read-only ownership required')
    issuer=value['issuer']
    keys={'pid','start','uid','root','rootIdentity','lockIdentity','nonce','session','environment','compositorPID','compositorStart','socket','socketIdentity','adapter','sessionSource','executable','executableMaterial'}
    if not isinstance(issuer,dict) or set(issuer)!=keys:
        raise ValueError('complete retained read-only issuer required')
    for name in ('pid','start','compositorPID','compositorStart'):
        if type(issuer[name]) is not int or issuer[name]<1:raise ValueError('typed retained service/compositor lifetime required')
    if issuer['pid']!=keeper['servicePID'] or issuer['start']!=keeper['serviceStart'] or issuer['uid']!=os.getuid() or type(issuer['uid']) is not int or issuer['root']!=str(root) or issuer['rootIdentity']!=keeper['rootIdentity'] or issuer['environment']!=environment or issuer['session']!=guard.session or issuer['compositorPID']!=guard.pid or issuer['compositorStart']!=guard.start:
        raise ValueError('retained read-only ownership belongs to another service/root/session')
    if type(issuer['nonce']) is not str or re.fullmatch('[0-9a-f]{32}',issuer['nonce']) is None:raise ValueError('retained exact lease nonce required')
    for name in ('rootIdentity','lockIdentity','socketIdentity'):
        ident=issuer[name]
        if not isinstance(ident,list) or len(ident)!=2 or any(type(v) is not int or v<0 for v in ident) or ident[1]<1:raise ValueError('retained typed inode required')
    for where,name in [(Path(root),'rootIdentity'),(Path(root)/'runtime.lock','lockIdentity'),(guard.sockets[0],'socketIdentity')]:
        info=where.lstat()
        if [info.st_dev,info.st_ino]!=issuer[name]:raise ValueError('retained namespace inode replaced')
    if issuer['socket']!=str(guard.sockets[0]) or guard.sockets[0].resolve()!=guard.sockets[0].absolute():raise ValueError('retained selected control socket alias differs')
    if digest(issuer['adapter'])!=digest(material_path(__file__)) or digest(issuer['sessionSource'])!=digest(material_path(Path(__file__).with_name('native_runtime.py'))):raise ValueError('retained read-only source is not this reviewed implementation')
    selected=shutil.which('hyprctl',path=guard.env.get('PATH'))
    if selected!=issuer['executable'] or digest(material_path(selected))!=digest(issuer['executableMaterial']):raise ValueError('retained selected executable replaced')
    rows=value['history']
    if not isinstance(rows,list) or len(rows)>MAX_HISTORY:raise ValueError('complete bounded retained read-only history required')
    seen=set();expected_issuer=digest(issuer);requests={wire.decode('ascii') for wire,shape in REQUESTS.values()}
    fields={'id','actor','thread','fd','fdIdentity','issuerSHA256','request','requestSHA256','registeredNs','closed','published','outcome','evidence','error'}
    for row in rows:
        if not isinstance(row,dict) or set(row)-{'finishedNs'}!=fields or type(row['id']) is not str or re.fullmatch('[0-9a-f]{32}',row['id']) is None or row['id'] in seen:raise ValueError('complete unique retained connection row required')
        seen.add(row['id'])
        if row['actor'] is not None and (type(row['actor']) is not int or row['actor']<1):raise ValueError('typed retained actor tag required')
        for name in ('thread','registeredNs'):
            if type(row[name]) is not int or row[name]<1:raise ValueError('typed retained connection observation required')
        if type(row['fd']) is not int or row['fd']<0 or not isinstance(row['fdIdentity'],list) or len(row['fdIdentity'])!=2 or any(type(v) is not int or v<0 for v in row['fdIdentity']) or row['fdIdentity'][1]<1:raise ValueError('exact retained descriptor identity required')
        if row['issuerSHA256']!=expected_issuer or row['request'] not in requests or row['requestSHA256']!=hashlib.sha256(row['request'].encode('ascii')).hexdigest():raise ValueError('retained source/request binding differs')
        if type(row['closed']) is not bool or type(row['published']) is not bool or row['outcome'] not in ('pending','complete','refused'):raise ValueError('retained connection phase unknown')
        if row['outcome']=='pending':
            if row['closed'] or row['evidence'] is not None or row['error'] is not None or 'finishedNs' in row:raise ValueError('pending read-only data cannot carry completion')
            continue
        if type(row.get('finishedNs')) is not int or row['finishedNs']<row['registeredNs'] or row['published'] is not True:raise ValueError('retained connection completion publication missing')
        evidence=row['evidence']
        if not isinstance(evidence,dict) or set(evidence)!={'completeServerEOF','replyBytes','replySHA256','peer','socketIdentity'} or type(evidence['completeServerEOF']) is not bool or type(evidence['replyBytes']) is not int or not 0<=evidence['replyBytes']<=MAX_REPLY+1 or type(evidence['replySHA256']) is not str or re.fullmatch('[0-9a-f]{64}',evidence['replySHA256']) is None or evidence['socketIdentity']!=issuer['socketIdentity']:raise ValueError('complete retained raw reply evidence required')
        if row['outcome']=='complete':
            peer=evidence['peer']
            if row['closed'] is not True or row['error'] is not None or evidence['completeServerEOF'] is not True or not isinstance(peer,dict) or set(peer)!={'pid','uid','gid'} or any(type(v) is not int for v in peer.values()) or peer['pid']!=guard.pid or peer['uid']!=os.getuid() or not 0<evidence['replyBytes']<=MAX_REPLY:raise ValueError('retained returned data lacks exact closed peer/EOF proof')
        elif not isinstance(row['error'],dict) or set(row['error'])!={'type','message'} or any(type(v) is not str for v in row['error'].values()):raise ValueError('retained refusal error missing')
    return deepcopy(value)


def _validate_rows(rows, issuer, *, root, environment, guard):
    if not isinstance(rows, list) or len(rows) > MAX_HISTORY:
        raise ValueError('bounded active or archived rows required')
    original_issuer = deepcopy(issuer)
    current_source = original_issuer.pop('currentSource', None)
    if current_source != material_path(Path(__file__).with_name('readonly_current.py')):
        raise ValueError('retained current-read source replaced')
    archive_source = original_issuer.pop('archiveSource', None)
    if archive_source != material_path(Path(__file__).with_name('readonly_archive.py')):
        raise ValueError('retained archive source replaced')
    projected = []
    previous = 0
    for row in rows:
        if (not isinstance(row, dict) or type(row.get('serial')) is not int or row['serial'] < 1 or
                row['serial'] <= previous or row.get('id') != f"{row['serial']:032x}" or
                row.get('issuerSHA256') != digest(issuer)):
            raise ValueError('exact unique monotonic retained serial/issuer required')
        previous = row['serial']
        legacy = deepcopy(row)
        legacy.pop('serial')
        # An unpublished refusal is retained raw; this projection validates its
        # descriptor/error shape only. It remains ineligible for reclamation or bytes.
        if legacy.get('outcome') == 'refused' and legacy.get('published') is False:
            legacy['published'] = True
        legacy['issuerSHA256'] = digest(original_issuer)
        projected.append(legacy)
    keeper = {'servicePID': issuer['pid'], 'serviceStart': issuer['start'],
              'rootIdentity': issuer['rootIdentity']}
    # Reuse every original shape/FD/EOF/lifetime/source/request refusal predicate.
    _checked_active({'version': 1, 'issuer': original_issuer, 'history': projected, 'fault': False},
                    root=root, environment=environment, keeper=keeper, guard=guard)


def _validate_dataset(value, *, root, environment, guard, store):
    fields = {'version', 'issuer', 'history', 'fault', 'serial', 'epoch', 'archiveTip',
              'archiveDirectory', 'predecessor'}
    if (not isinstance(value, dict) or set(value) != fields or type(value['version']) is not int or
            value['version'] != 2 or value['fault'] is not False or
            type(value['serial']) is not int or value['serial'] < 0 or
            type(value['epoch']) is not int or value['epoch'] < 0 or
            value['archiveDirectory'] != store.directory or not isinstance(value['issuer'], dict)):
        raise ValueError('complete unfaulted retained archival dataset required')
    issuer = value['issuer']
    _validate_rows(value['history'], issuer, root=root, environment=environment, guard=guard)
    archived = segment_chain(store, value['archiveTip'], issuer=digest(issuer), epoch=value['epoch'],
                             validate_rows=lambda rows: _validate_rows(rows, issuer, root=root,
                                                                       environment=environment, guard=guard))
    serials = [r['serial'] for r in value['history'] + archived]
    if (len(serials) != value['serial'] or len(set(serials)) != len(serials) or
            serials and (min(serials) != 1 or max(serials) != value['serial'])):
        raise ValueError('complete active/archive serial coverage required')


def validate_storage(value, *, root, environment, guard):
    """All historical evidence verified, but never returned as current data/effect authority."""
    if not isinstance(value, dict) or not isinstance(value.get('issuer'), dict):
        raise ValueError('retained archival issuer required')
    store = ArchiveStore(root, value['issuer'].get('rootIdentity'), value.get('archiveDirectory'))
    _validate_dataset(value, root=root, environment=environment, guard=guard, store=store)
    pointer = deepcopy(value['predecessor'])
    seen = set()
    while pointer is not None:
        ArchiveStore.check_pointer(pointer)
        if pointer['name'] in seen: raise ValueError('cyclic predecessor chain')
        seen.add(pointer['name'])
        body = store.read(pointer)
        if (set(body) != {'version', 'kind', 'issuerSHA256', 'epoch', 'ledger', 'previous'} or
                body['kind'] != 'predecessor' or not isinstance(body['ledger'], dict) or
                body['issuerSHA256'] != digest(body['ledger'].get('issuer')) or
                body['previous'] != body['ledger'].get('predecessor') or
                body['epoch'] != (1 if body['previous'] is None else body['previous']['epoch'] + 1)):
            raise ValueError('complete ordered predecessor retention required')
        _validate_dataset(body['ledger'], root=root, environment=environment, guard=guard, store=store)
        pointer = body['previous']
    return deepcopy(value)


def checked_retained(value, *, root, environment, keeper, guard):
    validate_storage(value, root=root, environment=environment, guard=guard)
    issuer = value['issuer']
    if (issuer['pid'] != keeper['servicePID'] or issuer['start'] != keeper['serviceStart'] or
            issuer['rootIdentity'] != keeper['rootIdentity']):
        raise ValueError('retained archival issuer belongs to another old service')
    return deepcopy(value)


def seal_predecessor(value, *, root, environment, guard, lease_verify):
    """Retain all old rows including pending rows. Never marks any old result complete."""
    from native_runtime import NativeSession
    from service_runtime import RuntimeLease
    lease = getattr(lease_verify, '__self__', None)
    if (type(guard) is not NativeSession or type(lease) is not RuntimeLease or
            getattr(lease_verify, '__func__', None) is not RuntimeLease.verify or
            lease.root != Path(root) or lease.session != guard.session):
        raise ValueError('predecessor requires actual selected runtime lease/session')
    lease_verify()
    owner = (deepcopy(lease.owner), lease.nonce, lease.root_identity, lease.lock_identity, lease.fd)
    def confirm_owner():
        lease_verify()
        if (owner != (deepcopy(lease.owner), lease.nonce, lease.root_identity, lease.lock_identity, lease.fd) or
                lease.owner['nonce'] != lease.nonce):
            raise ValueError('predecessor current owner changed during confirmation')
    confirm_owner()
    before = validate_storage(value, root=root, environment=environment, guard=guard)
    store = ArchiveStore(root, value['issuer']['rootIdentity'], value['archiveDirectory'])
    previous = value['predecessor']
    body = {'version': 1, 'kind': 'predecessor', 'issuerSHA256': digest(value['issuer']),
            'epoch': 1 if previous is None else previous['epoch'] + 1,
            'ledger': deepcopy(value), 'previous': deepcopy(previous)}
    pointer = store.write(body, allow_existing=True)
    confirm_owner()
    if validate_storage(value, root=root, environment=environment, guard=guard) != before:
        raise ValueError('predecessor retained dataset changed during sealing')
    if store.read(pointer) != body: raise ValueError('predecessor post-disk confirmation differs')
    confirm_owner()
    return pointer


def validate_predecessor(pointer, *, root, root_identity, environment, guard):
    """Validate startup-only lineage before inherited native recovery is entered."""
    store = ArchiveStore(root, root_identity)
    body = store.read(pointer)
    if (set(body) != {'version', 'kind', 'issuerSHA256', 'epoch', 'ledger', 'previous'} or
            body['kind'] != 'predecessor' or not isinstance(body['ledger'], dict) or
            body['issuerSHA256'] != digest(body['ledger'].get('issuer')) or
            body['previous'] != body['ledger'].get('predecessor') or
            body['epoch'] != (1 if body['previous'] is None else body['previous']['epoch'] + 1)):
        raise ValueError('complete authenticated startup predecessor required')
    validate_storage(body['ledger'], root=root, environment=environment, guard=guard)
    if store.read(pointer) != body:
        raise ValueError('startup predecessor changed before confirmation')
    return deepcopy(pointer)
