"""Fresh actual authenticated SCM_RIGHTS fixture for adopted local capture storage."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v106')
p=root/'native/capture-resource-fd-source-fixture.hpp';assert not p.exists()
s=(root/'native/capture-resource-source-fixture.hpp').read_text()
def replace(old,new):
 global s
 assert s.count(old)==1,(old,s.count(old));s=s.replace(old,new)
replace('std::array<uint8_t,8>{137,80,78,71,13,10,26,10}','std::array<uint8_t,16>{137,80,78,71,13,10,26,10,1,2,3,4,5,6,7,8}')
replace('uint64_t session{},frontend{},incarnation{},request{};','uint64_t session{},frontend{},incarnation{},request{},deadline{},completed{};preview::Context context{};')
replace('probe.incarnation=subject;probe.request=id;','probe.incarnation=subject;probe.request=id;probe.deadline=deadline;probe.completed=9007199254740993ULL+id*1000000ULL;probe.context=context;')
replace('mode=="capture-malformed"?deadline:deadline-1','mode=="capture-malformed"?deadline:9007199254740993ULL+id*1000000ULL')
old='bool running=true;std::map<pid_t,uint64_t> frontends;'
new=r'''fd::Owned fdListener(::socket(AF_UNIX,SOCK_SEQPACKET|SOCK_CLOEXEC,0));
                auto [fdAddress,fdLength]=fd::address("fixture_preview_"+std::to_string(getpid()));
                require(fdListener && bind(fdListener.get(),reinterpret_cast<const sockaddr*>(&fdAddress),fdLength)==0 && listen(fdListener.get(),8)==0,"Actual child FD listener");
                bool running=true;std::map<pid_t,uint64_t> frontends;'''
replace(old,new)
replace('pollfd items[2]{{signal[0],POLLIN,0},{listener.get(),POLLIN,0}};auto n=poll(items,2,10000);',
        'pollfd items[3]{{signal[0],POLLIN,0},{listener.get(),POLLIN,0},{fdListener.get(),POLLIN,0}};auto n=poll(items,3,10000);')
old='                    fd::Owned connection(accept4(listener.get(),nullptr,nullptr,SOCK_CLOEXEC));'
new=r'''                    if(items[2].revents & POLLIN) {
                        fd::Owned channel(accept4(fdListener.get(),nullptr,nullptr,SOCK_CLOEXEC));require(bool(channel),"Actual authenticated FD accept");
                        ucred caller{};socklen_t bytes=sizeof(caller);require(getsockopt(channel.get(),SOL_SOCKET,SO_PEERCRED,&caller,&bytes)==0 && caller.uid==getuid(),"Actual kernel FD peer");
                        auto received=fd::receive<fd::RCount>(channel.get(),0);require(received.has_value(),"Actual closed binary FD request");const auto& query=received->words;
                        auto found=captures.find(caller.pid);require(found!=captures.end(),"Actual original capture before FD operation");auto& probe=found->second;
                        require(query[fd::RMagic]==fd::MAGIC && query[fd::RVersion]==1 && query[fd::RLifetime]==UINT64_MAX &&
                            query[fd::RSession]==uint64_t(caller.pid) && query[fd::RFrontend]==frontends.at(caller.pid) &&
                            query[fd::RCapture]==probe.request && query[fd::RSubject]==probe.incarnation,"Original authenticated FD capture correlation");
                        fd::Header header{};header[fd::Magic]=fd::MAGIC;header[fd::Version]=1;header[fd::Lifetime]=UINT64_MAX;
                        header[fd::Session]=probe.session;header[fd::Frontend]=probe.frontend;header[fd::Request]=query[fd::RRequest];
                        header[fd::Capture]=probe.request;header[fd::Subject]=probe.incarnation;header[fd::Output]=probe.context.output.value;
                        header[fd::Completed]=probe.completed;header[fd::Now]=probe.completed;header[fd::Width]=header[fd::Height]=1;
                        header[fd::Bytes]=16;header[fd::Charge]=4096;header[fd::Transfer]=9007199254740995ULL;
                        header[fd::Privacy]=probe.context.privacy.value;header[fd::Rendering]=probe.context.rendering.value;
                        header[fd::Scene]=probe.context.scene.value;header[fd::Content]=probe.context.content.value;
                        header[fd::Flags]=11;header[fd::Deadline]=probe.deadline;header[fd::Expires]=probe.completed+2000000000ULL;
                        if(query[fd::ROp]==fd::Get) {
                            require(probe.exported && query[fd::RTransfer]==0,"Actual original exported FD before transfer");
                            require(fd::send(channel.get(),header,probe.exported->file.get()),"Actual sealed SCM_RIGHTS capture transfer");
                            uint64_t count=0;std::ifstream(root/"fd-count")>>count;std::ofstream(root/"fd-count")<<count+1;
                        }else {
                            require(query[fd::ROp]==fd::Release && probe.exported && query[fd::RTransfer]==probe.exported->transfer,"Original binary export release");
                            probe.exported.reset();std::ofstream(root/"export-count")<<0;
                            // The actual export closes, but its original binary
                            // acknowledgment is rejected. New scoped metadata
                            // must repair this uncertainty; no recapture.
                            header[fd::Status]=4;require(fd::send(channel.get(),header),"Original lost release acknowledgment stimulus");
                        }
                        continue;
                    }
                    fd::Owned connection(accept4(listener.get(),nullptr,nullptr,SOCK_CLOEXEC));'''
replace(old,new);p.write_text(s)
print('Actual authenticated child FD listener and original sealed transfer/release stimulus prepared; synthetic pixels remain unqualified')
