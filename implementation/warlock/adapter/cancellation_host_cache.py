"""Join a previously C-accepted cached receipt to validated V7 custody.

Caller owns one host_guard and supplies an already-validated current V7 state.
This reader never creates receipts, edits companions, retires Pending or grants
native rights. Actual owned backend acceptance by C remains a separate boundary.
"""
import os
import re
import stat
from contextlib import contextmanager
from endpoint import Refused
from cancellation_host_admission import decode
from cancellation_host_settlement import MAX_FRAME, make_settlement, validate_settlement

DIRECTORY='cancellation-settlements-v1'
CAPACITY=64
ACK_RANK={'NotSent':0,'Pending':1,'Acknowledged':2}

@contextmanager
def cache_directory_locked(owner):
    fd=None
    try:
        try:fd=os.open(DIRECTORY,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=owner.fd)
        except FileNotFoundError:
            yield None
            return
        st=os.fstat(fd)
        if st.st_uid!=os.getuid() or stat.S_IMODE(st.st_mode)!=0o700:
            raise Refused('Cancellation settlement directory ownership')
        names=os.listdir(fd)
        if len(names)>CAPACITY or any(not re.fullmatch(r'[0-9a-f]{64}\.json',name) for name in names):
            raise Refused('Cancellation settlement directory inventory')
        yield fd
    except OSError:
        owner.poisoned=True
        raise
    finally:
        if fd is not None:
            try:os.close(fd)
            except OSError:
                owner.poisoned=True
                raise

def cached_retirement_locked(owner, companion, validated_state):
    """None means the exact local fence remains. Invalid cache refuses.

    The cache's saved delivery binding is provenance, never current native
    authority. Independently require matching V7 AdmissionRetired+certificate.
    Reconfirm the file and directory durability before admitting another key;
    mere visibility after an interrupted C cache rename is insufficient.
    """
    try:
        with cache_directory_locked(owner) as directory:
            if directory is None:return None
            name=companion['key']+'.json'
            raw=owner.raw(directory,name,MAX_FRAME)
            if raw is None:return None
            frame=decode(raw)
            if not isinstance(frame,dict) or 'binding' not in frame:
                raise Refused('Cancellation settlement cache envelope')
            frame=validate_settlement(frame,companion,frame['binding'])
            matches=[r for r in validated_state['cancellations'] if r['key']==companion['key']]
            if len(matches)!=1 or matches[0]['stage']!='AdmissionRetired' or matches[0]['certificate'] is None:
                raise Refused('Cached settlement lacks matching V7 retired certificate')
            record=matches[0]
            expected=make_settlement(record,companion,frame['binding'])
            if any(frame[key]!=expected[key] for key in expected if key not in ('ackState','acknowledgement')):
                raise Refused('Cached settlement differs from stored terminal')
            if ACK_RANK[frame['ackState']]>ACK_RANK[record['ackState']]:
                raise Refused('Cached ACK is ahead of durable V7')
            if frame['ackState']=='Acknowledged' and frame['acknowledgement']!=record['acknowledgement']:
                raise Refused('Cached acknowledgement differs from stored native ACK')
            fd=os.open(name,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=directory)
            try:
                owner.verify(fd)
                if os.read(fd,MAX_FRAME+1)!=raw:
                    raise Refused('Cancellation cache changed under host guard')
                os.fsync(fd)
            finally:
                try:os.close(fd)
                except OSError:
                    owner.poisoned=True
                    raise
            os.fsync(directory)
            return frame
    except OSError:
        owner.poisoned=True
        raise
