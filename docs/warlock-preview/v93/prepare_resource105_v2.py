"""Fresh C capability-order witness; preserve accepted initial resource fixture."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v105')
p=root/'native/capture-resource-c-test-v2.cpp';assert not p.exists()
s=(root/'native/capture-resource-c-test.cpp').read_text();old='  dispatch(ticket);dispatch(ticket);'
assert s.count(old)==1
s=s.replace(old,old+r'''
  {
   const auto source=endpoint.native([](auto& broker){return broker.nativeScope(1);});
   uri::Endpoint foreign({2,8,2,128ULL*1024*1024},4,2,[](uint64_t)->std::optional<uri::NativeTime>{return {};});
   check(foreign.native([&](auto& broker){return broker.enroll(1,source,4096);}) && foreign.registerView(77,binding,{1}),"Actual different native receipt Endpoint");
   ReceiptDelivery wrong(foreign,binding,77);
   refuse(warlock_imported_clients_retirement_poll(owner,&wrong,popup,&text,&error));
   check(!text && count(server.root/"resource-count")==0 && endpoint.native([](auto& broker){return broker.charge()==8192;}),"Foreign receipt capability refuses before original native resource cleanup");
  }
''')
p.write_text(s)
p=root/'qa/capture-resource-check-v2.py';assert not p.exists()
s=(root/'qa/capture-resource-check.py').read_text().replace("('capture-resource-check-'+","('capture-resource-check-v2-'+").replace('native/capture-resource-c-test.cpp','native/capture-resource-c-test-v2.cpp')
old="  ('accept-foreign-resource-target'";assert s.count(old)==1
s=s.replace(old,"""  ('poll-before-receipt-capability-check','native/imported-clients.cpp','o.value.actorCounts(o.popup,*static_cast<ReceiptDelivery*>(delivery),o.subjects);',';',cargs,'Foreign receipt capability refuses before original native resource cleanup'),
"""+old)
p.write_text(s)
print('Fresh C resource capability witness and four compiled mutation checks prepared')
