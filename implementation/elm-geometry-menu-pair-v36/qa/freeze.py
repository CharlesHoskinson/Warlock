"""Append-only freeze of the accepted exact legacy menu/core tuple; no GUI."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import time
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PAIR = REPO/'implementation/elm-geometry-authority-pair-v34'
DOC = REPO/'docs/elm-roadmap/delivery/GEOMETRY-LEGACY-MENU-V36-ACCEPTANCE.md'
NATIVE = ROOT/'qa/native-1791099601538725381/report.json'
CPU = ROOT/'qa/source-check-1791099411995988294/report.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inventory(root, excluded):
    result = []
    for path in sorted(root.rglob('*')):
        if path in excluded:
            continue
        if path.is_symlink():
            result.append({'path':str(path.relative_to(root)), 'symlink':os.readlink(path)})
        elif path.is_file():
            result.append({'path':str(path.relative_to(root)), 'size':path.stat().st_size,
                           'mode':stat.S_IMODE(path.stat().st_mode), 'sha256':digest(path)})
    return result


def main():
    sys.path.insert(0, '/home/hoskinson/window-integration-qa')
    from qa_launch import require_qa_scope
    qa_scope = require_qa_scope()
    targets = [PAIR/'component-manifest.json', ROOT/'component-manifest.json']
    if any(path.exists() for path in targets):
        raise RuntimeError('Do not overwrite frozen component evidence')
    source = (ROOT/'qa/native.py').read_text()
    original = (ROOT/'qa/inherited/native.py').read_text()
    expected = original.replace("CORE = REPO/'implementation/elm-buffer-authority-pair-v8'", "CORE = REPO/'implementation/elm-geometry-authority-pair-v34'").replace("REPO/'implementation/elm-parent-input-probe-v10/native/parent-input-client.c'", "REPO/'implementation/elm-parent-button-lifecycle-v14/native/parent-input-client.c'")
    assert source == expected, 'Preserve all original regression logic and deadlines'
    def gates(text):
        return [ast.dump(node,include_attributes=False) for node in ast.walk(ast.parse(text))
                if isinstance(node,ast.Assert) or isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('check','wait')]
    assert gates(source) == gates(original)
    cpu = json.loads(CPU.read_text())
    assert cpu['passed'] is True and cpu['nativeAssertionsRun'] is False
    for path,value in cpu['sources'].items(): assert digest(path) == value, path
    spec = importlib.util.spec_from_file_location('geometry_pair_freeze_host', ROOT/'candidate_host.py')
    host = importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
    pair = host.pair_tuple()
    module,client,input_packet = host.input_tuple()
    aq,lib = host.base.aq_tuple()
    native = json.loads(NATIVE.read_text())
    assert native['passed'] is True and native['cleanupPassed'] is True
    assert len(native['checks']) == 68 and all(row['passed'] is True for row in native['checks'])
    assert native['mainDesktopActions'] is False
    for path,value in native['inputs'].items(): assert digest(path) == value, path
    for relative,value in native['artifacts'].items(): assert digest(NATIVE.parent/relative) == value, relative
    build_path = Path(native['buildReport'])
    assert digest(build_path) == native['buildReportSHA256']
    build = json.loads(build_path.read_text())
    assert build['passed'] is True
    menu = REPO/'implementation/elm-menu-native-pair-v8'
    for relative,value in build['inputs'].items(): assert digest(menu/relative) == value, relative
    assert digest(build_path.parent/'elm-host') == build['binarySHA256']
    assert native['pair'] == pair['nativePair']
    pair_manifest = PAIR/'qa/build-pair-manifest.json'
    assert digest(pair_manifest) == native['sourceManifestSHA256']
    private = native['privateHost']
    assert private['runtimeGone'] is True and not private['cleanupErrors'] and not private['unexpectedInnerDescendants'] and not private['remainingDescendants']
    assert private['mainDisplayUsed'] is False
    core,plugin = pair['nativePair']['core'],pair['nativePair']['plugin']
    assert private['hyprlandMaps']['files'][str(Path(core['path']).resolve())] == core['sha256']
    assert private['hyprlandMaps']['files'][str(lib.resolve())] == aq['librarySHA256']
    assert native['pluginMapsAfterLoad']['files'][str(Path(plugin['path']).resolve())] == plugin['sha256']
    assert private['westonMaps']['files'][str(module.resolve())] == digest(module)
    assert private['parentInput']['clientSHA256'] == digest(client)
    qualification = {'nativeReport':str(NATIVE),'nativeReportSHA256':digest(NATIVE),'nativeChecks':68,
                     'normalCleanup':True,'originalAssertionsAndDeadlinesUnchanged':True,
                     'sourceCheckReport':str(CPU),'sourceCheckReportSHA256':digest(CPU),
                     'parentInputManifestSHA256':host.EXPECTED_INPUT_MANIFEST,
                     'parentInputNativeChecks':105,'parentInputInventoryEntries':134,
                     'core':core,'plugin':plugin,'aquamarine':{'path':str(lib),'sha256':aq['librarySHA256']},
                     'parentModule':{'path':str(module),'sha256':digest(module)}}
    common = {'schema':1,'passed':True,'frozenUTCUnixNs':time.time_ns(),'qaScope':qa_scope,
              'nativeScope':'Original 68 legacy menu assertions on exact V28/V34/V14 private tuple only',
              'legacyMenuNativeAccepted':True,'fullRoadmapAccepted':False,'geometryMenuAccepted':False,
              'newMaximizeCapabilities':False,'deploymentAccepted':False,'quintGeometryModelLogicApproved':False,
              'nativeQualification':qualification,'acceptanceDocument':str(DOC),'acceptanceDocumentSHA256':digest(DOC)}
    pair_packet = dict(common, scope='Unchanged authority compile/link closure plus separately accepted legacy native menu regression',
                       buildPairManifest=str(pair_manifest),buildPairManifestSHA256=digest(pair_manifest),
                       files=inventory(PAIR,set(targets)))
    menu_packet = dict(common, scope='Preserved V13 menu cases/deadlines with qualified owning core and fixed parent probe',
                       upstreamSHA256=digest(ROOT/'upstream.json'),files=inventory(ROOT,set(targets)))
    # Compute both inventories before emitting either manifest to avoid circularity.
    for target,packet in zip(targets,[pair_packet,menu_packet]):
        with target.open('x') as output: output.write(json.dumps(packet,indent=2)+'\n')
    print(json.dumps({'passed':True,'nativeChecks':68,'manifests':{str(path):digest(path) for path in targets},
                      'nativeReportSHA256':digest(NATIVE),'acceptanceDocumentSHA256':digest(DOC)}),flush=True)


if __name__=='__main__':
    main()
