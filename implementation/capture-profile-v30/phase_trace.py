"""Opt-in bounded in-memory observer. No pixels, argv, titles or native actions."""
import contextlib
import json
import os
from pathlib import Path
import stat
import threading
import time

class Trace:
    def __init__(self, limit=2048):
        if not 1 <= limit <= 8192: raise ValueError('invalid trace bound')
        self.limit=limit; self.records=[]; self.dropped=0; self.lock=threading.Lock()
    def emit(self, phase, status):
        # Labels are fixed by instrumentation, never untrusted message fields.
        if phase not in PHASES or status not in ('begin','end','error','observed'): return
        row={'monotonic_ns':time.monotonic_ns(),'phase':phase,'status':status,'thread':threading.get_ident()}
        with self.lock:
            if len(self.records)<self.limit:self.records.append(row)
            else:self.dropped+=1
    def publish(self, destination):
        path=Path(destination); parent=path.parent
        info=parent.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o700:
            raise ValueError('trace parent must be private owned 0700 directory')
        # Check parent path components too; no indirect symlink traversal.
        if any(p.is_symlink() for p in (parent,*parent.parents)):raise ValueError('symlink trace parent')
        directory=os.open(parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            current=os.fstat(directory)
            if (current.st_dev,current.st_ino)!=(info.st_dev,info.st_ino):raise ValueError('trace parent changed')
            fd=os.open(path.name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
            with self.lock:body={'version':1,'clock':'monotonic_ns','records':list(self.records),'dropped':self.dropped,
                'limitations':['receipt time is observer time, not presentation timestamp','lock/helper spans include supervision','no encode/decode/upload duration measured']}
            with os.fdopen(fd,'w') as out:json.dump(body,out,separators=(',',':'))
        finally:os.close(directory)

PHASES={'capture_lock_wait','capture_lock_held','snapshot_lock_wait','snapshot_lock_held','capture_source','capture_source_impl','hidden_capture','preview_finish','query','identity_check','capture_helper','conversion_helper','other_helper','renderer_seed_queued','renderer_uploaded_receipt','renderer_seeded_receipt','renderer_presented_receipt','renderer_other_receipt'}
active=None
@contextlib.contextmanager
def span(phase):
    trace=active
    if trace is not None:trace.emit(phase,'begin')
    try:yield
    except BaseException:
        if trace is not None:trace.emit(phase,'error')
        raise
    finally:
        if trace is not None:trace.emit(phase,'end')
@contextlib.contextmanager
def measured_lock(lock, name):
    with span(name+'_wait'):lock.acquire()
    try:
        with span(name+'_held'):yield
    finally:lock.release()
def measured_call(phase, function, *args, **kwargs):
    if phase=='helper':
        executable=Path(str(args[0][0])).name if args and args[0] else ''
        phase={'grim':'capture_helper','magick':'conversion_helper'}.get(executable,'other_helper')
    with span(phase):return function(*args,**kwargs)
def observed_event(event):
    if active is None or not isinstance(event,dict):return
    phase={'uploaded':'renderer_uploaded_receipt','seeded':'renderer_seeded_receipt','presented':'renderer_presented_receipt'}.get(event.get('event'),'renderer_other_receipt')
    active.emit(phase,'observed')
def observed_command(message):
    if active is not None and message.get('command')=='seed':active.emit('renderer_seed_queued','observed')
