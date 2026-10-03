"""Immutable read-only provenance. Import opens no file and grants no authority."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import stat

MAX_FILE = 16777216
POINTER = {'kind', 'name', 'sha256', 'identity', 'issuerSHA256', 'epoch'}
NAME = re.compile(r'(segment|predecessor)-([0-9a-f]{64})-([1-9][0-9]*)-([0-9a-f]{64})\.json')


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def identity(info):
    return [info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_nlink, info.st_size]


def directory_identity(info):
    return identity(info)[:5]  # directory size and link count vary with new immutable files.


class ArchiveStore:
    def __init__(self, root, root_identity, directory=None, *, create=False):
        self.root = Path(root)
        self.root_identity = list(root_identity)
        self.path = self.root / 'readonly-ledger'
        self.directory = directory
        self.verify_root()
        if create:
            try:
                self.path.mkdir(mode=0o700)
                fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
                try: os.fsync(fd)
                finally: os.close(fd)
            except FileExistsError: pass
        info = self.path.lstat()
        self._safe_directory(info)
        if directory is not None and directory_identity(info) != directory:
            raise ValueError('archive directory identity replaced')
        self.directory = directory_identity(info)
        self.verify()

    def _safe_directory(self, info):
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or
                stat.S_IMODE(info.st_mode) != 0o700 or self.path.resolve() != self.path.absolute()):
            raise ValueError('exact private canonical archive directory required')

    def verify_root(self):
        info = self.root.lstat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or
                stat.S_IMODE(info.st_mode) != 0o700 or [info.st_dev, info.st_ino] != self.root_identity or
                self.root.resolve() != self.root.absolute()):
            raise ValueError('selected archive root replaced or unsafe')

    def verify(self):
        self.verify_root()
        info = self.path.lstat()
        self._safe_directory(info)
        if directory_identity(info) != self.directory:
            raise ValueError('archive directory identity replaced')

    def open_directory(self):
        self.verify()
        fd = os.open(self.path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            if directory_identity(os.fstat(fd)) != self.directory:
                raise ValueError('archive directory changed during open')
            self.verify()
            return fd
        except BaseException:
            os.close(fd)
            raise

    @staticmethod
    def check_pointer(pointer):
        if not isinstance(pointer, dict) or set(pointer) != POINTER:
            raise ValueError('complete archive pointer required')
        match = NAME.fullmatch(pointer['name']) if type(pointer['name']) is str else None
        if (match is None or pointer['kind'] not in ('segment', 'predecessor') or
                match.group(1) != pointer['kind'] or match.group(2) != pointer['issuerSHA256'] or
                type(pointer['epoch']) is not int or pointer['epoch'] < 1 or
                int(match.group(3)) != pointer['epoch'] or type(pointer['sha256']) is not str or
                re.fullmatch('[0-9a-f]{64}', pointer['sha256']) is None or
                not isinstance(pointer['identity'], list) or len(pointer['identity']) != 7 or
                any(type(v) is not int or v < 0 for v in pointer['identity'])):
            raise ValueError('typed canonical archive pointer required')
        return match

    def read(self, pointer):
        match = self.check_pointer(pointer)
        directory = self.open_directory()
        fd = None
        try:
            named = os.stat(pointer['name'], dir_fd=directory, follow_symlinks=False)
            fd = os.open(pointer['name'], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                         dir_fd=directory)
            before = os.fstat(fd)
            actual = identity(before)
            if (not stat.S_ISREG(before.st_mode) or before.st_uid != os.getuid() or
                    stat.S_IMODE(before.st_mode) != 0o600 or before.st_nlink != 1 or
                    not 0 < before.st_size <= MAX_FILE or actual != identity(named) or
                    actual != pointer['identity']):
                raise ValueError('exact immutable archive file identity required')
            parts = []
            remaining = MAX_FILE + 1
            while remaining:
                chunk = os.read(fd, min(65536, remaining))
                if not chunk: break
                parts.append(chunk)
                remaining -= len(chunk)
            data = b''.join(parts)
            after = os.fstat(fd)
            named_after = os.stat(pointer['name'], dir_fd=directory, follow_symlinks=False)
            self.verify()
            if (actual != identity(after) or actual != identity(named_after) or len(data) != before.st_size or
                    hashlib.sha256(data).hexdigest() != pointer['sha256']):
                raise ValueError('archive bytes/identity changed during read')
            value = json.loads(data)
            if (not isinstance(value, dict) or set(value) != {'body', 'sha256'} or
                    sha(value['body']) != value['sha256'] or value['sha256'] != match.group(4) or
                    encoded(value) != data or not isinstance(value['body'], dict) or
                    value['body'].get('version') != 1 or type(value['body'].get('version')) is not int or
                    value['body'].get('kind') != pointer['kind'] or
                    value['body'].get('issuerSHA256') != pointer['issuerSHA256'] or
                    value['body'].get('epoch') != pointer['epoch'] or type(value['body'].get('epoch')) is not int):
                raise ValueError('archive checksum/schema/issuer/epoch mismatch')
            return value['body']
        finally:
            if fd is not None: os.close(fd)
            os.close(directory)

    def write(self, body):
        if (body.get('version') != 1 or type(body.get('version')) is not int or
                body.get('kind') not in ('segment', 'predecessor') or
                type(body.get('epoch')) is not int or body['epoch'] < 1 or
                type(body.get('issuerSHA256')) is not str or
                re.fullmatch('[0-9a-f]{64}', body['issuerSHA256']) is None):
            raise ValueError('exact immutable archive body required')
        checksum = sha(body)
        name = f"{body['kind']}-{body['issuerSHA256']}-{body['epoch']}-{checksum}.json"
        data = encoded({'body': body, 'sha256': checksum})
        if len(data) > MAX_FILE: raise ValueError('archive exceeds full bounded file size')
        directory = self.open_directory()
        fd = None
        try:
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                         0o600, dir_fd=directory)
            with os.fdopen(fd, 'wb') as stream:
                fd = None
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
                material = identity(os.fstat(stream.fileno()))
            os.fsync(directory)
            self.verify()
        finally:
            if fd is not None: os.close(fd)
            os.close(directory)
        pointer = {'kind': body['kind'], 'name': name, 'sha256': hashlib.sha256(data).hexdigest(),
                   'identity': material, 'issuerSHA256': body['issuerSHA256'], 'epoch': body['epoch']}
        if self.read(pointer) != body: raise ValueError('archive durable readback differs')
        return pointer


def segment_chain(store, tip, *, issuer, epoch, validate_rows):
    """Full referenced chain, provenance only. Orphans are never discovered as authority."""
    rows = []
    seen_names = set()
    seen_serials = set()
    pointer = deepcopy(tip)
    expected = epoch
    while pointer is not None:
        if pointer['name'] in seen_names: raise ValueError('cyclic archive chain')
        seen_names.add(pointer['name'])
        body = store.read(pointer)
        if (set(body) != {'version', 'kind', 'issuerSHA256', 'epoch', 'previous', 'rows', 'first', 'last'} or
                body['kind'] != 'segment' or body['issuerSHA256'] != issuer or body['epoch'] != expected or
                not isinstance(body['rows'], list) or not body['rows'] or len(body['rows']) > 512):
            raise ValueError('complete ordered archive segment required')
        validate_rows(body['rows'])
        serials = [r['serial'] for r in body['rows']]
        if serials != sorted(serials) or len(set(serials)) != len(serials) or body['first'] != serials[0] or body['last'] != serials[-1]:
            raise ValueError('archive serial interval/order differs')
        if any(r['closed'] is not True or r['published'] is not True or r['outcome'] not in ('complete', 'refused') for r in body['rows']):
            raise ValueError('unfinished row cannot be reclaimed')
        if seen_serials.intersection(serials): raise ValueError('duplicate archived connection serial')
        seen_serials.update(serials)
        rows.extend(body['rows'])
        pointer = body['previous']
        expected -= 1
    if expected != 0: raise ValueError('missing archive chain epoch')
    return rows
