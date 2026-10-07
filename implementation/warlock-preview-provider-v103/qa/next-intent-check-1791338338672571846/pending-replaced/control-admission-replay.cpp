#include "imported_control_admission.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
struct Fixture {
    Binding binding{{17},{18},{19}};
    uri::Endpoint endpoint{{16,8,2,128*1024*1024},1,2,[](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{17},10};}};
    PreviewControlDelivery channel{};PreviewControlGrant grant{17,18,19,77,1};
    std::unique_ptr<ControlReservations> controls;
    std::unique_ptr<ImportedControlAdmission> admission;
    ImportedIntentLedger ledger{binding,16};
    bool low{};uint64_t through{1};
    explicit Fixture(bool small=false):low(small) {
        require(endpoint.enableDemand({{16,8,2,128*1024*1024},{17},{17},1}),"Actual shared owning demand/Broker");
        require(endpoint.registerControlView(77,binding),"Actual native receiver before subject/job enrollment");
        grant.epoch=endpoint.registeredView(77)->epoch;
        require(preview_control_delivery_init(&channel,grant),"Original actual endpoint epoch");
        controls=std::make_unique<ControlReservations>(channel,small?7:105);
        endpoint.native([&](auto& broker){admission=std::make_unique<ImportedControlAdmission>(*controls,grant,broker,16);});
    }
    Scope scope(uint64_t entry)const{return {binding,{{17},{20+entry},{1},{1},{1},{1},{1}},{17},10*entry,true,true,false,true};}
    bool pending() {
        for(uint64_t entry=1;entry<=admission->jobCount();++entry)if(!admission->retainedJob(entry))return true;
        return false;
    }
};
int main(){try {
    auto fixture=std::make_unique<Fixture>();int last=0;uint64_t events=0;char raw[128];
    while(fgets(raw,sizeof(raw),stdin)) {
        raw[strcspn(raw,"\r\n")]='\0';const std::string event=raw;
        if(event=="Low"){require(events==0,"Separate first-event small-capacity fixture");fixture=std::make_unique<Fixture>(true);last=1;}
        else {auto& f=*fixture;try {
            if(event=="CloseView"){f.endpoint.unregisterView(77);last=1;}
            else if(event=="ReplaceView"){last=f.endpoint.registerControlView(77,f.binding)?1:0;if(last)f.through=f.endpoint.registeredView(77)->epoch;}
            else if(event=="RepeatEnrollment")last=f.endpoint.registerControlView(77,f.binding)?1:0;
            else if(event=="EmptyRead") {
                GError* error=nullptr;gsize length=0;auto stream=f.endpoint.open(77,"elm-shell://preview/0000000000000000000000000000000000000000000000000000000000000001",&length,&error);
                require(!stream && error && !length && f.endpoint.readers()==0,"Empty or foreign membership cannot authorize URI reading");g_error_free(error);last=1;
            }else {
                const auto entry=event=="Retry"?1:f.admission->jobCount()+1;auto scope=f.scope(entry);auto actual=f.grant;
                if(event=="ForeignReceiver")actual.receiver++;
                else if(event=="ForeignEpoch")actual.epoch++;
                else if(event=="ForeignBinding")scope.binding.frontend.value++;
                else require(event=="Admit" || event=="Retry" || event=="ThrowAfterIssue" || event=="HideIssuedJob","Known native admission event");
                f.endpoint.nativeDemandView(77,[&](auto& queue,uri::View* view){
                    ImportedStartAttempt result;
                    if(event=="ThrowAfterIssue" || event=="HideIssuedJob") {
                        result=f.admission->admit(actual,view,queue.nativeBroker(),entry,scope,[&]()->ImportedStartAttempt{
                            auto issued=reserveImportedIntent(queue,f.ledger,entry,scope,4096,1,1,scope.now+2000000000ULL,view);
                            require(issued.native.job.has_value(),"Actual original Broker retained job before fault");
                            if(event=="ThrowAfterIssue")throw std::runtime_error("Explicit fault after actual native issuance");
                            return {};
                        });
                    }else result=f.admission->reserveIntent(queue,f.ledger,actual,view,entry,scope,4096,1,1,scope.now+2000000000ULL);
                    last=result.intent==ImportedIntentLedger::Admission::Capacity?0:1;
                    if(result.native.job) {
                        // Real Broker terminal proof; no capture/FD/native compositor.
                        const auto terminal=queue.nativeBroker().producerRefused(entry,*result.native.job);
                        require(terminal.receipts.size()==1,"Actual one-proof refusal for quota fixture");
                    }
                    // Refusal before issuer means no intent, scope or request floor.
                    if(!last && !f.ledger.find(entry)) {
                        bool absent=false;try{queue.nativeBroker().nativeScope(entry);}catch(const std::out_of_range&){absent=true;}
                        require(absent,"Transport refusal precedes native scope/job/floor enrollment");
                    }
                });
            }
        }catch(const std::runtime_error&){last=-1;}}
        ++events;auto& f=*fixture;auto view=f.endpoint.registeredView(77);
        f.endpoint.nativeDemand([&](auto& queue){
            for(const auto& record:queue.nativeBroker().inspect()) {
                require(record.job.request.value==1 && record.job.deadline==2000000000ULL+record.entry*10,
                    "Actual original job request and deadline preserved");
                require(f.ledger.original(record.entry).deadline==record.job.deadline,"Original native intent deadline preserved");
            }
            std::cout<<"{\"jobs\":"<<f.admission->jobCount()<<",\"actors\":"<<f.admission->actorCount()<<",\"records\":"<<queue.nativeBroker().recordCount()
                <<",\"intents\":"<<f.ledger.size()<<",\"slots\":"<<queue.slotCount()<<",\"members\":"<<(view?view->entries.size():0)
                <<",\"epoch\":"<<(view?view->epoch:0)<<",\"through\":"<<f.through<<",\"reserved\":"<<f.controls->reserved()<<",\"groups\":"<<f.controls->reservationThrough()
                <<",\"pending\":"<<(f.pending()?"true":"false")<<",\"last\":"<<last<<",\"charge\":"<<queue.nativeBroker().charge()<<",\"low\":"<<(f.low?"true":"false")<<"}\n";
        });
    }
    return ferror(stdin)?2:0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
