"""Qualified V28 core host composed with the fixed, frozen V14 parent probe."""
import importlib.util
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
BASE = REPO/'implementation/elm-window-geometry-map-state-v28/core'
INPUT = REPO/'implementation/elm-parent-button-lifecycle-v14'
PAIR = REPO/'implementation/elm-geometry-authority-pair-v34'
EXPECTED_BASE_HOST = '4f8c7192cea489fa93058b3867a6d16b339338689ae38dd18fabb4bfa10221cd'
EXPECTED_INPUT_MANIFEST = '5c39d644a9254043f7262ffa2b509e761abe4a6198662ad49872a54b44d3274b'
EXPECTED_PAIR_MANIFEST = 'ffe5d603d59d1da75a19b415f3d4bbd730b940025dce85cf8951816b01e1878a'
import hashlib
def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
if digest(BASE/'candidate_host.py') != EXPECTED_BASE_HOST:
    raise RuntimeError('Qualified core host source changed')
spec = importlib.util.spec_from_file_location('geometry_menu_qualified_v28_host', BASE/'candidate_host.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
original = base.original


def input_tuple():
    manifest = INPUT/'qa/implementation-manifest.json'
    if digest(manifest) != EXPECTED_INPUT_MANIFEST:
        raise RuntimeError('Fixed parent input inventory changed')
    packet = json.loads(manifest.read_text())
    if packet['passed'] is not True or packet['nativeChecks'] != 105 or len(packet['files']) != 134:
        raise RuntimeError('Fixed parent input qualification missing')
    for entry in packet['files']:
        path = INPUT/entry['path']
        if path.is_symlink() or not path.is_file() or path.stat().st_size != entry['size'] or digest(path) != entry['sha256']:
            raise RuntimeError('Fixed parent input inventory file changed: '+entry['path'])
        if stat.S_IMODE(path.stat().st_mode) != entry['mode']:
            raise RuntimeError('Fixed parent input inventory mode changed: '+entry['path'])
    descriptor = json.loads((INPUT/'parent-probe-build.json').read_text())
    build_path, native_path = Path(packet['buildReport']), Path(packet['nativeReport'])
    if descriptor['buildReport'] != str(build_path) or descriptor['buildReportSHA256'] != packet['buildReportSHA256']:
        raise RuntimeError('Fixed parent input descriptor mismatch')
    if digest(build_path) != packet['buildReportSHA256'] or digest(native_path) != packet['nativeReportSHA256']:
        raise RuntimeError('Fixed parent input build/native evidence changed')
    build, native = json.loads(build_path.read_text()), json.loads(native_path.read_text())
    if build['passed'] is not True or native['passed'] is not True or native['cleanupPassed'] is not True:
        raise RuntimeError('Fixed parent input build or cleanup not accepted')
    if len(native['checks']) != 105 or not all(row['passed'] is True for row in native['checks']):
        raise RuntimeError('Fixed parent input native assertions differ')
    for section in ('inputs', 'owningFiles', 'dependencies'):
        for path, value in build[section].items():
            selected_path = Path(path) if Path(path).is_absolute() else INPUT/path
            if digest(selected_path) != value:
                raise RuntimeError('Fixed parent input owning source changed: '+path)
    module, client = Path(build['module']), Path(build['client'])
    if digest(module) != build['moduleSHA256'] or digest(client) != build['clientSHA256']:
        raise RuntimeError('Fixed parent input module/client changed')
    return module, client, packet


def pair_tuple():
    manifest = PAIR/'qa/build-pair-manifest.json'
    if digest(manifest) != EXPECTED_PAIR_MANIFEST:
        raise RuntimeError('Geometry core/legacy authority pair manifest changed')
    packet = json.loads(manifest.read_text())
    if packet['passed'] is not True:
        raise RuntimeError('Geometry core/authority pair not compiled')
    for relative, value in packet['files'].items():
        if digest(PAIR/relative) != value:
            raise RuntimeError('Geometry pair inventory changed: '+relative)
    descriptor = json.loads((PAIR/'native-build-report.json').read_text())
    selected = base.core_tuple()
    if descriptor['binary'] != selected['binary'] or descriptor['sha256'] != selected['sha256']:
        raise RuntimeError('Selected core differs from legacy authority pair')
    build_path = PAIR/packet['buildReport']
    if digest(build_path) != packet['buildReportSHA256']:
        raise RuntimeError('Authority build evidence changed')
    build = json.loads(build_path.read_text())
    for section in ('dependencies', 'coreDependencies', 'linkedLibraries'):
        for path, value in build[section].items():
            if digest(path) != value:
                raise RuntimeError('Geometry pair dependency changed: '+path)
    if digest(build['linkClosureReport']) != build['linkClosureReportSHA256']:
        raise RuntimeError('Authority link closure changed')
    closure = json.loads(Path(build['linkClosureReport']).read_text())
    if closure['passed'] is not True or closure['missingSymbols']:
        raise RuntimeError('Authority strong-symbol closure missing')
    return packet


class ReviewedWestonHost(base.ReviewedWestonHost):
    def verify(self):
        super().verify()
        pair_tuple()
        module, client, packet = input_tuple()
        self.evidence['parentInput'] = {'module':str(module), 'moduleSHA256':digest(module),
                                       'client':str(client), 'clientSHA256':digest(client),
                                       'manifestSHA256':EXPECTED_INPUT_MANIFEST,
                                       'nativeChecks':packet['nativeChecks'], 'scope':'Fixed private parent Weston only'}

    def launch(self, name, command, env=None):
        if name == 'weston':
            module, _, _ = input_tuple()
            if (not command or str(command[0]) != str(original.PREFIX/'usr/bin/weston')
                    or '--backend=headless' not in command or '--fake-seat' not in command
                    or any(str(arg).startswith('--modules=') for arg in command)):
                raise RuntimeError('Fixed parent input requires exact private headless fake-seat host')
            selected = dict(self.env if env is None else env)
            selected['ELM_PARENT_INPUT_QA'] = '1'
            return super().launch(name, [*command, '--modules='+str(module)], selected)
        return super().launch(name, command, env)


class PrivateHyprSession(base.PrivateHyprSession):
    def __init__(self, output, main_env, width, height, nested_lua, dri_prime=None, mesa_vendor=False):
        super().__init__(output, main_env, width, height, nested_lua, dri_prime, mesa_vendor)
        self.host = ReviewedWestonHost(output, main_env, width, height, dri_prime, mesa_vendor)
        self.evidence = self.host.evidence

    def __enter__(self):
        super().__enter__()
        try:
            packet = pair_tuple()
            core = packet['nativePair']['core']
            if self.evidence['hyprlandMaps']['files'].get(str(Path(core['path']).resolve())) != core['sha256']:
                raise RuntimeError('Mapped child differs from exact geometry core')
            module, _, _ = input_tuple()
            if self.evidence['westonMaps']['files'].get(str(module.resolve())) != digest(module):
                raise RuntimeError('Mapped parent module differs from fixed V14 tuple')
            self.evidence['geometryCorePair'] = {'manifestSHA256':EXPECTED_PAIR_MANIFEST, 'mappedCoreVerified':True,
                                                'pluginMapCheck':'native runner verifies after load'}
            return self
        except BaseException:
            self.host.close()
            raise
