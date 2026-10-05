#pragma once
#include "preview_uri.hpp"
#include "preview_wire.hpp"

namespace preview::bridge {
// No second journal: Broker retains exact terminal proofs until final Ack.
// One native-enrolled popup receives only its own fixed family subjects.
class ReceiptDelivery {
    uri::Endpoint& endpoint_;
    Binding owner_;
    uint64_t popup_,epoch_;
    std::map<uint64_t,Id<Incarnation>> subjects_;
    void view(uint64_t popup) const {
        require(popup && popup==popup_,"Exact native popup receiver");
        auto registered=endpoint_.registeredView(popup);
        require(registered && registered->binding==owner_ && registered->epoch==epoch_,"Current native receiver enrollment");
    }
    static std::string encode(const Receipt& receipt) {
        Wire out;out.text("kind","event").text("identity","family:"+std::to_string(receipt.job.context.incarnation.value)).begin("event").text("kind","receipt").counter("sequence",receipt.sequence.value).begin("event");
        switch(receipt.kind) {
            case Receipt::Kind::Refused:out.text("kind","refused").begin("job").job(receipt.job).end();break;
            case Receipt::Kind::Cancelled:out.text("kind","cancelled").begin("job").job(receipt.job).end();break;
            case Receipt::Kind::Released: {
                require(receipt.packet && receipt.packet->job==receipt.job,"Exact native released packet");const auto& packet=*receipt.packet;
                const auto handle=uri::encode(packet.token).substr(std::string_view("elm-shell://preview/").size());
                out.text("kind","released").begin("frame").begin("job").job(packet.job).end().text("handle",handle).boolean("owned",true).boolean("signaled",packet.signaled).text("fidelity",packet.fidelity==Packet::Fidelity::Family?"family":"client").array("coverage");
                const std::array<const char*,4> names{"client","decoration","modal","popup"};for(size_t i=0;i<names.size();++i)if(packet.coverage&(1<<i))out.element(names[i]);
                out.endArray().counter("expires",packet.expires).end();break;
            }
            default:require(false,"Only native terminal journal receipts are projected");
        }
        out.end().end();auto encoded=out.finish();require(encoded.size()<=4096,"Bounded native receipt wire");return encoded;
    }
public:
    ReceiptDelivery(uri::Endpoint& endpoint,Binding owner,uint64_t popup):endpoint_(endpoint),owner_(owner),popup_(popup) {
        auto registered=endpoint_.registeredView(popup);require(registered && registered->binding==owner,"Native enrolled popup binding");epoch_=registered->epoch;
        endpoint_.native([&](Broker& broker) {
            require(registered->entries.size()<=broker.limits().entries,"Bounded native receipt subjects");
            for(auto entry:registered->entries) {const auto& scope=broker.nativeScope(entry);require(scope.binding==owner && scope.context.lifetime==owner.lifetime,"Native receipt subject binding");subjects_.emplace(entry,scope.context.incarnation);}
        });
    }
    ReceiptDelivery(const ReceiptDelivery&)=delete;ReceiptDelivery& operator=(const ReceiptDelivery&)=delete;
    std::vector<std::string> pending(uint64_t popup) {
        view(popup);return endpoint_.native([&](Broker& broker) {
            std::vector<std::string> wires;
            for(const auto& record:broker.inspect()) {
                auto subject=subjects_.find(record.entry);
                if(!record.terminal || subject==subjects_.end() || record.job.binding!=owner_ || record.job.context.incarnation!=subject->second)continue;
                for(const auto& proof:record.proofs) {
                    require(proof.entry==record.entry && proof.job==record.job,"Native journal proof correlation");wires.push_back(encode(proof));
                }
            }
            return wires;
        });
    }
    bool acknowledge(uint64_t popup,const std::string& identity,const std::string& command) {
        view(popup);Json message(command);auto object=message.object();Json::fields(object,{"kind","job","sequence"});
        require(std::string_view(Json::text(object,"kind"))=="acknowledge","Only terminal acknowledgement accepted here");
        auto job=decodeJob(Json::child(object,"job"));const auto sequence=message.counter("sequence");
        require(job.binding==owner_ && identity=="family:"+std::to_string(job.context.incarnation.value),"Native receipt acknowledgement family and own binding");
        return endpoint_.native([&](Broker& broker) {
            auto entry=broker.owningEntry(job);if(!entry)return false;
            auto subject=subjects_.find(*entry);if(subject==subjects_.end() || subject->second!=job.context.incarnation)return false;
            return broker.acknowledge(*entry,owner_,job,{sequence});
        });
    }
};
}
