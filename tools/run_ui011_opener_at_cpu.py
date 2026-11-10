#!/usr/bin/python3
"""Fixed CPU opener build/admission and isolated AT transport tests; no GUI execution."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import time

ROOT = Path('/home/hoskinson/Projects/Warlock')
HERE = ROOT / '.warlock-contributor/evidence/nextloop-20261106/ui011-observed-opener-closure-plan-20261110/fixed-opener-at-prerequisite-v7'
BUNDLE = ROOT / '.warlock-contributor/evidence/nextloop-20261106/ui011-observed-opener-closure-plan-20261110/fixed-opener-at-fixtures-v6'
INPUT_SHA = None
OUTPUTS = ROOT / '.warlock-contributor/ui011-opener-at-cpu-runs'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def load(name, relative, pins):
    path = ROOT / relative
    if digest(path) != pins[relative]:
        raise ValueError('Helper source changed: ' + relative)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def input_data():
    if digest(HERE / 'inputs.json') != INPUT_SHA:
        raise ValueError('Fixed inputs changed')
    data = json.loads((HERE / 'inputs.json').read_text())
    for name, expected in {**{str(ROOT / p): h for p, h in data['sourceHashes'].items()}, **data['immutableFiles']}.items():
        path = Path(name)
        if path.is_symlink() or not path.is_file() or digest(path) != expected:
            raise ValueError('Current or immutable source differs: ' + name)
    for suffix, key in (('haskell', 'haskellFiles'), ('src', 'elmFiles')):
        base = ROOT / 'implementation/warlock' / suffix
        names = set()
        for path in base.rglob('*'):
            relative = path.relative_to(base)
            if any(part in ('dist-newstyle', '__pycache__') for part in relative.parts):
                continue
            if path.is_symlink() or (not path.is_file() and not path.is_dir()):
                raise ValueError('Source alias or special file')
            if path.is_file():
                names.add(str(relative))
        if names != set(data[key]):
            raise ValueError('Complete source membership changed: ' + suffix)
    return data


def modules(data):
    sys.path.insert(0, str(ROOT / 'tools'))
    sys.path.insert(0, str(ROOT / 'window-integration-qa'))
    pins = data['sourceHashes']
    qa = load('qa_launch', 'window-integration-qa/qa_launch.py', pins)
    arm = load('arm64_toolchain', 'tools/arm64_toolchain.py', pins)
    build = load('fixed_watch_build', 'tools/run_ux024_menu_focus_build.py', pins)
    elm = load('fixed_watch_elm', 'tools/check_elm_cpu.py', pins)
    return qa, arm, build, elm


def tools_for(profile, data, arm, build, elm):
    if profile != 'opener-at':
        raise ValueError('Only fixed opener/AT prerequisite profile')
    return build.verify_inputs(data)


def terminate(child):
    if child.poll() is None:
        os.killpg(child.pid, signal.SIGKILL)
    child.wait(timeout=2)


TARGETS = (('ui011-opener-fixture', 'warlock-runtime:exe:ui011-opener-fixture'), ('ui011-opener-admission-controls', 'warlock-runtime:test:ui011-opener-admission-controls'), ('ui-display-controls', 'warlock-runtime:test:ui-display-controls'), ('ui-engine-controls', 'warlock-runtime:test:ui-engine-controls'))
AT_NAMES = ['absent-keeps-legacy-display-and-ignores-ambient-session', 'missing-selected-socket-refused', 'owned-at-address-survives-public-capture', 'capture-selects-no-session-or-system-bus', 'empty-selection-refused', 'abstract-address-refused', 'tcp-address-refused', 'multiple-addresses-refused', 'guid-or-parameter-suffix-refused', 'relative-path-refused', 'ambient-user-bus-refused', 'wrong-private-leaf-refused', 'foreign-runtime-refused', 'traversal-refused', 'overlong-refused', 'shared-runtime-refused', 'symlink-at-socket-refused', 'regular-at-endpoint-refused']
ADMISSION_SENTINEL = "UI011 opener admission: 22 contracts and 32 seeded triples passed"

def admission_result(code, stdout):
    if code != 0 or stdout.splitlines() != [ADMISSION_SENTINEL]:
        raise ValueError('Frozen opener22/32 admission execution did not complete')
    return {'passed': True, 'contractCount': 22, 'seedCount': 32,
            'evidence': 'exit0 plus exact terminal sentinel after all frozen assertions'}


def at_result(code, stdout):
    rows = re.findall(r'^owned-at:([a-z0-9-]+)=(PASS|FAIL)$', stdout, re.M)
    fixed = [(n,s) for n,s in rows if not n.startswith('literal-seed-')]
    seeds = [(n,s) for n,s in rows if n.startswith('literal-seed-')]
    if [n for n,_ in fixed] != AT_NAMES or [n for n,_ in seeds] != ['literal-seed-'+str(i) for i in range(32)]:
        raise ValueError('All18 fixed AT controls and32 literal seeds must execute')
    all_pass = all(s == 'PASS' for _,s in rows)
    expected_red = all((s == 'PASS') == (n in {AT_NAMES[0], 'shared-runtime-refused'}) for n,s in fixed)
    expected_red = expected_red and all((s == 'PASS') == (i % 4 == 1) for i,(_,s) in enumerate(seeds))
    if not ((code == 0 and all_pass) or (code != 0 and expected_red)):
        raise ValueError('AT result differs from complete GREEN or exact missing-transport RED')
    return {'passed': all_pass, 'classification': 'component-pass' if all_pass else 'at-transport-semantic-red',
            'checks': [{'name':n,'passed':s=='PASS'} for n,s in fixed],
            'seeded': [{'seed':i,'passed':s=='PASS'} for i,(_,s) in enumerate(seeds)],
            'caseCount':18, 'seedCount':32}


def require_admission_source_root(stanza):
    parts=stanza.split('\ntest-suite ui011-opener-admission-controls\n')
    if len(parts)!=2:
        raise ValueError('One frozen admission component required')
    component=parts[1]
    roots=re.findall(r'^  hs-source-dirs: (.+)$',component,re.M)
    mains=re.findall(r'^  main-is: (.+)$',component,re.M)
    if roots!=['test-ui011-opener'] or mains!=['Main.hs']:
        raise ValueError('Pure admission must not search the native Main.hsc directory')


def main():
    global INPUT_SHA
    parser = argparse.ArgumentParser()
    parser.add_argument('profile', choices=('opener-at',))
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--inside-private', type=Path)
    args = parser.parse_args()
    if digest(HERE / 'manifest.json') != args.manifest_sha256:
        raise ValueError('Reviewed execution manifest differs')
    frozen = json.loads((HERE / 'manifest.json').read_text())
    if frozen['kind'] != 'ui011-fixed-opener-at-prerequisite' or frozen['profiles'] != {'opener-at':300}:
        raise ValueError('Only fixed opener/admission/AT/engine four-target profile')
    INPUT_SHA = frozen['inputs']['sha256']
    for row in frozen['files']:
        if digest(row['path']) != row['sha256']:
            raise ValueError('Frozen execution source differs')
    data = input_data()
    qa, arm, build, elm = modules(data)
    scope = qa.require_qa_scope()
    selected = tools_for(args.profile, data, arm, build, elm)
    core = load('fixed_watch_core', 'plugins/warlock-contributor/scripts/warlock.py', data['sourceHashes'])
    record = json.loads((ROOT / data['record']).read_text()); record['_recordPath'] = data['record']
    reqs, state = core.context(ROOT); core.current_selection(record, state, data['selectionGeneration'])
    if core.record_identity(record,data['record']) != data['recordIdentitySha256'] or core.effective_delivery_authorization(record) != data['authorizationLimitUTC']:
        raise ValueError('Actual canonical same-record authorization differs')
    expires = datetime.datetime.fromisoformat(data['authorizationLimitUTC'].replace('Z', '+00:00')).timestamp()
    if time.time() >= expires:
        raise ValueError('Renewed operational limit expired; Root must re-authorize a successor')
    if args.inside_private is None:
        # Root independently checks the effective record/goal under lock at spawn.
        # Canonical job identity remains owned by the protected parent launcher.
        OUTPUTS.mkdir(mode=0o700, exist_ok=True)
        output = OUTPUTS / (args.profile + '-' + str(time.time_ns()))
        output.mkdir(mode=0o700)
        deadline = min(time.monotonic() + data['profiles'][args.profile], time.monotonic() + expires - time.time())
        save(output / 'limits.json', {'profile': args.profile, 'deadline': deadline, 'expires': expires, 'scope': scope})
        save(output / 'record-at-spawn.json', {'path': str(ROOT / data['record']), 'sha256': digest(ROOT / data['record']), 'authorityValidation': 'Root performs actual goal/effective-authorization check under record lock; this file is provenance only'})
        argv = ['/usr/bin/bwrap', '--die-with-parent', '--unshare-net', '--unshare-pid', '--ro-bind', '/', '/', '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp', '--tmpfs', '/run', '--dir', '/run/user', '--bind', str(output), str(output), '--chdir', str(output), '--', '/usr/bin/python3', '-B', str(Path(__file__).resolve()), args.profile, '--manifest-sha256', args.manifest_sha256, '--inside-private', str(output)]
        env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'HOME': str(output / 'home'), 'TMPDIR': '/tmp', 'PYTHONDONTWRITEBYTECODE': '1'}
        forced = False
        with (output / 'outer.stdout').open('xb') as stdout, (output / 'outer.stderr').open('xb') as stderr:
            child = subprocess.Popen(argv, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                code = child.wait(timeout=max(0.001, deadline - time.monotonic()) + 2)
            except BaseException:
                forced = True
                terminate(child)
                raise
            finally:
                save(output / 'outer-terminal.json', {'exit': child.returncode, 'forced': forced, 'argv': argv})
        build.require_group_absent(child)
        input_data()
        tools_for(args.profile, data, arm, build, elm)
        print(json.dumps({'profile': args.profile, 'exit': code, 'output': str(output), 'cpuOnly': True}))
        return code
    output = args.inside_private
    if output.parent != OUTPUTS or output.resolve() != output or not re.fullmatch(args.profile + r'-[0-9]+', output.name):
        raise ValueError('Unrecognized private output')
    limits = json.loads((output / 'limits.json').read_text())
    if limits['profile'] != args.profile or limits['expires'] != expires or limits['deadline'] - time.monotonic() > data['profiles'][args.profile]:
        raise ValueError('Original profile deadline differs')
    deadline = limits['deadline']
    report = {'schema': 1, 'profile': args.profile, 'passed': False, 'classification': 'setup-or-compile-failed', 'privateEvidenceOnly': False, 'managedAdmissionClaimed': True, 'nativeAcceptance': False, 'originalAcceptance': False, 'integrationClaimed': False, 'sourceHashes': data['sourceHashes'], 'bundle': data['bundle'], 'commands': [], 'scope': scope, 'toolchain': selected, 'cleanupQualified': False}
    logs = output / 'logs'
    logs.mkdir(mode=0o700)
    env = dict(os.environ, NO_COLOR='1', GHC_ENVIRONMENT='-', CABAL_DIR=str(output / 'cabal-home'))
    for key in ('NODE_OPTIONS', 'NODE_PATH', 'FORCE_COLOR'):
        env.pop(key, None)
    def run(label, argv, cwd=output, allow_failure=False):
        input_data()
        remaining = min(120, deadline - time.monotonic(), expires - time.time())
        if remaining <= 0:
            raise TimeoutError('Original private profile deadline exhausted')
        row = {'name': label, 'argv': [str(x) for x in argv], 'exit': None}
        report['commands'].append(row)
        with (logs / (label + '.stdout')).open('xb') as stdout, (logs / (label + '.stderr')).open('xb') as stderr:
            child = subprocess.Popen(row['argv'], cwd=cwd, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                row['exit'] = child.wait(timeout=remaining)
            except BaseException:
                row['forced'] = True
                terminate(child)
                raise
        build.require_group_absent(child)
        input_data()
        if row['exit'] and not allow_failure:
            raise RuntimeError(label + ': exit ' + str(row['exit']))
        return row['exit'], (logs / (label + '.stdout')).read_text()
    def copy(source, target):
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if digest(source) != digest(target):
            raise ValueError('Staged body changed')
    try:
        work = output / 'haskell'
        packages = ('held-document', 'process-custody', 'protocol', 'runtime')
        for name in data['haskellFiles']:
            if Path(name).parts[0] in packages:
                copy(ROOT / 'implementation/warlock/haskell' / name, work / name)
        for source, target in (
            ('OpenerMain.hsc', 'runtime/fixture-ui011-opener/Main.hsc'),
            ('OpenerAdmission.hs', 'runtime/fixture-ui011-opener/OpenerAdmission.hs'),
            ('OpenerAdmission.hs', 'runtime/test-ui011-opener/OpenerAdmission.hs'),
            ('OpenerAdmissionControls.hs', 'runtime/test-ui011-opener/Main.hs'),
            ('ATTransportControls.hs', 'runtime/test-ui-display/Main.hs')):
            copy(BUNDLE / source, work / target)
        # Keep every frozen fixture byte. StrictJson is a private library module;
        # only the staged QA components receive its exact local source/dependency.
        copy(ROOT / 'implementation/warlock/haskell/protocol/src/Warlock/Protocol/StrictJson.hs',
             work / 'runtime/fixture-ui011-opener/Warlock/Protocol/StrictJson.hs')
        copy(ROOT / 'implementation/warlock/haskell/protocol/src/Warlock/Protocol/StrictJson.hs',
             work / 'runtime/test-ui011-opener/Warlock/Protocol/StrictJson.hs')
        stanza = (BUNDLE / 'runtime.cabal.fragment').read_text()
        require_admission_source_root(stanza)
        if stanza.count('  other-modules: OpenerAdmission') != 2 or stanza.count('bytestring, text,') != 2:
            raise ValueError('Frozen two-component opener stanza differs')
        stanza = stanza.replace('  other-modules: OpenerAdmission', '  other-modules: Warlock.Protocol.StrictJson, OpenerAdmission')
        stanza = stanza.replace('bytestring, text,', 'bytestring, containers, text,')
        cabal = work / 'runtime/runtime.cabal'
        cabal.write_text(cabal.read_text() + '\n' + stanza)
        dependencies = output / 'dependencies'
        shutil.copytree(selected['dependencies'], dependencies)
        if arm.inventory(dependencies) != selected['trees'][selected['dependencies']]:
            raise ValueError('Selected dependency source staging differs')
        dependency_manifest = json.loads((ROOT / 'tools/haskell-dependencies.json').read_text())
        for item in dependency_manifest['packages']:
            if digest(dependencies / item['directory'] / (item['name'] + '.cabal')) != item['metadataSHA256']:
                raise ValueError('Dependency metadata changed')
        (work / 'cabal.project').write_text('packages: ' + ' '.join(packages) + '\npackages: ' + ' '.join(str(dependencies / item['directory']) for item in dependency_manifest['packages']) + '\nactive-repositories: :none\n')
        (output / 'cabal.config').write_text('active-repositories: :none\nstore-dir: ' + str(output / 'store') + '\nremote-repo-cache: ' + str(output / 'repo-cache') + '\n')
        env['PATH'] = selected['ghcPrefix'] + '/bin:/usr/bin:/bin'
        plan = build.command_plan(selected, output, work, TARGETS)
        run(*plan[0], cwd=work)
        images = {}
        for (name,_), command in zip(TARGETS,plan[1:]):
            _, image_text = run(*command, cwd=work)
            image = Path(image_text.strip())
            if not image.is_relative_to(output / 'dist') or image.is_symlink() or not image.is_file():
                raise ValueError('Fresh fixed image missing or outside private output')
            before=image.stat(); image_sha=digest(image); after=image.stat()
            if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):
                raise ValueError('Compiled image changed while pinning')
            images[name]={'path':str(image),'sha256':image_sha,'device':str(after.st_dev),
                          'inode':str(after.st_ino),'size':str(after.st_size)}
        if set(images)!={name for name,_ in TARGETS}:
            raise ValueError('All four fixed targets must be built and listed')
        report.update(compiledImages=images, buildTargets=[target for _,target in TARGETS], openerExecuted=False)
        code, observed = run('opener-admission-controls', [images['ui011-opener-admission-controls']['path']], work, True)
        report['openerAdmission']=admission_result(code, observed)
        code, observed = run('at-transport-controls', [images['ui-display-controls']['path']], work, True)
        result=at_result(code, observed)
        report.update(classification=result['classification'],passed=result['passed'],atTransport=result)
        run('ui-engine-controls', [images['ui-engine-controls']['path']], work)
        report['engineCustody']={'passed':True,'evidence':'unchanged public ui-engine-controls completed exit0; raw stdout/stderr retained'}
        for image in images.values():
            if digest(image['path'])!=image['sha256']:
                raise ValueError('Fixed executable changed after controls')
        input_data()
        tools_for(args.profile, data, arm, build, elm)
        report['sourceInputsUnchanged'] = True
        report['cleanupQualified'] = True
    except Exception as error:
        report.update(passed=False, classification='setup-compile-or-verification-failed', error=str(error))
    finally:
        save(output / 'report.json', report)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
