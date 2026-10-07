#include "imported-clients.h"
#include "imported_clients.hpp"
#include "imported_subjects.hpp"
#include "preview_bootstrap_lifetime.hpp"
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
    bool controlled{};
    GThread* thread{g_thread_self()};
    std::optional<Native::LegacyPreviewClaim> legacyClaim;
    std::optional<Native::PreviewControlClaim> controlClaim;
    PreviewControlDelivery controlDelivery{};
    std::unique_ptr<ControlReservations> controlBank;
    std::unique_ptr<ImportedControlAdmission> controlAdmission;
    ImportedSubjects subjects;
    std::optional<RetirementJournal> retirementJournal;
    std::optional<DetachmentJournal> detachmentJournal;
    bool detachPollTurn{};
    std::string initial;
    WarlockImportedClients(Native& native,uint64_t popup,uint64_t first,uint64_t second,uint64_t publication,uint64_t lease):
        value(native),native(native),popup(popup),subjects(2,{{first},{second}}) {
        legacyClaim.emplace(native);
        auto a=value.start(1,{first},publication,lease);auto b=value.start(2,{second},publication,lease);
        require(a.size()>2 && b.size()>2 && a.front()=='[' && a.back()==']' && b.front()=='[' && b.back()==']',"Actual shared imported seed/request arrays");
        a.pop_back();initial=a+","+b.substr(1);
        require(value.endpoint().registerView(popup,native.binding(),{1,2}),"Actual GTK receiver for shared imported ownership");
        epoch=value.endpoint().registeredView(popup)->epoch;
        retirementJournal.emplace(native.binding(),popup,epoch);
    }
    WarlockImportedClients(Native& native,uint64_t popup,uint64_t first,uint64_t publication,uint64_t lease):
        value(native,256),native(native),popup(popup),dynamic(true),subjects(256,{{first}}) {
        legacyClaim.emplace(native);
        initial=value.start(1,{first},publication,lease);
        require(value.endpoint().registerView(popup,native.binding(),{1}),"Actual dynamic GTK imported receiver");
        epoch=value.endpoint().registeredView(popup)->epoch;
        retirementJournal.emplace(native.binding(),popup,epoch);
    }
    WarlockImportedClients(Native& native,uint64_t popup,uint64_t first,uint64_t publication,uint64_t lease,bool enable):
        value(native,256),native(native),popup(popup),dynamic(true),controlled(enable),subjects(256,{{first}}) {
        require(enable,"Explicit controlled native factory");controlClaim.emplace(native);
        const auto binding=native.binding();auto& endpoint=value.endpoint();
        require(endpoint.registerControlView(popup,binding,controlClaim->epoch()),"Original empty native receiver before controlled admission");
        epoch=endpoint.registeredView(popup)->epoch;
        const PreviewControlGrant grant{binding.lifetime.value,binding.session.value,binding.frontend.value,popup,epoch};
        require(preview_control_delivery_init(&controlDelivery,grant),"Original actual native controlled receiver epoch");
        controlBank=std::make_unique<ControlReservations>(controlDelivery,1065);
        endpoint.native([&](auto& broker){controlAdmission=std::make_unique<ImportedControlAdmission>(*controlBank,grant,broker,256);});
        value.attachControlAdmission(*controlAdmission,grant);
        auto started=value.tryStartAtReceiver(popup,epoch,1,{first},publication,lease);
        require(started.native.status==demand::Attempt::Status::Started && started.native.job,
            "Original first job under native cleanup reservations");initial=std::move(started.events);
        retirementJournal.emplace(binding,popup,epoch);
        detachmentJournal.emplace(binding,popup,epoch);
    }
    PreviewControlGrant controlGrant(gpointer receiver,bool liveCore=true) {
        require(controlled && thread==g_thread_self() && receiver && reinterpret_cast<uint64_t>(receiver)==popup &&
            controlBank && controlAdmission,"Actual original controlled C receiver and creator thread");
        const auto grant=controlDelivery.grant;
        const Binding binding{{grant.lifetime},{grant.session},{grant.frontend}};
        require(grant.receiver==popup && grant.epoch==epoch && (!liveCore || native.binding()==binding),"Original controlled C native binding");
        value.endpoint().nativeView(popup,[&](auto&,const uri::View* view){require(importedReceiver(view,binding,epoch),"Original native controlled receiver enrollment");});
        return grant;
    }
    std::string grantWire()const {
        return Wire().begin("binding").binding(native.binding()).end().counter("receiverEpoch",epoch).integer("capacity",1065).finish();
    }
    std::string controlReceipt()const {
        const auto ordinal=preview_control_delivery_receipt(&controlDelivery);if(!ordinal)return "[]";
        const auto& grant=controlDelivery.grant;const Binding binding{{grant.lifetime},{grant.session},{grant.frontend}};
        return Wire().integer("previewProtocol",3).text("kind","preview-control-delivered").begin("binding").binding(binding).end()
            .counter("receiverEpoch",epoch).counter("controlOrdinal",ordinal).finish();
    }
    uint64_t controlActorEntry(const std::string& identity)const {
        require(controlAdmission && retirementJournal,"Original native control actor ledger");
        // Completed native actors are no longer in C subjects. Resolve only
        // actual retained completion/control rows, never a renderer serial.
        require(identity.starts_with("family:"),"Canonical original native control actor identity");
        const auto subject=decimal(std::string_view(identity).substr(7));
        const auto entry=controlAdmission->actorEntry({subject});require(entry.has_value(),"Unknown original native control actor family");return *entry;
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
extern "C" WarlockImportedClients* warlock_imported_clients_open_controlled(void* transport,gpointer popup,guint64 first,guint64 publication,guint64 lease,char** initial,char** grant,void** endpoint,GError** error) {
    if(initial)*initial=nullptr;
    if(grant)*grant=nullptr;
    if(endpoint)*endpoint=nullptr;
    try {
        require(transport && popup && first && publication && lease && initial && grant && endpoint,"Trusted controlled native C enrollment");
        auto owner=std::make_unique<WarlockImportedClients>(*static_cast<Native*>(transport),reinterpret_cast<uint64_t>(popup),first,publication,lease,true);
        *initial=g_strdup(owner->initial.c_str());*grant=g_strdup(owner->grantWire().c_str());*endpoint=&owner->value.endpoint();owner->controlClaim->publish();return owner.release();
    }catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return nullptr;}
}
extern "C" gboolean warlock_imported_clients_control_receipt(WarlockImportedClients* owner,gpointer popup,char** receipt,GError** error) {
    return output(owner,receipt,error,[&](auto& o){o.controlGrant(popup,false);return o.controlReceipt();});
}
static std::string recoveryPage(WarlockImportedClients& owner,PreviewControlGrant grant,uint64_t after){
    const auto state=owner.controlBank->recover(grant,after);
    const Binding binding{{grant.lifetime},{grant.session},{grant.frontend}};
    auto page=Wire().integer("previewProtocol",3).text("kind","preview-control-recovery")
        .begin("binding").binding(binding).end().counter("receiverEpoch",grant.epoch).integer("capacity",1065)
        .text("issuedThrough",std::to_string(state.issued)).text("deliveredThrough",std::to_string(state.delivered))
        .text("confirmedThrough",std::to_string(state.confirmed)).text("afterOrdinal",std::to_string(state.after)).finish();
    std::string ticket="null";
    if(state.next)ticket=Wire().integer("previewProtocol",3).text("kind","preview-control-ticket")
        .begin("binding").binding(binding).end().counter("receiverEpoch",grant.epoch).counter("controlOrdinal",state.next->ordinal)
        .boolean("alreadyDelivered",false).text("wire",state.next->wire).finish();
    page.pop_back();page+=",\"ticket\":"+ticket+"}";
    require(page.size()<=16384,"Bounded single-ticket recovery page");return page;
}
extern "C" gboolean warlock_imported_clients_control_recovery_begin(WarlockImportedClients* owner,gpointer popup,guint64 sender_epoch,char** page,GError** error){
    return output(owner,page,error,[&](auto& o){const auto grant=o.controlGrant(popup,false);
        require(sender_epoch && sender_epoch==o.epoch,"Original renderer realm before recovery inventory");
        return recoveryPage(o,grant,o.controlDelivery.confirmed);
    });
}
extern "C" gboolean warlock_imported_clients_control_recovery_next(WarlockImportedClients* owner,gpointer popup,guint64 sender_epoch,guint64 issued,guint64 delivered,guint64 confirmed,guint64 after,char** page,GError** error){
    return output(owner,page,error,[&](auto& o){const auto grant=o.controlGrant(popup,false);
        require(sender_epoch && sender_epoch==o.epoch && issued==o.controlBank->issued() &&
            delivered==o.controlDelivery.prefix.delivered && confirmed==o.controlDelivery.confirmed,
            "Unchanged original realm and all captured recovery frontiers");
        return recoveryPage(o,grant,after);
    });
}
extern "C" gboolean warlock_imported_clients_propose_control(WarlockImportedClients* owner,void* delivery,gpointer popup,const char* identity,const char* command,char** proposal,GError** error) {
    return output(owner,proposal,error,[&](auto& o){
        const auto grant=o.controlGrant(popup);
        require(delivery && identity && command && strlen(command)<=4096,"Bounded original native proposal inputs");
        // Validate the borrowed receipt capability even when this command does
        // not consume a terminal proof. It must own the SAME actual Endpoint.
        auto& receipt=*static_cast<ReceiptDelivery*>(delivery);
        o.value.actorCounts(o.popup,receipt,o.subjects);
        Json message(command);const std::string_view kind=Json::text(message.object(),"kind");
        const bool actor=kind=="retire-ready" || kind=="retire-delivery-ack";
        const bool detached=kind=="detach-ready" || kind=="detach-delivery-ack";
        auto result=kind=="reconcile"?o.value.proposeReconciliation(grant,identity,command):
            detached?o.value.proposeDetachmentControl(grant,o.controlActorEntry(identity),identity,command,*o.detachmentJournal,o.subjects):
            actor?o.value.proposeActorControl(grant,o.controlActorEntry(identity),identity,command,*o.retirementJournal):
            o.value.proposeJobControl(grant,o.controlActorEntry(identity),identity,command);
        require(result.has_value(),"Original native reserved proposal capacity");
        return Wire().integer("previewProtocol",3).text("kind","preview-control-ticket").begin("binding").binding(o.native.binding()).end()
            .counter("receiverEpoch",o.epoch).counter("controlOrdinal",result->ticket.ordinal)
            .boolean("alreadyDelivered",result->alreadyDelivered).text("wire",result->ticket.wire).finish();
    });
}
extern "C" gboolean warlock_imported_clients_propose_control_at_epoch(WarlockImportedClients* owner,void* delivery,gpointer popup,guint64 sender_epoch,
        const char* identity,const char* command,char** proposal,GError** error){
    if(proposal)*proposal=nullptr;
    try{require(owner && owner->controlled && owner->thread==g_thread_self() && sender_epoch && sender_epoch==owner->epoch,
        "Original renderer sender epoch before native purpose reservation");}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
    return warlock_imported_clients_propose_control(owner,delivery,popup,identity,command,proposal,error);
}
extern "C" gboolean warlock_imported_clients_propose_envelope(WarlockImportedClients* owner,void* delivery,gpointer popup,const char* envelope,char** ticket,GError** error) {
    if(ticket)*ticket=nullptr;
    try {
        require(owner && ticket && envelope && strlen(envelope)<=4096,"Bounded exact original Elm proposal envelope");
        const auto grant=owner->controlGrant(popup);
        Json message(envelope);auto root=message.object();
        ;
        require(Json::integer(root,"previewProtocol")==3 && std::string_view(Json::text(root,"kind"))=="preview-proposals" &&
            decodeBinding(Json::child(root,"binding"))==owner->native.binding() && message.counter("receiverEpoch")==grant.epoch,
            "Original singleton Elm proposal realm before native purpose reservation");
        auto node=json_object_get_member(root,"entries");require(node && JSON_NODE_HOLDS_ARRAY(node),"Original proposal entries array");
        auto entries=json_node_get_array(node);require(json_array_get_length(entries)==1,"One native-approved proposal per bounded ingress");
        auto row=json_array_get_element(entries,0);require(row && JSON_NODE_HOLDS_OBJECT(row),"Original proposal row object");
        auto entry=json_node_get_object(row);Json::fields(entry,{"identity","commands"});
        auto identity=Json::text(entry,"identity");auto commandsNode=json_object_get_member(entry,"commands");
        require(commandsNode && JSON_NODE_HOLDS_ARRAY(commandsNode),"Original proposal commands array");
        auto commands=json_node_get_array(commandsNode);require(json_array_get_length(commands)==1,"One original command per proposal");
        auto command=json_array_get_element(commands,0);require(command && JSON_NODE_HOLDS_OBJECT(command),"Original proposal command object");
        g_autofree char* wire=json_to_string(command,FALSE);
        return warlock_imported_clients_propose_control_at_epoch(owner,delivery,popup,grant.epoch,identity,wire,ticket,error);
    }catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
extern "C" gboolean warlock_imported_clients_confirm_control(WarlockImportedClients* owner,gpointer popup,const char* confirmation,char** receipt,GError** error) {
    return output(owner,receipt,error,[&](auto& o){
        const auto grant=o.controlGrant(popup,false);const Binding binding{{grant.lifetime},{grant.session},{grant.frontend}};
        require(confirmation && strlen(confirmation)<=4096,"Bounded original native receipt confirmation");
        Json message(confirmation);auto object=message.object();Json::fields(object,{"previewProtocol","kind","binding","receiverEpoch","controlOrdinal"});
        require(Json::integer(object,"previewProtocol")==3 && std::string_view(Json::text(object,"kind"))=="preview-control-confirmed" &&
            decodeBinding(Json::child(object,"binding"))==binding && message.counter("receiverEpoch")==o.epoch,
            "Original typed native control receipt confirmation");
        require(preview_control_delivery_confirm(&o.controlDelivery,grant,message.counter("controlOrdinal")),"Confirmed original delivered prefix only");
        o.value.settleConfirmedActorControls(grant);return o.controlReceipt();
    });
}
extern "C" gboolean warlock_imported_clients_dispatch_control(WarlockImportedClients* owner,void* delivery,gpointer popup,const char* ticket,char** events,char** receipt,GError** error) {
    if(events)*events=nullptr;
    if(receipt)*receipt=nullptr;
    uint64_t invoking=0;
    try {
        require(owner && events && receipt,"Original native controlled dispatch outputs");const auto grant=owner->controlGrant(popup,false);
        const Binding binding{{grant.lifetime},{grant.session},{grant.frontend}};
        require(delivery && ticket && strlen(ticket)<=4096,"Bounded original native ticket");
        auto& journal=*static_cast<ReceiptDelivery*>(delivery);owner->value.actorCounts(owner->popup,journal,owner->subjects);
        Json packet(ticket);auto object=packet.object();Json::fields(object,{"previewProtocol","kind","binding","receiverEpoch","controlOrdinal","entries"});
        require(Json::integer(object,"previewProtocol")==3 && std::string_view(Json::text(object,"kind"))=="preview-commands" &&
            decodeBinding(Json::child(object,"binding"))==binding && packet.counter("receiverEpoch")==owner->epoch,
            "Original typed native control ticket grant");
        const auto ordinal=packet.counter("controlOrdinal");
        // A confirmed released ticket can echo ONLY the latest original C
        // receipt. It cannot begin another invocation or authorize an effect.
        if(ordinal==owner->controlDelivery.prefix.delivered && std::string_view(ticket)==owner->controlDelivery.latest) {
            require(!owner->controlDelivery.prefix.inFlight,"No reentrant original native receipt echo");
            *events=g_strdup("[]");*receipt=g_strdup(owner->controlReceipt().c_str());return TRUE;
        }
        require(owner->native.binding()==binding && owner->controlBank->ownsTicket(grant,ordinal,ticket),"Only original native-issued immutable ticket on live core may invoke");
        auto node=json_object_get_member(object,"entries");require(node && JSON_NODE_HOLDS_ARRAY(node),"Original native control entry array");
        auto entries=json_node_get_array(node);require(json_array_get_length(entries)==1 && JSON_NODE_HOLDS_OBJECT(json_array_get_element(entries,0)),"One original native control entry");
        auto entry=json_node_get_object(json_array_get_element(entries,0));Json::fields(entry,{"identity","commands"});const std::string identity=Json::text(entry,"identity");
        node=json_object_get_member(entry,"commands");require(node && JSON_NODE_HOLDS_ARRAY(node),"Original native command array");
        auto commands=json_node_get_array(node);require(json_array_get_length(commands)==1 && JSON_NODE_HOLDS_OBJECT(json_array_get_element(commands,0)),"One original native command");
        const auto kind=std::string(Json::text(json_node_get_object(json_array_get_element(commands,0)),"kind"));
        // Extract the exact original command substring, including whitespace.
        // Native purpose guards retain these bytes; parsing/reserializing this
        // command would invalidate a readiness ticket during native polling.
        const auto bodyStart=std::string_view(ticket).find("\"commands\":[");require(bodyStart!=std::string_view::npos,"Original native ticket body marker");
        const auto rawStart=bodyStart+std::string_view("\"commands\":[").size();
        require(std::string_view(ticket).ends_with("]}]}"),"Original native ticket envelope suffix");
        const std::string command(std::string_view(ticket).substr(rawStart,strlen(ticket)-rawStart-4));
        require(preview_control_delivery_receive(&owner->controlDelivery,grant,ordinal,ticket,strlen(ticket))==PREVIEW_CONTROL_INVOKE,
            "Original contiguous nonreentrant native ticket prefix");invoking=ordinal;
        std::string result="[]";
        if(kind=="reconcile")owner->value.reconcileAtReceiver(grant,identity,command);
        else if(kind=="acknowledge")require(journal.acknowledge(owner->popup,identity,command),"Actual native terminal proof acknowledgment");
        else if(kind=="retire-ready") {
            const auto retired=owner->value.retireAtReceiver(owner->popup,owner->epoch,owner->controlActorEntry(identity),journal,owner->subjects,&*owner->retirementJournal,command);
            if(retired)result="["+*retired+"]";
        }else if(kind=="detach-ready"){
            const auto detached=owner->value.detachAtReceiver(owner->popup,owner->epoch,owner->controlActorEntry(identity),journal,owner->subjects,*owner->detachmentJournal,command);
            if(detached)result="["+*detached+"]";
        }else if(kind=="detach-delivery-ack"){
            require(owner->value.acknowledgeDetachmentDelivery(owner->popup,owner->epoch,journal,*owner->detachmentJournal,command),"Actual scoped final actor processing ACK");
            result=owner->value.pendingDetachmentDelivery(owner->popup,owner->epoch,journal,*owner->detachmentJournal);
        }else if(kind=="retire-delivery-ack") {
            require(owner->value.acknowledgeRetirementDelivery(owner->popup,owner->epoch,journal,*owner->retirementJournal,command),"Actual original final actor processing ACK");
            result=owner->value.pendingRetirementDelivery(owner->popup,owner->epoch,journal,*owner->retirementJournal);
        }else result=owner->value.command(owner->controlActorEntry(identity),identity,command);
        require(preview_control_delivery_complete(&owner->controlDelivery,ordinal),"Original native dispatcher return recorded once");invoking=0;
        *events=g_strdup(result.c_str());*receipt=g_strdup(owner->controlReceipt().c_str());return TRUE;
    }catch(const std::exception& exception) {
        // Fixed-size native prefix storage can complete independently of an
        // effect exception. Retain this receipt and every Unknown obligation;
        // transport retry must never call that handler again.
        if(owner && invoking && preview_control_delivery_complete(&owner->controlDelivery,invoking)) {
            if(events)*events=g_strdup("[]");
            if(receipt)*receipt=g_strdup(owner->controlReceipt().c_str());
        }
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;
    }
}
extern "C" gboolean warlock_imported_clients_enroll(WarlockImportedClients* owner,gpointer popup,guint64 subject,guint64 publication,guint64 lease,WarlockImportedAdmission* admission,char** events,GError** error) {
    if(admission)*admission=WARLOCK_IMPORTED_INVALID;
    return output(owner,events,error,[&](auto& o) {
        require(admission && popup,"Typed dynamic imported result receiver");
        std::string result="[]";*admission=o.enroll(reinterpret_cast<uint64_t>(popup),subject,publication,lease,result);return result;
    });
}
extern "C" gboolean warlock_imported_clients_command(WarlockImportedClients* owner,const char* identity,const char* command,char** events,GError** error) {
    return output(owner,events,error,[&](auto& o){require(command && !o.controlled,"Legacy raw command cannot invoke controlled native owner");return o.value.command(o.entry(identity),identity,command);});
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
        require(!o.controlled && delivery && popup && reinterpret_cast<uint64_t>(popup)==o.popup && retired,"Legacy raw retirement cannot invoke controlled native owner");
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
extern "C" gboolean warlock_imported_clients_detachment_inventory(WarlockImportedClients* owner,gpointer popup,const char* identity,char** facts,GError** error){
    return output(owner,facts,error,[&](auto& o){
        require(identity && o.detachmentJournal,"Controlled original scoped inventory owner");o.controlGrant(popup);
        const auto fact=o.value.detachmentInventory(o.popup,o.epoch,o.entry(identity),o.subjects);
        return Wire().integer("detachProtocol",1).text("kind","native-preview-detach-seed").text("identity",identity)
            .begin("binding").binding(fact.binding).end().counter("receiverEpoch",fact.epoch).counter("subject",fact.subject.value)
            .counter("entry",fact.entry).counter("entryIssuedThrough",fact.entryIssuedThrough).text("requestFloor",std::to_string(fact.requestFloor)).finish();
    });
}
extern "C" gboolean warlock_imported_clients_detachment_pending(WarlockImportedClients* owner,void* delivery,gpointer popup,char** events,GError** error){
    return output(owner,events,error,[&](auto& o){
        require(delivery && o.detachmentJournal,"Controlled original scoped completion owner");o.controlGrant(popup,false);
        o.value.actorCounts(o.popup,*static_cast<ReceiptDelivery*>(delivery),o.subjects);
        return o.value.pendingDetachmentDelivery(o.popup,o.epoch,*static_cast<ReceiptDelivery*>(delivery),*o.detachmentJournal);
    });
}
extern "C" gboolean warlock_imported_clients_retirement_poll(WarlockImportedClients* owner,void* delivery,gpointer popup,char** events,GError** error) {
    return output(owner,events,error,[&](auto& o) {
        require(delivery && popup && reinterpret_cast<uint64_t>(popup)==o.popup && o.retirementJournal,
            "Own original retained readiness polling receiver");
        // Check the borrowed receipt capability before any resource effect.
        // A foreign Endpoint must not gain cleanup by failing a later check.
        o.value.actorCounts(o.popup,*static_cast<ReceiptDelivery*>(delivery),o.subjects);
        if(o.controlled)o.value.pollReconciliation(o.controlGrant(popup));
        auto& receipt=*static_cast<ReceiptDelivery*>(delivery);
        const bool detached=o.detachmentJournal && o.detachmentJournal->hasReadiness();
        const bool permanent=o.retirementJournal->hasReadiness();
        std::string old="[]",scoped="[]";
        if(detached && (!permanent || o.detachPollTurn)){
            o.detachPollTurn=false;
            scoped=o.value.pollDetachmentDelivery(o.popup,o.epoch,receipt,o.subjects,*o.detachmentJournal);
            old=o.value.pendingRetirementDelivery(o.popup,o.epoch,receipt,*o.retirementJournal);
        }else{
            if(permanent)o.detachPollTurn=true;
            old=o.value.pollRetirementDelivery(o.popup,o.epoch,receipt,o.subjects,*o.retirementJournal);
            if(o.detachmentJournal)scoped=o.value.pendingDetachmentDelivery(o.popup,o.epoch,receipt,*o.detachmentJournal);
        }
        if(old=="[]")return scoped;
        if(scoped=="[]")return old;
        old.pop_back();return old+","+scoped.substr(1);
    });
}
extern "C" gboolean warlock_imported_clients_retirement_control(WarlockImportedClients* owner,void* delivery,gpointer popup,const char* identity,const char* command,char** events,GError** error) {
    return output(owner,events,error,[&](auto& o) {
        require(!o.controlled && delivery && popup && reinterpret_cast<uint64_t>(popup)==o.popup && identity && command && o.retirementJournal,
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
extern "C" gboolean warlock_imported_clients_empty(WarlockImportedClients* owner){
    try {return owner && owner->thread==g_thread_self() && owner->value.empty() &&
        (!owner->retirementJournal || owner->retirementJournal->size()==0) &&
        (!owner->detachmentJournal || owner->detachmentJournal->size()==0) &&
        (!owner->controlled || owner->value.canCloseControlBinding(owner->controlDelivery.grant));}
    catch(...){return FALSE;}
}
namespace {
gboolean closeImported(WarlockImportedClients* owner,WarlockPreviewBootstrap* bootstrap,GError** error) {
    if(!owner)return TRUE;
    try {require(warlock_imported_clients_empty(owner),"Outstanding shared imported physical, proof, actor or control delivery ownership");
        if(bootstrap)require(owner->controlled && bootstrapCanReleaseImported(bootstrap,&owner->native,&owner->value.endpoint(),owner->popup,owner->epoch),
            "Exact owning Bootstrap and settled borrowed receipt receiver before C close");
        if(owner->controlled){require(owner->value.closeControlBinding(owner->controlDelivery.grant) && owner->controlBank->transportEmpty(),"Original confirmed native binding quota release");owner->controlClaim->complete();}
        if(bootstrap)bootstrapReleaseImported(bootstrap);
        owner->value.endpoint().unregisterView(owner->popup);delete owner;return TRUE;}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
}
extern "C" gboolean warlock_imported_clients_close(WarlockImportedClients* owner,GError** error){return closeImported(owner,nullptr,error);}
extern "C" gboolean warlock_imported_clients_close_bootstrap(WarlockImportedClients* owner,WarlockPreviewBootstrap* bootstrap,GError** error){
    if(!bootstrap){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Exact native Bootstrap required for borrowed receipt closure");return FALSE;}
    return closeImported(owner,bootstrap,error);
}
