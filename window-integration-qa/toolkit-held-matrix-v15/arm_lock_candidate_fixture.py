"""TEST-ONLY bounded journal-lock candidate before runtime adoption; no import actions."""
from contextlib import contextmanager
import errno,fcntl,os,time
import helper_observer as observer

def remaining(deadline):
    value=deadline-time.monotonic()
    if value<=0:raise TimeoutError('Original evaluation arm deadline expired')
    return value

@contextmanager
def locked_until(path,deadline,on_busy=None):
    while True:
        remaining(deadline)
        identity=observer.regular(path,0o600)
        fd=os.open(path,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC)
        stream=None
        try:
            info=os.fstat(fd)
            if (info.st_dev,info.st_ino)!=identity or observer.regular(path,0o600)!=identity:
                raise RuntimeError('Helper log replaced during bounded acquisition')
            remaining(deadline)
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except OSError as error:
                if error.errno not in (errno.EAGAIN,errno.EWOULDBLOCK):raise
                if on_busy is not None:on_busy()
            else:
                remaining(deadline)
                if observer.regular(path,0o600)!=identity:raise RuntimeError('Helper log replaced after bounded acquisition')
                stream=os.fdopen(fd,'r+');fd=None
                with stream:
                    yield stream
                return
        finally:
            if fd is not None:os.close(fd)
        time.sleep(min(.03,remaining(deadline)))
