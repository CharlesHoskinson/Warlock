#include "preview-policy-driver.h"
#include <jsc/jsc.h>
#include <json-glib/json-glib.h>
#include <cstring>
#include <deque>
#include <memory>
#include <mutex>
#include <string>
#include <unordered_set>
#include <vector>

namespace {
constexpr size_t byte_limit=16*1024*1024;
constexpr size_t input_limit=1065;
// Original C dispatch returns at most two closed frame events or one original
// journal completion. Reserve their conservative wire budget before any effect.
// Qualification of that producer contract and pressure progress is mandatory.
constexpr size_t output_reservation=8192;
constexpr size_t output_batch_limit=3*input_limit;
constexpr size_t output_byte_limit=output_batch_limit*output_reservation;
std::mutex driver_registry_mutex;
std::unordered_set<WarlockImportedClients*> driver_registry;
bool fail(GError** error,const char* text,GIOErrorEnum code=G_IO_ERROR_FAILED) {g_set_error_literal(error,G_IO_ERROR,code,text);return false;}
bool exact(JsonObject* object,std::initializer_list<const char*> names) {
    if(!object || json_object_get_size(object)!=names.size())return false;
    for(auto* name:names)if(!json_object_has_member(object,name))return false;
    return true;
}
std::string encode(JsonNode* node) {g_autofree char* text=json_to_string(node,FALSE);return text;}
bool counter(JsonNode* node,guint64& result,bool zero=false) {
    if(!node || json_node_get_value_type(node)!=G_TYPE_STRING)return false;
    const char* text=json_node_get_string(node);const size_t length=std::strlen(text);
    if(!length || length>20 || (length>1 && text[0]=='0') || (!zero && text[0]=='0'))return false;
    result=0;
    for(size_t i=0;i<length;i++) {if(text[i]<'0' || text[i]>'9')return false;unsigned digit=text[i]-'0';if(result>(G_MAXUINT64-digit)/10)return false;result=result*10+digit;}
    return true;
}
std::string input(const char* kind,JsonNode* value) {
    g_autoptr(JsonNode) node=json_node_new(JSON_NODE_OBJECT);auto* object=json_object_new();json_node_take_object(node,object);
    json_object_set_string_member(object,"kind",kind);json_object_set_member(object,"value",json_node_copy(value));return encode(node);
}
}
struct _WarlockPolicyDriver {
    GThread* creator{g_thread_ref(g_thread_self())};
    WarlockImportedClients* owner{};
    WarlockImportedClients* registry_owner{};
    WarlockPreviewBootstrap* bootstrap{};
    gpointer popup{};
    void* delivery{};
    WarlockPreviewPolicy* policy{};
    JSCContext* transport{jsc_context_new()};
    JSCValue *retain{},*acknowledge{},*retry{},*snapshot{};
    guint64 epoch{};
    std::string domain,latest,pending_issued,last_receipt,native_error;
    std::deque<std::string> inputs,posts,confirmations,returned_events;
    size_t input_bytes{},returned_bytes{};
    bool active{},unknown{},native_closed{};
    ~_WarlockPolicyDriver() {
        g_clear_object(&retain);g_clear_object(&acknowledge);g_clear_object(&retry);g_clear_object(&snapshot);
        g_clear_object(&transport);g_thread_unref(creator);
        if(registry_owner) {std::lock_guard<std::mutex> lock(driver_registry_mutex);driver_registry.erase(registry_owner);}
    }
};
namespace {
bool owner(WarlockPolicyDriver* self,GError** error) {
    if(!self)return fail(error,"Original driver required");
    if(self->creator!=g_thread_self())return fail(error,"Original driver creator required");
    if(self->active || self->unknown)return fail(error,"Inflight/uncertain driver cannot reset or replay its policy");
    return true;
}
struct Active {WarlockPolicyDriver& self;bool enabled{true};explicit Active(WarlockPolicyDriver& value):self(value){self.active=true;}~Active(){if(enabled)self.active=false;}void release(){self.active=false;enabled=false;}};
void post(const char* wire,gpointer raw) {
    auto& self=*static_cast<WarlockPolicyDriver*>(raw);
    if(!self.active || self.creator!=g_thread_self() || !wire || std::strlen(wire)>4096 || self.posts.size()>=2){self.unknown=true;return;}
    self.posts.emplace_back(wire); // Store only. Native effects wait for step().
}
void confirm(const char* wire,gpointer raw) {
    auto& self=*static_cast<WarlockPolicyDriver*>(raw);
    if(!self.active || self.creator!=g_thread_self() || !wire || std::strlen(wire)>4096 || self.confirmations.size()>=2){self.unknown=true;return;}
    self.confirmations.emplace_back(wire); // Separate receipt observation custody.
}
guint utf8_size(const char* text,gpointer) {return text?std::strlen(text):0;}
bool transport_call(WarlockPolicyDriver& self,JSCValue* function,const std::string* wire,GError** error) {
    g_autoptr(JSCValue) value=wire?jsc_value_new_string(self.transport,wire->c_str()):nullptr;
    JSCValue* args[]={value};g_autoptr(JSCValue) result=jsc_value_function_callv(function,wire?1:0,args);
    if(!result || jsc_context_get_exception(self.transport) || self.unknown){self.unknown=true;return fail(error,"Original native outbox execution uncertain; custody retained");}
    if(!jsc_value_is_boolean(result) || !jsc_value_to_boolean(result)){self.unknown=true;return fail(error,"Native outbox did not retain/observe the exact original ticket or receipt");}
    return true;
}
bool invoke(WarlockPolicyDriver& self,const std::string& wire,GError** error) {
    g_autofree char* result=nullptr;
    if(!warlock_preview_policy_invoke(self.policy,wire.c_str(),&result,error)) {
        if(!error || !*error || (*error)->domain!=g_quark_from_static_string("warlock-preview-policy") || (*error)->code!=WARLOCK_POLICY_WOULD_BLOCK)self.unknown=true;
        return false;
    }
    self.latest=result;return true;
}
std::string native_input(WarlockPolicyDriver& self,JsonNode* event) {
    g_autoptr(JsonParser) parser=json_parser_new();
    if(!json_parser_load_from_data(parser,self.domain.c_str(),-1,nullptr))g_error("Invalid held native driver domain");
    auto* domain=json_node_get_object(json_parser_get_root(parser));
    g_autoptr(JsonNode) node=json_node_new(JSON_NODE_OBJECT);auto* envelope=json_object_new();json_node_take_object(node,envelope);
    json_object_set_int_member(envelope,"previewProtocol",3);json_object_set_string_member(envelope,"kind","native-preview-realm-event");
    json_object_set_member(envelope,"binding",json_node_copy(json_object_get_member(domain,"binding")));
    json_object_set_member(envelope,"receiverEpoch",json_node_copy(json_object_get_member(domain,"receiverEpoch")));
    json_object_set_member(envelope,"event",json_node_copy(event));return input("native",node);
}
bool retain_batch(WarlockPolicyDriver& self,const char* wire,GError** error) {
    if(!wire || std::strlen(wire)>byte_limit)return fail(error,"Bounded original native event batch required");
    g_autoptr(JsonParser) parser=json_parser_new();
    if(!json_parser_load_from_data(parser,wire,-1,nullptr) || !JSON_NODE_HOLDS_ARRAY(json_parser_get_root(parser)))return fail(error,"Original native event array required");
    auto* events=json_node_get_array(json_parser_get_root(parser));std::vector<std::string> retained;size_t bytes=0;
    if(json_array_get_length(events)>input_limit-self.inputs.size())return fail(error,"Original event batch remains with producer until input custody admits it",G_IO_ERROR_WOULD_BLOCK);
    for(guint i=0;i<json_array_get_length(events);i++) {
        auto* event=json_array_get_element(events,i);if(!JSON_NODE_HOLDS_OBJECT(event))return fail(error,"Typed original native event required");
        auto wrapped=native_input(self,event);bytes+=wrapped.size();
        if(bytes>byte_limit-self.input_bytes)return fail(error,"Original native batch remains with producer until retained byte custody admits it",G_IO_ERROR_WOULD_BLOCK);
        retained.push_back(std::move(wrapped));
    }
    for(auto& row:retained)self.inputs.push_back(std::move(row));
    self.input_bytes+=bytes;return true;
}
bool domain_input(WarlockPolicyDriver& self,const char* kind,GError** error) {
    g_autoptr(JsonParser) parser=json_parser_new();
    if(!json_parser_load_from_data(parser,self.domain.c_str(),-1,nullptr)){self.unknown=true;return fail(error,"Original domain custody uncertain");}
    return invoke(self,input(kind,json_parser_get_root(parser)),error);
}
bool returned_step(WarlockPolicyDriver& self,gboolean* progressed,GError** error) {
    g_autoptr(JsonParser) events=json_parser_new();
    if(!json_parser_load_from_data(events,self.returned_events.front().c_str(),-1,nullptr) || !JSON_NODE_HOLDS_ARRAY(json_parser_get_root(events))) {self.unknown=true;return fail(error,"Original native returned event custody uncertain");}
    auto* array=json_node_get_array(json_parser_get_root(events));
    if(!json_array_get_length(array)) {self.returned_bytes-=self.returned_events.front().size();self.returned_events.pop_front();*progressed=TRUE;return TRUE;}
    if(!invoke(self,native_input(self,json_array_get_element(array,0)),error))return FALSE;
    self.returned_bytes-=self.returned_events.front().size();json_array_remove_element(array,0);
    if(json_array_get_length(array)) {self.returned_events.front()=encode(json_parser_get_root(events));self.returned_bytes+=self.returned_events.front().size();}
    else self.returned_events.pop_front();
    *progressed=TRUE;return TRUE;
}
}
WarlockPolicyDriver* warlock_policy_driver_new(const char* source,gsize length,const char* outbox,gsize outbox_length,
    WarlockImportedClients* imported,WarlockPreviewBootstrap* bootstrap,gpointer popup,const char* grant,GError** error) {
    if(!source || !outbox || !outbox_length || outbox_length>byte_limit || std::memchr(outbox,0,outbox_length) || !g_utf8_validate(outbox,outbox_length,nullptr) || !imported || !bootstrap || !popup || !grant || std::strlen(grant)>4096){fail(error,"Trusted native driver sources, realm and owner required");return nullptr;}
    auto self=std::make_unique<WarlockPolicyDriver>();self->owner=imported;self->bootstrap=bootstrap;self->popup=popup;
    g_autoptr(JsonParser) parser=json_parser_new();
    if(!json_parser_load_from_data(parser,grant,-1,nullptr) || !JSON_NODE_HOLDS_OBJECT(json_parser_get_root(parser))){fail(error,"Original native grant required");return nullptr;}
    auto* fields=json_node_get_object(json_parser_get_root(parser));
    if(!exact(fields,{"binding","receiverEpoch","capacity"}) || !counter(json_object_get_member(fields,"receiverEpoch"),self->epoch)){fail(error,"Exact original driver realm required");return nullptr;}
    self->delivery=warlock_preview_bootstrap_delivery(bootstrap,popup,error);if(!self->delivery)return nullptr;
    g_autofree char* recovery=nullptr;
    if(!warlock_imported_clients_control_recovery_begin(imported,popup,self->epoch,&recovery,error))return nullptr;
    g_autoptr(JsonParser) page=json_parser_new();
    if(!json_parser_load_from_data(page,recovery,-1,nullptr)){fail(error,"Original readonly native namespace required");return nullptr;}
    auto* recovered=json_node_get_object(json_parser_get_root(page));guint64 issued=1,delivered=1,confirmed=1;
    if(!counter(json_object_get_member(recovered,"issuedThrough"),issued,true) || !counter(json_object_get_member(recovered,"deliveredThrough"),delivered,true) || !counter(json_object_get_member(recovered,"confirmedThrough"),confirmed,true) || issued || delivered || confirmed ||
       !json_node_equal(json_object_get_member(fields,"binding"),json_object_get_member(recovered,"binding")) || !json_node_equal(json_object_get_member(fields,"receiverEpoch"),json_object_get_member(recovered,"receiverEpoch")) || !json_node_equal(json_object_get_member(fields,"capacity"),json_object_get_member(recovered,"capacity"))) {
        fail(error,"Only original exact empty native-issued realm may initialize a fresh driver");return nullptr;
    }
    g_autoptr(JsonNode) domain=json_node_new(JSON_NODE_OBJECT);auto* object=json_object_new();json_node_take_object(domain,object);
    json_object_set_member(object,"binding",json_node_copy(json_object_get_member(fields,"binding")));json_object_set_member(object,"receiverEpoch",json_node_copy(json_object_get_member(fields,"receiverEpoch")));self->domain=encode(domain);
    {
        std::lock_guard<std::mutex> lock(driver_registry_mutex);
        if(!driver_registry.insert(imported).second){fail(error,"Original native owner already has its single policy driver");return nullptr;}
        self->registry_owner=imported;
    }
    g_autoptr(JSCValue) post_function=jsc_value_new_function(self->transport,"nativePost",G_CALLBACK(post),self.get(),nullptr,G_TYPE_NONE,1,G_TYPE_STRING);
    g_autoptr(JSCValue) confirm_function=jsc_value_new_function(self->transport,"nativeConfirm",G_CALLBACK(confirm),self.get(),nullptr,G_TYPE_NONE,1,G_TYPE_STRING);
    g_autoptr(JSCValue) utf8_function=jsc_value_new_function(self->transport,"nativeUTF8Size",G_CALLBACK(utf8_size),nullptr,nullptr,G_TYPE_UINT,1,G_TYPE_STRING);
    jsc_context_set_value(self->transport,"nativePost",post_function);jsc_context_set_value(self->transport,"nativeConfirm",confirm_function);jsc_context_set_value(self->transport,"nativeUTF8Size",utf8_function);
    const auto program=std::string("globalThis.TextEncoder=function(){};TextEncoder.prototype.encode=function(s){return {length:nativeUTF8Size(s)};};\n")+std::string(outbox,outbox_length)+
        "\nconst heldOutbox=WarlockNativePreviewControlOutbox("+grant+",nativePost,nativeConfirm);function heldRetain(s){return heldOutbox.retain(JSON.parse(s));}function heldAcknowledge(s){return heldOutbox.acknowledge(JSON.parse(s));}function heldRetry(){return heldOutbox.retry();}function heldSnapshot(){return JSON.stringify(heldOutbox.snapshot());}";
    g_autoptr(JSCValue) initialized=jsc_context_evaluate(self->transport,program.data(),program.size());
    if(!initialized || jsc_context_get_exception(self->transport) || self->unknown){fail(error,"Held native outbox constructor failed before policy grant");return nullptr;}
    self->retain=jsc_context_get_value(self->transport,"heldRetain");self->acknowledge=jsc_context_get_value(self->transport,"heldAcknowledge");self->retry=jsc_context_get_value(self->transport,"heldRetry");self->snapshot=jsc_context_get_value(self->transport,"heldSnapshot");
    if(!jsc_value_is_function(self->retain) || !jsc_value_is_function(self->acknowledge) || !jsc_value_is_function(self->retry) || !jsc_value_is_function(self->snapshot)){fail(error,"Private original outbox methods required");return nullptr;}
    self->policy=warlock_preview_policy_new(source,length,error);if(!self->policy)return nullptr;
    if(!invoke(*self,input("grant",json_parser_get_root(parser)),error))return self.release(); // Unknown live custody must not be silently destroyed.
    return self.release();
}
gboolean warlock_policy_driver_native(WarlockPolicyDriver* self,guint64 epoch,const char* events,GError** error) {
    if(!owner(self,error))return FALSE;
    if(!epoch || epoch!=self->epoch || self->native_closed)return fail(error,"Original native source epoch before input retention");
    return retain_batch(*self,events,error);
}
gboolean warlock_policy_driver_presentation(WarlockPolicyDriver* self,const char* snapshot,GError** error) {
    if(!owner(self,error))return FALSE;
    if(!snapshot || std::strlen(snapshot)>byte_limit || self->native_closed)return fail(error,"Original admitted presentation required");
    g_autoptr(JsonParser) parser=json_parser_new();if(!json_parser_load_from_data(parser,snapshot,-1,nullptr))return fail(error,"Bounded presentation JSON required");
    auto wire=input("presentation",json_parser_get_root(parser));
    if(self->inputs.size()>=input_limit || wire.size()>byte_limit-self->input_bytes)return fail(error,"Original presentation remains with producer until input custody admits it",G_IO_ERROR_WOULD_BLOCK);
    self->input_bytes+=wire.size();self->inputs.push_back(std::move(wire));return TRUE;
}
gboolean warlock_policy_driver_quarantine(WarlockPolicyDriver* self,guint64 epoch,GError** error) {
    if(!owner(self,error))return FALSE;
    if(!epoch || epoch!=self->epoch || self->native_closed)return fail(error,"Original urgent native realm required");
    Active active(*self);return domain_input(*self,"quarantine",error);
}
WarlockPreviewPolicy* warlock_policy_driver_policy(WarlockPolicyDriver* self,GError** error) {
    if(!owner(self,error))return nullptr;
    return self->policy;
}
gboolean warlock_policy_driver_step(WarlockPolicyDriver* self,gboolean* progressed,GError** error) {
    if(progressed)*progressed=FALSE;
    if(!owner(self,error))return FALSE;
    if(!progressed || self->native_closed)return fail(error,"Open original driver and progress output required");
    Active active(*self);
    if(!self->pending_issued.empty()) {
        g_autoptr(JsonParser) parser=json_parser_new();if(!json_parser_load_from_data(parser,self->pending_issued.c_str(),-1,nullptr)){self->unknown=true;return fail(error,"Original retained ticket custody uncertain");}
        if(!invoke(*self,input("issued",json_parser_get_root(parser)),error))return FALSE;
        self->pending_issued.clear();*progressed=TRUE;return TRUE;
    }
    if(!self->confirmations.empty()) {
        g_autofree char* receipt=nullptr;
        if(!warlock_imported_clients_confirm_control(self->owner,self->popup,self->confirmations.front().c_str(),&receipt,error))return FALSE;
        self->confirmations.pop_front();*progressed=TRUE;return TRUE;
    }
    if(!self->returned_events.empty()) {
        g_autoptr(JsonParser) cache=json_parser_new();
        if(!json_parser_load_from_data(cache,self->latest.c_str(),-1,nullptr)){self->unknown=true;return fail(error,"Original policy output custody required before scheduling returned events");}
        auto* realm=json_object_get_object_member(json_node_get_object(json_parser_get_root(cache)),"realm");
        // Drain original admitted native results ahead of further effect output
        // when the unchanged policy's deferred-input gate permits admission.
        if(!json_object_get_int_member(realm,"deferred"))return returned_step(*self,progressed,error);
    }
    if(!self->posts.empty()) {
        if(self->returned_events.size()>=output_batch_limit || self->returned_bytes>output_byte_limit-output_reservation)
            return fail(error,"Retain exact native ticket until reserved returned-output custody admits dispatch",G_IO_ERROR_WOULD_BLOCK);
        g_autofree char *events=nullptr,*receipt=nullptr;GError* native_error=nullptr;
        const bool successful=warlock_imported_clients_dispatch_control(self->owner,self->delivery,self->popup,self->posts.front().c_str(),&events,&receipt,&native_error);
        if(!receipt) {if(native_error)g_propagate_error(error,native_error);else fail(error,"Original ticket has no native returned receipt; exact transport custody retained");return FALSE;}
        if(events && std::strcmp(events,"[]")) {self->returned_events.emplace_back(events);self->returned_bytes+=std::strlen(events);}
        self->last_receipt=receipt;
        if(events && std::strcmp(events,"[]")) {
            g_autoptr(JsonParser) result=json_parser_new();
            if(std::strlen(events)>output_reservation || !json_parser_load_from_data(result,events,-1,nullptr) || !JSON_NODE_HOLDS_ARRAY(json_parser_get_root(result)) || json_array_get_length(json_node_get_array(json_parser_get_root(result)))>2) {
                // An unexpected producer-contract violation is live uncertainty.
                // Keep every original event, ticket and receipt for recovery;
                // do not discard it or infer a successful bounded dispatch.
                self->unknown=true;g_clear_error(&native_error);
                return fail(error,"Native returned-output contract uncertain; exact events/ticket/receipt retained");
            }
        }
        if(!successful)self->native_error=native_error?native_error->message:"Native effect outcome Unknown";
        g_clear_error(&native_error);self->posts.pop_front();
        if(!transport_call(*self,self->acknowledge,&self->last_receipt,error))return FALSE;
        *progressed=TRUE;return TRUE;
    }
    g_autoptr(JsonParser) parser=json_parser_new();
    if(!json_parser_load_from_data(parser,self->latest.c_str(),-1,nullptr)){self->unknown=true;return fail(error,"Original successful policy output custody required");}
    auto* root=json_node_get_object(json_parser_get_root(parser));auto* realm=json_object_get_object_member(root,"realm");auto* ingress=json_object_get_object_member(realm,"ingress");auto* intents=json_object_get_array_member(ingress,"intents");
    if(json_array_get_length(intents)) {
        g_autoptr(JsonParser) domain=json_parser_new();if(!json_parser_load_from_data(domain,self->domain.c_str(),-1,nullptr))g_error("Invalid held native driver domain");
        auto* grant=json_node_get_object(json_parser_get_root(domain));g_autoptr(JsonNode) proposal=json_node_new(JSON_NODE_OBJECT);auto* fields=json_object_new();json_node_take_object(proposal,fields);
        json_object_set_int_member(fields,"previewProtocol",3);json_object_set_string_member(fields,"kind","preview-proposals");json_object_set_member(fields,"binding",json_node_copy(json_object_get_member(grant,"binding")));json_object_set_member(fields,"receiverEpoch",json_node_copy(json_object_get_member(grant,"receiverEpoch")));
        auto* rows=json_array_new();json_array_add_element(rows,json_node_copy(json_array_get_element(intents,0)));json_object_set_array_member(fields,"entries",rows);auto wire=encode(proposal);g_autofree char* ticket=nullptr;
        if(!warlock_imported_clients_propose_envelope(self->owner,self->delivery,self->popup,wire.c_str(),&ticket,error)) {self->unknown=true;return FALSE;}
        self->pending_issued=ticket; // Own exact ticket before JS can stage a post.
        if(!transport_call(*self,self->retain,&self->pending_issued,error))return FALSE;
        *progressed=TRUE;return TRUE;
    }
    if(json_object_get_int_member(realm,"deferred")) {if(!domain_input(*self,"retry",error))return FALSE;*progressed=TRUE;return TRUE;}
    if(!self->returned_events.empty()) {
        return returned_step(*self,progressed,error);
    }
    if(!self->inputs.empty()) {
        if(!invoke(*self,self->inputs.front(),error))return FALSE;
        self->input_bytes-=self->inputs.front().size();self->inputs.pop_front();*progressed=TRUE;return TRUE;
    }
    return TRUE;
}
gboolean warlock_policy_driver_inspect(WarlockPolicyDriver* self,char** output,GError** error) {
    if(output)*output=nullptr;
    if(!owner(self,error))return FALSE;
    if(!output)return fail(error,"Private native diagnostic output required");
    Active active(*self);g_autoptr(JSCValue) snapshot=jsc_value_function_callv(self->snapshot,0,nullptr);
    if(!snapshot || jsc_context_get_exception(self->transport) || !jsc_value_is_string(snapshot)){self->unknown=true;return fail(error,"Private outbox observation uncertain");}
    g_autofree char* wire=jsc_value_to_string(snapshot);g_autoptr(JsonParser) parser=json_parser_new();if(!json_parser_load_from_data(parser,wire,-1,nullptr)){self->unknown=true;return fail(error,"Private original transport state required");}
    g_autoptr(JsonParser) policy=json_parser_new();if(!json_parser_load_from_data(policy,self->latest.c_str(),-1,nullptr))g_error("Invalid held policy output");
    g_autoptr(JsonNode) node=json_node_new(JSON_NODE_OBJECT);auto* object=json_object_new();json_node_take_object(node,object);
    json_object_set_int_member(object,"retainedInputs",self->inputs.size());json_object_set_int_member(object,"retainedInputBytes",self->input_bytes);json_object_set_boolean_member(object,"ticketUnnotified",!self->pending_issued.empty());json_object_set_int_member(object,"postedTickets",self->posts.size());json_object_set_int_member(object,"confirmations",self->confirmations.size());json_object_set_boolean_member(object,"returnedEventsRetained",!self->returned_events.empty());json_object_set_int_member(object,"returnedEventBatches",self->returned_events.size());json_object_set_int_member(object,"returnedEventBytes",self->returned_bytes);json_object_set_string_member(object,"nativeEffectError",self->native_error.c_str());
    json_object_set_member(object,"transport",json_node_copy(json_parser_get_root(parser)));json_object_set_member(object,"privatePolicy",json_node_copy(json_parser_get_root(policy)));*output=g_strdup(encode(node).c_str());return TRUE;
}
gboolean warlock_policy_driver_close(WarlockPolicyDriver* self,GError** error) {
    if(!owner(self,error))return FALSE;
    if(!self->inputs.empty() || !self->posts.empty() || !self->confirmations.empty() || !self->pending_issued.empty() || !self->returned_events.empty())return fail(error,"Original input/ticket/receipt custody prevents normal driver closure");
    Active active(*self);
    if(!self->native_closed) {
        g_autoptr(JsonParser) parser=json_parser_new();if(!json_parser_load_from_data(parser,self->latest.c_str(),-1,nullptr))g_error("Invalid held policy output");
        auto* root=json_node_get_object(json_parser_get_root(parser));auto* realm=json_object_get_object_member(root,"realm");auto* ingress=json_object_get_object_member(realm,"ingress");
        if(json_array_get_length(json_object_get_array_member(root,"models")) || json_object_get_int_member(ingress,"pending") || json_object_get_int_member(realm,"deferred"))return fail(error,"Original policy membership/ingress/deferred custody prevents close");
        if(!warlock_imported_clients_close_bootstrap(self->owner,self->bootstrap,error))return FALSE;
        self->native_closed=true;self->owner=nullptr;self->delivery=nullptr;
        if(!domain_input(*self,"closed",error))return FALSE;
    }
    if(!warlock_preview_policy_close(self->policy,error))return FALSE;
    self->policy=nullptr;active.release();delete self;return TRUE;
}
