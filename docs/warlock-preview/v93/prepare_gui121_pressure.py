"""Qualify pre-effect output refusal through a labeled stricter reservation gate."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v121')
s=(root/'native/preview-policy-driver.cpp').read_text();old='return batches<output_batch_limit && bytes<=output_byte_limit-output_reservation;';assert s.count(old)==1
p=root/'native/preview-policy-driver-output-gate.cpp';assert not p.exists();p.write_text('extern bool qa_withhold_original_output_capacity;\n'+s.replace(old,'return !qa_withhold_original_output_capacity && batches<output_batch_limit && bytes<=output_byte_limit-output_reservation;'))
s=(root/'native/policy-driver-fixture.cpp').read_text();old='#include "preview-policy-driver.h"';assert s.count(old)==1;s=s.replace(old,'bool qa_withhold_original_output_capacity=false;\n#include "preview-policy-driver-output-gate.cpp"')
old='else if(op=="step")';assert s.count(old)==1
new='''else if(op=="output-held") {qa_withhold_original_output_capacity=Json::boolean(object,"value");ok=true;}
        else if(op=="output-room") {const auto count=Json::integer(object,"count"),size=Json::integer(object,"bytes");require(count>=0 && size>=0,"Nonnegative synthetic output-accounting boundary");result=output_room(count,size)?"true":"false";ok=true;}
        else if(op=="held-ticket") {result=Wire().text("wire",driver->posts.empty()?"":driver->posts.front()).finish();ok=true;}
        '''+old
s=s.replace(old,new);p=root/'native/policy-driver-output-gate-fixture.cpp';assert not p.exists();p.write_text(s)
s=(root/'qa/policy-driver-roundtrip.js').read_text();old="const setup=await next(),epoch=setup.epoch;";assert s.count(old)==1
new=old+'''
 for(const [count,bytes,expected] of [[0,0,true],[3194,26165248,true],[3195,0,false],[0,26165249,false],[0,26173440,false],[0,Number.MAX_SAFE_INTEGER,false]]) {
  const r=await call('output-room',{count,bytes});check(r.ok && r.result===expected,'Compiled original output reservation predicate at exact count/byte boundaries');
 }
''';s=s.replace(old,new)
old="await one();state=await inspect();same(state.transport.deliveredThrough,'1','Actual native dispatch receipt observed');";assert s.count(old)==1
new='''const exactTicket=(await call('held-ticket')).result.wire;check(exactTicket.length>0,'Original exact native post ticket visible only to QA');
 check((await call('output-held',{value:true})).ok,'Labeled stricter compiled gate withholds output capacity before any effect');
 const pressure=await call('step');check(!pressure.ok && pressure.code===27 && !pressure.progressed,'Output capacity refusal is WOULD_BLOCK before original native dispatch');
 same(await inspect(),state,'Output refusal leaves exact policy/input/outbox custody unchanged');same((await call('native-status')).result,baseline,'Original native capture/effect counters unchanged under output pressure');same((await call('held-ticket')).result.wire,exactTicket,'Pressure retains exact original native-issued ticket bytes');
 check((await call('quarantine',{epoch})).ok,'Original urgent quarantine remains admissible through output pressure');
 const quarantined=await inspect();check(!quarantined.privatePolicy.models[0].model.demand && quarantined.privatePolicy.models[0].model.known.length===1,'Quarantine retains known physical obligation while demand is revoked');same((await call('held-ticket')).result.wire,exactTicket,'Urgent quarantine does not replace or discard the held native ticket');
 const stillBlocked=await call('step');check(!stillBlocked.ok && stillBlocked.code===27,'Original held ticket still waits for output capacity after quarantine');same((await call('native-status')).result,baseline,'Quarantine/refused output performs no native effect');
 check((await call('output-held',{value:false})).ok,'Labeled reservation becomes available without resetting Native or dropping real custody');
 '''+old
s=s.replace(old,new).replace('actualControlledC:true','compiledStricterOutputGate:true,actualOutputQueueExhaustion:false,actualControlledC:true')
p=root/'qa/policy-driver-output-gate-roundtrip.js';assert not p.exists();p.write_text(s)
s=(root/'qa/policy-driver-check.py').read_text().replace('policy-driver-check-','policy-driver-output-gate-check-').replace('policy-driver-roundtrip.js','policy-driver-output-gate-roundtrip.js').replace('policy-driver-check.py','policy-driver-output-gate-check.py').replace('native/policy-driver-fixture.cpp','native/policy-driver-output-gate-fixture.cpp').replace(",'native/preview-policy-driver.cpp'",'').replace('Actual creator-owned native driver integrates','A labeled compiled stricter output-reservation gate withholds capacity before native effects, then releases this test gate without changing any real input/ticket/native custody. Numeric count/byte bounds use the actual compiled original predicate. This is not actual native output queue exhaustion or workload/RSS qualification. Actual creator-owned native driver integrates')
ast.parse(s);p=root/'qa/policy-driver-output-gate-check.py';assert not p.exists();p.write_text(s);print(p)
