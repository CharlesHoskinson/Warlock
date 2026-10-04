"""Exact V8 menu host with the frozen V10 private parent-seat input module."""
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
MENU = REPO/'implementation/elm-menu-native-pair-v8'
INPUT = REPO/'implementation/elm-parent-input-probe-v10'
spec = importlib.util.spec_from_file_location('elm_menu_v8_reviewed_host', MENU/'candidate_host.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
original = base.original
digest = base.digest
EXPECTED_INPUT_MANIFEST = '480d1bfaa50611a6348af2d9b9c9ed8c0676b8c8c333fe9215f5c14c69044ce0'

def input_tuple():
    manifest = INPUT/'qa/slice-manifest.json'
    if digest(manifest) != EXPECTED_INPUT_MANIFEST:
        raise RuntimeError('Frozen parent input manifest changed')
    packet = json.loads(manifest.read_text())
    if not packet['passed'] or not packet['normalCleanup']:
        raise RuntimeError('Parent input native acceptance is absent')
    for relative, sha in packet['source'].items():
        if digest(INPUT/relative) != sha:
            raise RuntimeError('Parent input source changed: '+relative)
    build_path = Path(packet['buildReport'])
    native_path = Path(packet['nativeReport'])
    if digest(build_path) != packet['buildReportSHA256'] or digest(native_path) != packet['nativeReportSHA256']:
        raise RuntimeError('Parent input build/native report changed')
    build = json.loads(build_path.read_text())
    native = json.loads(native_path.read_text())
    if not build['passed'] or not native['passed'] or not native['cleanupPassed']:
        raise RuntimeError('Parent input build/native run is not accepted')
    for path, sha in build['inputs'].items():
        if digest(path) != sha:
            raise RuntimeError('Parent input owning input changed: '+path)
    for name, sha in build['binaries'].items():
        if digest(build_path.parent/name) != sha:
            raise RuntimeError('Parent input binary changed: '+name)
    return build_path.parent/'parent-input.so', build_path.parent/'parent-input-client', packet

class ReviewedWestonHost(base.ReviewedWestonHost):
    def verify(self):
        super().verify()
        module, client, packet = input_tuple()
        self.evidence['parentInput'] = {'module':str(module), 'moduleSHA256':digest(module),
                                        'client':str(client), 'clientSHA256':digest(client),
                                        'manifestSHA256':EXPECTED_INPUT_MANIFEST,
                                        'scope':'Private parent Weston only'}

    def launch(self, name, command, env=None):
        if name == 'weston':
            module, _, _ = input_tuple()
            if (not command or str(command[0]) != str(original.PREFIX/'usr/bin/weston')
                    or '--backend=headless' not in command or '--fake-seat' not in command
                    or any(str(arg).startswith('--modules=') for arg in command)):
                raise RuntimeError('Parent input requires exact private headless fake-seat host')
            selected = dict(self.env if env is None else env)
            selected['ELM_PARENT_INPUT_QA'] = '1'
            return super().launch(name, [*command, '--modules='+str(module)], selected)
        return super().launch(name, command, env)

class PrivateHyprSession(base.PrivateHyprSession):
    def __init__(self, output, main_env, width, height, nested_lua, dri_prime=None, mesa_vendor=False):
        super().__init__(output, main_env, width, height, nested_lua, dri_prime, mesa_vendor)
        self.host = ReviewedWestonHost(output, main_env, width, height, dri_prime, mesa_vendor)
        self.evidence = self.host.evidence
