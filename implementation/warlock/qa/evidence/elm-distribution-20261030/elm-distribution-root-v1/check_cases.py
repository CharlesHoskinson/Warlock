"""Protected real correspondence plus safety/refusal cases; no remote execution."""
import base64
import copy
import gzip
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import traceback

HERE = Path(__file__).resolve().parent
REPO = Path('/home/charles/Warlock')
TARGET = REPO/'implementation/warlock/qa/check-elm-distribution.py'


def main():
    sys.path.insert(0, str(REPO/'window-integration-qa'))
    from qa_launch import require_qa_scope
    scope = require_qa_scope()
    raw = TARGET.read_bytes()
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader('elm_distribution', loader=None))
    m.__file__ = str(TARGET)
    exec(compile(raw, str(TARGET), 'exec'), m.__dict__)
    report = dict(passed=False, scope=scope, sourceSHA256=m.sha(raw), checks=[],
                  nativeAcceptance=False, releaseAccepted=False, redistributionApproved=False)
    def check(name, value):
        report['checks'].append(dict(name=name, passed=bool(value)))
        if not value:
            raise AssertionError(name)
    def rejects(name, call):
        try:
            call()
        except (ValueError, OSError, tarfile.TarError, EOFError) as error:
            report['checks'].append(dict(name=name, passed=True, error=str(error)))
        else:
            check(name, False)
    try:
        try:
            run = subprocess.run(['/usr/bin/python3', '-B', str(TARGET)], capture_output=True, timeout=90)
        except subprocess.TimeoutExpired as error:
            (HERE/'proof.stdout').write_bytes(error.stdout or b'')
            (HERE/'proof.stderr').write_bytes(error.stderr or b'')
            raise
        (HERE/'proof.stdout').write_bytes(run.stdout)
        (HERE/'proof.stderr').write_bytes(run.stderr)
        check('Actual protected checker exits normally', run.returncode == 0)
        result = json.loads(run.stdout)
        check('Both published distributions and eight members observed', result['passed'] and len(result['archives']) == 2 and sum(len(p['files']) for p in result['archives']) == 8)
        check('Observed alias bytes equal exact held compiler', result['installed']['node_modules/elm/bin/elm']['sha256'] == result['installed']['node_modules/@elm_binaries/linux_x64/elm']['sha256'] == m.BINARY_SHA)
        check('No grant or upstream source build correspondence claimed', not result['redistributionApproved'] and not result['upstreamSourceBuildCorrespondenceEstablished'] and not result['releaseAccepted'])
        held, lock = m.frozen_inputs()
        rejects('Changed lock bytes refused', lambda: m.verify(held, lock+b' '))
        damaged = dict(held)
        damaged['elm.tgz'] += b'bad'
        rejects('Changed actual archive body refused by response join', lambda: m.verify(damaged, lock))
        entry = m.decode(lock)['packages']['node_modules/elm']
        rejects('Actual SRI validator rejects altered archive', lambda: m.archive_files(held['elm.tgz']+b'bad', entry['integrity']))
        rejects('Duplicate JSON keys refused', lambda: m.decode(b'{"x":1,"x":2}'))
        fifo = HERE/'nonregular-input'
        os.mkfifo(fifo, 0o600)
        rejects('FIFO refused without blocking read', lambda: m.read_regular(fifo))
        def changed_response(name, change):
            candidate = dict(held)
            data = copy.deepcopy(m.decode(held['responses.json']))
            change(data['responses'][0])
            candidate['responses.json'] = json.dumps(data).encode()
            rejects(name, lambda: m.verify(candidate, lock))
        changed_response('Wrong requested URL refused', lambda row: row.update(requestedURL='https://example.invalid/'))
        changed_response('Wrong response URL refused', lambda row: row.update(responseURL='https://example.invalid/'))
        changed_response('Wrong response status refused', lambda row: row.update(status=404))
        changed_response('Wrong response body size refused', lambda row: row.update(size=row['size']+1))
        changed_response('Wrong HTTP content length refused', lambda row: row['headers'].update({'content-length': '1'}))
        changed_response('Encoded response refused', lambda row: row['headers'].update({'content-encoding': 'gzip'}))
        candidate = dict(held)
        meta = m.decode(held['elm.json']);meta['version'] = 'wrong'
        candidate['elm.json'] = json.dumps(meta).encode()
        responses = m.decode(held['responses.json'])
        responses['responses'][0].update(size=len(candidate['elm.json']), sha256=m.sha(candidate['elm.json']))
        responses['responses'][0]['headers']['content-length'] = str(len(candidate['elm.json']))
        candidate['responses.json'] = json.dumps(responses).encode()
        rejects('Changed metadata refused after matching body receipt', lambda: m.verify(candidate, lock))
        def synthetic(names, link=False, oversize=False, member_type=None):
            out = io.BytesIO()
            if oversize:
                item = tarfile.TarInfo('package/large');item.size=60_000_001
                data = item.tobuf()+b'\0'*1024
            else:
                with tarfile.open(fileobj=out, mode='w') as tar:
                    for name in names:
                        item = tarfile.TarInfo(name)
                        if link:
                            item.type=tarfile.SYMTYPE;item.linkname='../outside'
                            tar.addfile(item)
                        else:
                            item.type=member_type or tarfile.REGTYPE
                            item.size=0 if item.type==tarfile.DIRTYPE else 1
                            tar.addfile(item, io.BytesIO(b'x'))
                data = out.getvalue()
            compressed = gzip.compress(data)
            sri = 'sha512-'+base64.b64encode(hashlib.sha512(compressed).digest()).decode()
            return compressed, sri
        for name, args in [
            ('Nonpackage archive prefix refused', synthetic(['other/x'])),
            ('Traversal refused', synthetic(['package/../x'])),
            ('Absolute path refused', synthetic(['/package/x'])),
            ('Duplicate member refused', synthetic(['package/x', 'package/x'])),
            ('Archive link refused', synthetic(['package/x'], link=True)),
            ('Contiguous-file extension refused', synthetic(['package/x'], member_type=tarfile.CONTTYPE)),
            ('Directory outside exact file-only scope refused', synthetic(['package/x'], member_type=tarfile.DIRTYPE)),
            ('Oversized declared member refused before read', synthetic([], oversize=True)),
        ]:
            rejects(name, lambda args=args: m.archive_files(*args))
        # Copy only the two npm packages as a bounded negative fixture. Never
        # hardlink mutable test files into the immutable retained toolchain.
        fixture = HERE/'installed-negative'
        for _, key, _, _ in m.PACKAGES:
            shutil.copytree(m.INSTALLED/key, fixture/key)
        check('Independent copied layout is a reachable positive control', m.verify(held, lock, root=fixture)['passed'])
        target = fixture/'node_modules/elm/bin/elm'
        with target.open('r+b') as stream:
            stream.seek(100);old=stream.read(1);stream.seek(100);stream.write(bytes([old[0]^1]))
        rejects('Actual changed installed binary copy refused', lambda: m.verify(held, lock, root=fixture))
        report['counterexample'] = dict(path=str(target), offset=100, beforeByte=old[0], afterByte=old[0]^1,
                                         sha256=m.sha(target.read_bytes()), originalToolchainModified=False)
        check('Original toolchain still validates after negative', m.verify(held, lock)['passed'])
        check('Executed checker source unchanged', TARGET.read_bytes() == raw)
        report['passed'] = True
    except Exception as error:
        report.update(error=repr(error), traceback=traceback.format_exc())
    (HERE/'cases-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=report['passed'], checks=len(report['checks']), report=str(HERE/'cases-report.json'), error=report.get('error'))))
    return 0 if report['passed'] else 1
if __name__ == '__main__':
    sys.exit(main())
