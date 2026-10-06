#include "imported-clients.h"
#include "imported_clients.hpp"
#include "imported_subjects.hpp"
using namespace preview;using namespace preview::bridge;
namespace {
WarlockImportedAdmission admissionOf(const ImportedStartAttempt& attempted) {
    switch(attempted.intent) {
        case ImportedIntentLedger::Admission::Capacity:return WARLOCK_IMPORTED_CAPACITY;
        case ImportedIntentLedger::Admission::Conflict:return WARLOCK_IMPORTED_CONFLICT;
        case ImportedIntentLedger::Admission::Expired:return WARLOCK_IMPORTED_EXPIRED;
        case ImportedIntentLedger::Admission::Invalid:return WARLOCK_IMPORTED_INVALID;
        case ImportedIntentLedger::Admission::Admitted:break;
    }
    switch(attempted.native.status) {
        case demand::Attempt::Status::Started:return WARLOCK_IMPORTED_STARTED;
        case demand::Attempt::Status::NotReady:return WARLOCK_IMPORTED_WAITING;
        case demand::Attempt::Status::Capacity:return WARLOCK_IMPORTED_CAPACITY;
        case demand::Attempt::Status::Exhausted:return WARLOCK_IMPORTED_EXHAUSTED;
        case demand::Attempt::Status::NativeRejected:return WARLOCK_IMPORTED_NATIVE_REJECTED;
    }
    return WARLOCK_IMPORTED_INVALID;
}
}
struct WarlockImportedClients {
    ImportedClients value;
    Native& native;
    uint64_t popup;
    uint64_t epoch{};
    bool dynamic{};
    GThread* thread{g_thread_self()};
    ImportedSubjects subjects;
    std::optional<RetirementJournal> retirementJournal;
    std::string initial;
    WarlockImportedClients(Native& native,uint64_t popup,uint64_t first,uint64_t second,uint64_t publication,uint64_t lease):
        value(native),native(native),popup(popup),subjects(2,{{first},{second}}) {
        auto a=value.start(1,{first},publication,lease);auto b=value.start(2,{second},publication,lease);
        require(a.size()>2 && b.size()>2 && a.front()=='[' && a.back()==']' && b.front()=='[' && b.back()==']',"Actual shared imported seed/request arrays");
        a.pop_back();initial=a+","+b.substr(1);
        require(value.endpoint().registerView(popup,native.binding(),{1,2}),"Actual GTK receiver for shared imported ownership");
        epoch=value.endpoint().registeredView(popup)->epoch;
        retirementJournal.emplace(native.binding(),popup,epoch);
    }
    WarlockImportedClients(Native& native,uint64_t popup,uint64_t first,uint64_t publication,uint64_t lease):
        value(native,256),native(native),popup(popup),dynamic(true),subjects(256,{{first}}) {
        initial=value.start(1,{first},publication,lease);
        require(value.endpoint().registerView(popup,native.binding(),{1}),"Actual dynamic GTK imported receiver");
        epoch=value.endpoint().registeredView(popup)->epoch;
        retirementJournal.emplace(native.binding(),popup,epoch);
    }
    uint64_t entry(const char* identity)const {
        require(identity,"Typed own imported family identity");
        for(const auto& [entry,subject]:subjects.active())if(std::string_view(identity)=="family:"+std::to_string(subject.value))return entry;
        throw std::runtime_error("Foreign imported family identity");
    }
    WarlockImportedAdmission enroll(uint64_t receiver,uint64_t subject,uint64_t publication,uint64_t lease,std::string& events,std::string* feedback=nullptr,bool laterIntent=false) {
        require(dynamic && thread==g_thread_self() && receiver==popup && subject && publication && lease,"Own trusted GTK dynamic imported enrollment");
        const auto binding=native.binding();
        // Refuse replacement before even retaining a new C actor identity.
        value.endpoint().nativeView(popup,[&](auto&,const uri::View* view) {
            require(importedReceiver(view,binding,epoch),"Original dynamic imported receiver epoch");
        });
        auto owned=subjects.find({subject});
        std::optional<ImportedSubjects::Pending> staged;
        if(!owned) {
            if(subjects.size()>=256)return WARLOCK_IMPORTED_CAPACITY;
            if(subjects.exhausted())return WARLOCK_IMPORTED_EXHAUSTED;
            staged.emplace(subjects.stage({subject}));owned=staged->entry;
        }
        const uint64_t entry=*owned;
        const auto original=value.originalIntent(entry);
        if(original && (original->publication!=publication || original->lease!=lease) && !feedback)return WARLOCK_IMPORTED_CONFLICT;
        if(value.hasJob(entry))return WARLOCK_IMPORTED_RETAINED;
        auto attempted=laterIntent?value.tryNextUnissuedAtReceiver(popup,epoch,entry,{subject},publication,lease):
            value.tryStartAtReceiver(popup,epoch,entry,{subject},publication,lease);
        if(staged && (value.originalIntent(entry) || value.hasJob(entry)))subjects.commit(std::move(*staged));
        events=std::move(attempted.events);
        if(feedback)*feedback=std::move(attempted.feedback);
        return admissionOf(attempted);
    }
};
namespace {
template<class F> gboolean output(WarlockImportedClients* owner,char** result,GError** error,F call) {
    if(result)*result=nullptr;
    try {require(owner && result && owner->thread==g_thread_self(),"Own creator-thread shared imported bridge output");*result=g_strdup(call(*owner).c_str());return TRUE;}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
}
extern "C" WarlockImportedClients* warlock_imported_clients_open(void* transport,gpointer popup,guint64 first,guint64 second,guint64 publication,guint64 lease,char** initial,void** endpoint,GError** error) {
    if(initial)*initial=nullptr;
    if(endpoint)*endpoint=nullptr;
    try {
        require(transport && popup && first && second && first!=second && publication && lease && initial && endpoint,"Trusted shared imported GTK enrollment");
        auto owner=std::make_unique<WarlockImportedClients>(*static_cast<Native*>(transport),reinterpret_cast<uint64_t>(popup),first,second,publication,lease);
        *initial=g_strdup(owner->initial.c_str());*endpoint=&owner->value.endpoint();return owner.release();
    }catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return nullptr;}
}
extern "C" WarlockImportedClients* warlock_imported_clients_open_dynamic(void* transport,gpointer popup,guint64 first,guint64 publication,guint64 lease,char** initial,void** endpoint,GError** error) {
    if(initial)*initial=nullptr;
    if(endpoint)*endpoint=nullptr;
    try {
        require(transport && popup && first && publication && lease && initial && endpoint,"Trusted dynamic GTK imported enrollment");
        auto owner=std::make_unique<WarlockImportedClients>(*static_cast<Native*>(transport),reinterpret_cast<uint64_t>(popup),first,publication,lease);
        *initial=g_strdup(owner->initial.c_str());*endpoint=&owner->value.endpoint();return owner.release();
    }catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return nullptr;}
}
extern "C" gboolean warlock_imported_clients_enroll(WarlockImportedClients* owner,gpointer popup,guint64 subject,guint64 publication,guint64 lease,WarlockImportedAdmission* admission,char** events,GError** error) {
    if(admission)*admission=WARLOCK_IMPORTED_INVALID;
    return output(owner,events,error,[&](auto& o) {
        require(admission && popup,"Typed dynamic imported result receiver");
        std::string result="[]";*admission=o.enroll(reinterpret_cast<uint64_t>(popup),subject,publication,lease,result);return result;
    });
}
extern "C" gboolean warlock_imported_clients_command(WarlockImportedClients* owner,const char* identity,const char* command,char** events,GError** error) {
    return output(owner,events,error,[&](auto& o){require(command,"Typed imported command text");return o.value.command(o.entry(identity),identity,command);});
}
extern "C" gboolean warlock_imported_clients_poll(WarlockImportedClients* owner,const char* identity,char** events,GError** error) {
    return output(owner,events,error,[&](auto& o){return o.value.poll(o.entry(identity));});
}
extern "C" gboolean warlock_imported_clients_retirement_state(WarlockImportedClients* owner,const char* identity,char** facts,GError** error) {
    return output(owner,facts,error,[&](auto& o) {
        require(o.thread==g_thread_self(),"Own imported retirement creator thread");
        return encodeIncarnationRetirement(o.value.retirementAtReceiver(o.popup,o.epoch,o.entry(identity)));
    });
}
extern "C" gboolean warlock_imported_clients_retire_native(WarlockImportedClients* owner,void* delivery,gpointer popup,const char* identity,gboolean* retired,char** facts,GError** error) {
    if(retired)*retired=FALSE;
    return output(owner,facts,error,[&](auto& o) {
        require(delivery && popup && reinterpret_cast<uint64_t>(popup)==o.popup && retired,"Own native actor retirement receiver and result");
        auto result=o.value.retireAtReceiver(o.popup,o.epoch,o.entry(identity),*static_cast<ReceiptDelivery*>(delivery),o.subjects);
        *retired=result.has_value();return result.value_or("null");
    });
}
extern "C" gboolean warlock_imported_clients_actor_counts(WarlockImportedClients* owner,void* delivery,char** facts,GError** error) {
    return output(owner,facts,error,[&](auto& o){require(delivery,"Own native actor count journal");return o.value.actorCounts(o.popup,*static_cast<ReceiptDelivery*>(delivery),o.subjects);});
}
extern "C" gboolean warlock_imported_clients_retirement_observe(WarlockImportedClients* owner,gpointer popup,const char* identity,char** events,GError** error) {
    return output(owner,events,error,[&](auto& o) {
        require(popup && reinterpret_cast<uint64_t>(popup)==o.popup && o.retirementJournal,
            "Own original retained retirement observation receiver");
        auto observed=o.value.observeRetirementForDelivery(o.popup,o.epoch,o.entry(identity),*o.retirementJournal);
        return observed?"["+*observed+"]":std::string("[]");
    });
}
extern "C" gboolean warlock_imported_clients_retirement_pending(WarlockImportedClients* owner,void* delivery,gpointer popup,char** events,GError** error) {
    return output(owner,events,error,[&](auto& o) {
        require(delivery && popup && reinterpret_cast<uint64_t>(popup)==o.popup && o.retirementJournal,
            "Own original retained retirement delivery receiver");
        return o.value.pendingRetirementDelivery(o.popup,o.epoch,*static_cast<ReceiptDelivery*>(delivery),*o.retirementJournal);
    });
}
extern "C" gboolean warlock_imported_clients_retirement_control(WarlockImportedClients* owner,void* delivery,gpointer popup,const char* identity,const char* command,char** events,GError** error) {
    return output(owner,events,error,[&](auto& o) {
        require(delivery && popup && reinterpret_cast<uint64_t>(popup)==o.popup && identity && command && o.retirementJournal,
            "Own original retirement control receiver");
        Json message(command);const std::string_view kind=Json::text(message.object(),"kind");
        auto& receipt=*static_cast<ReceiptDelivery*>(delivery);
        if(kind=="retire-ready") {
            auto result=o.value.retireAtReceiver(o.popup,o.epoch,o.entry(identity),receipt,o.subjects,
                &*o.retirementJournal,command);
            return result?"["+*result+"]":std::string("[]");
        }
        require(kind=="retire-delivery-ack","Closed retirement control union");
        require(o.value.acknowledgeRetirementDelivery(o.popup,o.epoch,receipt,*o.retirementJournal,command),
            "Contiguous retirement processing acknowledgment");
        return o.value.pendingRetirementDelivery(o.popup,o.epoch,receipt,*o.retirementJournal);
    });
}
extern "C" gboolean warlock_imported_clients_poll_at(WarlockImportedClients* owner,const char* identity,guint64 publication,guint64 lease,char** events,GError** error) {
    return output(owner,events,error,[&](auto& o){return o.value.poll(o.entry(identity),publication,lease);});
}
extern "C" gboolean warlock_imported_clients_resume(WarlockImportedClients* owner,const char* identity,guint64 publication,guint64 lease,char** events,GError** error) {
    return output(owner,events,error,[&](auto& o){require(o.thread==g_thread_self(),"Own imported resume creator thread");return o.value.resumeAtReceiver(o.popup,o.epoch,o.entry(identity),publication,lease).events;});
}
extern "C" gboolean warlock_imported_clients_resume_at(WarlockImportedClients* owner,const char* identity,guint64 publication,guint64 lease,WarlockImportedAdmission* admission,char** events,GError** error) {
    if(admission)*admission=WARLOCK_IMPORTED_INVALID;
    return output(owner,events,error,[&](auto& o){
        require(admission && o.thread==g_thread_self(),"Typed own imported resume creator thread");
        auto result=o.value.resumeAtReceiver(o.popup,o.epoch,o.entry(identity),publication,lease);
        switch(result.intent) {
            case ImportedIntentLedger::Admission::Invalid:*admission=WARLOCK_IMPORTED_INVALID;break;
            case ImportedIntentLedger::Admission::Expired:*admission=WARLOCK_IMPORTED_EXPIRED;break;
            case ImportedIntentLedger::Admission::Conflict:*admission=WARLOCK_IMPORTED_CONFLICT;break;
            case ImportedIntentLedger::Admission::Capacity:*admission=WARLOCK_IMPORTED_CAPACITY;break;
            case ImportedIntentLedger::Admission::Admitted:
                switch(result.native.status) {
                    case demand::Attempt::Status::Started:*admission=WARLOCK_IMPORTED_STARTED;break;
                    case demand::Attempt::Status::Capacity:*admission=WARLOCK_IMPORTED_CAPACITY;break;
                    case demand::Attempt::Status::NotReady:*admission=WARLOCK_IMPORTED_WAITING;break;
                    case demand::Attempt::Status::Exhausted:*admission=WARLOCK_IMPORTED_EXHAUSTED;break;
                    case demand::Attempt::Status::NativeRejected:*admission=WARLOCK_IMPORTED_NATIVE_REJECTED;break;
                }
        }
        return result.events;
    });
}
extern "C" gboolean warlock_imported_clients_enroll_feedback(WarlockImportedClients* owner,gpointer popup,guint64 subject,guint64 publication,guint64 lease,WarlockImportedAdmission* admission,char** events,char** feedback,GError** error) {
    if(admission)*admission=WARLOCK_IMPORTED_INVALID;
    if(events)*events=nullptr;
    if(feedback)*feedback=nullptr;
    try {
        require(owner && popup && admission && events && feedback && events!=feedback,"Distinct typed imported feedback outputs");
        std::string issued="[]",local="[]";
        *admission=owner->enroll(reinterpret_cast<uint64_t>(popup),subject,publication,lease,issued,&local);
        *events=g_strdup(issued.c_str());*feedback=g_strdup(local.c_str());return TRUE;
    }catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
extern "C" gboolean warlock_imported_clients_resume_feedback(WarlockImportedClients* owner,const char* identity,guint64 publication,guint64 lease,WarlockImportedAdmission* admission,char** events,char** feedback,GError** error) {
    if(admission)*admission=WARLOCK_IMPORTED_INVALID;
    if(events)*events=nullptr;
    if(feedback)*feedback=nullptr;
    try {
        require(owner && admission && events && feedback && events!=feedback && owner->thread==g_thread_self(),"Own creator and distinct typed imported feedback outputs");
        auto attempted=owner->value.resumeAtReceiver(owner->popup,owner->epoch,owner->entry(identity),publication,lease);
        *admission=admissionOf(attempted);*events=g_strdup(attempted.events.c_str());*feedback=g_strdup(attempted.feedback.c_str());return TRUE;
    }catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
extern "C" gboolean warlock_imported_clients_enroll_next_feedback(WarlockImportedClients* owner,gpointer popup,guint64 subject,guint64 publication,guint64 lease,WarlockImportedAdmission* admission,char** events,char** feedback,GError** error) {
    if(admission)*admission=WARLOCK_IMPORTED_INVALID;
    if(events)*events=nullptr;
    if(feedback)*feedback=nullptr;
    try {
        require(owner && popup && admission && events && feedback && events!=feedback,"Distinct explicit later imported intent outputs");
        std::string issued="[]",local="[]";
        *admission=owner->enroll(reinterpret_cast<uint64_t>(popup),subject,publication,lease,issued,&local,true);
        *events=g_strdup(issued.c_str());*feedback=g_strdup(local.c_str());return TRUE;
    }catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
extern "C" gboolean warlock_imported_clients_resume_next_feedback(WarlockImportedClients* owner,const char* identity,guint64 publication,guint64 lease,WarlockImportedAdmission* admission,char** events,char** feedback,GError** error) {
    if(admission)*admission=WARLOCK_IMPORTED_INVALID;
    if(events)*events=nullptr;
    if(feedback)*feedback=nullptr;
    try {
        require(owner && admission && events && feedback && events!=feedback && owner->thread==g_thread_self(),"Own creator and distinct explicit later resume outputs");
        auto attempted=owner->value.resumeNextAtReceiver(owner->popup,owner->epoch,owner->entry(identity),publication,lease);
        *admission=admissionOf(attempted);*events=g_strdup(attempted.events.c_str());*feedback=g_strdup(attempted.feedback.c_str());return TRUE;
    }catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
extern "C" guint64 warlock_imported_clients_lease(WarlockImportedClients* owner,const char* identity) {
    try {require(owner && owner->thread==g_thread_self(),"Own creator-thread imported lease source");return owner->value.lease(owner->entry(identity));}
    catch(...){return 0;}
}
extern "C" gboolean warlock_imported_clients_uri(WarlockImportedClients* owner,const char* identity,char** uriOutput,GError** error) {
    return output(owner,uriOutput,error,[&](auto& o){
        const auto entry=o.entry(identity);const auto packet=o.value.packet(entry);if(!packet)return std::string{};
        return o.value.endpoint().native([&](auto& broker){return broker.fetch(entry,packet->job.binding,packet->token)?uri::encode(packet->token):std::string{};});
    });
}
extern "C" gboolean warlock_imported_clients_status(WarlockImportedClients* owner,char** status,GError** error) {
    return output(owner,status,error,[](auto& o){
        std::string result="[";
        for(const auto& [entry,subject]:o.subjects.active()) {
            if(result.size()>1)result+=",";
            if(o.value.hasJob(entry))result+=o.value.status(entry);
            else {
                const auto intent=o.value.originalIntent(entry);Wire out;
                out.counter("entry",entry).counter("subject",subject.value).text("status","unissued");
                if(intent)out.counter("originalDeadline",intent->deadline);
                result+=out.finish();
            }
        }
        return result+"]";
    });
}
extern "C" gboolean warlock_imported_clients_empty(WarlockImportedClients* owner){return owner && owner->thread==g_thread_self() && owner->value.empty() && (!owner->retirementJournal || owner->retirementJournal->size()==0);}
extern "C" gboolean warlock_imported_clients_close(WarlockImportedClients* owner,GError** error) {
    if(!owner)return TRUE;
    try {require(owner->thread==g_thread_self() && owner->value.empty() && (!owner->retirementJournal || owner->retirementJournal->size()==0),"Outstanding shared imported physical, proof or retirement delivery ownership");owner->value.endpoint().unregisterView(owner->popup);delete owner;return TRUE;}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
