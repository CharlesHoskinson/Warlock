"""Derive original authenticated socket fixture for retained capture failures."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v104')
s=(root/'native/actor-retirement-channel-test-v2.cpp').read_text().split('int main(int argc,char** argv)')[0]
old='else {require((kind=="preview-capture-probe-scope-request" || kind=="preview-client-scope-request")'
assert s.count(old)==1
insert='''else if(kind=="preview-client-scoped-request") {
                        auto object=envelope.object();Json::fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation","deadlineNs","context"});
                        const auto id=decimal(Json::text(object,"requestId")),subject=decimal(Json::text(object,"subjectIncarnation")),deadline=decimal(Json::text(object,"deadlineNs"));
                        const auto context=decodeContext(Json::child(object,"context"));const preview::Binding binding{{UINT64_MAX},{uint64_t(peer.pid)},{frontend}};
                        require(decodeBinding(Json::child(object,"binding"))==binding && context.incarnation.value==subject,"Original capture fixture grant and subject");
                        uint64_t count=0;std::ifstream(root/"capture-count")>>count;std::ofstream(root/"capture-count")<<count+1;
                        std::ofstream(root/"capture-wire.json")<<request.substr(14);
                        if(mode=="capture-refused")text="{\\"protocolVersion\\":3,\\"kind\\":\\"refused\\",\\"reason\\":\\"fixture-capture-refused\\"}";
                        else text=Wire().integer("protocolVersion",3).text("kind","preview-client-owned").begin("binding").binding(binding).end()
                            .counter("requestId",id).counter("subjectIncarnation",subject).counter("captureRequest",id).counter("outputGeneration",context.output.value)
                            .counter("completedNs",mode=="capture-malformed"?deadline:deadline-1).integer("width",1).integer("height",1)
                            .counter("encodedBytes",16).counter("ownedBytes",4096).text("crc32","0").text("encoding","PNG-RGBA8-straight")
                            .text("planeSpace","client-logical-unqualified").boolean("previewEligible",false).finish();
                    }
                    '''
s=s.replace(old,insert+old)
old='\\"previewFdAddress\\":\\"fixture_preview\\"'
new='\\"previewFdAddress\\":\\"fixture_preview_"+std::to_string(core)+"\\"'
assert s.count(old)==1;s=s.replace(old,new)
p=root/'native/capture-intent-source-fixture.hpp';assert not p.exists();p.write_text(s);print(p)
