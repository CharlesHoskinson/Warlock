#include "control_reservations.hpp"
#include <iostream>
using namespace preview::bridge;
int main(){try {
    unsigned checks=0;auto check=[&](bool ok,const char* why){require(ok,why);++checks;};
    auto refused=[&](auto operation,const char* why){bool denied=false;try{operation();}catch(const std::runtime_error&){denied=true;}check(denied,why);};
    const PreviewControlGrant owner{17,18,19,77,1};PreviewControlDelivery channel{};
    check(preview_control_delivery_init(&channel,owner),"One original native fixture grant");
    ControlReservations bank(channel,4);
    const std::string body="{\"identity\":\"fixture:A\",\"commands\":[{\"kind\":\"cancel\"}]}";
    auto a=bank.reserve(owner,2),b=bank.reserve(owner,2);
    check(a && b && bank.reserved()==4,"All queue capacity reserved before synthetic admission");
    check(!bank.reserve(owner,1),"Speculative reservation cannot spend cleanup capacity");
    auto first=bank.issue(owner,*a,1,body),second=bank.issue(owner,*b,1,body);
    check(first && second && first->ordinal==1 && second->ordinal==2,"Native globally contiguous ticket issuance");
    check(bank.reserved()==2 && bank.ticketCount()==2 && !bank.reserve(owner,1),"Issued tickets retain capacity");
    for(const auto& ticket:{*first,*second}) {
        check(bank.ownsTicket(owner,ticket.ordinal,ticket.wire),"Native owns exact packet before dispatch");
        auto changed=ticket.wire;changed.push_back(' ');
        check(!bank.ownsTicket(owner,ticket.ordinal,changed),"Changed exact transport bytes refused");
        check(preview_control_delivery_receive(&channel,owner,ticket.ordinal,ticket.wire.c_str(),ticket.wire.size())==PREVIEW_CONTROL_INVOKE,"Original C dispatcher entered once");
        check(preview_control_delivery_complete(&channel,ticket.ordinal),"Native dispatcher returned without effect success assertion");
    }
    check(!bank.release(owner,*a) && !bank.release(owner,*b),"Returned handlers cannot release unconfirmed tickets");
    check(preview_control_delivery_confirm(&channel,owner,1),"Original first receipt confirmed");
    check(bank.release(owner,*a) && !bank.release(owner,*b),"Confirmation releases only covered reservation");
    check(!bank.transportEmpty(),"Remaining reservation blocks close");
    check(!bank.ownsTicket(owner,first->ordinal,first->wire),"Released ticket loses transport authority");
    check(bank.issued()==2 && bank.reservationThrough()==2,"Releasing does not reset original counters");
    refused([&]{bank.issue(owner,*a,1,body);},"Released reservation cannot resurrect");
    check(preview_control_delivery_confirm(&channel,owner,2) && bank.release(owner,*b) && bank.transportEmpty(),"Final confirmation clears only transport reservations");
    auto c=bank.reserve(owner,1);check(c && *c==3,"Fresh reservation retains issuer namespace");
    for(const auto& malformed:std::vector<std::string>{"", "{\"identity\":\"fixture:A\",\"commands\":1}", "{\"identity\":\"fixture:A\",\"commands\":[]}", "{\"identity\":\"fixture:A\",\"commands\":[{},{}]}", "{\"identity\":\"fixture:A\",\"commands\":[null]}", "{\"identity\":\"fixture:A\",\"identity\":\"fixture:B\",\"commands\":[{}]}", "{\"identity\":\"fixture:A\",\"commands\":[{}],\"extra\":0}"}) {
        refused([&]{bank.issue(owner,*c,1,malformed);},"Malformed native-approved entry cannot consume an ordinal");
        check(bank.issued()==2 && bank.reserved()==1 && !bank.ticketCount(),"Refusal leaves all original quota intact");
    }
    std::string oversized="{\"identity\":\"fixture:A\",\"commands\":[{\"kind\":\"cancel\",\"text\":\""+std::string(3850,'X')+"\"}]}";
    // Entry fits the local bound; its complete granted envelope exceeds 4096.
    check(oversized.size()<4096,"Explicit full-envelope overflow fixture");
    refused([&]{bank.issue(owner,*c,1,oversized);},"Full granted packet byte limit before publication");
    check(bank.issued()==2 && bank.reserved()==1 && !bank.ticketCount(),"Envelope overflow consumes no ticket or ordinal");
    for(unsigned field=0;field<5;++field) {
        auto foreign=owner;
        switch(field){case 0:foreign.lifetime++;break;case 1:foreign.session++;break;case 2:foreign.frontend++;break;case 3:foreign.receiver++;break;default:foreign.epoch++;}
        refused([&]{bank.reserve(foreign,1);},"Every foreign grant field refused at reservation");
        refused([&]{bank.issue(foreign,*c,1,body);},"Every foreign grant field refused at ticket issuance");
        refused([&]{bank.release(foreign,*c);},"Every foreign grant field refused at release");
    }
    refused([&]{ControlReservations duplicate(channel,4);},"Second issuer cannot claim the original namespace");
    check(bank.release(owner,*c) && bank.transportEmpty(),"Unused quota rolls back without physical issuance");
    PreviewControlDelivery tail{};auto boundary=owner;boundary.receiver=78;
    check(preview_control_delivery_init(&tail,boundary),"Separate explicit boundary fixture grant");
    tail.prefix.delivered=UINT64_MAX-3;tail.prefix.ordered=TRUE;tail.confirmed=UINT64_MAX-3;
    ControlReservations tailBank(tail,3);auto reserve=tailBank.reserve(boundary,3);
    check(reserve && !tailBank.reserve(boundary,1),"Last three ordinals remain reserved for cleanup");
    std::optional<ControlReservations::Ticket> last;
    for(uint64_t slot=1;slot<=3;++slot){last=tailBank.issue(boundary,*reserve,slot,body);check(last && last->ordinal==UINT64_MAX-3+slot,"Reserved cleanup reaches original maximum without wrapping");}
    auto retry=tailBank.issue(boundary,*reserve,3,body);
    check(retry && retry->ordinal==UINT64_MAX && retry->wire==last->wire,"Exact retry at exhausted namespace needs no new ordinal");
    check(!tailBank.reserve(boundary,1) && tailBank.issued()==UINT64_MAX,"Exhaustion cannot admit another obligation");
    check(!tailBank.release(boundary,*reserve) && !tailBank.transportEmpty(),"Exhausted tickets still await confirmation");
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
