"""Exercise original native FD offer/fence output without changing the refusal oracle."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v121')
p=root/'native/policy-driver-positive-fixture.cpp';assert not p.exists();s=(root/'native/policy-driver-fixture.cpp').read_text();old='Server server("capture-refused")';assert s.count(old)==1;p.write_text(s.replace(old,'Server server("valid")'))
s=(root/'qa/policy-driver-roundtrip.js').read_text()
old="const dispatched=(await call('native-status')).result;check(dispatched.captures==='1' && dispatched.charge==='4096' && !dispatched.terminal,'Actual capture refusal retains original Unknown physical obligation');"
new="""const dispatched=(await call('native-status')).result;check(dispatched.captures==='1' && dispatched.charge==='4096' && !dispatched.terminal,'Actual synthetic native FD capture retains original physical obligation');
 same(state.returnedEventBatches,1,'Original actual C offer/fence retained in one separate batch');
 check(state.returnedEventBytes>0 && state.returnedEventBytes<=8192 && state.nativeEffectError==='','Original successful C FD/mapping produces bounded offer/fence bytes before policy processing');"""
assert s.count(old)==1;s=s.replace(old,new)
old="check((await call('close-probe')).refused,'Known job prevents normal driver closure');"
new=old+"""
 const beforeOffer=await inspect();await one();const offered=await inspect();
 check(offered.returnedEventBatches===1 && offered.returnedEventBytes<beforeOffer.returnedEventBytes,'Exactly one original admitted offer processed before further effect output');
 same(offered.privatePolicy.realm.ingress.pending,0,'Offer admission introduces no extra native acquisition');
 await one();const fenced=await inspect();same(fenced.returnedEventBatches,0,'Exactly one original fence consumes the remaining retained batch');
 check(fenced.privatePolicy.models[0].model.image?.startsWith('elm-shell://preview/'),'Original offer/fence reaches the single policy drawable state');
 same((await call('native-status')).result,dispatched,'Processing native outputs performs no native dispatch or physical settlement');
"""
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('actualCapturedFD:false','actualSyntheticCapturedFD:true,realCoreCapturedFD:false,actualCapturedFD:false')
p=root/'qa/policy-driver-positive-roundtrip.js';assert not p.exists();p.write_text(s)
s=(root/'qa/policy-driver-check.py').read_text().replace('policy-driver-check-','policy-driver-positive-check-').replace('policy-driver-roundtrip.js','policy-driver-positive-roundtrip.js').replace('policy-driver-check.py','policy-driver-positive-check.py').replace('native/policy-driver-fixture.cpp','native/policy-driver-positive-fixture.cpp').replace('Unknown capture remains until actual terminal/detachment processing.','Actual original C capture via authenticated synthetic peer produces a real sealed FD/local mapping and two original offer/fence events. This is not real Core/captured window/pixel acceptance. Original physical/terminal/detachment processing remains required.')
ast.parse(s);p=root/'qa/policy-driver-positive-check.py';assert not p.exists();p.write_text(s);print(p)
