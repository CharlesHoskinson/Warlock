#pragma once
#include "preview_client.hpp"

namespace preview::bridge {
inline Binding decodeBinding(JsonObject* object) {
    Json::fields(object,{"lifetime","session","frontend"});
    return {{decimal(Json::text(object,"lifetime"))},{decimal(Json::text(object,"session"))},{decimal(Json::text(object,"frontend"))}};
}
inline Context decodeContext(JsonObject* object) {
    Json::fields(object,{"lifetime","incarnation","output","privacy","rendering","scene","content"});
    return {{decimal(Json::text(object,"lifetime"))},{decimal(Json::text(object,"incarnation"))},{decimal(Json::text(object,"output"))},{decimal(Json::text(object,"privacy"))},{decimal(Json::text(object,"rendering"))},{decimal(Json::text(object,"scene"))},{decimal(Json::text(object,"content"))}};
}
inline Job decodeJob(JsonObject* object) {
    Json::fields(object,{"binding","context","request","origin","clock","deadline"});
    Job job{decodeBinding(Json::child(object,"binding")),decodeContext(Json::child(object,"context")),{decimal(Json::text(object,"request"))},{decimal(Json::text(object,"origin"))},{decimal(Json::text(object,"clock"))},decimal(Json::text(object,"deadline"))};
    require(job.binding.lifetime==job.context.lifetime,"Native job lifetime correlation");return job;
}
// JsonBuilder owns all intermediate nodes; counters never pass through doubles.
class Wire {
    JsonBuilder* builder_=json_builder_new();
public:
    Wire(){json_builder_begin_object(builder_);}
    ~Wire(){g_object_unref(builder_);}
    Wire(const Wire&)=delete;Wire& operator=(const Wire&)=delete;
    Wire& name(const char* key){json_builder_set_member_name(builder_,key);return *this;}
    Wire& text(const char* key,const std::string& value){name(key);json_builder_add_string_value(builder_,value.c_str());return *this;}
    Wire& counter(const char* key,uint64_t value){require(value>0,"Positive wire identity");return text(key,std::to_string(value));}
    Wire& integer(const char* key,int64_t value){name(key);json_builder_add_int_value(builder_,value);return *this;}
    Wire& boolean(const char* key,bool value){name(key);json_builder_add_boolean_value(builder_,value);return *this;}
    Wire& begin(const char* key){name(key);json_builder_begin_object(builder_);return *this;}
    Wire& end(){json_builder_end_object(builder_);return *this;}
    Wire& array(const char* key){name(key);json_builder_begin_array(builder_);return *this;}
    Wire& beginElement(){json_builder_begin_object(builder_);return *this;}
    Wire& element(const char* value){json_builder_add_string_value(builder_,value);return *this;}
    Wire& endArray(){json_builder_end_array(builder_);return *this;}
    Wire& binding(const Binding& b){counter("lifetime",b.lifetime.value).counter("session",b.session.value).counter("frontend",b.frontend.value);return *this;}
    Wire& context(const Context& c){counter("lifetime",c.lifetime.value).counter("incarnation",c.incarnation.value).counter("output",c.output.value).counter("privacy",c.privacy.value).counter("rendering",c.rendering.value).counter("scene",c.scene.value).counter("content",c.content.value);return *this;}
    Wire& job(const Job& j){begin("binding").binding(j.binding).end().begin("context").context(j.context).end().counter("request",j.request.value).counter("origin",j.origin.value).counter("clock",j.clock.value).counter("deadline",j.deadline);return *this;}
    std::string finish(){json_builder_end_object(builder_);auto root=json_builder_get_root(builder_);auto bytes=json_to_string(root,FALSE);std::string result(bytes);g_free(bytes);json_node_unref(root);return result;}
};
}
