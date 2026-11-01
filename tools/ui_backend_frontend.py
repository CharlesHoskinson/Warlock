"""Compile the actual Elm Main for the fixed Haskell backend bridge campaign.

Called inside the protected offline Haskell runner, never a general command API.
"""
import importlib.util
import json
from pathlib import Path
import shutil


def prepare(root, work, env, run, digest):
    def tree(directory):
        result = {}
        for path in sorted(directory.rglob('*')):
            if path.is_symlink():
                raise RuntimeError('Unexpected symlink in UI source: ' + str(path))
            if path.is_file():
                result[str(path.relative_to(directory))] = digest(path)
        return result
    source = root / 'implementation/warlock/src'
    source_before = tree(source)
    source_files = {name: root / name for name in (
        'implementation/warlock/elm.json', 'implementation/warlock/qa/ui-backend-port.cjs')}
    if source.is_symlink() or any(p.is_symlink() or not p.is_file() for p in source_files.values()):
        raise RuntimeError('Expected regular nonsymlink UI source inputs')
    file_hashes = {name: digest(path) for name, path in source_files.items()}
    held = root / 'implementation/warlock-preview-provider-v143'
    spec = importlib.util.spec_from_file_location('ui_backend_held_toolchain', held / 'qa/toolchain.py')
    toolchain = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(toolchain)
    compiler_pin = toolchain.verify()
    from check_elm_cpu import quint_toolchain
    node_pin, _ = quint_toolchain()
    node = Path(node_pin['node']['path'])
    if node.is_symlink() or digest(node) != node_pin['node']['sha256']:
        raise RuntimeError('Pinned UI bridge Node differs')
    frontend = work / 'frontend'
    frontend.mkdir(mode=0o700)
    shutil.copytree(source, frontend / 'src', symlinks=True)
    shutil.copytree(held / compiler_pin['elmHome'], frontend / 'elm-home')
    from elm_http_dependencies import stage as stage_http_dependencies
    http_dependencies = stage_http_dependencies(frontend / 'elm-home')
    shutil.copyfile(root / 'implementation/warlock/elm.json', frontend / 'elm.json')
    harness = frontend / 'ui-backend-port.cjs'
    shutil.copyfile(root / 'implementation/warlock/qa/ui-backend-port.cjs', harness)
    if (tree(frontend / 'src') != source_before or tree(source) != source_before
            or digest(frontend / 'elm.json') != file_hashes['implementation/warlock/elm.json']
            or digest(harness) != file_hashes['implementation/warlock/qa/ui-backend-port.cjs']
            or any(digest(path) != file_hashes[name] for name, path in source_files.items())):
        raise RuntimeError('UI source changed during staging')
    compile_env = dict(env, ELM_HOME=str(frontend / 'elm-home'), NO_COLOR='1')
    for name in ('NODE_OPTIONS', 'NODE_PATH', 'FORCE_COLOR'):
        compile_env.pop(name, None)
    main = frontend / 'Main.js'
    command = run([held / compiler_pin['compiler'], 'make', 'src/Main.elm', '--optimize',
                   '--output=' + str(main)], frontend, compile_env, work / 'logs',
                  'ui-compile-main', timeout=180)
    if command['exit'] != 0 or command['forcedCleanup']:
        raise RuntimeError('Actual UI Main compile failed; see retained logs')
    documents, document_commands = {}, []
    for role, entry in (('controller', 'HttpMain'), ('bar', 'HttpBar'), ('popup', 'HttpPopup')):
        document = frontend / (entry + '.html')
        info = run([held / compiler_pin['compiler'], 'make', 'src/' + entry + '.elm', '--optimize',
                    '--output=' + str(document)], frontend, compile_env, work / 'logs',
                   'ui-compile-' + entry, timeout=180)
        document_commands.append(info)
        if info['exit'] != 0 or info['forcedCleanup']:
            raise RuntimeError('Actual HTTP UI compile failed: ' + entry)
        status = document.stat()
        parents = list(reversed(document.parents))
        if any(p.is_symlink() or not p.is_dir() for p in parents):
            raise RuntimeError('Unexpected UI document ancestor')
        documents[role] = {'path': str(document), 'device': str(status.st_dev), 'inode': str(status.st_ino),
                           'size': str(status.st_size), 'sha256': digest(document),
                           'ancestors': [{'path': str(p), 'device': str(p.stat().st_dev),
                                          'inode': str(p.stat().st_ino)} for p in parents if p != p.parent]}
    toolchain.verify()
    quint_toolchain()
    if node.is_symlink() or not node.is_file() or digest(node) != node_pin['node']['sha256']:
        raise RuntimeError('Pinned UI bridge Node changed during compilation')
    if (tree(frontend / 'src') != source_before or tree(source) != source_before
            or any(digest(path) != file_hashes[name] for name, path in source_files.items())
            or digest(frontend / 'elm.json') != file_hashes['implementation/warlock/elm.json']
            or digest(harness) != file_hashes['implementation/warlock/qa/ui-backend-port.cjs']):
        raise RuntimeError('UI source changed during compiler execution')
    manifest = {name: {'path': str(path), 'sha': digest(path)}
                for name, path in (('node', node), ('main', main), ('harness', harness))}
    manifest['node']['sha'] = node_pin['node']['sha256']
    return manifest, {'compiler': compiler_pin, 'node': node_pin['node'], 'httpDependencies': http_dependencies,
                      'documents': documents, 'documentCommands': document_commands,
                      'sourceHashes': source_before, 'fileHashes': file_hashes,
                      'command': command, 'manifest': manifest}
