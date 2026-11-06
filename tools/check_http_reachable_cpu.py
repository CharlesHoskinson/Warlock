#!/usr/bin/env python3
"""Fixed private continuation of the admitted ARM subscription campaign."""
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys

from arm64_toolchain import digest, inventory, verify
from qa_cpu import arm64_inputs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'window-integration-qa'))
from qa_launch import require_qa_scope

FIXTURES = {
    'reachable-literals.cjs': '97fde2ebe21362922dcaa3968c103069b59053584ae51a3cd48fa1eca01a09e6',
    'reachable-observer.cjs': '2c93be152b21b6bce7641b16f9eb68d0725eb742446f432accc2bd398b481eff',
    'run-reachable.cjs': '7b107124c7163f1249179c6b14b618a694b784ed526d5dd9135dff50a3e8c408',
}


def regular(path):
    if path.is_symlink() or not path.is_file() or path.resolve() != path:
        raise RuntimeError('Expected canonical regular reachable input: ' + str(path))


def main():
    require_qa_scope()
    if len(sys.argv) != 3:
        raise RuntimeError('Expected fixed subscription output and context digest')
    output = Path(sys.argv[1])
    if (output.resolve() != output or output.name != 'subscriptions'
            or output.parent.parent != ROOT / '.warlock-contributor'
            or not re.fullmatch('arm64-cpu-[0-9]+', output.parent.name)
            or not re.fullmatch('[0-9a-f]{64}', sys.argv[2])):
        raise RuntimeError('Unexpected fixed reachable output/context')
    context_path = output / 'reachable-compilation-context.json'
    regular(context_path)
    if digest(context_path) != sys.argv[2]:
        raise RuntimeError('Reachable compile context changed')
    context = json.loads(context_path.read_text())
    outer = json.loads((output.parent / 'report.json').read_text())
    approved = outer['sourceHashes']
    if (outer.get('mode') != '--subscriptions'
            or set(approved) != set(arm64_inputs(ROOT, subscriptions=True))
            or any(digest(ROOT / name) != sha for name, sha in approved.items())
            or any(approved.get(name) != sha for name, sha in context['sourceHashes'].items())):
        raise RuntimeError('Reachable source differs from admitted full packet')
    pinned = verify()
    if (context.get('schema') != 1 or context.get('profile') != 'reachable-legacy-v2'
            or context.get('node') != pinned['node'] or context.get('elm') != pinned['elm']
            or context.get('elmHome') != pinned['elmHome']
            or context.get('toolchainManifestSHA256') != pinned['manifestSHA256']
            or outer.get('toolchainManifestSHA256') != pinned['manifestSHA256']
            or context.get('initialElmHomeInventory') != pinned['trees'][pinned['elmHome']]):
        raise RuntimeError('Reachable actual compiler/cache identity differs')
    bundle = output / 'HttpPopup.plain.js'
    regular(bundle)
    expected_command = [pinned['elm'], 'make', 'src/HttpPopup.elm', '--output=' + str(bundle)]
    commands = [row for row in context['commands'] if row['name'] == 'compile-plain-HttpPopup']
    if (len(commands) != 1 or commands[0]['exit'] != 0 or commands[0]['argv'] != expected_command
            or digest(bundle) != context['bundleSha256']):
        raise RuntimeError('Existing debug compilation receipt/image differs')
    staged_manifest = output / 'work/elm.json'
    regular(staged_manifest)
    expected_config = json.loads((ROOT / 'implementation/warlock/elm.json').read_text())
    expected_config['source-directories'] = ['src', 'qa']
    if (digest(staged_manifest) != context['stagedElmManifestSHA256']
            or json.loads(staged_manifest.read_text()) != expected_config):
        raise RuntimeError('Actual staged compiler Elm manifest differs')
    files = {str(ROOT / name): sha for name, sha in approved.items()}
    source_hashes = {}
    for name, sha in approved.items():
        prefix = 'implementation/warlock/src/'
        if name.startswith(prefix):
            staged = output / 'work/src' / name[len(prefix):]
            regular(staged)
            if digest(staged) != sha:
                raise RuntimeError('Actual compiled Elm source stage differs')
            files[str(staged)] = sha
            source_hashes[str(ROOT / name)] = sha
    source_hashes[str(ROOT / 'implementation/warlock/elm.json')] = approved['implementation/warlock/elm.json']
    stage = output / 'work/qa/reachable-legacy'
    stage.mkdir(mode=0o700)
    for name, sha in FIXTURES.items():
        key = 'implementation/warlock/qa/reachable-legacy/' + name
        source = ROOT / key
        regular(source)
        if approved.get(key) != sha or digest(source) != sha:
            raise RuntimeError('Unreviewed reachable fixture bytes')
        shutil.copyfile(source, stage / name)
        files[str(stage / name)] = sha
    # Reuse the existing observer stage, binding it to the same admitted files.
    baseline_prefix = 'implementation/warlock/qa/http-full-subscriptions-v2/'
    for name, sha in approved.items():
        if name.startswith(baseline_prefix) and Path(name).suffix in ('.cjs', '.json'):
            staged = output / 'subscription-source' / name
            regular(staged)
            if digest(staged) != sha:
                raise RuntimeError('Existing full observer stage differs')
            files[str(staged)] = sha
    cache_modes = {}
    for cache in (Path(pinned['elmHome']), output / 'elm-home'):
        if cache.resolve() != cache or cache.is_symlink():
            raise RuntimeError('Expected canonical actual Elm cache')
        for path in sorted(cache.rglob('*')):
            if path.is_symlink() or not (path.is_file() or path.is_dir()):
                raise RuntimeError('Unexpected Elm cache entry')
            if path.is_file():
                files[str(path)] = digest(path)
                cache_modes[str(path)] = stat.S_IMODE(path.stat().st_mode)
    if inventory(Path(pinned['elmHome'])) != pinned['trees'][pinned['elmHome']]:
        raise RuntimeError('Approved input Elm cache changed')
    for path in (Path(pinned['node']), Path(pinned['elm']), bundle, staged_manifest, context_path):
        regular(path)
        files[str(path)] = digest(path)
    compile_receipt = output / 'reachable-compile-receipt.json'
    provenance = {'schema': 1, 'profile': 'reachable-legacy-v2', 'bundle': str(bundle),
        'bundleSha256': context['bundleSha256'], 'elm': pinned['elm'],
        'elmSha256': pinned['files'][pinned['elm']], 'node': pinned['node'],
        'nodeSha256': pinned['files'][pinned['node']], 'elmHome': pinned['elmHome'],
        'stagedElmHome': str(output / 'elm-home'), 'cacheModes': cache_modes,
        'initialElmHomeInventory': context['initialElmHomeInventory'],
        'toolchainManifestSha256': pinned['manifestSHA256'], 'sourceHashes': source_hashes,
        'stagedElmManifest': str(staged_manifest), 'stagedElmManifestSHA256': digest(staged_manifest),
        'compileCommand': commands[0], 'contextSHA256': digest(context_path)}
    compile_receipt.write_text(json.dumps(provenance, sort_keys=True) + '\n')
    files[str(compile_receipt)] = digest(compile_receipt)
    closure = {'schema': 1, 'profile': 'reachable-legacy-v2', 'root': str(ROOT),
        'bundle': str(bundle), 'node': pinned['node'], 'elm': pinned['elm'], 'elmHome': pinned['elmHome'],
        'launcher': str(ROOT / 'window-integration-qa/qa_launch.py'),
        'toolchainManifest': str(ROOT / 'tools/arm64-toolchain.json'),
        'compileReceipt': str(compile_receipt), 'files': files}
    closure_path = output / 'reachable-closure.json'
    closure_path.write_text(json.dumps(closure, sort_keys=True) + '\n')
    # Same PID: the existing caller's hard120s covers inventory/copy and Node.
    os.execv(pinned['node'], [pinned['node'], str(stage / 'run-reachable.cjs'),
                            str(ROOT), str(bundle), str(closure_path), digest(closure_path)])


if __name__ == '__main__':
    main()
