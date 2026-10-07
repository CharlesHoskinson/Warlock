#pragma once
#include "preview_wire.hpp"
#include "preview-control-delivery.h"

namespace preview::bridge {
// Native transport bookkeeping, never physical retirement authority. The caller
// reserves an obligation's verified worst-case quota before physical admission,
// chooses its stable native slot keys, and validates commands against native jobs.
// Releasing unused quota additionally requires the caller's original physical,
// terminal-proof and actor barriers; confirmation alone cannot establish them.
class ControlReservations {
    struct Row {
        uint64_t quota{},remaining{};
        std::map<uint64_t,uint64_t> slots;
    };
    PreviewControlDelivery& channel_;
    const size_t limit_;
    std::map<uint64_t,Row> rows_;
    std::map<uint64_t,std::string> tickets_;
    uint64_t issued_{},reserved_{},reservationThrough_{};
    void receiver(PreviewControlGrant actual)const {
        require(channel_.initialized && channel_.issuerClaimed &&
            preview_control_grant_equal(channel_.grant,actual),"Original native reservation receiver and grant");
    }
public:
    struct Ticket {uint64_t ordinal;std::string wire;};
    explicit ControlReservations(PreviewControlDelivery& channel,size_t capacity):channel_(channel),limit_(capacity) {
        require(capacity && channel.initialized && !channel.issuerClaimed &&
            preview_control_delivery_confirmed(&channel),"One native issuer with confirmed original prefix and explicit bounded capacity");
        issued_=channel.prefix.delivered;channel.issuerClaimed=TRUE;
    }
    ControlReservations(const ControlReservations&)=delete;
    ControlReservations& operator=(const ControlReservations&)=delete;
    uint64_t issued()const noexcept{return issued_;}
    uint64_t reserved()const noexcept{return reserved_;}
    uint64_t reservationThrough()const noexcept{return reservationThrough_;}
    size_t reservationCount()const noexcept{return rows_.size();}
    size_t ticketCount()const noexcept{return tickets_.size();}
    std::optional<uint64_t> reserve(PreviewControlGrant actual,uint64_t quota) {
        receiver(actual);require(quota,"Positive trusted native obligation quota");
        const auto remaining=UINT64_MAX-issued_;
        if(reservationThrough_==UINT64_MAX || quota>remaining || reserved_>remaining-quota ||
           quota>limit_ || tickets_.size()>limit_-quota || reserved_>limit_-quota-tickets_.size())return {};
        const auto id=reservationThrough_+1;
        // Allocate the row before publishing any counters or native admission.
        rows_.emplace(id,Row{quota,quota,{}});reserved_+=quota;reservationThrough_=id;return id;
    }
    std::optional<Ticket> issue(PreviewControlGrant actual,uint64_t reservation,
            uint64_t slot,std::string_view body) {
        receiver(actual);const auto found=rows_.find(reservation);
        require(found!=rows_.end() && slot && slot<=found->second.quota,
            "Original live obligation and bounded native slot");
        require(!body.empty() && body.size()<=4096,"Bounded native-approved command body");
        Json payload{std::string(body)};auto entry=payload.object();Json::fields(entry,{"identity","commands"});
        require(std::string_view(Json::text(entry,"identity")).size()<=512,"Bounded native-approved identity");
        auto commands=json_object_get_array_member(entry,"commands");
        require(commands && json_array_get_length(commands)==1 && JSON_NODE_HOLDS_OBJECT(json_array_get_element(commands,0)),"One native-approved command");
        auto encode=[&](uint64_t ordinal) {
            const auto& g=channel_.grant;const Binding binding{{g.lifetime},{g.session},{g.frontend}};
            auto prefix=Wire().integer("previewProtocol",3).text("kind","preview-commands")
                .begin("binding").binding(binding).end().counter("receiverEpoch",g.epoch)
                .counter("controlOrdinal",ordinal).finish();
            prefix.pop_back();return prefix+",\"entries\":["+std::string(body)+"]}";
        };
        auto& row=found->second;const auto previous=row.slots.find(slot);
        if(previous!=row.slots.end()) {
            const auto ticket=tickets_.find(previous->second);require(ticket!=tickets_.end(),"Retained original issued ticket");
            require(ticket->second==encode(ticket->first),"Exact original command bytes for native slot retry");
            return Ticket{ticket->first,ticket->second};
        }
        if(!row.remaining || !reserved_ || issued_==UINT64_MAX)return {};
        const auto ordinal=issued_+1;auto wire=encode(ordinal);require(wire.size()<=4096,"Original transport byte limit");
        // Construct the returned copy and both indexes before publishing an
        // ordinal. Allocation failure leaves no gap or abandoned reservation.
        Ticket result{ordinal,wire};auto ticket=tickets_.emplace(ordinal,std::move(wire));
        require(ticket.second,"Unique native issued control ordinal");
        try {require(row.slots.emplace(slot,ordinal).second,"Unique native reservation slot");}
        catch(...) {tickets_.erase(ticket.first);throw;}
        --row.remaining;--reserved_;issued_=ordinal;return result;
    }
    bool ownsTicket(PreviewControlGrant actual,uint64_t ordinal,std::string_view wire)const {
        receiver(actual);const auto ticket=tickets_.find(ordinal);
        return ticket!=tickets_.end() && ticket->second==wire;
    }
    bool release(PreviewControlGrant actual,uint64_t reservation) {
        receiver(actual);const auto found=rows_.find(reservation);
        require(found!=rows_.end(),"Known original reservation before quota release");
        for(const auto& [slot,ordinal]:found->second.slots) {
            (void)slot;if(ordinal>channel_.confirmed)return false;
        }
        // The trusted caller independently established physical/proof barriers.
        // This operation certifies only that no issued ticket is unconfirmed.
        reserved_-=found->second.remaining;
        for(const auto& [slot,ordinal]:found->second.slots){(void)slot;tickets_.erase(ordinal);}
        rows_.erase(found);return true;
    }
    bool transportEmpty()const noexcept {
        return rows_.empty() && tickets_.empty() && !reserved_ && preview_control_delivery_confirmed(&channel_);
    }
};
}
