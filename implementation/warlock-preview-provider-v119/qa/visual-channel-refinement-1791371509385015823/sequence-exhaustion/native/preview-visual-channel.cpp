#include "preview-visual-channel.h"
#include <json-glib/json-glib.h>
#include <cstring>
#include <string>

struct _WarlockVisualChannel {
    GThread* creator=g_thread_ref(g_thread_self());
    GObject* context{};
    guint64 lease{}, sequence{G_MAXUINT64-1};
    std::string domain, visual, packet, receipt;
    bool accepted{};
    ~_WarlockVisualChannel() {g_thread_unref(creator);}
};
namespace {
gboolean fail(GError** error, WarlockVisualError code, const char* message) {
    g_set_error_literal(error,g_quark_from_static_string("warlock-visual-channel"),code,message);return FALSE;
}
bool owner(WarlockVisualChannel* self,GError** error) {
    if(!self) return fail(error,WARLOCK_VISUAL_INVALID,"Owned channel required");
    if(self->creator!=g_thread_self()) return fail(error,WARLOCK_VISUAL_WRONG_THREAD,"Original channel creator required");
    return true;
}
bool context(WarlockVisualChannel* self,GObject* target,GError** error) {
    if(!owner(self,error))return false;
    if(!target || self->context!=target)return fail(error,WARLOCK_VISUAL_WRONG_CONTEXT,"Original attached native context required");
    return true;
}
void invalidate(WarlockVisualChannel& self) {
    self.accepted=false;self.visual.clear();self.packet.clear();self.receipt.clear();
}
std::string data(JsonNode* node) {g_autofree char* wire=json_to_string(node,FALSE);return wire;}
bool visual(WarlockPreviewPolicy* policy,std::string& bytes,std::string& domain,GError** error) {
    g_autofree char* wire=nullptr;if(!warlock_preview_policy_visual_projection(policy,&wire,error))return false;
    g_autoptr(JsonParser) parser=json_parser_new();
    if(!json_parser_load_from_data(parser,wire,-1,nullptr))return fail(error,WARLOCK_VISUAL_INVALID,"Owned visual JSON required");
    JsonObject* object=json_node_get_object(json_parser_get_root(parser));
    g_autoptr(JsonNode) node=json_node_new(JSON_NODE_OBJECT);auto* fields=json_object_new();json_node_take_object(node,fields);
    json_object_set_member(fields,"binding",json_node_copy(json_object_get_member(object,"binding")));
    json_object_set_member(fields,"receiverEpoch",json_node_copy(json_object_get_member(object,"receiverEpoch")));
    bytes=wire;domain=data(node);return true;
}
std::string envelope(WarlockVisualChannel& self,const char* kind,const char* sequenceField,bool projection) {
    g_autoptr(JsonParser) parser=json_parser_new();
    if(!json_parser_load_from_data(parser,self.domain.c_str(),-1,nullptr))g_error("Invalid owned visual domain");
    auto* source=json_node_get_object(json_parser_get_root(parser));
    g_autoptr(JsonNode) node=json_node_new(JSON_NODE_OBJECT);auto* object=json_object_new();json_node_take_object(node,object);
    json_object_set_int_member(object,"channelProtocol",1);json_object_set_string_member(object,"kind",kind);
    json_object_set_member(object,"binding",json_node_copy(json_object_get_member(source,"binding")));
    json_object_set_member(object,"receiverEpoch",json_node_copy(json_object_get_member(source,"receiverEpoch")));
    g_autofree char* lease=g_strdup_printf("%" G_GUINT64_FORMAT,self.lease);
    g_autofree char* sequence=g_strdup_printf("%" G_GUINT64_FORMAT,self.sequence);
    json_object_set_string_member(object,"rendererLease",lease);json_object_set_string_member(object,sequenceField,sequence);
    if(projection) {
        g_autoptr(JsonParser) content=json_parser_new();
        if(!json_parser_load_from_data(content,self.visual.c_str(),-1,nullptr))g_error("Invalid owned visual projection");
        json_object_set_member(object,"visual",json_node_copy(json_parser_get_root(content)));
    }
    return data(node);
}
bool same_current(WarlockVisualChannel& self,WarlockPreviewPolicy* policy,GError** error) {
    std::string bytes,domain;
    if(!visual(policy,bytes,domain,error)){invalidate(self);return false;}
    if(self.packet.empty() || bytes!=self.visual || domain!=self.domain) {
        invalidate(self);return fail(error,WARLOCK_VISUAL_NOT_CURRENT,"Pending visual no longer equals committed policy");
    }
    return true;
}
}
WarlockVisualChannel* warlock_visual_channel_new(void) {return new WarlockVisualChannel;}
gboolean warlock_visual_channel_attach(WarlockVisualChannel* self,WarlockPreviewPolicy* policy,GObject* target,char** grant,GError** error) {
    if(grant)*grant=nullptr;
    if(!owner(self,error))return FALSE;
    if(!target || !G_IS_OBJECT(target) || !grant || self->context)return fail(error,WARLOCK_VISUAL_INVALID,"Detached channel, native context and output required");
    if(self->lease==G_MAXUINT64)return fail(error,WARLOCK_VISUAL_EXHAUSTED,"Renderer lease exhausted without reset");
    std::string bytes,domain;if(!visual(policy,bytes,domain,error))return FALSE;
    self->context=G_OBJECT(g_object_ref(target));self->lease++;self->domain=domain;invalidate(*self);
    *grant=g_strdup(envelope(*self,"native-preview-renderer-grant","sequenceFloor",false).c_str());return TRUE;
}
gboolean warlock_visual_channel_offer(WarlockVisualChannel* self,WarlockPreviewPolicy* policy,GObject* target,char** packet,GError** error) {
    if(packet)*packet=nullptr;
    if(!context(self,target,error))return FALSE;
    if(!packet)return fail(error,WARLOCK_VISUAL_INVALID,"Owned packet output required");
    invalidate(*self);
    std::string bytes,domain;if(!visual(policy,bytes,domain,error))return FALSE;
    if(domain!=self->domain)return fail(error,WARLOCK_VISUAL_NOT_CURRENT,"Realm change requires native detach and a new lease");
    if(self->sequence==G_MAXUINT64)return fail(error,WARLOCK_VISUAL_EXHAUSTED,"Visual sequence exhausted without reset");
    self->sequence++;self->visual=bytes;
    self->packet=envelope(*self,"native-preview-projection","visualSequence",true);
    self->receipt=envelope(*self,"native-preview-projection-accepted","visualSequence",false);
    *packet=g_strdup(self->packet.c_str());return TRUE;
}
gboolean warlock_visual_channel_retry(WarlockVisualChannel* self,WarlockPreviewPolicy* policy,GObject* target,char** packet,GError** error) {
    if(packet)*packet=nullptr;
    if(!context(self,target,error))return FALSE;
    if(!packet)return fail(error,WARLOCK_VISUAL_INVALID,"Owned retry output required");
    if(!same_current(*self,policy,error))return FALSE;
    *packet=g_strdup(self->packet.c_str());return TRUE;
}
gboolean warlock_visual_channel_ack(WarlockVisualChannel* self,WarlockPreviewPolicy* policy,GObject* target,const char* receipt,GError** error) {
    if(!context(self,target,error))return FALSE;
    if(!receipt || std::strlen(receipt)>4096 || self->receipt.empty() || self->receipt!=receipt)
        return fail(error,WARLOCK_VISUAL_NOT_CURRENT,"Exact latest native-issued visual receipt required");
    if(!same_current(*self,policy,error))return FALSE;
    self->accepted=true;return TRUE;
}
gboolean warlock_visual_channel_current(WarlockVisualChannel* self,WarlockPreviewPolicy* policy,GObject* target,GError** error) {
    if(!context(self,target,error))return FALSE;
    if(!same_current(*self,policy,error))return FALSE;
    if(!self->accepted)return fail(error,WARLOCK_VISUAL_NOT_CURRENT,"Current projection has no exact renderer receipt");
    return TRUE;
}
gboolean warlock_visual_channel_invalidate(WarlockVisualChannel* self,GObject* target,GError** error) {
    if(!context(self,target,error))return FALSE;
    invalidate(*self);return TRUE;
}
gboolean warlock_visual_channel_detach(WarlockVisualChannel* self,GObject* target,GError** error) {
    if(!context(self,target,error))return FALSE;
    invalidate(*self);self->domain.clear();g_clear_object(&self->context);return TRUE;
}
gboolean warlock_visual_channel_close(WarlockVisualChannel* self,GError** error) {
    if(!owner(self,error))return FALSE;
    if(self->context || !self->packet.empty())return fail(error,WARLOCK_VISUAL_INVALID,"Original renderer must detach before channel destruction");
    delete self;return TRUE;
}
