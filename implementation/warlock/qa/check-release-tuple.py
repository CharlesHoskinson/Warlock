"""Protected checks of the explicit fresh tuple selection; no GUI acceptance."""
import hashlib, importlib.util, json, os, pathlib, sys, types, tempfile, copy, shlex, shutil
from unittest.mock import patch
repo = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo / 'window-integration-qa'))
from qa_launch import require_qa_scope
require_qa_scope()
sys.path.insert(0, str(repo / 'implementation/warlock/adapter'))
import release_builder as builder
import release_tuple

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def selection(path, digest):
    files = {}
    def add(p, role, expected=None):
        p = pathlib.Path(p)
        builder.add(files, p, role, expected)
    result = release_tuple.capture(repo, path, digest, add, builder.read, sha)
    return result, files

def refuses(fn):
    try:
        fn()
    except (ValueError, OSError, builder.ChangedInput, KeyError):
        return
    raise AssertionError('Expected refusal')

def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: check-release-tuple.py ABSOLUTE_TUPLE SHA256')
    path, digest = sys.argv[1:]
    tuple_data = builder.read(path)
    (pair, aliases, ref), files = selection(path, digest)
    assert set(pair) == {'core', 'plugin', 'aquamarine'}
    assert pair['plugin']['sha256'] == tuple_data['slots']['authority']['sha256']
    assert ref['nativeAcceptance'] is False and ref['historicalBinaryReproduction'] is False
    assert ref['missingObservation'] and aliases == {pathlib.Path(tuple_data['slots']['aquamarine']['sonameAlias']).name: tuple_data['slots']['aquamarine']['aliasTarget']}
    assert files
    refuses(lambda: selection(path, '0' * 64))
    refuses(lambda: selection(path, ''))
    refuses(lambda: builder.capture(repo, path, None))
    refuses(lambda: builder.capture(repo, None, digest))
    reports = tuple_data['reports']
    core_report = builder.read(reports['core-build-report.json']['path'])
    argv = core_report['commands'][0]['argv']
    core_source = pathlib.Path(argv[argv.index('-S') + 1])
    snapshot = builder.read(reports['core-consumed-source-snapshot.json']['path'])
    source_file = str(core_source / next(iter(snapshot['files'])))
    authority = builder.read(reports['authority/authority-build-report.json']['path'])
    dependency = next(iter(authority['dependencies']))
    aq_report = builder.read(reports['aquamarine-build-report.json']['path'])
    argv = aq_report['commands'][0]['argv']
    aq_source = str(pathlib.Path(argv[argv.index('-S') + 1]) / 'src/backend/Wayland.cpp')
    targets = [reports['core-build-report.json']['path'], source_file, dependency,
               tuple_data['slots']['core']['path'], aq_source]
    actual_sha = builder.sha
    for target in targets:
        with patch.object(builder, 'sha', side_effect=lambda p, t=target: '0' * 64 if str(p) == t else actual_sha(p)):
            refuses(lambda: selection(path, digest))
    # Re-pin a malformed report, so rejection must come from its internal
    # recorded-digest validation rather than an outer manifest hash mismatch.
    with tempfile.TemporaryDirectory(prefix='warlock-tuple-negative-') as directory:
        folder = pathlib.Path(directory)
        malformed = copy.deepcopy(snapshot)
        malformed['files'][next(iter(malformed['files']))] = None
        report = folder / 'snapshot.json'
        report.write_text(json.dumps(malformed))
        changed = copy.deepcopy(tuple_data)
        changed['reports']['core-consumed-source-snapshot.json'] = {'path': str(report), 'sha256': sha(report)}
        manifest = folder / 'tuple.json'
        manifest.write_text(json.dumps(changed))
        refuses(lambda: selection(str(manifest), sha(manifest)))
    report_path = tuple_data['reports']['core-build-report.json']['path']
    old_read_bytes = pathlib.Path.read_bytes
    with patch.object(pathlib.Path, 'read_bytes', lambda p: old_read_bytes(p) + b' ' if str(p) == report_path else old_read_bytes(p)):
        refuses(lambda: selection(path, digest))
    core_path = tuple_data['slots']['core']['path']
    bad_ldd = types.SimpleNamespace(returncode=0, stdout=' libaquamarine.so.14 => /usr/lib/libaquamarine.so.14 (0x1)\n', stderr='')
    with patch.object(builder.subprocess, 'run', return_value=bad_ldd):
        refuses(lambda: builder.add_dynamic({}, core_path, pathlib.Path(tuple_data['slots']['aquamarine']['sonameAlias'])))
    alias = tuple_data['slots']['aquamarine']['sonameAlias']
    real_readlink = os.readlink
    with patch.object(release_tuple.os, 'readlink', side_effect=lambda p: 'wrong-target' if str(p) == alias else real_readlink(p)):
        refuses(lambda: selection(path, digest))
    original = pathlib.Path.is_symlink
    with patch.object(pathlib.Path, 'is_symlink', lambda p: False if str(p) == alias else original(p)):
        refuses(lambda: selection(path, digest))
    tools = {'g++': {'path': shutil.which('g++')}}
    flags = shlex.split(builder.run([shutil.which('pkg-config'), '--cflags', '--libs', *builder.PACKAGES]))
    traced = {}
    trace = builder.native_link_inputs(traced, repo / 'implementation/warlock', tools, flags)
    missing_library = pathlib.Path('/usr/lib/libmvec.so.1').resolve()
    assert str(missing_library) in trace['inputs']
    assert traced[str(missing_library)]['sha256'] == sha(missing_library)
    assert 'host-link-trace-input' in traced[str(missing_library)]['roles']
    assert not any('warlock-link-inputs-' in p for p in traced)
    print(json.dumps({'passed': True, 'nativeAcceptance': False, 'traceInputCount': len(trace['inputs']), 'checks': ['fresh selection including retained failed compile and successful retry', 'tuple digest', 'missing digest', 'report mutation', 'source mutation', 'dependency mutation', 'artifact mutation', 'AQ source mutation', 're-pinned null recorded digest', 'report read race', 'wrong AQ provider', 'alias changed', 'alias missing', 'actual linker trace captures script-only libmvec dependency without probe artifacts']}))

if __name__ == '__main__':
    main()
