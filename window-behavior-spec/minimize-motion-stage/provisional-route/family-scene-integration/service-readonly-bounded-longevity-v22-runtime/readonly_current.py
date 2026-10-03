"""Typed same-owner fresh-data witnesses. Never historical/native/settlement authority."""
from copy import deepcopy
from dataclasses import dataclass
import fcntl
import hashlib
import json
import os
import stat
import threading
import uuid

from readonly_archive import encoded, sha, identity, directory_identity, MAX_FILE

SEALS = fcntl.F_SEAL_SEAL | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_GROW | fcntl.F_SEAL_WRITE | 32


def fd_material(fd, *, directory=False):
    info = os.fstat(fd)
    return {'number': fd, 'stat': directory_identity(info) if directory else identity(info),
            'target': os.readlink(f'/proc/self/fd/{fd}'),
            'flags': fcntl.fcntl(fd, fcntl.F_GETFL), 'fdFlags': fcntl.fcntl(fd, fcntl.F_GETFD)}


def same_material(left, right):
    """Canonical equality preserves JSON scalar types; bool is never an integer token."""
    return encoded(left) == encoded(right)


def no_exec_alias(fd):
    info = os.fstat(fd)
    device = (os.major(info.st_dev), os.minor(info.st_dev))
    with open('/proc/self/maps', encoding='utf-8') as stream:
        for line in stream:
            fields = line.split(maxsplit=5)
            if len(fields) < 5: raise ValueError('complete current root maps required')
            major, minor = (int(part, 16) for part in fields[3].split(':'))
            if (major, minor) == device and int(fields[4]) == info.st_ino and 'x' in fields[1]:
                raise ValueError('current data descriptor has executable alias')


class SealedData:
    def __init__(self, name, value):
        self.fd = os.memfd_create(name, os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING | 8)
        try:
            os.fchmod(self.fd, 0o600)
            raw = encoded(value)
            if not 0 < len(raw) <= MAX_FILE: raise ValueError('bounded sealed data body required')
            offset = 0
            while offset < len(raw): offset += os.write(self.fd, raw[offset:])
            fcntl.fcntl(self.fd, fcntl.F_ADD_SEALS, SEALS)
            self.expected = fd_material(self.fd)
            self.digest = hashlib.sha256(raw).hexdigest()
            self.value = deepcopy(value)
            self.verify()
        except BaseException:
            os.close(self.fd); self.fd = -1
            raise

    def verify(self):
        before = fd_material(self.fd)
        info = os.fstat(self.fd)
        if (not same_material(before, self.expected) or not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or
                stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 0 or
                before['flags'] & os.O_PATH or before['flags'] & os.O_ACCMODE != os.O_RDWR or
                before['fdFlags'] != fcntl.FD_CLOEXEC or fcntl.fcntl(self.fd, fcntl.F_GET_SEALS) != SEALS):
            raise ValueError('exact sealed current-data FD replaced or unsafe')
        no_exec_alias(self.fd)
        data = os.pread(self.fd, info.st_size + 1, 0)
        if (not same_material(fd_material(self.fd), before) or len(data) != info.st_size or
                hashlib.sha256(data).hexdigest() != self.digest or encoded(self.value) != data):
            raise ValueError('sealed current-data body/identity changed')
        return deepcopy(self.value)

    def close(self):
        if self.fd >= 0:
            os.close(self.fd); self.fd = -1


class PinnedTip:
    def __init__(self, store, directory_fd, pointer, token_body, generation):
        self.pointer = deepcopy(pointer)
        self.fd = None
        self.references = 0
        self.latest = False
        self.token = None
        try:
            if pointer is not None:
                store.check_pointer(pointer)
                self.fd = os.open(pointer['name'], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                                  dir_fd=directory_fd)
                self.expected = fd_material(self.fd)
            token_body = {**deepcopy(token_body), 'fileFD': deepcopy(getattr(self,'expected',None))}
            self.token = SealedData(f'readonly-current-{generation}-tip-{token_body["epoch"]}', token_body)
            self.token_expected = deepcopy(self.token.expected)
            self.verify(store, directory_fd)
        except BaseException:
            self.close(); raise

    def verify(self, store, directory_fd):
        if not same_material(self.token.expected, self.token_expected):
            raise ValueError('sealed current tip token FD replaced')
        token = self.token.verify()
        if not same_material(token['fileFD'], getattr(self,'expected',None)):
            raise ValueError('sealed tip file FD capture changed')
        if not same_material(token['pointer'], self.pointer): raise ValueError('sealed current tip pointer changed')
        if self.pointer is None:
            if self.fd is not None or token['epoch'] != 0 or token['archivedCount'] != 0:
                raise ValueError('explicit empty current tip required')
            return None
        store.check_pointer(self.pointer)
        before = fd_material(self.fd)
        info = os.fstat(self.fd)
        named = os.stat(self.pointer['name'], dir_fd=directory_fd, follow_symlinks=False)
        if (not same_material(before, self.expected) or not same_material(identity(info), self.pointer['identity']) or identity(named) != identity(info) or
                not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600 or
                info.st_nlink != 1 or not 0 < info.st_size <= MAX_FILE or before['flags'] & os.O_PATH or
                before['flags'] & os.O_ACCMODE != os.O_RDONLY or before['fdFlags'] != fcntl.FD_CLOEXEC):
            raise ValueError('exact pinned current tip FD/name identity replaced or unsafe')
        no_exec_alias(self.fd)
        parts = []; offset = 0
        while offset <= info.st_size:
            chunk = os.pread(self.fd, min(65536, info.st_size + 1 - offset), offset)
            if not chunk: break
            parts.append(chunk); offset += len(chunk)
        raw = b''.join(parts)
        if (not same_material(fd_material(self.fd), before) or identity(os.stat(self.pointer['name'],dir_fd=directory_fd,follow_symlinks=False)) != identity(info) or
                len(raw) != info.st_size or hashlib.sha256(raw).hexdigest() != self.pointer['sha256']):
            raise ValueError('pinned current tip bytes/identity changed')
        value = json.loads(raw)
        body = value.get('body') if isinstance(value,dict) else None
        if (not isinstance(body,dict) or set(value) != {'body','sha256'} or encoded(value) != raw or
                sha(body) != value['sha256'] or store.check_pointer(self.pointer).group(4) != value['sha256'] or
                body.get('version') != 1 or type(body.get('version')) is not int or body.get('kind') != 'segment' or
                body.get('issuerSHA256') != token['issuerSHA256'] or type(body.get('epoch')) is not int or body.get('epoch') != token['epoch'] or
                not same_material(body.get('previous'), token['previous'])):
            raise ValueError('bounded current tip schema/checksum/binding changed')
        return body

    def close(self):
        if self.fd is not None: os.close(self.fd); self.fd = None
        if self.token is not None: self.token.close()


@dataclass(frozen=True)
class CurrentReadWitness:
    """No full-history/native/recovery authority. Only an actual fresh data flow may use it."""
    issuerSHA256: str
    generation: str
    ownerFD: tuple
    latestToken: tuple
    borrowedToken: tuple


class CurrentReads:
    def __init__(self, store, lease, issuer, predecessor):
        self.store = store
        self.lock = threading.RLock()
        self.closed = False
        self.borrowers = 0
        self.generation = uuid.uuid4().hex
        self.root_fd = None; self.directory_fd = None; self.anchor = None; self.latest = None
        self.tips = set()
        try:
            self.root_fd = os.open(store.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
            self.directory_fd = store.open_directory()
            self.root_expected = fd_material(self.root_fd, directory=True)
            self.directory_expected = fd_material(self.directory_fd, directory=True)
            self.lease_expected = fd_material(lease.fd)
            payload = {'role':'current-fresh-read-only','generation':self.generation,'issuer':deepcopy(issuer),
                       'rootFD':self.root_expected,'directoryFD':self.directory_expected,'leaseFD':self.lease_expected,
                       'predecessor':deepcopy(predecessor),'startupFullValidated':True}
            self.anchor = SealedData(f'readonly-current-{self.generation}-owner', payload)
            self.anchor_expected = deepcopy(self.anchor.expected)
            self.latest = PinnedTip(store,self.directory_fd,None,
                {'role':'current-tip','generation':self.generation,'issuerSHA256':sha(issuer),
                 'epoch':0,'pointer':None,'previous':None,'archivedCount':0},self.generation)
            self.latest.latest=True;self.tips.add(self.latest)
            self.verify_owner(lease,issuer,predecessor)
        except BaseException:
            self.close(force=True); raise

    def verify_owner(self,lease,issuer,predecessor):
        if self.closed: raise ValueError('current read proof already retired')
        self.store.verify()
        if (not same_material(fd_material(self.root_fd,directory=True), self.root_expected) or
                not same_material(fd_material(self.directory_fd,directory=True), self.directory_expected) or
                not same_material(directory_identity(os.stat(self.store.path,follow_symlinks=False)), self.store.directory) or
                not same_material([os.fstat(self.root_fd).st_dev,os.fstat(self.root_fd).st_ino], self.store.root_identity) or
                not same_material(fd_material(lease.fd), self.lease_expected) or not same_material(self.anchor.expected, self.anchor_expected)):
            raise ValueError('current root/directory/lease/owner FD binding replaced')
        body=self.anchor.verify()
        expected={'role':'current-fresh-read-only','generation':self.generation,'issuer':deepcopy(issuer),
                  'rootFD':self.root_expected,'directoryFD':self.directory_expected,'leaseFD':self.lease_expected,
                  'predecessor':deepcopy(predecessor),'startupFullValidated':True}
        if not same_material(body, expected): raise ValueError('sealed current owner binding replaced')

    def acquire_latest(self,pointer,epoch,*,borrow=False,limit=None):
        with self.lock:
            if borrow and (type(limit) is not int or limit<1 or self.borrowers>=limit):
                raise ValueError('complete bounded history has no reclaimable current query proof slot')
            tip=self.latest
            token=tip.token.verify()
            if not same_material(tip.pointer, pointer) or type(epoch) is not int or type(token['epoch']) is not int or token['epoch'] != epoch or not(tip.latest):
                raise ValueError('latest current tip/token replaced outside owned publication')
            tip.references += 1
            if borrow:self.borrowers += 1
            return tip

    def release(self,tip,*,borrow=False):
        with self.lock:
            if tip not in self.tips or tip.references<1:raise ValueError('exact owned current tip reference required')
            if borrow and self.borrowers<1:raise ValueError('exact current query slot required')
            tip.references-=1
            if borrow:self.borrowers-=1
            if not tip.latest and tip.references==0:
                tip.close();self.tips.remove(tip)

    def prepare(self,pointer,previous,epoch,count,issuer):
        token={'role':'current-tip','generation':self.generation,'issuerSHA256':sha(issuer),
               'epoch':epoch,'pointer':deepcopy(pointer),'previous':deepcopy(previous),'archivedCount':count}
        return PinnedTip(self.store,self.directory_fd,pointer,token,self.generation)

    def adopt(self,prepared,previous):
        with self.lock:
            old=self.latest
            if not same_material(old.pointer, previous) or prepared in self.tips:
                raise ValueError('owned current-tip adoption no longer exact')
            old_token=old.token.verify();new_token=prepared.token.verify()
            if (not same_material(new_token['previous'], old.pointer) or new_token['epoch'] != old_token['epoch']+1 or
                    new_token['generation'] != self.generation or new_token['issuerSHA256'] != old_token['issuerSHA256']):
                raise ValueError('current tip is not exact authenticated own append')
            prepared.verify(self.store,self.directory_fd)
            prepared.latest=True;self.tips.add(prepared);self.latest=prepared;old.latest=False
            if old.references==0:old.close();self.tips.remove(old)

    def witness(self,latest,borrowed,issuer):
        with self.lock:
            if latest not in self.tips or borrowed not in self.tips or latest.references<1 or borrowed.references<1:
                raise ValueError('current data witness lacks exact live tip references')
            for tip in (latest,borrowed):
                token=tip.token.verify()
                if token['role']!='current-tip' or token['generation']!=self.generation or token['issuerSHA256']!=sha(issuer):
                    raise ValueError('current tip token belongs to another current binding')
            latest.verify(self.store,self.directory_fd)
            if borrowed is not latest:borrowed.verify(self.store,self.directory_fd)
            return CurrentReadWitness(sha(issuer),self.generation,
                (self.anchor_expected['number'],self.anchor_expected['stat'][0],self.anchor_expected['stat'][1]),
                (latest.token.expected['number'],latest.token.expected['stat'][1],latest.token.digest),
                (borrowed.token.expected['number'],borrowed.token.expected['stat'][1],borrowed.token.digest))

    def close(self,*,force=False):
        with self.lock:
            if not force and (self.borrowers or any(t.references for t in self.tips)):raise ValueError('current read proof still borrowed')
            for tip in self.tips:tip.close()
            self.tips.clear()
            self.borrowers=0
            if self.anchor is not None:self.anchor.close()
            for name in ('root_fd','directory_fd'):
                fd=getattr(self,name)
                if fd is not None:os.close(fd);setattr(self,name,None)
            self.closed=True

    def __del__(self):
        try:self.close(force=True)
        except BaseException:pass
