#include "imported_clients.hpp"
#include "imported-clients.h"
#include "preview-provider-bootstrap.h"
#include <iostream>
using namespace preview;using namespace preview::bridge;
struct CImporter {
    WarlockImportedClients* owner{};
    uri::Endpoint* borrowed{};
    std::string initial;
    std::array<uint64_t,2> subjects;
    CImporter(Native& native,uint64_t first,uint64_t second):subjects{first,second} {
        GError* error=nullptr;char* wire=nullptr;void* endpoint=nullptr;
        owner=warlock_imported_clients_open(&native,reinterpret_cast<gpointer>(77),first,second,1,1,&wire,&endpoint,&error);
        require(owner && wire && endpoint && !error,"Actual shared C bridge enrollment");initial=wire;g_free(wire);borrowed=static_cast<uri::Endpoint*>(endpoint);
    }
    std::string identity(uint64_t id)const{require(id==1 || id==2,"Witness own source index");return "family:"+std::to_string(subjects[id-1]);}
    std::string status(uint64_t id) {
        GError* error=nullptr;char* wire=nullptr;require(warlock_imported_clients_status(owner,&wire,&error) && wire && !error,"Actual C bridge status");
        Json status(std::string("{\"states\":")+wire+"}");g_free(wire);auto array=json_object_get_array_member(status.object(),"states");require(array && json_array_get_length(array)==2,"Two actual bridge ownership records");
        auto encoded=json_to_string(json_array_get_element(array,static_cast<guint>(id-1)),FALSE);require(encoded,"Actual shared status row");std::string result=encoded;g_free(encoded);return result;
    }
    Job job(uint64_t id){Json state(status(id));return decodeJob(Json::child(state.object(),"job"));}
    uri::Endpoint& endpoint(){return *borrowed;}
    std::string command(uint64_t id,const std::string& family,const std::string& text) {
        require(family==identity(id),"Own C bridge witness dispatch identity");GError* error=nullptr;char* wire=nullptr;
        require(warlock_imported_clients_command(owner,family.c_str(),text.c_str(),&wire,&error) && wire && !error,"Actual C bridge command");std::string result=wire;g_free(wire);return result;
    }
    std::string poll(uint64_t id) {
        GError* error=nullptr;char* wire=nullptr;const auto family=identity(id);require(warlock_imported_clients_poll(owner,family.c_str(),&wire,&error) && wire && !error,"Actual C bridge poll");std::string result=wire;g_free(wire);return result;
    }
    std::string resume(uint64_t id,uint64_t publication,uint64_t lease) {
        GError* error=nullptr;char* wire=nullptr;const auto family=identity(id);
        require(warlock_imported_clients_resume(owner,family.c_str(),publication,lease,&wire,&error) && wire && !error,"Actual per-entry C bridge resume");std::string result=wire;g_free(wire);return result;
    }
    uint64_t lease(uint64_t id){return warlock_imported_clients_lease(owner,identity(id).c_str());}
    bool pollRetirement(uint64_t id){require(poll(id)=="[]","No C bridge renewal during local retirement");Json state(status(id));return Json::boolean(state.object(),"mappedFDClosed");}
    std::optional<Packet> packet(uint64_t id) {
        const auto original=job(id);return borrowed->native([&](auto& broker)->std::optional<Packet>{for(const auto& row:broker.inspect())if(row.entry==id){require(row.job==original,"Actual C bridge retained original job");return row.packet;}return {};});
    }
    std::string currentURI(uint64_t id) {
        GError* error=nullptr;char* wire=nullptr;const auto family=identity(id);require(warlock_imported_clients_uri(owner,family.c_str(),&wire,&error) && wire && !error,"Actual C bridge URI");std::string result=wire;g_free(wire);return result;
    }
    bool empty(){return warlock_imported_clients_empty(owner);}
    void refusesClose() {GError* error=nullptr;require(!warlock_imported_clients_close(owner,&error) && error,"Actual C close preserves unresolved owner");g_clear_error(&error);}
    void close(){GError* error=nullptr;require(warlock_imported_clients_close(owner,&error) && !error,"Actual empty C bridge closes");owner=nullptr;borrowed=nullptr;}
};
int main(int argc,char** argv){const char* stage="bootstrap";try {
    require(argc==6,"Exact native config, two subjects, private control and snapshot prefix");
    GError* error=nullptr;auto bootstrap=warlock_preview_bootstrap_open(argv[1],&error);require(bootstrap && !error,"Own supervised native bootstrap");
    auto native=static_cast<Native*>(warlock_preview_bootstrap_native_transport(bootstrap,&error));require(native && !error,"Own enrolled native transport");
    CImporter importer(*native,decimal(argv[2]),decimal(argv[3]));std::map<uint64_t,Job> jobs;std::map<uint64_t,Packet> packets;std::map<uint64_t,std::string> releases;std::map<uint64_t,GInputStream*> held;
    stage="original-native-demand";
    std::cout<<"{\"stage\":\"issued\",\"events\":"<<importer.initial<<"}\n"<<std::flush;
    jobs[1]=importer.job(1);jobs[2]=importer.job(2);auto& endpoint=importer.endpoint();
    require(endpoint.registeredView(77).has_value(),"C bridge registered actual trusted witness receiver");ReceiptDelivery delivery(endpoint,native->binding(),77);
    auto status=[&](const char* name){std::cout<<"{\"stage\":\""<<name<<"\",\"first\":"<<importer.status(1)<<",\"second\":"<<importer.status(2)<<"}\n"<<std::flush;};
    auto requireBackendGone=[&]{
        Wire query;auto reply=native->control(query.integer("protocolVersion",3).text("kind","preview-client-state-request").begin("binding").binding(native->binding()).end().counter("requestId",native->next()).finish());
        Json::fields(reply.object(),{"protocolVersion","kind","reason"});require(Json::integer(reply.object(),"protocolVersion")==3 && std::string_view(Json::text(reply.object(),"kind"))=="refused" && std::string_view(Json::text(reply.object(),"reason"))=="preview-client-unavailable","Actual native capture registry absent after early retirement");
    };
    auto importEntry=[&](uint64_t id,const std::string& suffix) {
        stage="actual-shared-import";Wire acquire;auto events=importer.command(id,"family:"+std::to_string(jobs[id].context.incarnation.value),acquire.text("kind","acquire").begin("job").job(jobs[id]).end().finish());
        Json wire("{\"events\":"+events+"}");auto array=json_object_get_array_member(wire.object(),"events");require(array && json_array_get_length(array)==2,"Actual imported Offer/readiness pair");
        auto ready=Json::child(json_node_get_object(json_array_get_element(array,1)),"event");auto frame=Json::child(ready,"frame");
        require(decodeJob(Json::child(frame,"job"))==jobs[id],"Exact original issued imported job");
        auto encoded=json_to_string(json_object_get_member(ready,"frame"),FALSE);require(encoded,"Exact original native packet");releases[id]="{\"kind\":\"release\",\"frame\":"+std::string(encoded)+"}";g_free(encoded);
        require(importer.packet(id).has_value(),"Actual original physical packet");packets[id]=*importer.packet(id);
        Json ownStatus(importer.status(id));require(Json::boolean(ownStatus.object(),"producerRetired") && Json::boolean(ownStatus.object(),"exportReleased") && !Json::boolean(ownStatus.object(),"mappedFDClosed") && decimal(Json::text(ownStatus.object(),"charge"))>0,"Backend retired while actual local charge remains positive");
        requireBackendGone();require(importer.currentURI(id)==uri::encode(packets[id].token),"Actual C URI projection preserves original native token");
        stage="actual-imported-uri";gsize size{};auto stream=endpoint.open(77,uri::encode(packets[id].token),&size,&error);require(stream && !error && size>8,"Actual imported URI readable after native registry removal");
        fd::Owned image(::open((std::string(argv[5])+"."+std::to_string(id)+suffix+".png").c_str(),O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600));require(bool(image),"Private new imported pixel specimen");
        std::array<uint8_t,65536> bytes{};uint64_t total=0;
        for(;;) {const auto got=g_input_stream_read(stream,bytes.data(),bytes.size(),nullptr,&error);require(got>=0 && !error,"Actual native-guarded immutable PNG read");if(!got)break;size_t position=0;while(position<static_cast<size_t>(got)){auto n=::write(image.get(),bytes.data()+position,static_cast<size_t>(got)-position);if(n<0 && errno==EINTR)continue;require(n>0,"Actual imported PNG specimen write");position+=static_cast<size_t>(n);}total+=static_cast<uint64_t>(got);}
        require(total==size && g_input_stream_close(stream,nullptr,&error) && !error,"Exact original imported PNG length and stream closure");g_object_unref(stream);
        held[id]=endpoint.open(77,uri::encode(packets[id].token),&size,&error);require(held[id] && !error,"Actual retained imported reader");
        require(g_input_stream_read(held[id],bytes.data(),4,nullptr,&error)==4 && !error,"Actual held imported PNG read");
        std::cout<<"{\"stage\":\"imported-"<<id<<"\",\"events\":"<<events<<",\"status\":"<<importer.status(id)<<",\"nativeRegistryAbsent\":true,\"hardwarePresentation\":false}\n"<<std::flush;
    };
    for(uint64_t id=1;id<=2;++id)importEntry(id,"");
    require(packets[1].token!=packets[2].token && packets[1].job.binding==packets[2].job.binding && packets[1].job.context.incarnation!=packets[2].job.context.incarnation,"Distinct subjects and tokens under one own native grant");
    auto foreign=native->binding();foreign.frontend.value++;
    require(endpoint.registerView(88,foreign,{1,2}),"Foreign qualification view");gsize size{};auto refused=endpoint.open(88,uri::encode(packets[1].token),&size,&error);require(!refused && error,"Foreign receiver has no imported pixels");g_clear_error(&error);endpoint.unregisterView(88);importer.refusesClose();require(endpoint.registeredView(77).has_value(),"Refused C close preserves current receiver and terminal route");status("ready");
    const auto oldJob=jobs[1];const auto oldPacket=packets[1];const auto siblingJob=jobs[2];const auto siblingPacket=packets[2];
    auto ack=[&](uint64_t id,const Job& job,uint64_t sequence){Wire wire;return delivery.acknowledge(77,importer.identity(id),wire.text("kind","acknowledge").begin("job").job(job).end().counter("sequence",sequence).finish());};
    auto siblingUnchanged=[&]{require(importer.job(2)==siblingJob && importer.packet(2).has_value() && importer.packet(2)->token==siblingPacket.token && importer.packet(2)->expires==siblingPacket.expires && importer.lease(2)==1,"Charged sibling retains exact original job/token/expiry/lease");Json state(importer.status(2));require(!Json::boolean(state.object(),"mappedFDClosed") && decimal(Json::text(state.object(),"charge"))>0 && held[2],"Sibling still owns physical mapping/FD and held reader");};
    std::string prior;bool stopped=false,denied=false,firstRetired=false,resumed=false;
    for(;;) {
        std::ifstream control(argv[4]);std::string command;std::getline(control,command);require(bool(control) || control.eof(),"Private witness control read");
        if(command.empty() || command=="hold" || command==prior){::usleep(20000);continue;}prior=command;
        if(command=="retire-first") {
            stage="first-own-physical-retirement";
            require(!firstRetired && !resumed,"One asymmetric retirement");
            require(importer.command(1,importer.identity(1),releases[1])=="[]","First original exact Release");
            require(importer.resume(1,2,2)=="[]" && importer.job(1)==oldJob && importer.lease(1)==1,"Own held reader blocks resume without lease/job renewal");status("own-reader-blocked");
            require(g_input_stream_close(held[1],nullptr,&error) && !error,"First own held reader closes");g_object_unref(held[1]);held[1]=nullptr;
            require(importer.pollRetirement(1),"First local physical mmap/FD closes");siblingUnchanged();
            require(delivery.pending(77).size()==1 && importer.resume(1,2,2)=="[]" && importer.job(1)==oldJob && importer.lease(1)==1,"Own terminal journal blocks resume after physical drain");status("own-journal-blocked");
            require(ack(1,oldJob,5),"Exact first original terminal ACK5");siblingUnchanged();status("first-acked-sibling-held");firstRetired=true;
        }else if(command=="resume-first") {
            stage="native-resume-with-held-sibling";require(firstRetired && !resumed,"First physical retirement and exact ACK precede resumption");siblingUnchanged();
            const auto events=importer.resume(1,2,2);Json wire("{\"events\":"+events+"}");auto array=json_object_get_array_member(wire.object(),"events");require(array && json_array_get_length(array)==2,"Native fresh seed/request while sibling remains held");
            jobs[1]=importer.job(1);require(jobs[1].binding==oldJob.binding && jobs[1].clock==oldJob.clock && jobs[1].context.incarnation==oldJob.context.incarnation && jobs[1].request.value==oldJob.request.value+1 && jobs[1].origin.value==2 && jobs[1].deadline==jobs[1].issued+2000000000ULL && jobs[1].issued>oldJob.issued,"Own native request2 retains grant/clock and new original two-second issuance");
            std::cout<<"{\"stage\":\"resumed-demand\",\"events\":"<<events<<",\"first\":"<<importer.status(1)<<",\"second\":"<<importer.status(2)<<"}\n"<<std::flush;
            require(!ack(1,oldJob,5) && importer.job(1)==jobs[1],"Old ACK5 cannot retire new first reservation");
            auto stale=endpoint.open(77,uri::encode(oldPacket.token),&size,&error);require(!stale && error,"Old opaque first URI cannot alias request2");g_clear_error(&error);
            importEntry(1,".request-2");require(packets[1].token!=oldPacket.token && packets[1].token!=siblingPacket.token,"New native first token is distinct from both originals");siblingUnchanged();
            std::array<uint8_t,4> bytes{};require(g_input_stream_read(held[2],bytes.data(),bytes.size(),nullptr,&error)==4 && !error,"Original held sibling still reads through actual native authority");
            status("resumed-first-sibling-held");resumed=true;
        }else if(command=="finish-resume") {
            stage="asymmetric-final-retirement";require(resumed,"Actual second first capture precedes cleanup");
            for(uint64_t id=1;id<=2;++id)require(importer.command(id,importer.identity(id),releases[id])=="[]","Exact per-entry final Release preserves held physical readers");status("asymmetric-held-cleanup");
            for(uint64_t id=1;id<=2;++id){require(g_input_stream_close(held[id],nullptr,&error) && !error,"Exact asymmetric held reader closure");g_object_unref(held[id]);held[id]=nullptr;require(importer.pollRetirement(id),"Exact asymmetric local mmap/FD physical retirement");}
            require(delivery.pending(77).size()==2,"Two exact retained final terminal proofs");status("asymmetric-physical-retired");
            require(ack(1,jobs[1],8) && ack(2,jobs[2],9),"Exact new-first ACK8 and original sibling ACK9 follow physical retirement");require(importer.empty(),"Asymmetric shared physical and journal owner empty");status("asymmetric-complete");importer.close();warlock_preview_bootstrap_free(bootstrap);return 0;
        }else if(command=="stopped") {
            stage="actual-stopped-read";auto current=native->clientScope(jobs[1].context.incarnation);require(current.scope.present && !current.scope.sourceLive,"Actual native minimized source scope");
            std::array<uint8_t,4> bytes{};require(g_input_stream_read(held[1],bytes.data(),bytes.size(),nullptr,&error)==4 && !error,"Actual retained imported Historical read after native minimization");
            auto again=endpoint.open(77,uri::encode(packets[1].token),&size,&error);require(again && !error,"Actual new Historical URI read after native producer retirement");require(g_input_stream_close(again,nullptr,&error) && !error,"Actual Historical stream closure");g_object_unref(again);
            auto observations=importer.poll(1);Json events("{\"events\":"+observations+"}");auto array=json_object_get_array_member(events.object(),"events");require(array && json_array_get_length(array)==1,"Source-stop observation preserves original imported packet");
            require(importer.packet(1)->job==packets[1].job && importer.packet(1)->token==packets[1].token && importer.packet(1)->expires==packets[1].expires,"No Historical recapture or expiry renewal");
            std::cout<<"{\"stage\":\"historical\",\"events\":"<<observations<<",\"first\":"<<importer.status(1)<<"}\n"<<std::flush;stopped=true;
        }else if(command=="deny") {
            stage="actual-lock-read";require(stopped && !denied,"One stopped then locked imported campaign");
            endpoint.native([&](auto& broker){for(uint64_t id=1;id<=2;++id)require(static_cast<bool>(broker.fetch(id,jobs[id].binding,packets[id].token)),"Cached policy still grants before independent native lock guard");});
            for(uint64_t id=1;id<=2;++id) {
                uint8_t byte{};require(g_input_stream_read(held[id],&byte,1,nullptr,&error)==-1 && error && error->code==G_IO_ERROR_PERMISSION_DENIED,"Actual native lock denies held imported reader before policy");g_clear_error(&error);
                auto extra=endpoint.open(77,uri::encode(packets[id].token),&size,&error);require(!extra && error,"Actual native lock denies new imported URI before policy");g_clear_error(&error);
            }
            status("native-uri-denied-before-policy");denied=true;
        }else if(command=="finish") {
            stage="actual-local-retirement";require(denied,"Actual native authority refusal precedes cleanup");
            for(uint64_t id=1;id<=2;++id)require(importer.command(id,"family:"+std::to_string(jobs[id].context.incarnation.value),releases[id])=="[]","Exact original imported Release command");
            status("held-cleanup");
            for(uint64_t id=1;id<=2;++id) {
                require(g_input_stream_close(held[id],nullptr,&error) && !error,"Actual original held reader drain");g_object_unref(held[id]);held[id]=nullptr;
                require(importer.pollRetirement(id),"Actual local mmap/FD physical retirement");
            }
            require(delivery.pending(77).size()==2,"Two retained exact terminal proofs after physical retirement");status("physical-retired");
            for(uint64_t id=1;id<=2;++id) {Wire ack;require(delivery.acknowledge(77,"family:"+std::to_string(jobs[id].context.incarnation.value),ack.text("kind","acknowledge").begin("job").job(jobs[id]).end().counter("sequence",4+id).finish()),"Actual exact original terminal ACK after local physical retirement");}
            require(importer.empty(),"One physical Broker, native ownership and journal finally empty");status("complete");importer.close();warlock_preview_bootstrap_free(bootstrap);return 0;
        }else throw std::runtime_error("Unexpected private importer command");
    }
}catch(const std::exception& error){std::cerr<<stage<<": "<<error.what()<<'\n';return 1;}}
