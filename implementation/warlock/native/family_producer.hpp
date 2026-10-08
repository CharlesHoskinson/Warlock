#pragma once
#include "client_producer.hpp"
#include "family_frame.hpp"
#include "preview_delivery.hpp"

namespace preview::bridge {
inline std::optional<uri::NativeTime> familyNativeTime(Native& native,const stylecropfd::Header& frame,bool picker=false) noexcept {
    try {
        auto observed=native.familyQuery(fd::Observe,frame[fd::Capture],frame[fd::Subject],frame[fd::Transfer]);if(!observed)return {};
        const auto& h=observed->words;auto current=observeFamilySource(native,{frame[fd::Subject]},FamilyPlane::Transparent,picker);const auto& s=current.scope;
        if(!stylecropfd::imageHeader(frame) || !stylecropfd::imageHeader(h) || !(h[fd::Flags]&fd::Present) || !s.present || s.locked || !s.gpuReady || s.binding!=native.binding() || s.context.lifetime.value!=frame[fd::Lifetime] || s.context.incarnation.value!=frame[fd::Subject] || s.context.output.value!=frame[fd::Output] || s.context.privacy.value!=frame[fd::Privacy] || s.context.rendering.value!=frame[fd::Rendering] || h[fd::Now]<frame[fd::Now] || s.now<h[fd::Now] || s.now>=frame[fd::Expires])return {};
        return uri::NativeTime{s.clock,s.now};
    }catch(...){return {};}
}
inline std::optional<uri::NativeTime> familyNativeTime(Native& native,const backdropfd::Header& frame) noexcept {
    try {
        auto observed=native.backdropQuery(fd::Observe,frame[fd::Capture],frame[fd::Subject],frame[fd::Transfer]);if(!observed)return {};
        const auto& h=observed->words;auto current=observeFamilySource(native,{frame[fd::Subject]},FamilyPlane::GeneratedBackdrop);const auto& s=current.scope;
        if(!backdropfd::imageHeader(frame) || !backdropfd::imageHeader(h) || h[backdropfd::ColorARGB]!=frame[backdropfd::ColorARGB] || !(h[fd::Flags]&fd::Present) || !s.present || s.locked || !s.gpuReady || s.binding!=native.binding() || s.context.lifetime.value!=frame[fd::Lifetime] || s.context.incarnation.value!=frame[fd::Subject] || s.context.output.value!=frame[fd::Output] || s.context.privacy.value!=frame[fd::Privacy] || s.context.rendering.value!=frame[fd::Rendering] || h[fd::Now]<frame[fd::Now] || s.now<h[fd::Now] || s.now>=frame[fd::Expires])return {};
        return uri::NativeTime{s.clock,s.now};
    }catch(...){return {};}
}
inline ClientCommand decodeFamilyCommand(const std::string& identity,const std::string& text,const Job& expected,const std::optional<Packet>& packet) {
    require(identity=="family:"+std::to_string(expected.context.incarnation.value),"Exact native client family");
    Json wire(text);auto o=wire.object();const std::string_view kind=Json::text(o,"kind");
    if(kind=="acquire" || kind=="cancel") {
        Json::fields(o,{"kind","job"});require(decodeJob(Json::child(o,"job"))==expected,"Exact original native client job");
        return kind=="acquire"?ClientCommand::Acquire:ClientCommand::Cancel;
    }
    require(kind=="release" && packet.has_value(),"Owned client release command");Json::fields(o,{"kind","frame"});
    auto frame=Json::child(o,"frame");Json::fields(frame,{"job","handle","owned","signaled","fidelity","coverage","expires"});
    require(decodeJob(Json::child(frame,"job"))==expected && packet->job==expected,"Original client release job");
    require(std::string_view(Json::text(frame,"handle"))==uri::encode(packet->token).substr(std::string_view("elm-shell://preview/").size()),"Exact owned client handle");
    require(Json::boolean(frame,"owned") && Json::boolean(frame,"signaled") && packet->signaled && std::string_view(Json::text(frame,"fidelity"))=="family","Actual owned client packet correlation");
    auto node=json_object_get_member(frame,"coverage");require(node && JSON_NODE_HOLDS_ARRAY(node),"Typed client coverage");auto coverage=json_node_get_array(node);
    require(json_array_get_length(coverage)==4,"Native family sample coverage");
    const std::array<const char*,4> names{"client","decoration","modal","popup"};
    for(guint i=0;i<4;++i){auto member=json_array_get_element(coverage,i);require(member && json_node_get_value_type(member)==G_TYPE_STRING && std::string_view(json_node_get_string(member))==names[i],"Native family coverage member");}
    require(decimal(Json::text(frame,"expires"))==packet->expires,"Original client expiration");return ClientCommand::Release;
}
inline std::string familySourceJSON(const FamilySourceObservation& observed) {
    require(!observed.wire.empty(),"Own decoded native family wire");return observed.wire;
}
inline std::string familySeed(const FamilySourceObservation& observed,uint64_t publication,uint64_t lease) {
    require(publication && lease,"Admitted native client publication and lease");
    Wire seed;auto front=seed.text("kind","source-seed").counter("publication",publication).counter("lease",lease).text("identity","family:"+std::to_string(observed.scope.context.incarnation.value)).text("title","Native family sample").text("application","Native family").finish();
    front.pop_back();return front+",\"source\":"+familySourceJSON(observed)+"}";
}
inline std::string familyObservation(const FamilySourceObservation& observed) {
    const auto& s=observed.scope;Wire wire;
    return wire.text("kind","event").text("identity","family:"+std::to_string(s.context.incarnation.value)).begin("event").text("kind","observe").begin("scope").begin("binding").binding(s.binding).end().begin("context").context(s.context).end().counter("observation",observed.observation).counter("clock",s.clock.value).counter("now",s.now).boolean("present",s.present).boolean("sourceLive",s.sourceLive).boolean("locked",s.locked).boolean("gpuReady",s.gpuReady).end().end().finish();
}
inline bool familyFactsChanged(const FamilySourceObservation& old,const FamilySourceObservation& current) {
    const auto& a=old.scope;const auto& b=current.scope;
    return old.plane!=current.plane || old.generatedColor!=current.generatedColor || a.context!=b.context || a.present!=b.present || a.sourceLive!=b.sourceLive || a.locked!=b.locked || a.gpuReady!=b.gpuReady;
}
inline bool admitFamilyObservation(Broker& broker,const Job& original,const FamilySourceObservation& observed) {
    const auto& s=observed.scope;
    require(!observed.wire.empty() &&
        s.binding==original.binding && s.context.lifetime==original.context.lifetime && s.context.incarnation==original.context.incarnation && s.clock==original.clock,
        "Same own typed client observation authority");
    return broker.observe(1,s,observed.maximumTransferBytes);
}
inline std::optional<Job> reserveFamilyResume(demand::Coordinator& queue,const Job& prior,const FamilySourceObservation& previous,uint64_t oldLease,const FamilySourceObservation& fresh,uint64_t publication,uint64_t lease) {
    auto& broker=queue.nativeBroker();
    if(!publication || lease<=oldLease || broker.recordCount()!=0 || broker.charge()!=0)return {};
    const auto& s=fresh.scope;const auto& old=previous.scope;
    require(!fresh.wire.empty() &&
        s.binding==prior.binding && s.context.lifetime==prior.context.lifetime && s.context.incarnation==prior.context.incarnation && s.clock==prior.clock &&
        fresh.observation>previous.observation && fresh.request>previous.request && s.now>=old.now &&
        s.context.output>=old.context.output && s.context.privacy>=old.context.privacy && s.context.rendering>=old.context.rendering &&
        s.context.scene>=old.context.scene && s.context.content>=old.context.content &&
        (s.sourceLive==old.sourceLive || s.context.scene>old.context.scene),"Fresh own coherent native resume observation");
    if(!s.present || !s.sourceLive || s.locked || !s.gpuReady || fresh.maximumTransferBytes>broker.limits().bytes)return {};
    require(s.now<=UINT64_MAX-2000000000ULL && broker.requestFloor(1)==prior.request.value,"Original clock and retained request floor before new demand");
    require(queue.observe({1,lease,s,{lease},fresh.maximumTransferBytes,true}).accepted,"Fresh native resume demand admission");
    const auto attempt=queue.start(1,s.now+2000000000ULL);
    if(attempt.status==demand::Attempt::Status::NotReady || attempt.status==demand::Attempt::Status::Capacity)return {};
    require(attempt.status==demand::Attempt::Status::Started && attempt.job.has_value(),"Exact new native resume reservation");return attempt.job;
}
inline bool admitRetainedFamilyPresentation(Broker& broker,const Job& original,const FamilySourceObservation& current,const Packet& packet,uint64_t oldLease,uint64_t publication,uint64_t lease) {
    if(!publication || lease<=oldLease || packet.job!=original || !packet.signaled)return false;
    const auto& s=current.scope;const auto& admitted=broker.nativeScope(1);
    require(!current.wire.empty() &&
        s.binding==original.binding && s.context.lifetime==original.context.lifetime && s.context.incarnation==original.context.incarnation && s.clock==original.clock &&
        admitted.binding==s.binding && admitted.context==s.context && admitted.clock==s.clock && admitted.now==s.now &&
        admitted.present==s.present && admitted.sourceLive==s.sourceLive && admitted.locked==s.locked && admitted.gpuReady==s.gpuReady,
        "Retained presentation uses the exact current admitted own native scope");
    if(!s.present || s.locked || !s.gpuReady || s.now>=packet.expires)return false;
    const auto rows=broker.inspect();const auto retained=std::find_if(rows.begin(),rows.end(),[&](const auto& row){return row.entry==1 && row.job==original;});
    if(retained==rows.end() || retained->cleanup || retained->terminal || !retained->packet)return false;
    const auto& owned=*retained->packet;
    return owned.job==packet.job && owned.token==packet.token && owned.signaled==packet.signaled && owned.expires==packet.expires && owned.fidelity==packet.fidelity && owned.coverage==packet.coverage && static_cast<bool>(broker.fetch(1,original.binding,packet.token));
}
inline std::string familyRequest(const Job& job) {
    Wire request;return request.text("kind","event").text("identity","family:"+std::to_string(job.context.incarnation.value)).begin("event").text("kind","request").begin("trigger").begin("binding").binding(job.binding).end().begin("context").context(job.context).end().counter("origin",job.origin.value).counter("clock",job.clock.value).counter("deadline",job.deadline).end().end().finish();
}
inline std::string familyDenied(Broker& broker,const Job& original,const Packet& packet,const ScopeDenied& denied) {
    require(denied.binding==original.binding && denied.subject==original.context.incarnation && denied.request && packet.job==original,"Exact owned native scope denial");
    const auto entry=broker.owningEntry(original);require(entry && *entry==1,"Retained denied source owner");
    const auto rows=broker.inspect();const auto record=std::find_if(rows.begin(),rows.end(),[&](const auto& row){return row.entry==1 && row.job==original;});
    require(record!=rows.end() && !record->terminal && record->packet && record->packet->token==packet.token,"Exact retained denied packet authority");
    // Native scope denial revokes this allocator's URI authority immediately.
    // It neither completes the physical resource nor substitutes an Elm effect.
    broker.release(1,original.binding,original,packet.token);
    Wire wire;return wire.text("kind","event").text("identity","family:"+std::to_string(original.context.incarnation.value)).begin("event").text("kind","source-denied").begin("job").job(original).end().text("reason",denialName(denied.reason)).end().finish();
}
inline void familyPacketJSON(Wire& wire,const Packet& packet) {
    wire.begin("job").job(packet.job).end().text("handle",uri::encode(packet.token).substr(std::string_view("elm-shell://preview/").size())).boolean("owned",true).boolean("signaled",packet.signaled).text("fidelity","family").array("coverage").element("client").element("decoration").element("modal").element("popup").endArray().counter("expires",packet.expires);
}
inline std::string familyFrameEvent(const char* kind,const Packet& packet) {
    Wire wire;wire.text("kind","event").text("identity","family:"+std::to_string(packet.job.context.incarnation.value)).begin("event").text("kind",kind).begin("frame");familyPacketJSON(wire,packet);return wire.end().end().finish();
}
// One owning allocator, not a second frontend policy. Native demand reserves
// the original job; an exact actual Elm Acquire starts physical capture.
class FamilyProducer {
    Native& native_;
    FamilySourceObservation observed_;
    stylecropfd::Header header_{};
    backdropfd::Header backdropHeader_{};
    bool haveHeader_{},attempted_{},cleanup_{},exportReleased_{},producerRetired_{},mappingClosed_{},retirementPending_{},scopeDenied_{},staleRefused_{};
    uri::Endpoint endpoint_;
    uint64_t popup_,lease_,publication_;
    Job job_;
    std::optional<FamilyCapture> capture_;
    std::optional<Packet> packet_;
    stylecropfd::Mapped* mapping_{};
    backdropfd::Mapped* backdropMapping_{};
    bool mapped() const {return mapping_ || backdropMapping_;}
    std::string initial_;
    bool retire() {
        return endpoint_.native([&](Broker& broker) {
            if(!cleanup_ || !packet_ || !broker.consumerComplete(1,job_))return false;
            require(mapped(),"Owned client mapping pending retirement");
            require(backdropMapping_?backdropMapping_->close():mapping_->close(),"Physical client mapping and FD close");mappingClosed_=true;
            if(!exportReleased_) {require(releaseFamily(native_,*capture_,(backdropMapping_?backdropHeader_[fd::Transfer]:header_[fd::Transfer])),"Exact client export release");exportReleased_=true;}
            if(!producerRetired_) {
                const auto state=retireFamilyState(native_,observed_.plane,job_.context.incarnation.value,observed_.picker);retirementPending_=state==ClientRetirement::PendingLock;
                if(retirementPending_)return false;
                producerRetired_=true;
            }
            auto retired=broker.destroy(1,job_);require(retired.status==Result::Status::Complete && !retired.receipts.empty() && broker.charge()==0,"Physical client Broker proof after retirement");mapping_=nullptr;backdropMapping_=nullptr;return true;
        });
    }
public:
    FamilyProducer(Native& native,uint64_t popup,uint64_t subject,uint64_t publication,uint64_t lease,FamilyPlane plane=FamilyPlane::Transparent,bool picker=false):
        native_(native),observed_(observeFamilySource(native,{subject},plane,picker)),
        endpoint_({1,4,1,128ULL*1024*1024},1,1,[this](uint64_t)->std::optional<uri::NativeTime>{return haveHeader_?(observed_.plane==FamilyPlane::GeneratedBackdrop?familyNativeTime(native_,backdropHeader_):familyNativeTime(native_,header_,observed_.picker)):std::nullopt;}),popup_(popup),lease_(lease),publication_(publication) {
        require(popup && publication && lease && !observed_.wire.empty(),"Trusted qualification source/stamp");
        const auto& scope=observed_.scope;require(scope.binding==native_.binding() && scope.present && scope.sourceLive && !scope.locked && scope.gpuReady,"Own live native client scope");
        require(scope.now<=UINT64_MAX-2000000000ULL,"Original client deadline representable");
        require(endpoint_.enableDemand({{1,4,1,128ULL*1024*1024},scope.binding.lifetime,scope.clock,1}),"One physical native demand policy");
        require(endpoint_.nativeDemand([&](auto& q){return q.observe({1,lease,scope,{lease},observed_.maximumTransferBytes,true}).accepted;}),"Own native client demand");
        auto attempt=endpoint_.nativeDemand([&](auto& q){return q.start(1,scope.now+2000000000ULL);});require(attempt.status==demand::Attempt::Status::Started && attempt.job.has_value(),"Original native job reservation");job_=*attempt.job;
        require(endpoint_.registerView(popup,scope.binding,{1}),"Actual native WebKit receiver");
        auto front=familySeed(observed_,publication,lease);
        initial_="["+front+","+familyRequest(job_)+"]";
    }
    FamilyProducer(const FamilyProducer&)=delete;FamilyProducer& operator=(const FamilyProducer&)=delete;
    uri::Endpoint& endpoint(){return endpoint_;}
    const std::string& initial()const{return initial_;}
    const Job& job()const{return job_;}
    uint64_t lease()const{return lease_;}
    std::string currentURI()const{return packet_ && !cleanup_ && !scopeDenied_?uri::encode(packet_->token):"";}
    std::string refreshRefused(uint64_t publication,uint64_t lease) {
        if(!observed_.picker || !staleRefused_ || !publication || lease!=lease_ || !empty())return "[]";
        require(!capture_ && !mapped() && !attempted_,"Acknowledged no-capture refusal before changed source demand");
        auto fresh=observeFamilySource(native_,job_.context.incarnation,observed_.plane,true);
        if(fresh.scope.context==job_.context)return "[]";
        auto next=endpoint_.nativeDemand([&](auto& queue){return reserveFamilyResume(queue,job_,observed_,lease_-1,fresh,publication,lease);});
        if(!next)return "[]";
        observed_=fresh;job_=*next;publication_=publication;cleanup_=false;staleRefused_=false;
        return "["+familySeed(observed_,publication,lease)+","+familyRequest(job_)+"]";
    }
    std::string resume(uint64_t publication,uint64_t lease) {
        // No source query or new reservation while old physical or proof
        // ownership remains. New demand comes from the admitted GTK gate.
        if(!publication || lease<=lease_ || !empty())return "[]";
        require(!mapped() && (!attempted_ || (mappingClosed_ && exportReleased_ && producerRetired_ && !retirementPending_)),"Actual old producer retirement before new source query");
        FamilySourceObservation fresh;
        try {fresh=observeFamilySource(native_,job_.context.incarnation,observed_.plane,observed_.picker);}
        catch(const ScopeDenied&){return "[]";}
        auto next=endpoint_.nativeDemand([&](auto& queue){return reserveFamilyResume(queue,job_,observed_,lease_,fresh,publication,lease);});
        if(!next)return "[]";
        observed_=fresh;job_=*next;lease_=lease;publication_=publication;header_={};backdropHeader_={};haveHeader_=false;attempted_=false;cleanup_=false;
        exportReleased_=false;producerRetired_=false;mappingClosed_=false;retirementPending_=false;scopeDenied_=false;staleRefused_=false;capture_.reset();packet_.reset();
        return "["+familySeed(observed_,publication,lease_)+","+familyRequest(job_)+"]";
    }
    std::string command(const std::string& identity,const std::string& text) {
        const auto command=decodeFamilyCommand(identity,text,job_,packet_);
        if(command==ClientCommand::Acquire) {
            require(!attempted_ && !cleanup_,"Single original physical client capture");attempted_=true;
            try {capture_=captureFamily(native_,observed_,job_.deadline);}
            catch(const PickerCaptureRefused& refused) {
                // The authenticated exact request proved no native capture was
                // installed. Its original broker publishes a retained Refused
                // proof; only Elm's exact Ack can release this reservation.
                endpoint_.native([&](auto& b){return b.producerRefused(1,job_);});
                attempted_=false;cleanup_=true;staleRefused_=refused.stale;
                g_print("picker-native-refused: %s\n",refused.what());fflush(stdout);
                return "[]";
            }
            std::unique_ptr<const Buffer> payload;uint64_t expires=0;
            if(observed_.plane==FamilyPlane::GeneratedBackdrop) {
                auto received=native_.backdropQuery(fd::Get,capture_->request,job_.context.incarnation.value);
                require(received && received->rights.size()==1 && familyFrameMatches(received->words,*capture_),"Exact owned generated backdrop descriptor");backdropHeader_=received->words;haveHeader_=true;
                auto mapping=std::make_unique<backdropfd::Mapped>(std::move(received->rights.front()),backdropHeader_,observed_.maximumTransferBytes);backdropMapping_=mapping.get();payload=std::move(mapping);expires=backdropHeader_[fd::Expires];
            } else {
                auto received=native_.familyQuery(fd::Get,capture_->request,job_.context.incarnation.value);
                require(received && received->rights.size()==1 && familyFrameMatches(received->words,*capture_),"Exact owned client descriptor");header_=received->words;haveHeader_=true;
                auto mapping=std::make_unique<stylecropfd::Mapped>(std::move(received->rights.front()),header_,observed_.maximumTransferBytes);mapping_=mapping.get();payload=std::move(mapping);expires=header_[fd::Expires];
            }
            auto fresh=observeFamilySource(native_,job_.context.incarnation,observed_.plane,observed_.picker);require(fresh.scope.context==job_.context && fresh.scope.binding==job_.binding && fresh.scope.clock==job_.clock && fresh.generatedColor==observed_.generatedColor && fresh.scope.now<job_.deadline,"Native family source/deadline still current before offer");
            auto offered=endpoint_.native([&](auto& b){return b.allocate(1,job_,payload,expires,Packet::Fidelity::Family,15);});require(offered.receipts.size()==1 && offered.receipts.front().packet && !payload,"Physical client payload adopted");
            const auto before=*offered.receipts.front().packet;auto ready=endpoint_.native([&](auto& b){return b.producerComplete(1,job_);});require(ready.receipts.size()==1 && ready.receipts.front().packet,"Completed immutable client copy");packet_=*ready.receipts.front().packet;
            // Readiness concerns encoded immutable storage, never hardware presentation.
            return "["+familyFrameEvent("offer",before)+","+familyFrameEvent("fence",*packet_)+"]";
        }
        if(command==ClientCommand::Cancel) {
            endpoint_.native([&](auto& b){return b.cancel(1,job_.binding,job_);});cleanup_=true;
            if(!attempted_)endpoint_.native([&](auto& b){return b.producerRefused(1,job_);});
        } else {endpoint_.native([&](auto& b){return b.release(1,job_.binding,job_,packet_->token);});cleanup_=true;}
        if(mapped())retire();
        return "[]";
    }
    std::string poll(uint64_t publication,uint64_t lease) {
        if(mapped() && cleanup_)retire();
        if(!packet_ || cleanup_ || scopeDenied_)return "[]";
        // Original native source clock, not a frontend timer or renewed deadline.
        std::optional<FamilySourceObservation> currentObservation;std::string deniedEvent;
        endpoint_.native([&](auto& broker){
            try {auto fresh=observeFamilySource(native_,job_.context.incarnation,observed_.plane,observed_.picker);require(admitFamilyObservation(broker,job_,fresh),"Coherent own client authority update");currentObservation=fresh;}
            catch(const ScopeDenied& denied) {deniedEvent=familyDenied(broker,job_,*packet_,denied);scopeDenied_=true;}
        });
        if(!deniedEvent.empty())return "["+deniedEvent+"]";
        require(currentObservation.has_value(),"Native observation or exact denial");const auto& current=*currentObservation;
        const bool changed=familyFactsChanged(observed_,current);observed_=current;
        const bool refresh=observed_.picker && lease==lease_ && publication>publication_;
        const bool newPresentation=endpoint_.native([&](auto& broker){return admitRetainedFamilyPresentation(broker,job_,current,*packet_,refresh?lease_-1:lease_,publication,lease);});
        if(newPresentation){lease_=lease;publication_=publication;}
        std::string events;
        // The actual GTK gate supplies this stamp. Hidden/retired projections
        // receive observations of their retained owner, never a fresh enrollment.
        if(changed || newPresentation)events=(publication && lease==lease_)?familySeed(current,publication,lease):familyObservation(current);
        if(current.scope.now>=packet_->expires) {if(!events.empty())events+=",";events+=familyFrameEvent("expired",*packet_);}
        if(!events.empty())return "["+events+"]";
        return "[]";
    }
    bool empty(){return endpoint_.readers()==0 && endpoint_.native([](auto& b){return b.recordCount()==0 && b.charge()==0;});}
    std::string status(){return endpoint_.native([&](auto& b){Wire w;return w.begin("job").job(job_).end().text("charge",std::to_string(b.charge())).integer("records",b.recordCount()).boolean("mappedFDClosed",mappingClosed_).boolean("exportReleased",exportReleased_).boolean("producerRetired",producerRetired_).boolean("retirementPending",retirementPending_).finish();});}
    bool close() {
        endpoint_.unregisterView(popup_);
        // Never erase outstanding records merely because the popup/process closes.
        return empty();
    }
};
}
