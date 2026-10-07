#include "client-producer.h"
#include "client_producer.hpp"
#include "family_producer.hpp"
#include "preview_icons.hpp"
struct WarlockClientProducer {
 preview::bridge::Native::LegacyPreviewClaim legacyClaim;
 std::unique_ptr<preview::bridge::ClientProducer> client;
 std::unique_ptr<preview::bridge::FamilyProducer> family;
 preview::bridge::Native& native;
 const uint64_t popup,subject;
 preview::bridge::WindowMetadata metadata;
 preview::icons::Endpoint icons;
 std::optional<std::string> icon;
 std::string iconKind="unavailable";
 GtkIconTheme* iconTheme=nullptr;
 gulong iconThemeHandler{};
 bool iconThemeDirty=true;
 static void iconThemeChanged(GtkIconTheme*,gpointer owner){static_cast<WarlockClientProducer*>(owner)->iconThemeDirty=true;}
 ~WarlockClientProducer(){if(iconThemeHandler)g_signal_handler_disconnect(iconTheme,iconThemeHandler);g_clear_object(&iconTheme);}

 std::string decorate(const std::string& events,bool refresh=false) {
  using namespace preview::bridge;
  Json envelope("{\"events\":"+events+"}");auto rows=json_object_get_array_member(envelope.object(),"events");
  bool seeded=false;
  for(guint i=0;i<json_array_get_length(rows);++i) {
   auto node=json_array_get_element(rows,i);require(node && JSON_NODE_HOLDS_OBJECT(node),"Own native event batch");auto row=json_node_get_object(node);
   if(std::string_view(Json::text(row,"kind"))=="source-seed")seeded=true;
  }
  if(!seeded && !refresh)return events;
  bool changed=seeded;
  // Metadata failure cannot suppress original source/cleanup/receipt events or
  // classify an unknown transport outcome as a source denial.
  try {
   auto fresh=windowMetadata(native,subject);
   require(fresh.revision>=metadata.revision,"Native metadata revision cannot regress");
   changed=seeded || iconThemeDirty || fresh.title!=metadata.title || fresh.application!=metadata.application;
   metadata=std::move(fresh);
   if(changed) {
    iconThemeDirty=false;
    const auto scope=native.clientScope({subject}).scope;
    icon.reset();iconKind="unavailable";
    if(scope.present && !scope.locked)if(auto asset=preview::icons::resolveApplication(metadata.application)) {iconKind=asset->kind;icon=icons.issue(metadata,scope,std::move(*asset));if(!icon)iconKind="unavailable";}
   }
  }catch(const std::exception&) {if(!seeded)return events;icon.reset();iconKind="unavailable";}
  if(!changed)return events;
  for(guint i=0;i<json_array_get_length(rows);++i) {
   auto row=json_node_get_object(json_array_get_element(rows,i));
   if(std::string_view(Json::text(row,"kind"))=="source-seed") {
    require(std::string_view(Json::text(row,"identity"))=="family:"+std::to_string(subject),"Own metadata seed subject");
    json_object_set_string_member(row,"title",metadata.title.c_str());json_object_set_string_member(row,"application",metadata.application.c_str());
   }
  }
  Wire wire;wire.text("kind","metadata").text("identity","family:"+std::to_string(subject)).begin("binding").binding(metadata.binding).end().counter("subject",subject).counter("revision",metadata.delivery).text("title",metadata.title).text("application",metadata.application).text("iconKind",iconKind);
  wire.text("icon",icon.value_or(""));Json record(wire.finish());
  if(!icon)json_object_set_null_member(record.object(),"icon");
  json_array_add_element(rows,json_node_copy(json_parser_get_root(record.parser)));
  char* raw=json_to_string(json_object_get_member(envelope.object(),"events"),FALSE);std::string result(raw);g_free(raw);return result;
 }

 WarlockClientProducer(preview::bridge::Native& owner,uint64_t view,uint64_t incarnation,uint64_t publication,uint64_t lease,bool useFamily=false,preview::bridge::FamilyPlane plane=preview::bridge::FamilyPlane::Transparent):legacyClaim(owner),native(owner),popup(view),subject(incarnation),metadata(preview::bridge::windowMetadata(owner,incarnation)),icons(view,owner.binding(),incarnation,[this](const preview::icons::Record& record){
  const auto scope=native.clientScope({subject}).scope;
  return scope.present && !scope.locked && scope.binding==record.metadata.binding && scope.context.incarnation.value==record.metadata.subject && scope.context.privacy.value==record.privacy && preview::bridge::windowMetadata(native,subject).application==record.metadata.application;
 }) {
  if(useFamily)family=std::make_unique<preview::bridge::FamilyProducer>(owner,view,incarnation,publication,lease,plane);else client=std::make_unique<preview::bridge::ClientProducer>(owner,view,incarnation,publication,lease);
  iconTheme=gtk_icon_theme_get_default();if(iconTheme){g_object_ref(iconTheme);iconThemeHandler=g_signal_connect(iconTheme,"changed",G_CALLBACK(iconThemeChanged),this);}
 }
 template<class F> auto visit(F&& call){if(family)return call(*family);return call(*client);}
};
namespace {
template<class F> gboolean output(WarlockClientProducer* owner,char** events,GError** error,F call,bool refresh=false) {
    if(events)*events=nullptr;
    try {preview::bridge::require(owner && events,"Own native client producer output");*events=g_strdup(owner->decorate(owner->visit(call),refresh).c_str());return TRUE;}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
}
extern "C" WarlockClientProducer* warlock_client_producer_open(void* native,gpointer popup,guint64 subject,guint64 publication,guint64 lease,char** initial,void** endpoint,GError** error) {
    if(initial)*initial=nullptr;
    if(endpoint)*endpoint=nullptr;
    try {preview::bridge::require(native && popup && initial && endpoint,"Trusted client producer enrollment");auto owner=std::make_unique<WarlockClientProducer>(*static_cast<preview::bridge::Native*>(native),reinterpret_cast<uintptr_t>(popup),subject,publication,lease);*initial=g_strdup(owner->decorate(owner->visit([](auto& value){return value.initial();})).c_str());*endpoint=owner->visit([](auto& value){return &value.endpoint();});return owner.release();}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return nullptr;}
}
extern "C" WarlockClientProducer* warlock_family_producer_open(void* native,gpointer popup,guint64 subject,guint64 publication,guint64 lease,char** initial,void** endpoint,GError** error) {
    if(initial)*initial=nullptr;
    if(endpoint)*endpoint=nullptr;
    try {preview::bridge::require(native && popup && initial && endpoint,"Trusted client producer enrollment");auto owner=std::make_unique<WarlockClientProducer>(*static_cast<preview::bridge::Native*>(native),reinterpret_cast<uintptr_t>(popup),subject,publication,lease,true);*initial=g_strdup(owner->decorate(owner->visit([](auto& value){return value.initial();})).c_str());*endpoint=owner->visit([](auto& value){return &value.endpoint();});return owner.release();}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return nullptr;}
}
extern "C" WarlockClientProducer* warlock_backdrop_producer_open(void* native,gpointer popup,guint64 subject,guint64 publication,guint64 lease,char** initial,void** endpoint,GError** error) {
    if(initial)*initial=nullptr;
    if(endpoint)*endpoint=nullptr;
    try {preview::bridge::require(native && popup && initial && endpoint,"Trusted client producer enrollment");auto owner=std::make_unique<WarlockClientProducer>(*static_cast<preview::bridge::Native*>(native),reinterpret_cast<uintptr_t>(popup),subject,publication,lease,true,preview::bridge::FamilyPlane::GeneratedBackdrop);*initial=g_strdup(owner->decorate(owner->visit([](auto& value){return value.initial();})).c_str());*endpoint=owner->visit([](auto& value){return &value.endpoint();});return owner.release();}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return nullptr;}
}
extern "C" gboolean warlock_client_producer_command(WarlockClientProducer* owner,const char* identity,const char* command,char** events,GError** error) {
    return output(owner,events,error,[&](auto& value){preview::bridge::require(identity && command,"Native client command wire");return value.command(identity,command);});
}
extern "C" gboolean warlock_client_producer_poll(WarlockClientProducer* owner,guint64 publication,guint64 lease,char** events,GError** error) {return output(owner,events,error,[&](auto& value){return value.poll(publication,lease);},publication && lease);}
extern "C" gboolean warlock_client_producer_resume(WarlockClientProducer* owner,guint64 publication,guint64 lease,char** events,GError** error) {return output(owner,events,error,[&](auto& value){return value.resume(publication,lease);});}
extern "C" guint64 warlock_client_producer_lease(WarlockClientProducer* owner) {return owner?owner->visit([](auto& value){return value.lease();}):0;}
extern "C" guint64 warlock_client_producer_request(WarlockClientProducer* owner) {return owner?owner->visit([](auto& value){return value.job().request.value;}):0;}
extern "C" gboolean warlock_client_producer_uri(WarlockClientProducer* owner,char** uri,GError** error) {if(uri)*uri=nullptr;
    try {preview::bridge::require(owner && uri,"Own URI output");*uri=g_strdup(owner->visit([](auto& value){return value.currentURI();}).c_str());return TRUE;}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}}
extern "C" gboolean warlock_client_producer_empty(WarlockClientProducer* owner) {return owner && owner->icons.readers()==0 && owner->visit([](auto& value){return value.empty();});}
extern "C" gboolean warlock_client_producer_status(WarlockClientProducer* owner,char** status,GError** error) {if(status)*status=nullptr;
    try {preview::bridge::require(owner && status,"Own status output");*status=g_strdup(owner->visit([](auto& value){return value.status();}).c_str());return TRUE;}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}}
extern "C" GInputStream* warlock_client_producer_stream(WarlockClientProducer* owner,gpointer popup,const char* uri,gsize* length,GError** error) {
    if(length)*length=0;
    try {
        preview::bridge::require(owner && popup && uri && length,"Own preview reader receiver");
        return owner->visit([&](auto& value){return value.endpoint().open(reinterpret_cast<uintptr_t>(popup),uri,length,error);});
    } catch(const std::exception& exception) {g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return nullptr;}
}
extern "C" gboolean warlock_client_producer_close(WarlockClientProducer* owner,GError** error) {
    if(!owner)return TRUE;
    try {
        preview::bridge::require(owner->icons.readers()==0 && owner->visit([](auto& value){return value.close();}),"Outstanding physical client/journal ownership at host teardown");
        preview::bridge::require(owner->icons.close(),"Outstanding physical icon ownership at host teardown");
        g_print("native-icon-retired: %s\n",owner->icons.status().c_str());fflush(stdout);
        delete owner;return TRUE;
    }
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}

extern "C" GInputStream* warlock_client_producer_icon_stream(WarlockClientProducer* owner,gpointer view,const char* uri,gsize* length,GError** error) {
    if(length)*length=0;
    try {preview::bridge::require(owner && view && uri && length,"Own icon receiver");return owner->icons.open(reinterpret_cast<uintptr_t>(view),uri,length,error);}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return nullptr;}
}
extern "C" gboolean warlock_client_producer_icon_status(WarlockClientProducer* owner,char** status,GError** error) {
    if(status)*status=nullptr;
    try {preview::bridge::require(owner && status,"Own icon status");*status=g_strdup(owner->icons.status().c_str());return TRUE;}
    catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
extern "C" gboolean warlock_client_producer_icon_uri(WarlockClientProducer* owner,char** uri,GError** error) {
    if(uri)*uri=nullptr;
    try {
        preview::bridge::require(owner && uri && owner->icon.has_value(),"Own current native icon token");
        *uri=g_strdup(("elm-shell://icon/"+*owner->icon).c_str());return TRUE;
    }catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
extern "C" gboolean warlock_client_producer_locked(WarlockClientProducer* owner,gboolean* locked,GError** error) {
    if(locked)*locked=FALSE;
    try {
        preview::bridge::require(owner && locked,"Own authenticated native lock observation");
        try {*locked=owner->native.clientScope({owner->subject}).scope.locked;return TRUE;}
        catch(const preview::bridge::ScopeDenied& denied) {
            preview::bridge::require(denied.binding==owner->native.binding() && denied.subject.value==owner->subject && denied.reason==preview::bridge::SourceDenial::Locked,"Exact owning locked-source denial");
            *locked=TRUE;return TRUE;
        }
    }catch(const std::exception& exception){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,exception.what());return FALSE;}
}
