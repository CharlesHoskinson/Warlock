"""Read-only root source/build audit; this script never starts a GUI."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

BASE = Path('/home/hoskinson/window-behavior-spec/pin-maximized-core-v3-hit-fallback')
QA = Path('/home/hoskinson/window-integration-qa')
errors = []
counts = {}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(path, expected, label):
    path = Path(path)
    if not path.is_absolute():
        path = BASE / path
    actual = path.stat()
    for key, value in expected.items():
        observed = {'sha256': lambda: digest(path),
                    'mode': lambda: stat.S_IMODE(actual.st_mode),
                    'size': lambda: actual.st_size,
                    'mtimeNs': lambda: actual.st_mtime_ns}.get(key)
        if observed and observed() != value:
            errors.append({'path': str(path), 'field': key, 'label': label})
    counts[label] = counts.get(label, 0) + 1


def closure(base, data, label):
    for name, value in data['files'].items():
        path = base / name
        if path.is_symlink() or not stat.S_ISREG(path.lstat().st_mode):
            errors.append({'path': str(path), 'field': 'regular-file'})
        metadata(path, value, label + 'Files')
    for name, value in data['links'].items():
        path = base / name
        if (not path.is_symlink() or os.readlink(path) != value['target']
                or stat.S_IMODE(path.lstat().st_mode) != value['mode']):
            errors.append({'path': str(path), 'field': 'literal-link'})
        counts[label + 'Links'] = counts.get(label + 'Links', 0) + 1
    for name, mode in data['directories'].items():
        path = base / name
        if path.is_symlink() or not path.is_dir() or stat.S_IMODE(path.stat().st_mode) != mode:
            errors.append({'path': str(path), 'field': 'directory'})
        counts[label + 'Directories'] = counts.get(label + 'Directories', 0) + 1


ready = json.loads((BASE / 'SOURCE_READY.json').read_text())
inventory = json.loads((BASE / 'SOURCE_READY_INPUTS.json').read_text())
assert digest(BASE / 'SOURCE_READY.json') == '0235a02ae77f5e144b93e036bf6013d0d0da0954130a184448a5ef4154b2373a'
assert digest(BASE / 'SOURCE_READY_INPUTS.json') == ready['sourceClosureSHA256'] == '82eaec349bc2bb4b9fce35eca431c607d9171f38566f4c299d882bfc160823f0'
closure(BASE, inventory, 'v3')
for ancestor in inventory['ancestors']:
    original = Path(ancestor['stage'])
    closure(original, ancestor, 'ancestor')
    metadata(original / 'SOURCE_READY.json', ancestor['sourceReady'], 'ancestorDescriptors')
    metadata(original / 'SOURCE_READY_INPUTS.json', ancestor['sourceReadyInputs'], 'ancestorDescriptors')

build = json.loads((BASE / 'final-review/build-input-output-closure.json').read_text())
for key in ['tools', 'linkInputs', 'buildInputs', 'outputs']:
    for path, value in build[key].items():
        metadata(path, value, key)
assert build['coreExit'] == build['pluginExit'] == 0
assert build['coreSession'] == 57713 and build['pluginSession'] == 73151
libraries = json.loads((BASE / 'final-review/compiler-and-linked-library-closure.json').read_text())
for path, value in libraries['compilerComponents'].items():
    metadata(path, value, 'compilerComponents')
for path, value in libraries['libraries'].items():
    metadata(path, value['metadata'], 'libraries')
metadata('/etc/ld.so.cache', libraries['loaderCache'], 'loaderCache')

objects = json.loads((BASE / 'final-review/core-object-freshness.json').read_text())
assert not objects['newerDependencies']
for row in objects['objects']:
    metadata(row['path'], row['metadata'], 'coreObjects')
    if digest(BASE / row['dependencyFile']) != row['dependencyFileSHA256']:
        errors.append({'path': row['dependencyFile'], 'field': 'dependency-file'})
    for dependency in row['dependencies']:
        if Path(dependency).stat().st_mtime_ns > (BASE / row['path']).stat().st_mtime_ns:
            errors.append({'path': dependency, 'field': 'newer-than-object'})
for path, value in objects['dependencies'].items():
    metadata(path, value, 'coreDependencies')
plugin = json.loads((BASE / 'final-review/plugin-dependency-freshness.json').read_text())
assert not plugin['newerDependencies'] and all(row['exitCode'] == 0 for row in plugin['commands'])
for path, value in plugin['dependencies'].items():
    metadata(path, value, 'pluginDependencies')

delta = json.loads((BASE / 'final-review/v2-runtime-delta-conservation.json').read_text())
expected_delta = {'core/src/desktop/state/ViewHitTester.cpp', 'core/src/managers/input/InputManager.cpp',
                  'core/src/desktop/state/pin/CorePolicyBuild.hpp', 'helper/pin_helper.py'}
assert set(delta['changed']) == expected_delta and not delta['missingSourceFiles'] and delta['allOtherBytesExact'] is True
inverse = json.loads((BASE / 'final-review/v2-to-v3-whole-inverse-map.json').read_text())
for row in inverse['paths']:
    metadata(row['path'], row['after'], 'changedSources')
    metadata(BASE / row['wholeInverse'], row['before'], 'wholePreimages')
ancestor = Path(inventory['ancestors'][0]['stage'])
for root in ['core', 'helper', 'plugin']:
    for path in (ancestor / root).rglob('*'):
        if not path.is_file() or path.is_symlink() or path.suffix not in {'.cpp', '.hpp', '.h', '.py', '.qnt'}:
            continue
        rel = path.relative_to(ancestor)
        current = BASE / rel
        if str(rel) not in expected_delta and (not current.is_file() or digest(current) != digest(path)):
            errors.append({'path': str(rel), 'field': 'unauthorized-source-delta'})
        counts['sourceDeltaComparisons'] = counts.get('sourceDeltaComparisons', 0) + 1

note = subprocess.run(['/usr/bin/readelf', '-n', str(BASE / 'build-core-make/Hyprland')], capture_output=True, text=True, check=True).stdout
assert ready['coreELFBuildID'] in note
gate = json.loads((BASE / 'final-review/final-gate.json').read_text())
assert gate['actualOwningChecks'] == 33 and gate['actualCompiledPolicyChecks'] == 38
assert gate['originalUpstreamCPUTests'] == 270 and gate['pluginCPUCases'] == 311 and gate['helperSchemaConservationTests'] == 72
assert gate['approvedDesignNamed'] == 129 and gate['approvedDesignTraces'] == 6000
assert gate['transferNamed'] == 20 and gate['transferTraces'] == 2000
assert gate['newHitNamed'] == 24 and gate['newHitTraces'] == 2000 and gate['actualHitRowsEach'] == 26
assert not ready['nativeAccepted'] and not gate['nativeExecuted']

report = dict(result='pass' if not errors else 'fail', counts=counts, errors=errors,
              sourceReadySHA256=digest(BASE / 'SOURCE_READY.json'),
              sourceClosureSHA256=digest(BASE / 'SOURCE_READY_INPUTS.json'),
              corePolicyBuild=ready['corePolicyBuild'], coreELFBuildID=ready['coreELFBuildID'],
              sourceAndBuildAccepted=not errors, nativeAuthorized=False, nativeAccepted=False,
              exactApprovedDelta=sorted(expected_delta), gates=gate,
              limits=['CPU owning fixtures are not actual window admission or Seat focus',
                      'Original14 native run and separate native MAX/scroll/transfer campaign remain',
                      'Symbol availability is not native load/unload proof'])
destination = QA / 'pin-max-core-v3-root-source-review-v1.json'
with destination.open('x') as output:
    output.write(json.dumps(report, indent=2, sort_keys=True) + '\n')
    output.flush()
    os.fsync(output.fileno())
print(json.dumps({'result': report['result'], 'counts': counts, 'errors': errors,
                  'review': str(destination), 'sha256': digest(destination)}))
raise SystemExit(bool(errors))
