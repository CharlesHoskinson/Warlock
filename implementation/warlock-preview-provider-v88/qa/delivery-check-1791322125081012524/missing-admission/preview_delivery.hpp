#pragma once
#include "preview_uri.hpp"
#include "preview_wire.hpp"

namespace preview::bridge {
// No second journal: Broker retains exact terminal proofs until final Ack.
// One native-enrolled popup receives only explicitly admitted own subjects.
class ReceiptDelivery {
    friend class ImportedClients;
    uri::Endpoint& endpoint_;
    Binding owner_;
    uint64_t popup_,epoch_;
    std::map<uint64_t,Id<Incarnation>> subjects_;
    bool canForgetRetired(const uri::Endpoint& endpoint,uint64_t popup,const uri::View* registered,uint64_t entry,const Binding& owner,Id<Incarnation> subject)const {
        if(&endpoint!=&endpoint_ || popup!=popup_ || owner!=owner_ || !registered || registered->binding!=owner_ || registered->epoch!=epoch_)return false;
        const auto record=subjects_.find(entry);
        return record==subjects_.end() || record->second==subject;
    }
    void forgetRetired(uint64_t entry)noexcept {subjects_.erase(entry);}
    void view(uint64_t popup,const uri::View* registered) const {
        require(popup && popup==popup_,"Exact native popup receiver");
        require(registered && registered->binding==owner_ && registered->epoch==epoch_,"Current native receiver enrollment");
    }
    void admit(Broker& broker,const uri::View& registered) {
        require(!registered.entries.empty() && registered.entries.size()<=broker.limits().entries,"Bounded native receipt subjects");
        auto joined=subjects_;
        std::set<uint64_t> incarnations;
        for(const auto& [entry,incarnation]:subjects_) {
            (void)incarnation;require(registered.entries.contains(entry),"Retain original receipt subjects");
        }
        for(auto entry:registered.entries) {
            const auto& scope=broker.nativeScope(entry);
            require(entry && scope.binding==owner_ && scope.context.lifetime==owner_.lifetime && scope.context.incarnation.value,"Native receipt subject binding");
            require(incarnations.insert(scope.context.incarnation.value).second,"Distinct native receipt incarnations");
            auto existing=joined.find(entry);
            require(existing==joined.end() || existing->second==scope.context.incarnation,"Immutable native receipt incarnation");
            joined.emplace(entry,scope.context.incarnation);
        }
        require(joined.size()<=broker.limits().entries,"Bounded retained native receipt subjects");
        subjects_=std::move(joined);
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
    size_t subjectCount()const noexcept{return subjects_.size();}
    bool ownsReceiver(uint64_t popup)const {
        return endpoint_.nativeView(popup,[&](Broker&,const uri::View* registered) {
            view(popup,registered);return true;
        });
    }
    ReceiptDelivery(uri::Endpoint& endpoint,Binding owner,uint64_t popup):endpoint_(endpoint),owner_(owner),popup_(popup) {
        endpoint_.nativeView(popup,[&](Broker& broker,const uri::View* registered) {
            require(popup && registered && registered->binding==owner,"Native enrolled popup binding");epoch_=registered->epoch;
            admit(broker,*registered);
        });
    }
    ReceiptDelivery(const ReceiptDelivery&)=delete;ReceiptDelivery& operator=(const ReceiptDelivery&)=delete;
    // Native caller supplies only its already enrolled receiver identity.
    // Membership and incarnations come from actual own native view/scopes;
    // no UI fields authorize subjects, reset the journal or replace its epoch.
    bool extendSubjects(uint64_t popup) {
        return endpoint_.nativeView(popup,[&](Broker& broker,const uri::View* registered) {
            (void)broker;view(popup,registered);return true;
        });
    }
    std::vector<std::string> pending(uint64_t popup) {
        return endpoint_.nativeView(popup,[&](Broker& broker,const uri::View* registered) {
            view(popup,registered);
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
        Json message(command);auto object=message.object();Json::fields(object,{"kind","job","sequence"});
        require(std::string_view(Json::text(object,"kind"))=="acknowledge","Only terminal acknowledgement accepted here");
        auto job=decodeJob(Json::child(object,"job"));const auto sequence=message.counter("sequence");
        require(job.binding==owner_ && identity=="family:"+std::to_string(job.context.incarnation.value),"Native receipt acknowledgement family and own binding");
        return endpoint_.nativeView(popup,[&](Broker& broker,const uri::View* registered) {
            view(popup,registered);
            auto entry=broker.owningEntry(job);if(!entry)return false;
            auto subject=subjects_.find(*entry);if(subject==subjects_.end() || subject->second!=job.context.incarnation)return false;
            return broker.acknowledge(*entry,owner_,job,{sequence});
        });
    }
};
}
