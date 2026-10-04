"""Protected CPU source/tuple admission checks; never import the native runner."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time
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
        original = parent.read_text()
        changed = (ROOT/'qa/native.py').read_text()
        expected = original.replace("CORE = REPO/'implementation/elm-buffer-authority-pair-v8'", "CORE = REPO/'implementation/elm-geometry-authority-pair-v34'").replace("REPO/'implementation/elm-parent-input-probe-v10/native/parent-input-client.c'", "REPO/'implementation/elm-parent-button-lifecycle-v14/native/parent-input-client.c'")
        assert changed==expected, 'Native runner may change only authorized tuple paths'
        def gates(text):
            return [ast.dump(node,include_attributes=False) for node in ast.walk(ast.parse(text)) if isinstance(node,ast.Assert) or isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('check','wait')]
        assert gates(original)==gates(changed)
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
        report['passed']=False;report['error']=repr(error)
    target=out/'report.json';target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'report':str(target),'error':report.get('error')}),flush=True)
    return not report['passed']

if __name__=='__main__':
    raise SystemExit(main())
