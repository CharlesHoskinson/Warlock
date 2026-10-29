#!/usr/bin/env python3
"""Source-bound native wire protocol check; no GUI or native clock claim."""
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile

REPO = Path('/home/charles/Warlock')
PRODUCT = REPO / 'implementation/warlock'
HERE = Path(__file__).resolve().parent
RAW = PRODUCT / 'qa/evidence/lossless-deadline-20261029/observations.json'
RAW_SHA = '98f0504aab46254df52a3545362fac354500b57d3816c7aba8b09411459ed847'
PINS = {'native/preview_wire.hpp': '2b02108a819e97106cbf38e420871bc4ee10656fd6f98905f25c30fd838d283d',
        'native/preview_client.hpp': 'b4eb7386f0bfae58aaf07816b0b70f7605c921694ff30681bad848abac11fb38',
        'native/client_producer.hpp': 'b93355d804613a68593bfd2447295287ac04c76427007c5772e6244b4c51d990',
        'native/preview_broker.hpp': '9c57428130093f8d815b7851004f103897deca278bbe4196e2116bec85a323ed',
        'native/preview_uri.cpp': '9ea85c70a77841c5035dce95f61932f92153f607e7be78bbd122819a3c3d8f77',
        'qa/check-deadline-bridge.py': 'e7fb7ac8687914d623f06496c527c32151ee8399e26661d1c19cd2ce74421c40',
        'qa/DeadlineBridgeReplay.elm': 'e7a0dd41a597a8298bef90c7122ea9a63d9d982ef0ad4dade1bd078a722e5468',
        'qa/deadline-bridge-replay.cjs': 'bd6632d1da77611874ec07b27e41b90f7743747b9aac49303625fc2d93c41753'}
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(argv, report, cwd, timeout=120):
    result = subprocess.run([str(a) for a in argv], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    report['processes'].append({'argv': [str(a) for a in argv], 'exit': result.returncode,
                                'stdout': result.stdout, 'stderr': result.stderr})
    if result.returncode:
        raise RuntimeError('command failed: ' + str(argv[0]))
    return result.stdout


def dependencies(text):
    # GCC makefile continuation and shell-style escaped spaces.
    return [Path(name).resolve() for name in shlex.split(text.replace('\\\n', ' ').split(':', 1)[1])]


def main():
    report = {'passed': False, 'requirement': 'ELM-REV-007', 'processes': [],
              'scope': 'Native production wire protocol; inputs are semantically reserialized retained Elm worker JSON, not original JS wire bytes. No native clock, Main, Popup/host continuity, native GUI, or requirement acceptance.'}
    try:
        report['protectedScope'] = require_qa_scope()
        assert sha(RAW) == RAW_SHA
        raw = json.loads(RAW.read_text()); assert raw['passed'] is True
        for name, digest in PINS.items():
            assert sha(PRODUCT / name) == digest, name
        report['rawEvidence'] = {'path': str(RAW), 'sha256': RAW_SHA}
        report['sourcePins'] = PINS
        report['fixtureSources'] = {str(p): sha(p) for p in (HERE / 'native-deadline-wire.cpp', Path(__file__).resolve())}
        high = '9007199254740993'
        binding = {'lifetime': high, 'session': '1', 'frontend': '1'}
        context = {'lifetime': high, 'incarnation': high, 'output': '1', 'privacy': '1',
                   'rendering': '1', 'scene': '1', 'content': '1'}
        selected = [('adjacent-deadline-first', 'commands', 'acquire', high),
                    ('adjacent-deadline-second', 'commands', 'acquire', '9007199254740994'),
                    ('clock-reaches-original-deadline', 'clockCommands', 'cancel', '9007199254740994')]
        commands = []; expected_jobs = []
        for name, field, kind, deadline in selected:
            matches = [row for row in raw['receipts'] if row['name'] == name]
            assert len(matches) == 1 and matches[0]['passed'] is True
            row = matches[0]; trigger = row['input']['request']['trigger']
            expected = {'binding': binding, 'context': context, 'request': '1',
                        'origin': '1', 'clock': high, 'deadline': deadline}
            assert trigger == {'binding': binding, 'context': context, 'origin': '1', 'clock': high, 'deadline': deadline}
            assert row['output']['accepted'] is True and len(row['output'][field]) == 1
            command = row['output'][field][0]
            assert command == {'kind': kind, 'job': expected}
            commands.append(json.dumps(command, separators=(',', ':'), ensure_ascii=True))
            expected_jobs.append(expected)
        report['inputCommands'] = [{'receipt': row[0], 'semanticJSON': text,
                                     'sha256': hashlib.sha256(text.encode()).hexdigest()} for row, text in zip(selected, commands)]
        cc = Path('/usr/bin/g++').resolve(); pkg = Path('/usr/bin/pkg-config').resolve(); ldd = Path('/usr/bin/ldd').resolve()
        report['tools'] = {str(p): sha(p) for p in (cc, pkg, ldd)}
        run([cc, '--version'], report, PRODUCT)
        run([pkg, '--version'], report, PRODUCT)
        packages = ['gtk+-3.0', 'json-glib-1.0', 'gio-unix-2.0']
        for package in packages:
            run([pkg, '--modversion', package], report, PRODUCT)
            pc = Path(run([pkg, '--path', package], report, PRODUCT).strip()).resolve()
            report.setdefault('packageMetadata', {})[str(pc)] = sha(pc)
        cflags = shlex.split(run([pkg, '--cflags', *packages], report, PRODUCT))
        libs = shlex.split(run([pkg, '--libs', *packages], report, PRODUCT))
        for tool in ('cc1plus', 'as', 'ld'):
            path = Path(run([cc, '-print-prog-name=' + tool], report, PRODUCT).strip())
            if not path.is_absolute():
                import shutil
                found = shutil.which(str(path)); assert found, tool
                path = Path(found)
            path = path.resolve(); report['tools'][str(path)] = sha(path)
        with tempfile.TemporaryDirectory(prefix='warlock-native-deadline-wire-') as temp:
            temp = Path(temp); binary = temp / 'native-deadline-wire'; depfile = temp / 'headers.d'
            source = HERE / 'native-deadline-wire.cpp'
            common = [cc, '-std=c++20', '-Wall', '-Wextra', '-Werror', '-I' + str(PRODUCT / 'native'), *cflags]
            units = [source, PRODUCT / 'native/preview_uri.cpp']
            before = set()
            for unit in units:
                before.update(dependencies(run([*common, '-M', unit], report, PRODUCT)))
            source_hashes = {str(path): sha(path) for path in sorted(before)}
            objects, depfiles, after = [], [], set()
            for index, unit in enumerate(units):
                obj = temp / ('unit-' + str(index) + '.o')
                depfile = temp / ('unit-' + str(index) + '.d')
                run([*common, '-MD', '-MF', depfile, '-c', unit, '-o', obj], report, PRODUCT)
                objects.append(obj); depfiles.append(depfile)
                after.update(dependencies(depfile.read_text()))
            assert after == before, 'compiler dependency set changed'
            run([cc, *objects, '-o', binary, *libs], report, PRODUCT)
            assert all(sha(path) == digest for path, digest in source_hashes.items()), 'source changed during compile'
            report['dependencySHA256'] = source_hashes
            report['dependencyFilesSHA256'] = {str(path): sha(path) for path in depfiles}
            report['compiledSHA256'] = sha(binary)
            linked = run([ldd, binary], report, PRODUCT)
            report['linkedProviders'] = {}
            for line in linked.splitlines():
                assert 'not found' not in line, line
                match = re.search(r'(?:=>\s*)?(/\S+)\s+\(', line)
                if match:
                    provider = Path(match.group(1)).resolve(); report['linkedProviders'][str(provider)] = sha(provider)
            assert report['linkedProviders'], 'no link providers recorded'
            stdout = run([binary, *commands], report, PRODUCT)
            receipts = [json.loads(line) for line in stdout.splitlines()]
            assert len(receipts) == 152 and all(row['passed'] is True for row in receipts)
            assert len({row['name'] for row in receipts}) == len(receipts)
            for prefix, expected in zip(('first-acquire', 'second-acquire', 'second-cancel'), expected_jobs):
                row = next(row for row in receipts if row['name'] == prefix + '.wire-job')
                assert json.loads(row['detail']) == expected
            distinct = {'binding': {'lifetime': '9007199254741000', 'session': '9007199254741001', 'frontend': '9007199254741002'},
                        'context': {'lifetime': '9007199254741000', 'incarnation': '9007199254741003', 'output': '9007199254741004',
                                    'privacy': '9007199254741005', 'rendering': '9007199254741006', 'scene': '9007199254741007', 'content': '9007199254741008'},
                        'request': '9007199254741009', 'origin': '9007199254741010', 'clock': '9007199254741011'}
            for index, deadline in enumerate(('9007199254740993', '9007199254740994'), 1):
                row = next(row for row in receipts if row['name'] == 'distinct-' + str(index) + '.wire-job')
                assert json.loads(row['detail']) == {**distinct, 'deadline': deadline}
            assert sha(RAW) == RAW_SHA
            assert all(sha(PRODUCT / name) == digest for name, digest in PINS.items())
            assert all(sha(path) == digest for path, digest in source_hashes.items())
            assert all(sha(path) == digest for path, digest in report['fixtureSources'].items())
            assert all(sha(path) == digest for path, digest in report['tools'].items())
            assert all(sha(path) == digest for path, digest in report['packageMetadata'].items())
            assert all(sha(path) == digest for path, digest in report['linkedProviders'].items())
            report['receipts'] = receipts
        report['passed'] = True
    except Exception as error:
        report['error'] = repr(error)
    print(json.dumps(report, indent=2))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
