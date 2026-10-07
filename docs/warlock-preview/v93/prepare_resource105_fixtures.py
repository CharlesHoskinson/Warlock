"""Fresh socket fixture uses the actual plugin19 resource engine and wire encoder."""
import hashlib,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v105')
p=root/'native/capture-resource-source-fixture.hpp';assert not p.exists()
s=(root/'native/capture-intent-source-fixture.hpp').read_text()
s=s.replace('#include "preview_retirement.hpp"','#include "preview_retirement.hpp"\n#include "capture-resources.hpp"')
defs=r'''
struct ResourceImage {uint64_t charge()const{return 4096;}};
struct ResourceReservation {uint64_t bytes()const{return 4096;}};
struct ResourceExport {
    fd::Owned file{fd::seal(std::array<uint8_t,8>{137,80,78,71,13,10,26,10})};
    ResourceReservation reservation;uint64_t transfer{9007199254740995ULL};
};
struct ResourceProbe {
    uint64_t session{},frontend{},incarnation{},request{};
    bool client{true},popup{},family{},crop{},styled{},backdrop{};
    std::unique_ptr<ResourceImage> image{std::make_unique<ResourceImage>()};
    std::unique_ptr<ResourceExport> exported{std::make_unique<ResourceExport>()};
};
'''
s=s.replace('struct Server {',defs+'\nstruct Server {',1)
old='bool running=true;std::map<pid_t,uint64_t> frontends;'
new=old+'std::map<pid_t,ResourceProbe> captures;uint64_t resourceSequence=0;bool lostRelease=false,lostRetire=false;'
assert s.count(old)==1;s=s.replace(old,new)
old='if(mode=="capture-refused")text='
assert s.count(old)==1
new='''if(mode!="capture-refused") {
                            ResourceProbe probe;probe.session=peer.pid;probe.frontend=frontend;probe.incarnation=subject;probe.request=id;
                            captures.insert_or_assign(peer.pid,std::move(probe));
                            std::ofstream(root/"producer-count")<<1;std::ofstream(root/"export-count")<<1;
                        }
                        if(mode=="capture-refused")text='''
s=s.replace(old,new)
old='                    else {require((kind=="preview-capture-probe-scope-request"'
assert s.count(old)==1
new=r'''                    else if(kind=="preview-client-resource-state-request" || kind=="preview-client-resource-release-request" || kind=="preview-client-resource-retire-request") {
                        auto object=envelope.object();Json::fields(object,{"protocolVersion","kind","binding","requestId","captureRequest","subjectIncarnation","transfer"});
                        const preview::Binding binding{{UINT64_MAX},{uint64_t(peer.pid)},{frontend}};
                        require(Json::integer(object,"protocolVersion")==3 && decodeBinding(Json::child(object,"binding"))==binding,"Actual kernel peer and original resource fixture grant");
                        const auto id=decimal(Json::text(object,"requestId")),capture=decimal(Json::text(object,"captureRequest")),subject=decimal(Json::text(object,"subjectIncarnation"));
                        const std::string_view raw=Json::text(object,"transfer");const auto transfer=raw=="0"?0:decimal(raw);
                        const auto action=kind=="preview-client-resource-state-request"?preview::resources::Operation::Observe:
                            kind=="preview-client-resource-release-request"?preview::resources::Operation::ReleaseExport:preview::resources::Operation::RetireProducer;
                        const bool locked=fs::exists(root/"locked");
                        text=preview::resources::execute(captures,peer.pid,preview::resources::Binding{UINT64_MAX,uint64_t(peer.pid),frontend},
                            preview::resources::Target{capture,subject},id,9007199254740993ULL+id*1000000ULL,locked,action,transfer,resourceSequence,preview::resources::wire);
                        auto current=captures.find(peer.pid);std::ofstream(root/"producer-count")<<(current!=captures.end());
                        std::ofstream(root/"export-count")<<(current!=captures.end() && bool(current->second.exported));
                        uint64_t count=0;std::ifstream(root/"resource-count")>>count;std::ofstream(root/"resource-count")<<count+1;
                        if(mode=="resource-lost-release" && action==preview::resources::Operation::ReleaseExport && !lostRelease) {lostRelease=true;text="{";}
                        if(mode=="resource-lost-retire" && action==preview::resources::Operation::RetireProducer && !locked && !lostRetire) {lostRetire=true;text="{";}
                        if(fs::exists(root/"bad-resource-reply"))replace(text,"\"subjectIncarnation\":\""+std::to_string(subject)+"\"","\"subjectIncarnation\":\"1\"");
                    }
                    else {require((kind=="preview-capture-probe-scope-request"'''
s=s.replace(old,new)
p.write_text(s)
print({'fixture':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'Authenticated synthetic socket with actual plugin19 owned-map resource engine and encoder; no real compositor pixels/capture FD acceptance'})
