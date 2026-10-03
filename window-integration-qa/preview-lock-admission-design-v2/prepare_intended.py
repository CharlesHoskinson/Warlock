"""Draft only: reconstruct proposed source, never edit selected frozen files."""
from pathlib import Path
import difflib
import hashlib
import json
import os

D=Path(__file__).parent
S=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24')
P=D/'proposed';P.mkdir(mode=0o700)

helpers='''    @staticmethod
    def _remaining(deadline_ns):
        if deadline_ns is None:return None
        if type(deadline_ns) is not int or deadline_ns<0:raise ValueError('exact absolute preview deadline required')
        remaining=deadline_ns-time.monotonic_ns()
        if remaining<=0:raise TimeoutError('original preview receipt deadline')
        return remaining/1000000000
    @classmethod
    @contextmanager
    def _receipt_guard(cls,reservation_lock,deadline_ns):
        if deadline_ns is None:
            with reservation_lock:yield
            return
        # Timed acquisition holds no receipt/Keeper/lifecycle lock while waiting.
        if not reservation_lock.acquire(timeout=cls._remaining(deadline_ns)):
            raise TimeoutError('original preview receipt deadline')
        try:
            cls._remaining(deadline_ns)
            yield
        finally:reservation_lock.release()
    @staticmethod
    def _preview_lock_identity(info):
        if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.getuid():raise ValueError('exact preview lock required')
        # The unchanged shell writer truncates this inode BEFORE flock. Size,
        # mtime and ctime cannot authenticate a reusable coordination lock.
        return info.st_dev,info.st_ino,stat.S_IFMT(info.st_mode),info.st_uid
    @contextmanager
    def _preview_locks(self,rows,*,current,reservation_lock,deadline_ns):
        addresses=tuple(sorted(row['window']['address'] for _,row in rows))
        if len(set(addresses))!=len(addresses):raise ValueError('ambiguous preview lock addresses')
        captured={}
        with ExitStack() as admitted:
            while True:
                self._remaining(deadline_ns)
                with self._receipt_guard(reservation_lock,deadline_ns):
                    if not current():raise ValueError('batch receipt was superseded')
                busy=False
                with ExitStack() as attempt:
                    observations=[]
                    for address in addresses:
                        self._remaining(deadline_ns)
                        path=self.preview/(address+'.lock')
                        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
                        attempt.callback(os.close,fd)
                        identity=self._preview_lock_identity(os.fstat(fd))
                        if self._preview_lock_identity(path.lstat())!=identity:raise ValueError('preview lock path changed')
                        if address in captured and captured[address]!=identity:raise ValueError('preview lock inode changed during admission')
                        if address not in captured and identity in captured.values():raise ValueError('preview lock inode aliases another address')
                        captured[address]=identity;observations.append((path,fd,identity))
                        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
                        except BlockingIOError as error:
                            # Only this selected flock's exact busy errno retries.
                            if deadline_ns is None or error.errno not in (errno.EAGAIN,errno.EWOULDBLOCK):raise
                            busy=True;break
                        if self._preview_lock_identity(path.lstat())!=identity:raise ValueError('preview lock path changed after flock')
                    if not busy:
                        self._remaining(deadline_ns)
                        # Only the complete set remains held for this bounded
                        # receipt guard. Partial sets are never kept on a retry.
                        with self._receipt_guard(reservation_lock,deadline_ns):
                            if not current():raise ValueError('batch receipt was superseded')
                        for path,fd,identity in observations:
                            if self._preview_lock_identity(os.fstat(fd))!=identity or self._preview_lock_identity(path.lstat())!=identity:raise ValueError('preview lock identity changed before admission')
                        self._remaining(deadline_ns)
                        admitted.enter_context(attempt.pop_all())
                        break
                # Closing every attempt descriptor releases all partial flocks.
                # This wait holds no receipt/Keeper/lifecycle/address lock.
                time.sleep(min(.005,self._remaining(deadline_ns)))
            yield tuple(observations)
    def _check_preview_locks(self,observations):
        for path,fd,identity in observations:
            if self._preview_lock_identity(os.fstat(fd))!=identity or self._preview_lock_identity(path.lstat())!=identity:raise ValueError('admitted preview lock identity changed')
'''

original=(S/'batch_preview.py').read_text()
proposed=original.replace('from contextlib import ExitStack','from contextlib import ExitStack, contextmanager',1)
proposed=proposed.replace('import fcntl\n','import fcntl\nimport errno\n',1).replace('import threading\n','import threading\nimport time\n',1)
signature='    def finish(self,sources,members,*,clients,current,reservation_lock):\n'
assert proposed.count(signature)==1
proposed=proposed.replace(signature,helpers+'    def finish(self,sources,members,*,clients,current,reservation_lock,deadline_ns=None):\n        self._remaining(deadline_ns)\n',1)
proposed=proposed.replace('            with reservation_lock:\n                if not current():raise ValueError(\'batch receipt was superseded\')','            with self._receipt_guard(reservation_lock,deadline_ns):\n                if not current():raise ValueError(\'batch receipt was superseded\')',1)
start=proposed.index('                for address in sorted(row[')
end=proposed.index('                self.check_family(members,clients())',start)
proposed=proposed[:start]+'''                lock_observations=stack.enter_context(self._preview_locks(rows,current=current,reservation_lock=reservation_lock,deadline_ns=deadline_ns))
'''+proposed[end:]
launch='''                try:
                    result=self.commands.run'''
assert proposed.count(launch)==1
proposed=proposed.replace(launch,'''                try:
                    self._check_preview_locks(lock_observations)
                    if not self._closed():raise ValueError('outstanding actor helper prevents thumbnail launch')
                    with self._receipt_guard(reservation_lock,deadline_ns):
                        if not current():raise ValueError('batch receipt was superseded before thumbnail dispatch')
                    # Guarded dispatch entry, NOT a deadline proof for child G.
                    self._remaining(deadline_ns)
                    result=self.commands.run''',1)
publication='''                with reservation_lock:
                    if not current():raise ValueError('batch receipt was superseded before preview publication')
                    for pinned in inputs:pinned.check()
                    for path,destination in publication:path.replace(destination)
                    with self.lock:
                        for epoch,_ in rows:self.pending.pop(epoch)'''
assert proposed.count(publication)==1
proposed=proposed.replace(publication,'''                with self._receipt_guard(reservation_lock,deadline_ns):
                    if not current():raise ValueError('batch receipt was superseded before preview publication')
                    for pinned in inputs:pinned.check()
                    self._check_preview_locks(lock_observations)
                    for path,destination in publication:
                        self._remaining(deadline_ns)
                        path.replace(destination)
                    # Partial cache replacement is not completed publication.
                    with self.lock:
                        self._remaining(deadline_ns)
                        for epoch,_ in rows:self.pending.pop(epoch)''',1)
drafts={'batch_preview.py':proposed}
original=(S/'native_desktop.py').read_text()
drafts['native_desktop.py']=original.replace('def finish_capture_previews(self,sources,members,*,current,reservation_lock):','def finish_capture_previews(self,sources,members,*,current,reservation_lock,deadline_ns=None):',1).replace('self.preview_batch.finish(sources,members,clients=self.clients,current=current,reservation_lock=reservation_lock)','self.preview_batch.finish(sources,members,clients=self.clients,current=current,reservation_lock=reservation_lock,deadline_ns=deadline_ns)',1)
original=(S/'scene_controller.py').read_text()
drafts['scene_controller.py']=original.replace('finisher(sources,members,current=lambda:self.owns(record),reservation_lock=self.lock)','finisher(sources,members,current=lambda:self.owns(record),reservation_lock=self.lock,\n                    deadline_ns=record.profile[\'receivedNs\']+2000000000)',1)
original=(S/'test_batch_preview.py').read_text()
# Exactly two fixture callbacks have a strict signature; the failing callback
# already accepts **options. All outcome assertions/timeouts remain identical.
assert original.count('def finish(sources,members,*,current,reservation_lock):')==2
drafts['test_batch_preview.py']=original.replace('def finish(sources,members,*,current,reservation_lock):','def finish(sources,members,*,current,reservation_lock,deadline_ns=None):')

patch=[];mapping={}
for name,proposed in drafts.items():
    original=(S/name).read_text();compile(proposed,str(S/name),'exec')
    with os.fdopen(os.open(P/(name+'.txt'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as output:output.write(proposed)
    patch.extend(difflib.unified_diff(original.splitlines(True),proposed.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    mapping[name]={'originalSHA256':hashlib.sha256(original.encode()).hexdigest(),'proposedSHA256':hashlib.sha256(proposed.encode()).hexdigest(),'originalMode':(S/name).stat().st_mode&0o777,'path':str(P/(name+'.txt'))}
for name,value in [('intended.patch',''.join(patch)),('intended-source-map.json',json.dumps(mapping,indent=2)+'\n')]:
    with os.fdopen(os.open(D/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as output:output.write(value)
print(json.dumps(mapping))
