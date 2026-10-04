"""Protected CPU source/tuple admission checks; never import the native runner."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time
import traceback
ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    sys.path.insert(0, '/home/hoskinson/window-integration-qa')
    from qa_launch import require_qa_scope
    qa_scope = require_qa_scope()
    out = ROOT/'qa'/('source-check-'+str(time.time_ns()))
    out.mkdir(mode=0o700)
    report = {'passed':False,'scope':'CPU source/tuple checks only; original 68 native assertions unrun', 'qaScope':qa_scope}
    paths = [ROOT/'qa/native.py', ROOT/'candidate_host.py', ROOT/'upstream.json', Path(__file__).resolve()]
    hashes = {str(path):digest(path) for path in paths}
    for path in paths:
        target = out/'inputs'/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,target);target.chmod(0o400)
    try:
        upstream = json.loads((ROOT/'upstream.json').read_text())
        parent = Path(upstream['parentNativeSource'])
        assert digest(parent)==upstream['parentNativeSourceSHA256']
        for name, inventory_base in (('parentManifest', parent.parents[1]), ('coreComponentManifest', ROOT.parents[1])):
            inventory_path = Path(upstream[name])
            assert digest(inventory_path) == upstream[name+'SHA256']
            inventory = json.loads(inventory_path.read_text())
            assert inventory['passed'] is True
            for entry in inventory['files']:
                path = inventory_base / entry['path']
                assert path.is_file() and not path.is_symlink() and path.stat().st_size == entry['size'] and digest(path) == entry['sha256'], path
        original = parent.read_text()
        changed = (ROOT/'qa/native.py').read_text()
        expected = original.replace("CORE = REPO/'implementation/elm-geometry-authority-pair-v34'", "CORE = REPO/'implementation/elm-window-geometry-owning-pair-v49'").replace("sys.path.insert(0, str(CORE/'adapter'))", "sys.path.insert(0, str(REPO/'implementation/elm-geometry-authority-pair-v34/adapter'))")
        assert changed==expected, 'Native runner may change only authorized tuple paths'
        def gates(text):
            return [ast.dump(node,include_attributes=False) for node in ast.walk(ast.parse(text)) if isinstance(node,ast.Assert) or isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('check','wait')]
        assert gates(original)==gates(changed)
        for path, value in upstream['legacyAdapterInputs'].items():
            assert digest(path) == value, path
        original_root = Path(upstream['originalElmRoot'])
        build_path = sorted((original_root/'qa').glob('build-*/report.json'))[-1]
        assert str(build_path) == upstream['originalElmBuildReport']
        assert digest(build_path) == upstream['originalElmBuildReportSHA256']
        build = json.loads(build_path.read_text())
        assert build['passed'] is True
        for relative, value in build['inputs'].items():
            assert digest(original_root / relative) == value, relative
        assert digest(build_path.parent/'elm-host') == build['binarySHA256']
        backend = build_path.parent/'inputs/adapter/daemon.py'
        assert digest(backend) == upstream['originalFrozenBackendSHA256']
        spec=importlib.util.spec_from_file_location('geometry_menu_cpu_host',ROOT/'candidate_host.py')
        host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
        module,client,input_packet=host.input_tuple()
        pair=host.pair_tuple()
        report.update(passed=True, assertionsAndCheckWaitCallsUnchanged=True, gateASTNodes=len(gates(changed)),
                      originalNativeChecks=68, nativeAssertionsRun=False, parentInputNativeChecks=input_packet['nativeChecks'],
                      parentInputInventoryEntries=len(input_packet['files']), parentInputModule=str(module), parentInputClient=str(client),
                      selectedCore=pair['nativePair']['core'], selectedPlugin=pair['nativePair']['plugin'], sources=hashes)
        for path,value in hashes.items():assert digest(path)==value,path
    except Exception as error:
        report['passed']=False;report['error']=repr(error);report['traceback']=traceback.format_exc()
    target=out/'report.json';target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'report':str(target),'error':report.get('error')}),flush=True)
    return not report['passed']

if __name__=='__main__':
    raise SystemExit(main())
