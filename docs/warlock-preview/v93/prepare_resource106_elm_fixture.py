"""Fresh actual mapped capture terminal wire/compiled Elm final-ACK witness."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v106')
p=root/'native/capture-resource-elm-test.cpp';assert not p.exists()
s=(root/'native/capture-resource-fd-test.cpp').read_text()
old='take(text);Json grant(take(grantText));';assert s.count(old)==1;s=s.replace(old,'const auto seeds=take(text);Json grant(take(grantText));')
old='const auto ack=Wire().text("kind","acknowledge").begin("job").job(job).end().counter("sequence",terminal.proofs.back().sequence.value).finish();auto acknowledged=propose("family:21",ack);dispatch(acknowledged);confirm(acknowledged.ordinal);'
assert s.count(old)==1
new=r'''const auto proofs=static_cast<ReceiptDelivery*>(delivery)->pending(77);
 check(proofs.size()==2,"Actual retained mapped terminal wire pair");
 auto header=Wire().boolean("postTransferAllocationFault",fault).finish();header.pop_back();header+=",\"seeds\":"+seeds+",\"receipts\":[";
 for(const auto& proof:proofs){if(header.back()!='[')header+=",";header+=proof;}header+="]}";std::cout<<header<<std::endl;
 std::string ack;check(bool(std::getline(std::cin,ack)),"Actual compiled Elm final acknowledgment returned");
 Json typed(ack);check(std::string_view(Json::text(typed.object(),"kind"))=="acknowledge" && decodeJob(Json::child(typed.object(),"job"))==job && typed.counter("sequence")==terminal.proofs.back().sequence.value,"Actual compiled Elm exact original mapped final proof");
 auto acknowledged=propose("family:21",ack);dispatch(acknowledged);confirm(acknowledged.ordinal);
 check(endpoint.native([](auto& broker){return !broker.recordCount() && !broker.charge();}),"Actual compiled Elm ACK removes original physical Broker journal");'''
s=s.replace(old,new);p.write_text(s)
print(p)
