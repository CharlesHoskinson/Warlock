#!/usr/bin/env python3
"""ELM-DEL-004: two clean offline builds and a retained comparison verdict."""
import argparse
import errno
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import socket
import subprocess
import sys

import release_builder as builder


def observe(manifest, parent_port, hidden_marker):
    builder.require_scope()
    network = socket.socket(); network.settimeout(1)
    try:
        network.connect(('127.0.0.1', parent_port))
        blocked = False
    except OSError:
        blocked = True
    finally:
        network.close()
    source = Path(manifest['candidate']) / 'native/shared-host.c'
    try:
        fd = os.open(source, os.O_WRONLY); os.close(fd)
        read_only = False
    except OSError as error:
        read_only = error.errno in (errno.EROFS, errno.EACCES)
    return {'namespaces': {name: os.readlink('/proc/self/ns/' + name)
                           for name in ('net', 'mnt', 'pid')},
            'networkBlocked': blocked, 'readOnlySource': read_only,
            'hostMarkerHidden': not Path(hidden_marker).exists(),
            'coreLimit': list(resource.getrlimit(resource.RLIMIT_CORE)),
            'cgroup': Path('/proc/self/cgroup').read_text()}


def prepare_snapshot(manifest, lock, snapshot):
    """Copy only hash-locked files and aliases, never an entire host directory."""
    snapshot.mkdir(mode=0o700)
    canonical = {row['resolved'] for row in manifest['inputs'].values()}
    expected = {row['resolved']: row['sha256'] for row in manifest['inputs'].values()}
    for name in sorted(canonical):
        target = snapshot / name.lstrip('/')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(name, target)
        target.chmod(Path(name).stat().st_mode & 0o777)
        if builder.sha(target) != expected[name]:
            raise builder.ChangedInput('Locked input changed during snapshot: ' + name)
    for name, target in sorted(manifest['symlinks'].items(),
                               key=lambda item: (item[0].count('/'), item[0])):
        path = snapshot / name.lstrip('/')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target)
    for name in ('build', 'proc', 'dev', 'tmp'):
        (snapshot / name).mkdir(exist_ok=True)
    shutil.copyfile(lock, snapshot / 'input-lock.json')
    if builder.sha(snapshot / 'input-lock.json') != builder.sha(lock):
        raise builder.ChangedInput('Lock changed during snapshot')
    return {'canonicalFiles': len(canonical), 'symlinks': len(manifest['symlinks']),
            'lockSHA256': builder.sha(snapshot / 'input-lock.json'),
            'inputFileHashesSHA256': hashlib.sha256(json.dumps(
                sorted(expected.items()), separators=(',', ':')).encode()).hexdigest()}


def sandbox_args(manifest, snapshot, output, port, marker):
    # The root contains only verified inputs and explicit aliases. No desktop
    # socket, host directory or mutable package cache is bound.
    args = ['--unshare-user', '--unshare-pid', '--unshare-net', '--unshare-ipc',
            '--unshare-uts', '--die-with-parent', '--new-session', '--clearenv']
    args += ['--ro-bind', str(snapshot), '/', '--bind', str(output), '/build',
             '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp']
    for name, value in manifest['environment'].items():
        if value is not None:
            args += ['--setenv', name, value]
    # Retain HOME's value; its host contents are absent from the new filesystem.
    if os.environ.get('HOME'):
        args += ['--setenv', 'HOME', os.environ['HOME']]
    for name, value in {'PYTHONDONTWRITEBYTECODE': '1', 'XDG_CACHE_HOME': '/tmp/cache',
                        'XDG_CONFIG_HOME': '/tmp/config', 'XDG_DATA_HOME': '/tmp/data',
                        'XDG_STATE_HOME': '/tmp/state'}.items():
        args += ['--setenv', name, value]
    args += ['--chdir', manifest['candidate'], '--',
             manifest['tools']['python3']['path'], '-B',
             str(Path(manifest['candidate']) / 'adapter/release_repro.py'), 'inside',
             '--lock', '/input-lock.json', '--sha256', builder.sha(snapshot / 'input-lock.json'),
             '--output', '/build/artifacts', '--parent-port', str(port),
             '--host-marker', str(marker)]
    return args


def compare(left, right):
    """Compare real payloads/archives and reject changed recorded artifacts."""
    inputs = []
    states = []
    for directory in (Path(left), Path(right)):
        report = builder.read(directory / 'report.json')
        real = {str(p.relative_to(directory / 'package')): builder.sha(p)
                for p in sorted((directory / 'package').rglob('*')) if p.is_file()}
        links = {str(p.relative_to(directory / 'package')): os.readlink(p)
                 for p in sorted((directory / 'package').rglob('*')) if p.is_symlink()}
        states.append({'directory': str(directory), 'payload': real,
                       'links': links,
                       'archive': builder.sha(directory / 'warlock-candidate.tar'),
                       'report': report})
    differences = []
    for index, state in enumerate(states):
        if not state['report']['passed']:
            differences.append({'kind': 'failed-build', 'side': index})
        if state['payload'] != state['report']['payload']:
            differences.append({'kind': 'changed-recorded-payload', 'side': index})
        expected_links = {name: row['symlink'] for name, row in
                          state['report']['packageManifest']['files'].items()
                          if row['symlink'] is not None}
        if state['links'] != expected_links:
            differences.append({'kind': 'changed-recorded-symlinks', 'side': index,
                                'expected': expected_links, 'actual': state['links']})
        if state['archive'] != state['report']['archiveSHA256']:
            differences.append({'kind': 'changed-recorded-archive', 'side': index,
                'expected': state['report']['archiveSHA256'], 'actual': state['archive']})
    for name in sorted(set(states[0]['payload']) | set(states[1]['payload'])):
        hashes = [state['payload'].get(name) for state in states]
        if hashes[0] != hashes[1]:
            differences.append({'kind': 'payload', 'path': name, 'hashes': hashes})
    if states[0]['archive'] != states[1]['archive']:
        differences.append({'kind': 'archive', 'hashes': [s['archive'] for s in states]})
    for name in sorted(set(states[0]['links']) | set(states[1]['links'])):
        targets = [state['links'].get(name) for state in states]
        if targets[0] != targets[1]:
            differences.append({'kind': 'payload-link', 'path': name, 'targets': targets})
    identities = [s['report']['packageManifest']['inputContentSHA256'] for s in states]
    if identities[0] != identities[1]:
        inputs.append({'kind': 'input-content', 'hashes': identities})
    return {'matched': not differences and not inputs, 'releaseBlocked': bool(differences or inputs),
            'differentInputs': inputs, 'distributableDifferences': differences,
            'archiveHashes': [s['archive'] for s in states],
            'inputContentHashes': identities, 'payloadFileCount': len(states[0]['payload'])}


def run_pair(manifest, lock, output):
    builder.verify(manifest)
    output = Path(output).absolute(); output.mkdir(mode=0o700)
    marker = output / 'host-only-marker'; marker.write_text('private host filesystem marker')
    listener = socket.socket(); listener.bind(('127.0.0.1', 0)); listener.listen()
    port = listener.getsockname()[1]
    with socket.create_connection(('127.0.0.1', port), timeout=1):
        accepted, _ = listener.accept(); accepted.close()
    parent = {name: os.readlink('/proc/self/ns/' + name) for name in ('net', 'mnt', 'pid')}
    results = []
    verdict = {'matched': False, 'releaseBlocked': True}
    snapshot_report = None
    try:
        snapshot = output / 'locked-root'
        snapshot_report = prepare_snapshot(manifest, lock, snapshot)
        for label in ('A', 'B'):
            folder = output / label; folder.mkdir(mode=0o700)
            args = sandbox_args(manifest, snapshot, folder, port, marker)
            command = [manifest['tools']['bwrap']['path'], *args]
            (folder / 'sandbox-args.json').write_text(json.dumps(args, indent=2) + '\n')
            row = {'label': label, 'exitCode': None,
                   'argumentsSHA256': hashlib.sha256(json.dumps(args).encode()).hexdigest()}
            results.append(row)
            try:
                child = subprocess.run(command, text=True, capture_output=True, timeout=600)
            except subprocess.TimeoutExpired as error:
                row['timedOut'] = True
                for name, body in (('stdout', error.stdout), ('stderr', error.stderr)):
                    (folder / ('sandbox.' + name)).write_text(
                        body.decode(errors='replace') if isinstance(body, bytes) else body or '')
                raise
            (folder / 'sandbox.stdout').write_text(child.stdout)
            (folder / 'sandbox.stderr').write_text(child.stderr)
            row['exitCode'] = child.returncode
            if child.returncode:
                raise builder.ChangedInput('Offline build ' + label + ' failed: ' + child.stderr + child.stdout)
            observed = builder.read(folder / 'environment.json')
            row['environment'] = observed
            if (not all(observed['namespaces'][name] != parent[name] for name in parent)
                    or not observed['networkBlocked'] or not observed['readOnlySource']
                    or not observed['hostMarkerHidden'] or observed['coreLimit'] != [1, 1]):
                raise builder.ChangedInput('Offline build isolation observation failed: ' + label)
        verdict = compare(output / 'A/artifacts', output / 'B/artifacts')
    except (builder.ChangedInput, OSError, subprocess.TimeoutExpired) as error:
        verdict['error'] = str(error)
    finally:
        listener.close()
    report = {**verdict, 'builds': results, 'parentNamespaces': parent,
              'snapshot': snapshot_report,
              'lockSHA256': builder.sha(lock), 'nativeAcceptance': False,
              'fullReleaseAccepted': False}
    (output / 'reproducibility-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    for name in ('inside', 'run'):
        item = sub.add_parser(name); item.add_argument('--lock', required=True)
        item.add_argument('--sha256', required=True); item.add_argument('--output', required=True)
        if name == 'inside':
            item.add_argument('--parent-port', required=True, type=int)
            item.add_argument('--host-marker', required=True)
    args = parser.parse_args(argv)
    try:
        if builder.sha(args.lock) != args.sha256:
            raise builder.ChangedInput('Release lock identity changed')
        manifest = builder.read(args.lock)
        if args.operation == 'inside':
            observed = observe(manifest, args.parent_port, args.host_marker)
            (Path(args.output).parent / 'environment.json').write_text(json.dumps(observed, indent=2) + '\n')
            if not all(observed[key] for key in ('networkBlocked', 'readOnlySource', 'hostMarkerHidden')):
                raise builder.ChangedInput('Sandbox pre-build isolation failed')
            builder.build(manifest, args.output)
            result = {'passed': True, 'output': args.output}
        else:
            result = run_pair(manifest, Path(args.lock).absolute(), args.output)
        print(json.dumps(result), flush=True)
        return 4 if result.get('releaseBlocked') else 0
    except (builder.ChangedInput, OSError, ValueError) as error:
        print(json.dumps({'matched': False, 'releaseBlocked': True, 'error': str(error)}), flush=True)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
