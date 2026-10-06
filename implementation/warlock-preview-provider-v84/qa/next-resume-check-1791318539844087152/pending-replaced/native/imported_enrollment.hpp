#pragma once
#include "imported_admission.hpp"
#include "preview_uri.hpp"

namespace preview::bridge {
// Called only inside Endpoint.nativeDemandView with a native-owned observation.
// This never extends ReceiptDelivery: its subject admission remains explicit.
inline bool importedReceiver(const uri::View* view,Binding owner,uint64_t epoch) {
    return view && epoch && view->epoch==epoch && view->binding==owner;
}
inline ImportedStartAttempt reserveImportedIntent(demand::Coordinator& queue,
        ImportedIntentLedger& ledger,uint64_t entry,const Scope& scope,uint64_t cost,
        uint64_t publication,uint64_t lease,uint64_t deadline,uri::View* view=nullptr) {
    const auto intent=ledger.remember(entry,{scope.binding,scope.context.incarnation,scope.clock,publication,lease,deadline},scope.now);
    if(intent!=ImportedIntentLedger::Admission::Admitted)return {intent,{},"[]"};
    if(!queue.observe({entry,lease,scope,{lease},cost,true}).accepted)return {intent,{},"[]"};
    if(view) {
        // Scope enrollment above can fail without admitting a new receiver
        // subject. Validate the complete union before publishing membership.
        auto joined=view->entries;joined.insert(entry);
        if(joined.size()>queue.nativeBroker().limits().entries)throw std::invalid_argument("Bounded imported receiver subjects");
        std::set<uint64_t> subjects;
        for(auto id:joined) {
            const auto& s=queue.nativeBroker().nativeScope(id);
            if(!id || s.binding!=view->binding || s.context.lifetime!=view->binding.lifetime ||
               !s.context.incarnation.value || !subjects.insert(s.context.incarnation.value).second)
                throw std::invalid_argument("Distinct own native imported receiver subjects");
        }
        view->entries=std::move(joined);
    }
    return {intent,queue.start(entry,ledger.original(entry).deadline),"[]"};
}
}
