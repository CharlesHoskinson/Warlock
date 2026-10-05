#pragma once
#include "client_frame.hpp"
#include "preview_delivery.hpp"

namespace preview::bridge {
enum class ClientCommand {Acquire,Cancel,Release};
inline ClientCommand decodeClientCommand(const std::string& identity,const std::string& text,const Job& expected,const std::optional<Packet>& packet) {
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
    require(Json::boolean(frame,"owned") && Json::boolean(frame,"signaled") && packet->signaled && std::string_view(Json::text(frame,"fidelity"))=="client","Actual owned client packet correlation");
    auto node=json_object_get_member(frame,"coverage");require(node && JSON_NODE_HOLDS_ARRAY(node),"Typed client coverage");auto coverage=json_node_get_array(node);
    require(json_array_get_length(coverage)==1,"Client-only coverage");auto member=json_array_get_element(coverage,0);
    require(member && json_node_get_value_type(member)==G_TYPE_STRING && std::string_view(json_node_get_string(member))=="client","Client coverage member");
    require(decimal(Json::text(frame,"expires"))==packet->expires,"Original client expiration");return ClientCommand::Release;
}
inline std::string sourceJSON(const SourceObservation& observed) {
    require(observed.kind==SourceObservation::Kind::UnqualifiedClientMain && !observed.previewEligible,"Explicit unqualified client source");
    const auto& s=observed.scope;Wire out;
    out.integer("protocolVersion",3).text("kind","preview-client-scope").begin("binding").binding(s.binding).end().counter("requestId",observed.request).begin("scope").begin("binding").binding(s.binding).end().begin("context").context(s.context).end().counter("observation",observed.observation).counter("clock",s.clock.value).counter("now",s.now).boolean("present",s.present).boolean("sourceLive",s.sourceLive).boolean("locked",s.locked).boolean("gpuReady",s.gpuReady).end().counter("maximumTransferBytes",observed.maximumTransferBytes).boolean("previewEligible",false).text("scopeKind","isolated-root-client-unqualified");return out.finish();
}
inline std::string clientSeed(const SourceObservation& observed,uint64_t publication,uint64_t lease) {
    require(publication && lease,"Admitted native client publication and lease");
    Wire seed;auto front=seed.text("kind","source-seed").counter("publication",publication).counter("lease",lease).text("identity","family:"+std::to_string(observed.scope.context.incarnation.value)).text("title","Client content").text("application","Native client").finish();
    front.pop_back();return front+",\"source\":"+sourceJSON(observed)+"}";
}
inline std::string clientObservation(const SourceObservation& observed) {
    const auto& s=observed.scope;Wire wire;
    return wire.text("kind","event").text("identity","family:"+std::to_string(s.context.incarnation.value)).begin("event").text("kind","observe").begin("scope").begin("binding").binding(s.binding).end().begin("context").context(s.context).end().counter("observation",observed.observation).counter("clock",s.clock.value).counter("now",s.now).boolean("present",s.present).boolean("sourceLive",s.sourceLive).boolean("locked",s.locked).boolean("gpuReady",s.gpuReady).end().end().finish();
}
inline bool clientFactsChanged(const SourceObservation& old,const SourceObservation& current) {
    const auto& a=old.scope;const auto& b=current.scope;
    return a.context!=b.context || a.present!=b.present || a.sourceLive!=b.sourceLive || a.locked!=b.locked || a.gpuReady!=b.gpuReady;
}
inline bool admitClientObservation(Broker& broker,const Job& original,const SourceObservation& observed) {
    const auto& s=observed.scope;
    require(observed.kind==SourceObservation::Kind::UnqualifiedClientMain && !observed.previewEligible &&
        s.binding==original.binding && s.context.lifetime==original.context.lifetime && s.context.incarnation==original.context.incarnation && s.clock==original.clock,
        "Same own typed client observation authority");
    return broker.observe(1,s,observed.maximumTransferBytes);
}
inline void packetJSON(Wire& wire,const Packet& packet) {
    wire.begin("job").job(packet.job).end().text("handle",uri::encode(packet.token).substr(std::string_view("elm-shell://preview/").size())).boolean("owned",true).boolean("signaled",packet.signaled).text("fidelity","client").array("coverage").element("client").endArray().counter("expires",packet.expires);
}
inline std::string frameEvent(const char* kind,const Packet& packet) {
    Wire wire;wire.text("kind","event").text("identity","family:"+std::to_string(packet.job.context.incarnation.value)).begin("event").text("kind",kind).begin("frame");packetJSON(wire,packet);return wire.end().end().finish();
}
// One owning allocator, not a second frontend policy. Native demand reserves
// the original job; an exact actual Elm Acquire starts physical capture.
class ClientProducer {
    Native& native_;
    SourceObservation observed_;
    fd::Header header_{};
    bool haveHeader_{},attempted_{},cleanup_{},exportReleased_{},producerRetired_{};
    uri::Endpoint endpoint_;
    uint64_t popup_,lease_;
    Job job_;
    std::optional<ClientCapture> capture_;
    std::optional<Packet> packet_;
    fd::Mapped* mapping_{};
    std::string initial_;
    bool retire() {
        return endpoint_.native([&](Broker& broker) {
            if(!cleanup_ || !packet_ || !broker.consumerComplete(1,job_))return false;
            require(mapping_!=nullptr,"Owned client mapping pending retirement");
            require(mapping_->close(),"Physical client mapping and FD close");
            if(!exportReleased_) {require(releaseClient(native_,*capture_,header_[fd::Transfer]),"Exact client export release");exportReleased_=true;}
            if(!producerRetired_) {require(retireClient(native_),"Original client producer retirement");producerRetired_=true;}
            auto retired=broker.destroy(1,job_);require(retired.status==Result::Status::Complete && !retired.receipts.empty() && broker.charge()==0,"Physical client Broker proof after retirement");mapping_=nullptr;return true;
        });
    }
public:
    ClientProducer(Native& native,uint64_t popup,uint64_t subject,uint64_t publication,uint64_t lease):
        native_(native),observed_(native.clientScope({subject})),
        endpoint_({1,4,1,observed_.maximumTransferBytes},1,1,[this](uint64_t)->std::optional<uri::NativeTime>{return haveHeader_?native_.time(header_):std::nullopt;}),popup_(popup),lease_(lease) {
        require(popup && publication && lease && observed_.kind==SourceObservation::Kind::UnqualifiedClientMain && !observed_.previewEligible,"Trusted qualification source/stamp");
        const auto& scope=observed_.scope;require(scope.binding==native_.binding() && scope.present && scope.sourceLive && !scope.locked && scope.gpuReady,"Own live native client scope");
        require(scope.now<=UINT64_MAX-2000000000ULL,"Original client deadline representable");
        require(endpoint_.enableDemand({{1,4,1,observed_.maximumTransferBytes},scope.binding.lifetime,scope.clock,1}),"One physical native demand policy");
        require(endpoint_.nativeDemand([&](auto& q){return q.observe({1,lease,scope,{lease},observed_.maximumTransferBytes,true}).accepted;}),"Own native client demand");
        auto attempt=endpoint_.nativeDemand([&](auto& q){return q.start(1,scope.now+2000000000ULL);});require(attempt.status==demand::Attempt::Status::Started && attempt.job.has_value(),"Original native job reservation");job_=*attempt.job;
        require(endpoint_.registerView(popup,scope.binding,{1}),"Actual native WebKit receiver");
        auto front=clientSeed(observed_,publication,lease);
        Wire request;request.text("kind","event").text("identity","family:"+std::to_string(subject)).begin("event").text("kind","request").begin("trigger").begin("binding").binding(job_.binding).end().begin("context").context(job_.context).end().counter("origin",job_.origin.value).counter("clock",job_.clock.value).counter("deadline",job_.deadline).end().end();
        initial_="["+front+","+request.finish()+"]";
    }
    ClientProducer(const ClientProducer&)=delete;ClientProducer& operator=(const ClientProducer&)=delete;
    uri::Endpoint& endpoint(){return endpoint_;}
    const std::string& initial()const{return initial_;}
    const Job& job()const{return job_;}
    std::string command(const std::string& identity,const std::string& text) {
        const auto command=decodeClientCommand(identity,text,job_,packet_);
        if(command==ClientCommand::Acquire) {
            require(!attempted_ && !cleanup_,"Single original physical client capture");attempted_=true;
            capture_=captureClient(native_,observed_,job_.deadline);auto received=native_.query(fd::Get,capture_->request,job_.context.incarnation.value);
            require(received && received->rights.size()==1 && clientFrameMatches(received->words,*capture_),"Exact owned client descriptor");header_=received->words;haveHeader_=true;
            auto mapping=std::make_unique<fd::Mapped>(std::move(received->rights.front()),header_,observed_.maximumTransferBytes,fd::SourcePlane::ClientMain);mapping_=mapping.get();std::unique_ptr<const Buffer> payload=std::move(mapping);
            auto offered=endpoint_.native([&](auto& b){return b.allocate(1,job_,payload,header_[fd::Expires]);});require(offered.receipts.size()==1 && offered.receipts.front().packet && !payload,"Physical client payload adopted");
            const auto before=*offered.receipts.front().packet;auto ready=endpoint_.native([&](auto& b){return b.producerComplete(1,job_);});require(ready.receipts.size()==1 && ready.receipts.front().packet,"Completed immutable client copy");packet_=*ready.receipts.front().packet;
            // Readiness concerns encoded immutable storage, never hardware presentation.
            return "["+frameEvent("offer",before)+","+frameEvent("fence",*packet_)+"]";
        }
        if(command==ClientCommand::Cancel) {
            endpoint_.native([&](auto& b){return b.cancel(1,job_.binding,job_);});cleanup_=true;
            if(!attempted_)endpoint_.native([&](auto& b){return b.producerRefused(1,job_);});
        } else {endpoint_.native([&](auto& b){return b.release(1,job_.binding,job_,packet_->token);});cleanup_=true;}
        if(mapping_)retire();
        return "[]";
    }
    std::string poll(uint64_t publication,uint64_t lease) {
        if(mapping_ && cleanup_)retire();
        if(!packet_ || cleanup_)return "[]";
        // Original native source clock, not a frontend timer or renewed deadline.
        const auto current=endpoint_.native([&](auto& broker){
            auto fresh=native_.clientScope(job_.context.incarnation);
            require(admitClientObservation(broker,job_,fresh),"Coherent own client authority update");return fresh;
        });
        const bool changed=clientFactsChanged(observed_,current);observed_=current;
        std::string events;
        // The actual GTK gate supplies this stamp. Hidden/retired projections
        // receive observations of their retained owner, never a fresh enrollment.
        if(changed)events=(publication && lease==lease_)?clientSeed(current,publication,lease):clientObservation(current);
        if(current.scope.now>=packet_->expires) {if(!events.empty())events+=",";events+=frameEvent("expired",*packet_);}
        if(!events.empty())return "["+events+"]";
        return "[]";
    }
    bool empty(){return endpoint_.readers()==0 && endpoint_.native([](auto& b){return b.recordCount()==0 && b.charge()==0;});}
    bool close() {
        endpoint_.unregisterView(popup_);
        // Never erase outstanding records merely because the popup/process closes.
        return empty();
    }
};
}
