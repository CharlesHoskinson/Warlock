"""Actual staged transport drain while a native transaction callback is blocked."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import time

from pipe_transport import PipeTransport


def main():
    with tempfile.TemporaryDirectory(prefix='motion-pipe-replay-') as directory:
        root = Path(directory)
        done = root / 'producer-finished-writes'
        producer = root / 'producer'
        producer.write_text('#!' + sys.executable + '\n' +
            'import json,sys,pathlib\n' +
            'print(json.dumps({"event":"ready","token":"abcdef123456-1"}),flush=True)\n' +
            'for i in range(80):\n' +
            ' print(json.dumps({"event":"presented","sequence":i,"payload":"x"*16384}),flush=True)\n' +
            'pathlib.Path(' + repr(str(done)) + ').write_text("all writes returned")\n' +
            'for line in sys.stdin:\n' +
            ' if json.loads(line).get("command")=="stop":break\n')
        producer.chmod(0o700)
        entered, release = threading.Event(), threading.Event()
        failures = []
        transport = PipeTransport(producer, env=dict(__import__('os').environ), failure=failures.append)
        def native_callback(event):
            entered.set()
            if not release.wait(3):
                raise AssertionError('root did not release controlled native callback')
        transport.set_callback(native_callback)
        try:
            assert entered.wait(1), 'actual transport ready callback not reached'
            time.sleep(0.15)
            blocked = not done.exists()
            before = len(transport.events)
            release.set()
            deadline = time.monotonic() + 2
            while not done.exists() and time.monotonic() < deadline:
                time.sleep(0.005)
            assert done.exists(), 'producer never completed after callback release'
            deadline = time.monotonic() + 1
            while len(transport.events) < 81 and time.monotonic() < deadline:
                time.sleep(0.005)
            report = {'kind': 'actual copied PipeTransport continuous drain during blocked native callback',
                      'transportSHA256': hashlib.sha256(Path('pipe_transport.py').read_bytes()).hexdigest(),
                      'producerWritesBlockedUntilCallbackRelease': blocked,
                      'eventCountWhileCallbackBlocked': before,
                      'eventCountAfterCallbackRelease': len(transport.events),
                      'counterexampleReproduced': blocked and before == 1 and len(transport.events) == 81,
                      'nativeGUIUsed': False,
                      'scope': 'actual subprocess pipe/source transport; controlled callback latency, no attribution to retained V4 presentation failure'}
            assert report['counterexampleReproduced'], report
            Path('blocked-callback-pipe-counterexample.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps(report, indent=2))
        finally:
            release.set()
            transport.close()


if __name__ == '__main__':
    main()
