#!/usr/bin/python3
"""Review the typed marker correction and freeze its exact private derivative."""
from pathlib import Path
import ast, datetime, hashlib, importlib.util, json, sys
sys.dont_write_bytecode=True
QA=Path('/home/hoskinson/window-integration-qa');B=QA/'pin-max-native-campaign-b-v3';P=QA/'pin-max-native-campaign-b-v2'
from qa_launch import require_qa_scope
scope=require_qa_scope()
spec=importlib.util.spec_from_file_location('root_old_review',QA/'review_pin_campaign_b_controller_v1.py')
review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
sha=review.digest
assert sha(B/'SOURCE_READY.json')=='984af6b82ee7f7766b97a79912090386972093a46aea59c9be72007adb289852'
assert sha(B/'SOURCE_INPUTS.json')=='71d9ca325fd96be40f792abb741ff9a62c2ea78614685aabf2f9f8c210573416'
packet=json.loads((B/'SOURCE_INPUTS.json').read_bytes());review.verify(packet)
parent=json.loads((P/'frozen-inputs.json').read_bytes());review.contains(packet,parent)
before=(P/'controller/minimal_controller.py').read_text();after=(B/'controller/minimal_controller.py').read_text()
assert after.count("'restoreSpace','target'")==1
inverse=after.replace("'restoreSpace','target'","'restoreSpace','restoreOrigin','restoreManaged','target'",1)
lines=inverse.splitlines(True);removed=[line for line in lines if "require(" in line and "'exact native MAX " in line]
assert len(removed)==3
assert ''.join(line for line in lines if line not in removed)==before
oldtests=ast.parse((P/'tests/test_controller_packet.py').read_bytes());newtests=ast.parse((B/'tests/test_controller_packet.py').read_bytes())
def methods(tree):return {(cls.name,node.name):ast.dump(node,include_attributes=False) for cls in tree.body if isinstance(cls,ast.ClassDef) for node in cls.body if isinstance(node,ast.FunctionDef)}
oldmethods,newmethods=methods(oldtests),methods(newtests)
assert all(newmethods.get(k)==v for k,v in oldmethods.items())
assert sha(B/'MARKER_ORACLE.diff')=='91a370d5e6814eb208f35cd30949ff5799bb72cd3ddac51b382e73de9778665b'
conservation=json.loads((B/'marker-source-conservation.json').read_bytes())
for relative,meta in conservation['unchangedRuntimeAndFormal'].items():
    assert sha(B/relative)==meta['sha256']==sha(P/relative)
oldpair=json.loads((P/'PAIR_READY.json').read_bytes());pair=json.loads((B/'PAIR_READY.json').read_bytes())
for field,value in oldpair.items():
    if field in ['inputs','inputModes']:assert all(pair[field].get(k)==v for k,v in value.items())
    else:assert pair[field]==value,field
out=QA/'pin-max-native-b-v3-root-source-review-v1.json'
result=dict(schema='root-pin-b-markers-v3-review-v1',scope=scope,observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    sourceInputsSHA256=sha(B/'SOURCE_INPUTS.json'),files=len(packet['inputs']),wholeFailedParentFiles=len(parent['inputs']),
    allBytesModesLinksDirectoriesMatch=True,wholeControllerInverse=True,originalTestMethodsASTExact=True,
    reviewed='Complete typed marker diff, new three CPU cases, conservation/capture and owning ConfigActions/NativePinState/observer mapping.',
    priorRootInvariantClassificationIncorrect=True,expectedPinMarkers=[True,True],expectedUnpinMarkers=[False,True],
    remaining18ModeGeometryFieldsConservedImmediately=True,productChanged=False,
    approved='Freeze exact derivative, actual frozen location preflight then one private B01-B12 attempt.',nativeExecuted=False,fullBParityAccepted=False)
sys.path.insert(0,str(B));import capture_marker_packet as capture
capture.publish(out,result);row=capture.inventory()
for path in [out,Path(__file__).resolve(),QA/'pin-max-native-b-v3-source-preflight.json']:
    meta=capture.meta(path);row['inputs'][str(path)]=meta['sha256'];row['inputModes'][str(path)]=meta['mode']
review.contains(row,packet)
capture.publish(B/'frozen-inputs.json',row)
print(json.dumps(dict(result='pass',reviewSHA256=sha(out),manifestSHA256=sha(B/'frozen-inputs.json'),files=len(row['inputs']),links=len(row['symlinks']),directories=len(row['directoryModes']),nativeExecuted=False)))
