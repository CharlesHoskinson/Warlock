"""Actual process/executable identity with both supervisor start encodings."""
import hashlib, os, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'adapter'))
from endpoint import Endpoint, Refused, start_time

class ProcessOnly(Endpoint):
    def verify_paths(self):
        pass

pid = os.getpid()
start = start_time(pid)
digest = hashlib.file_digest(open('/proc/self/exe', 'rb'), 'sha256').hexdigest()
checks = 0
def admitted(value):
    global checks
    endpoint = ProcessOnly('/tmp', 'fixture', pid, value, digest)
    assert endpoint.start == start
    endpoint.verify_process()
    checks += 1
def refused(value, target=pid, binary=digest):
    global checks
    try:
        ProcessOnly('/tmp', 'fixture', target, value, binary)
    except Refused:
        checks += 1
        return
    raise AssertionError((value, target, binary))

admitted(start)
admitted(int(start))
for invalid in [True, False, 0, -1, 1.5, None, '', '0', '01', '-1', '1.0',
                '18446744073709551616', 18446744073709551616, str(int(start)+1), int(start)+1]:
    refused(invalid)
refused(start, target=True)
refused(start, target=0)
refused(start, binary='0'*64)
print('Exact live process identity controls:', checks)
