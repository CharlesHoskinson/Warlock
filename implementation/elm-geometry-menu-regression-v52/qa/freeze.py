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
PAIR = REPO/'implementation/elm-window-geometry-owning-pair-v49'
DOC = REPO/'docs/elm-roadmap/delivery/GEOMETRY-MENU-V52-ACCEPTANCE.md'
NATIVE = ROOT/'qa/native-1791102306170150678/report.json'
CPU = ROOT/'qa/source-check-1791102150688246558/report.json'


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
    targets = [ROOT/'component-manifest.json']
    if any(path.exists() for path in targets):
        raise RuntimeError('Do not overwrite frozen component evidence')
    source = (ROOT/'qa/native.py').read_text()
    upstream = json.loads((ROOT/'upstream.json').read_text())
    parent_source = Path(upstream['parentNativeSource'])
    assert digest(parent_source) == upstream['parentNativeSourceSHA256']
    original = parent_source.read_text()
    expected = original.replace("CORE = REPO/'implementation/elm-geometry-authority-pair-v34'", "CORE = REPO/'implementation/elm-window-geometry-owning-pair-v49'").replace("sys.path.insert(0, str(CORE/'adapter'))", "sys.path.insert(0, str(REPO/'implementation/elm-geometry-authority-pair-v34/adapter'))")
    assert source == expected, 'Preserve regression logic and deadlines'
    upstream_inventories = {}
    for name, inventory_base in (('parentManifest', parent_source.parents[1]), ('coreComponentManifest', REPO)):
        manifest_path = Path(upstream[name])
        assert digest(manifest_path) == upstream[name+'SHA256']
        packet = json.loads(manifest_path.read_text())
        assert packet['passed'] is True
        for entry in packet['files']:
            path = inventory_base/entry['path']
            assert path.is_file() and not path.is_symlink() and path.stat().st_size == entry['size'] and digest(path) == entry['sha256'], path
        upstream_inventories[name] = {'path':str(manifest_path),'sha256':digest(manifest_path),'entries':len(packet['files'])}
    for path,value in upstream['legacyAdapterInputs'].items(): assert digest(path)==value,path
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
    assert str(build_path) == upstream['originalElmBuildReport']
    assert digest(build_path) == upstream['originalElmBuildReportSHA256']
    assert digest(build_path.parent/'inputs/adapter/daemon.py') == upstream['originalFrozenBackendSHA256']
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
              'nativeScope':'Original 68 legacy menu assertions on exact V40/V49/V14 private tuple; original V8 backend and V34 adapter',
              'legacyMenuNativeAccepted':True,'fullRoadmapAccepted':False,'geometryMenuAccepted':False,
              'newMaximizeCapabilitiesAccepted':False,'geometryPipelineAccepted':False,'backendAbsoluteDeadlineAccepted':False,'deploymentAccepted':False,'quintGeometryModelLogicApproved':False,
              'nativeQualification':qualification,'acceptanceDocument':str(DOC),'acceptanceDocumentSHA256':digest(DOC)}
    menu_packet = dict(common, scope='Legacy menu compatibility regression only; preserved backend and observation deadlines do not qualify new geometry pipeline or absolute operation deadline',
                       upstreamSHA256=digest(ROOT/'upstream.json'),
                       upstreamInventories=upstream_inventories,
                       pairManifest={'path':str(pair_manifest),'sha256':digest(pair_manifest),'entries':len(pair['files'])},
                       legacyAdapterInputs=upstream['legacyAdapterInputs'],
                       originalFrozenBackendSHA256=upstream['originalFrozenBackendSHA256'],
                       files=inventory(ROOT,set(targets)))
    with targets[0].open('x') as output: output.write(json.dumps(menu_packet,indent=2)+'\n')
    verify = json.loads(targets[0].read_text())
    for entry in verify['files']:
        assert 'symlink' not in entry, entry
        path = ROOT/entry['path']
        assert path.stat().st_size == entry['size'] and digest(path)==entry['sha256'], path
        assert stat.S_IMODE(path.stat().st_mode)==entry['mode'],path
    print(json.dumps({'passed':True,'nativeChecks':68,'manifests':{str(path):digest(path) for path in targets},
                      'nativeReportSHA256':digest(NATIVE),'acceptanceDocumentSHA256':digest(DOC)}),flush=True)


if __name__=='__main__':
    main()
