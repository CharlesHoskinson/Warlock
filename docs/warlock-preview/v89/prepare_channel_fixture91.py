"""Retain the original channel fixture and add actual unissued zero-floor case."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v91')
p=r/'native/actor-retirement-channel-test-v2.cpp';assert not p.exists()
s=(r/'native/actor-retirement-channel-test-v1.cpp').read_text()
marker='  const auto ordinal=decimal(Json::text(delivery,"deliveryOrdinal"));';assert s.count(marker)==1
s=s.replace(marker,'  if(mode=="unissued")check(std::string_view(Json::text(final,"requestFloor"))=="0","Actual unissued native actor retains canonical zero request floor");\n'+marker)
marker=' settledInventory(2,2);';assert s.count(marker)==1
extra=r'''
 if(mode=="unissued") {
  WarlockImportedAdmission admission=WARLOCK_IMPORTED_INVALID;char* result=nullptr;
  check(warlock_imported_clients_enroll(owner,popup,20,1,1,&admission,&result,&error) && result && !error && admission==WARLOCK_IMPORTED_CAPACITY,
   "Two original physical jobs backpressure the third unissued C actor");g_free(result);
  check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error) && !error,"Unissued actor retains original receiver and journal enrollment");
  check(endpoint.native([](auto& broker){return broker.recordCount()==2 && broker.activeItems()==2 && broker.requestFloor(3)==0;}),"Unissued actor has no physical job or terminal-proof floor");
  retiredThrough(20);retire(20,true);settledInventory(2,3);
  check(endpoint.native([&](auto& broker){auto rows=broker.inspect();return rows.size()==2 && rows[1].job==neighbor && broker.requestFloor(2)==1;}),"Zero-floor actor removal preserves both original jobs and neighbor floor");
  ack(terminal(1));ack(terminal(2));
  check(warlock_imported_clients_empty(owner) && retirementPending()=="[]" && warlock_imported_clients_close(owner,&error) && !error,"Original physical and confirmed-delivery drain after unissued removal");
  warlock_preview_bootstrap_free(bootstrap);server.finish();
  std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"mode\":\"unissued\",\"zeroFloorActorRetired\":true,\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
 }
'''
s=s.replace(marker,extra+marker);p.write_text(s)
p=r/'qa/actor-retirement-channel-check-v2.py';assert not p.exists()
s=(r/'qa/actor-retirement-channel-check-v1.py').read_text().replace('actor-retirement-channel-check-v1-','actor-retirement-channel-check-v2-').replace('native/actor-retirement-channel-test-v1.cpp','native/actor-retirement-channel-test-v2.cpp')
s=s.replace("for mode in ['short','turnover']","for mode in ['unissued','short','turnover']").replace("assert evidence[1]['sequentialSubjects']>256","assert evidence[0]['zeroFloorActorRetired'] and evidence[2]['sequentialSubjects']>256")
ast.parse(s);p.write_text(s)
