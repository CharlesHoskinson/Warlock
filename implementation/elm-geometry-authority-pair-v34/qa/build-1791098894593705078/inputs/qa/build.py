"""Protected CPU-only build of an unchanged authority for the qualified V28 core."""
import hashlib
import json
import os
from pathlib import Path
import resource
import shlex
import shutil
import subprocess
import time
import sys

sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OWNER = REPO / 'implementation/maximized-stack-v1/native-core-v2'
OUT = ROOT / 'qa' / ('build-' + str(time.time_ns()))
OUT.mkdir()
report = {'passed': False, 'nativeAcceptance': False, 'installed': False,
          'scope': 'Exact owning binary/plugin compile closure only; no host or GUI', 'commands': []}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def verify_inventory(root, entries):
    for entry in entries:
        p = root / entry['path']
        if 'symlink' in entry:
            assert p.is_symlink() and os.readlink(p) == entry['symlink'], str(p)
        else:
            assert not p.is_symlink() and p.is_file(), str(p)
            assert p.stat().st_size == entry['size'] and sha(p) == entry['sha256'], str(p)


def run(name, command):
    p = subprocess.run(command, capture_output=True, text=True, timeout=240)
    (OUT / (name + '.stdout')).write_text(p.stdout)
    (OUT / (name + '.stderr')).write_text(p.stderr)
    report['commands'].append({'name': name, 'command': command, 'exitCode': p.returncode})
    print(name, p.returncode, flush=True)
    assert p.returncode == 0, p.stderr[-6000:]
    return p.stdout


# Capture the new runner and inherited source before validation, including
# failed attempts; prior report/input directories remain untouched.
files = [p for p in sorted(ROOT.rglob('*')) if p.is_file() and not any(part.startswith('build-') for part in p.relative_to(ROOT).parts[:-1]) and p.name != 'build-pair-manifest.json']
inputs = {str(p.relative_to(ROOT)): sha(p) for p in files}
for p in files:
    dest = OUT / 'inputs' / p.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)
    dest.chmod(0o444)
report['inputs'] = inputs

try:
    upstream = json.loads((ROOT / 'upstream.json').read_text())
    parent = Path(upstream['parent'])
    component = Path(upstream['coreComponent'])
    parent_manifest = parent / 'qa/build-pair-manifest.json'
    component_manifest = component / 'component-manifest.json'
    assert sha(parent_manifest) == upstream['parentPairManifestSHA256']
    assert sha(component_manifest) == upstream['coreComponentManifestSHA256']
    inventory = json.loads(component_manifest.read_text())
    assert inventory['passed'] and inventory['pluginABIQualified'] is False
    inventory_base = Path(upstream['inventoryBase'])
    verify_inventory(inventory_base, inventory['files'])
    inherited = {}
    for rel, digest in upstream['inheritedFiles'].items():
        local = ROOT / upstream['inheritedPaths'][rel]
        assert sha(parent / rel) == digest and sha(local) == digest, rel
        inherited[rel] = digest
    parent_pair = json.loads(parent_manifest.read_text())
    for rel, digest in parent_pair['files'].items():
        assert sha(parent / rel) == digest, rel
    pair = json.loads((ROOT / 'core-build-report.json').read_text())
    assert sha(ROOT / 'core-build-report.json') == upstream['coreDescriptorSHA256']
    assert pair['result'] == 'pass' and sha(pair['binary']) == pair['sha256']
    assert sha(pair['buildReport']) == pair['buildReportSHA256']
    core_report_rel = str(Path(pair['buildReport']).relative_to(inventory_base))
    assert any(entry['path'] == core_report_rel and entry.get('sha256') == pair['buildReportSHA256'] for entry in inventory['files'])
    core = json.loads(Path(pair['buildReport']).read_text())
    assert core['passed'] and core['binary'] == pair['binary'] and core['binarySHA256'] == pair['sha256']
    for rel, digest in core['inputs'].items():
        assert sha(component / 'core' / rel) == digest, rel
        assert sha(Path(pair['buildReport']).parent / 'inputs' / rel) == digest, rel
    for path, digest in core['dependencies'].items():
        assert sha(path) == digest, path
    for name in ('SceneModal.hpp', 'WindowPolicy.hpp', 'SceneTrace.hpp'):
        assert sha(ROOT / 'candidate' / name) == sha(Path(pair['buildReport']).parent / 'inputs/candidate' / name), name
    assert sha(OWNER / 'src/version.h') == core['owningVersionHeaderSHA256']
    # Bind V89's inherited compiler capture to the live owning headers before
    # copying. No /usr/include/hyprland or mutable owning source is compiled.
    core_closure = Path(pair['closureReport'])
    assert sha(core_closure) == pair['closureReportSHA256']
    closure = json.loads(core_closure.read_text())
    assert closure['passed'] and not closure['missingSymbols'] and closure['binary'] == pair['binary']
    previous_build = parent / parent_pair['buildReport']
    assert sha(previous_build) == parent_pair['buildReportSHA256']
    previous = json.loads(previous_build.read_text())
    for path, digest in previous['dependencies'].items():
        assert sha(path) == digest, path
    headers = dict(previous['owningHeaders'])
    for rel, digest in headers.items():
        p = previous_build.parent / 'owning-headers' / rel
        assert sha(p) == digest == sha(OWNER / rel), rel
        dest = OUT / 'owning-headers' / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        dest.chmod(0o444)
    include = OUT / 'include'
    include.mkdir()
    (include / 'hyprland').symlink_to(OUT / 'owning-headers', target_is_directory=True)
    flags = shlex.split(run('flags', ['pkg-config', '--cflags', 'json-glib-1.0', 'pixman-1', 'libdrm', 'libinput', 'wayland-server', 'libeis-1.0']))
    libs = shlex.split(run('libs', ['pkg-config', '--libs', 'json-glib-1.0']))
    binary = OUT / 'elm-window-effect-authority.so'
    run('compile', ['g++', '-std=c++23', '-O2', '-fPIC', '-shared', '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter',
        '-isystem', str(include), '-isystem', str(OUT / 'owning-headers'), '-isystem', str(OUT / 'owning-headers/src'),
        '-isystem', str(OUT / 'owning-headers/protocols'), '-I' + str(OUT / 'inputs/candidate'), *flags,
        '-MD', '-MF', str(OUT / 'authority.d'), str(OUT / 'inputs/native/authority.cpp'), '-o', str(binary), *libs])
    paths = shlex.split((OUT / 'authority.d').read_text().replace('\\\n', ' ').split(':', 1)[1])
    dependencies = {str(Path(p).resolve()): sha(Path(p).resolve()) for p in paths}
    assert not any(p.startswith('/usr/include/hyprland') or p.startswith(str(OWNER) + '/') for p in dependencies)
    symbols = run('core-symbols', ['nm', '-D', '-C', pair['binary']])
    for symbol in ('Desktop::WindowPolicy::applyMinimized', 'Desktop::WindowPolicy::isMinimized', 'Render::SceneTrace::snapshots'):
        assert symbol in symbols, symbol
    plugin_symbols = run('plugin-symbols', ['nm', '-D', '--defined-only', str(binary)])
    for symbol in ('pluginInit', 'pluginExit', 'pluginAPIVersion'):
        assert symbol in plugin_symbols, symbol
    # Strong undefined symbols must resolve through the selected core or exact
    # dynamic dependency exports. Versioned requests require exact versions.
    linked = {}
    for name, target in [('core', pair['binary']), ('plugin', str(binary))]:
        output = run(name + '-ldd', ['ldd', target])
        assert 'not found' not in output
        for line in output.splitlines():
            for word in line.split():
                if word.startswith('/') and Path(word).is_file():
                    p = Path(word).resolve(); linked[str(p)] = sha(p)
    exports = set()
    for index, path in enumerate([pair['binary'], *sorted(linked)]):
        for line in run('provider-symbols-' + str(index), ['nm', '-D', '--defined-only', path]).splitlines():
            words = line.split()
            if len(words) >= 3:
                symbol = words[-1].replace('@@', '@')
                exports.add(symbol); exports.add(symbol.split('@')[0])
    unresolved = []
    requested = []
    for line in run('plugin-undefined', ['nm', '-D', '--undefined-only', str(binary)]).splitlines():
        words = line.split()
        if len(words) == 2 and words[0] == 'U':
            symbol = words[1]; requested.append(symbol)
            if symbol not in exports: unresolved.append(symbol)
    assert not unresolved, unresolved
    link_report = {'passed': True, 'scope': 'Static strong dynamic symbol closure, not native loading acceptance',
                   'core': pair['binary'], 'coreSHA256': pair['sha256'],
                   'plugin': str(binary), 'pluginSHA256': sha(binary),
                   'strongUndefinedCount': len(requested), 'missingSymbols': unresolved,
                   'linkedLibraries': linked, 'providerExportCount': len(exports)}
    (OUT / 'link-closure.json').write_text(json.dumps(link_report, indent=2) + '\n')
    # Final checks cover both captured and live compilation inputs.
    for rel, digest in inputs.items():
        assert sha(ROOT / rel) == sha(OUT / 'inputs' / rel) == digest, rel
    for rel, digest in headers.items():
        assert sha(OWNER / rel) == sha(OUT / 'owning-headers' / rel) == digest, rel
    for path, digest in dependencies.items():
        assert sha(path) == digest, path
    verify_inventory(inventory_base, inventory['files'])
    assert sha(component_manifest) == upstream['coreComponentManifestSHA256']
    assert sha(parent_manifest) == upstream['parentPairManifestSHA256']
    for path, digest in core['dependencies'].items(): assert sha(path) == digest, path
    for path, digest in linked.items(): assert sha(path) == digest, path
    assert sha(core_closure) == pair['closureReportSHA256']
    assert sha(pair['binary']) == pair['sha256'] and sha(pair['buildReport']) == pair['buildReportSHA256']
    report.update(passed=True, binary=str(binary), binarySHA256=sha(binary), inputs=inputs,
                  owningHeaders=headers, dependencies=dependencies, inheritedFiles=inherited,
                  inheritedBuildReport=str(previous_build), inheritedBuildReportSHA256=sha(previous_build),
                  coreDependencies=core['dependencies'], coreClosureReport=str(core_closure),
                  coreClosureReportSHA256=sha(core_closure), linkedLibraries=linked,
                  linkClosureReport=str(OUT / 'link-closure.json'), linkClosureReportSHA256=sha(OUT / 'link-closure.json'),
                  tools={str(Path(shutil.which(name)).resolve()): sha(Path(shutil.which(name)).resolve()) for name in ('g++', 'pkg-config', 'nm', 'ldd')},
                  core={'path': pair['binary'], 'sha256': pair['sha256'], 'versionHeaderSHA256': core['owningVersionHeaderSHA256'],
                        'buildReport': pair['buildReport'], 'buildReportSHA256': pair['buildReportSHA256'],
                        'componentManifest': str(component_manifest), 'componentManifestSHA256': sha(component_manifest), 'inventoryBase': str(inventory_base)})
except Exception as e:
    report['error'] = repr(e)
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(OUT / 'report.json', flush=True)
raise SystemExit(not report['passed'])
