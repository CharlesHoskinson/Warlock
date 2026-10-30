"""Capture an explicitly reviewed derivative tuple; never infer native acceptance."""
import os
import hashlib
import json
import importlib.util
import sys
from pathlib import Path

REQUIRED_REPORTS = ('core-build-report.json', 'core-source-manifest.json',
    'core-consumed-source-snapshot.json', 'new-core-qualification.json',
    'aquamarine-build-report.json', 'authority/authority-build-report.json',
    'host/host-build-report.json')

def locked_read(path, expected, role, add):
    add(path, role, expected)
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Tuple JSON changed during read: ' + str(path))
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate tuple JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique)

def absolute(path):
    p = Path(path)
    if not p.is_absolute():
        raise ValueError('Tuple input path must be absolute: ' + str(path))
    return p

def inside(root, relative):
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('Invalid tuple source path: ' + str(relative))
    return root / p

def capture_composition(repo, path, digest, lock, add):
    """Validate the reviewed composition with its actual production validators."""
    adapter = Path(repo) / 'implementation/warlock/adapter'
    modules = {}
    for name in ('current_build', 'current_native'):
        module_path = (adapter / (name + '.py')).absolute()
        expected = lock['inputs'][str(module_path)]
        add(module_path, 'composition-validator', expected)
        body = module_path.read_bytes()
        if hashlib.sha256(body).hexdigest() != expected:
            raise ValueError('Composition validator changed during read: ' + str(module_path))
        spec = importlib.util.spec_from_loader(name, loader=None)
        module = importlib.util.module_from_spec(spec)
        module.__file__ = str(module_path)
        modules[name] = (module, body, module_path)
    previous = sys.modules.get('current_build')
    try:
        frontend, body, module_path = modules['current_build']
        exec(compile(body, str(module_path), 'exec'), frontend.__dict__)
        # Decode the same captured bytes that were checked, including nested
        # frontend receipt/lock reads. All other validator logic is unchanged.
        def exact_read(path, expected=None):
            path = Path(path)
            if expected is not None:
                add(path, 'composition-json', expected)
            raw = path.read_bytes()
            if expected is not None and hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError('Composition JSON changed during read: ' + str(path))
            return json.loads(raw, object_pairs_hook=frontend.unique)
        frontend.read = exact_read
        sys.modules['current_build'] = frontend
        native, body, module_path = modules['current_native']
        exec(compile(body, str(module_path), 'exec'), native.__dict__)
        receipt = lock['frontend']
        result = native.validate_composition(receipt['path'], receipt['sha256'], path, digest)
    except RuntimeError as error:
        raise ValueError('Current composition refused: ' + str(error)) from error
    finally:
        if previous is None:
            sys.modules.pop('current_build', None)
        else:
            sys.modules['current_build'] = previous
    if result != lock:
        raise ValueError('Composition changed during selection')
    for name, expected in result['inputs'].items():
        p = absolute(name)
        if str(p.resolve(strict=True)) != result['resolutions'][name]:
            raise ValueError('Composition input resolution changed: ' + name)
        add(p, 'current-composition-input', expected)
    for name, target in result['aliases'].items():
        p = absolute(name)
        if not p.is_symlink() or os.readlink(p) != target:
            raise ValueError('Composition alias changed: ' + name)
    assets = {}
    for name, expected in result['assets']['files'].items():
        source = inside(absolute(result['assets']['directory']), name)
        add(source, 'current-frontend-output', expected)
        assets['assets/' + name] = expected
    slots = result['slots']
    aq = slots['aquamarine']
    alias = absolute(aq['sonameAlias'])
    library = absolute(aq['path'])
    target = aq['aliasTarget']
    if (Path(target).name != target or alias.parent != library.parent or
            target != library.name or not alias.is_symlink() or
            os.readlink(alias) != target or alias.resolve() != library.resolve()):
        raise ValueError('Composition Aquamarine loader alias changed')
    add(alias, 'native-aquamarine-loader-alias', aq['sha256'])
    pair = {role: {'path': slots[name]['path'], 'sha256': slots[name]['sha256']}
            for role, name in (('core', 'core'), ('plugin', 'authority'), ('aquamarine', 'aquamarine'))}
    reference = {'path': str(path), 'sha256': digest,
        'sourceBase': result['historicalRevision'],
        'hostSourcePrefix': str(Path(repo) / 'implementation/warlock/native') + '/',
        'hostSHA256': slots['host']['sha256'],
        'loaderAlias': {'path': str(alias), 'target': target}, 'assets': assets,
        'nativeAcceptance': False, 'historicalBinaryReproduction': False,
        'compositionFrontend': result['frontend'], 'compositionFrontendLock': result['frontendLock'],
        'missingObservation': 'Complete at-build core and Aquamarine source, tool and dependency provenance is not attested by these receipts. Composition validates historical host and current frontend as separate roles; the host rebuild and two isolated offline comparisons remain unproven.'}
    return pair, {alias.name: target}, reference

def capture(repo, tuple_path, tuple_sha, add, read, sha):
    """Validate recorded inputs, add them to the immutable lock, return tuple data.

    The selected receipts do not attest all original native compiler/dependency
    inputs. Their absence remains a missing observation, never inferred from a
    successful build report or from captured current bytes.
    """
    record = add
    current_bytes = object()
    def add(path, role, expected=current_bytes):
        if expected is current_bytes:
            if role != 'native-aq-current-source':
                raise ValueError('Missing recorded digest: ' + str(path))
            return record(path, role)
        if not isinstance(expected, str) or len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
            raise ValueError('Invalid recorded digest: ' + str(path))
        return record(path, role, expected)
    if not tuple_path or not isinstance(tuple_sha, str) or len(tuple_sha) != 64 or any(c not in '0123456789abcdef' for c in tuple_sha):
        raise ValueError('Both native tuple path and lowercase SHA-256 are required')
    path = absolute(tuple_path)
    t = locked_read(path, tuple_sha, 'selected-native-tuple', add)
    if not isinstance(t, dict):
        raise ValueError('Native tuple must be a JSON object')
    if t.get('schema') == 1 and t.get('kind') == 'warlock-current-native-composition-lock':
        try:
            return capture_composition(repo, path, tuple_sha, t, add)
        except (RuntimeError, KeyError, TypeError) as error:
            raise ValueError('Current composition refused: ' + str(error)) from error
    if t.get('schema') != 1 or t.get('kind') != 'new derivative native tuple; not historical binary reproduction' or t.get('nativeAcceptance') is not False or t.get('pluginLoaded') is not False:
        raise ValueError('Unsupported native tuple scope')
    slots = t['slots']; refs = t['reports']
    if set(slots) != {'core', 'authority', 'aquamarine', 'host'} or set(refs) != set(REQUIRED_REPORTS):
        raise ValueError('Incomplete derivative tuple slots or reports')
    reports = {}
    for name in REQUIRED_REPORTS:
        row = refs[name]; rp = absolute(row['path'])
        reports[name] = locked_read(rp, row['sha256'], 'native-build-provenance', add)
    core, source, snap, qual, aq, authority, host = (reports[n] for n in REQUIRED_REPORTS)
    if (core.get('complete') is not True or aq.get('complete') is not True or
        authority.get('passed') is not True or host.get('complete') is not True or
        qual.get('passed') is not True or host.get('errors') or authority.get('missingSymbols') or
        any(r.get('nativeAcceptance') is not False for r in (core, aq, authority, host, qual)) or
        authority.get('pluginLoaded') is not False or host.get('sourceBase') != t.get('sourceBase') or
        source.get('historicalBinaryReproductionClaim') is not False):
        raise ValueError('Derivative native build report failed or scope changed')
    if (not isinstance(snap.get('files'), dict) or not snap['files'] or
        not isinstance(source.get('overlays'), list) or not source['overlays'] or
        set(slots['host'].get('assets', {})) != {'assets/elm.js', 'assets/bar.js', 'assets/popup.js'} or
        any(not isinstance(authority.get(k), dict) or not authority[k] for k in ('inputs', 'dependencies', 'tools', 'providerHashes')) or
        any(not isinstance(host.get(k), dict) or not host[k] for k in ('sourceHashes', 'compiledDependencyHashes', 'toolHashes', 'artifacts')) or
        authority.get('staticClosureOnly') is not True or
        any(not r.get('commands') or any(c.get('exitCode') != 0 for c in r['commands']) for r in (core, aq, authority))):
        raise ValueError('Derivative tuple inventories or command results incomplete')
    commands = host.get('commands')
    if not isinstance(commands, list) or not commands:
        raise ValueError('Missing host command receipts')
    failures = [(i, c) for i, c in enumerate(commands) if c.get('exitCode') != 0]
    if failures:
        # This report deliberately retains the first replay compilation failure.
        # Admit only its exact same-command successful retry, preserving history.
        if len(failures) != 1 or host.get('initialFailureRetained') != 'host-build-first-failure.json':
            raise ValueError('Unresolved host command failure')
        index, failed = failures[0]
        retry = commands[index + 1] if index + 1 < len(commands) else {}
        if (failed.get('name') != 'compile-NewInstanceReplay' or failed.get('exitCode') != 1 or
            retry.get('name') != 'compile-NewInstanceReplay-retry' or retry.get('exitCode') != 0 or
            retry.get('argv') != failed.get('argv') or retry.get('cwd') != failed.get('cwd')):
            raise ValueError('Host compilation retry does not resolve retained failure')
        failure_path = absolute(slots['host']['path']).parent / host['initialFailureRetained']
        retained = locked_read(failure_path, sha(failure_path), 'native-host-retained-failure', add)
        if (retained.get('complete') is not False or retained.get('nativeAcceptance') is not False or
            retained.get('sourceBase') != host.get('sourceBase') or
            retained.get('commands') != commands[:index + 1] or not retained.get('errors')):
            raise ValueError('Retained host failure does not match build history')
    for role in slots:
        row = slots[role]; add(absolute(row['path']), 'native-derivative-artifact', row['sha256'])
    for name in ('authority', 'host'):
        if slots[name].get('report') != refs['authority/authority-build-report.json' if name == 'authority' else 'host/host-build-report.json']:
            raise ValueError('Tuple slot report mismatch: ' + name)
    for role in ('core', 'aquamarine'):
        for report in (authority, host['tuple']):
            if report[role] != {'path': slots[role]['path'], 'sha256': slots[role]['sha256']}:
                raise ValueError('Native artifact report mismatch: ' + role)
    if (core['binary'] != slots['core']['path'] or core['binarySHA256'] != slots['core']['sha256'] or
        qual['binarySHA256'] != slots['core']['sha256'] or qual['aquamarineSHA256'] != slots['aquamarine']['sha256'] or
        qual['aquamarineResolved'] != slots['aquamarine']['path'] or
        aq['libraries'].get('lib/libaquamarine.so.0.15.0') != slots['aquamarine']['sha256'] or
        authority['binary'] != slots['authority']['path'] or authority['binarySHA256'] != slots['authority']['sha256'] or
        host['artifacts']['elm-host'] != slots['host']['sha256']):
        raise ValueError('Native artifact digest mismatch')
    if core['sourceAssemblySHA256'] != refs['core-source-manifest.json']['sha256'] or snap['sourceAssemblySHA256'] != core['sourceAssemblySHA256']:
        raise ValueError('Core source assembly mismatch')
    argv = core['commands'][0]['argv']; core_source = absolute(argv[argv.index('-S') + 1])
    for name, expected in snap['files'].items():
        add(inside(core_source, name), 'native-core-source', expected)
    add(core_source / 'src/version.h', 'native-core-generated-header', core['generatedVersionHeaderSHA256'])
    for item in source['overlays']:
        add(absolute(item['source']), 'native-core-origin', item['sha256'])
    for field in ('inputs', 'dependencies', 'tools', 'providerHashes'):
        for name, expected in authority[field].items():
            add(absolute(name), 'native-authority-' + field, expected)
    for field in ('compiledDependencyHashes', 'toolHashes'):
        for name, expected in host[field].items():
            add(absolute(name), 'native-host-' + field, expected)
    # Host receipt snapshots product inputs plus the unrelated release builder.
    # Bind product sources/assets and actual dependency maps; don't equate the
    # later release builder revision with host compiler input.
    unrelated_snapshot = []
    for name, expected in host['sourceHashes'].items():
        if (name.startswith(('implementation/warlock/src/', 'implementation/warlock/native/', 'implementation/warlock/assets/')) or name in ('implementation/warlock/elm.json', 'implementation/warlock/qa/NewInstanceReplay.elm', 'implementation/warlock/qa/feedback-replay.js', 'implementation/warlock/qa/NativePointerFixture.elm')):
            add(inside(Path(repo), name), 'native-host-elm-source', expected)
        else:
            source_file = inside(Path(repo), name)
            unrelated_snapshot.append({'path': name, 'recordedSHA256': expected,
                'currentSHA256': sha(source_file) if source_file.is_file() else None})
    host_dir = absolute(slots['host']['path']).parent
    host_compiles = [c for c in commands if c.get('name') == 'compile-shared-host.c']
    expected_host_source = Path(repo) / 'implementation/warlock/native/shared-host.c'
    if (len(host_compiles) != 1 or '-c' not in host_compiles[0]['argv'] or
        host_compiles[0]['argv'][host_compiles[0]['argv'].index('-c') + 1] != str(expected_host_source)):
        raise ValueError('Unsupported recorded host source filename')
    for name, expected in host['artifacts'].items():
        add(inside(host_dir, name), 'native-host-build-artifact', expected)
    for name, row in slots['host']['assets'].items():
        if host['artifacts'][name] != row['sha256'] or absolute(row['path']) != inside(host_dir, name):
            raise ValueError('Host asset report mismatch: ' + name)
    # Record currently available AQ source bytes while preserving the explicit
    # absence of a complete at-build source/tool/dependency receipt.
    baseline_path = absolute(aq['baseSourceManifest'])
    baseline = locked_read(baseline_path, aq['baseSourceManifestSHA256'], 'native-aq-baseline-manifest', add)
    checked = 0
    candidate_files = {}
    for entry in baseline['files']:
        name = entry['path']
        if name.startswith('candidate/'):
            add(inside(baseline_path.parent, name), 'native-aq-baseline-source', entry['sha256'])
            candidate_files[name[len('candidate/'):]] = entry['sha256']
            checked += 1
    if checked != aq['verifiedCandidateFiles'] or checked == 0:
        raise ValueError('Aquamarine baseline source inventory mismatch')
    aq_cmd = aq['commands'][0]['argv']; aq_source = absolute(aq_cmd[aq_cmd.index('-S') + 1])
    for name, expected in candidate_files.items():
        if name != 'src/backend/Wayland.cpp' and not (name.startswith('protocols/') and name.endswith(('.cpp', '.hpp'))):
            add(inside(aq_source, name), 'native-aq-derivative-source', expected)
    add(aq_source / 'src/backend/Wayland.cpp', 'native-aq-derivative-source', aq['currentWaylandSHA256'])
    for p in sorted(aq_source.rglob('*')):
        if p.is_file():
            add(p, 'native-aq-current-source')
    alias = absolute(slots['aquamarine']['sonameAlias']); target = slots['aquamarine']['aliasTarget']; library = absolute(slots['aquamarine']['path'])
    if (Path(target).name != target or alias.parent != library.parent or target != library.name or
        not alias.is_symlink() or os.readlink(alias) != target or alias.resolve() != library.resolve()):
        raise ValueError('Aquamarine loader alias changed')
    add(alias, 'native-aquamarine-loader-alias', slots['aquamarine']['sha256'])
    pair = {'core': slots['core'], 'plugin': {'path': slots['authority']['path'], 'sha256': slots['authority']['sha256']},
            'aquamarine': {'path': str(library), 'sha256': slots['aquamarine']['sha256']}}
    pair['core'] = {'path': slots['core']['path'], 'sha256': slots['core']['sha256']}
    reference = {'path': str(path), 'sha256': tuple_sha, 'sourceBase': t['sourceBase'],
        'hostSourcePrefix': str(expected_host_source.parent) + '/',
        'hostSHA256': slots['host']['sha256'], 'loaderAlias': {'path': str(alias), 'target': target}, 'assets': {n: v['sha256'] for n, v in slots['host']['assets'].items()},
        'nativeAcceptance': False, 'historicalBinaryReproduction': False,
        'hostUnrelatedSnapshot': unrelated_snapshot,
        'missingObservation': 'Complete at-build core and Aquamarine source, tool and dependency provenance is not attested by these receipts.'}
    return pair, {alias.name: target}, reference
