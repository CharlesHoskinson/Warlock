#pragma once
#include "preview_wire.hpp"
namespace preview::bridge {
struct WindowMetadata {Binding binding;uint64_t subject,revision;std::string title,application;uint64_t delivery;};
inline std::string metadataLabel(JsonObject* object,const char* name) {
    std::string value=Json::text(object,name);
    require(value.size()<=1024 && g_utf8_validate(value.data(),value.size(),nullptr),"Native metadata label bound/UTF8");
    for(const char* p=value.c_str();*p;p=g_utf8_next_char(p))require(!g_unichar_iscntrl(g_utf8_get_char(p)),"Native metadata control characters");
    return value;
}
inline WindowMetadata decodeWindowMetadata(const Json& reply,const Binding& owner,uint64_t request,uint64_t subject) {
    auto object=reply.object();Json::fields(object,{"protocolVersion","kind","binding","requestId","sequence","revision","windows"});
    require(Json::integer(object,"protocolVersion")==3 && std::string_view(Json::text(object,"kind"))=="snapshot" && decodeBinding(Json::child(object,"binding"))==owner && reply.counter("requestId")==request,"Own native metadata response identity");
    (void)reply.counter("sequence");const auto revision=reply.counter("revision");
    auto node=json_object_get_member(object,"windows");require(node && JSON_NODE_HOLDS_ARRAY(node),"Native metadata window array");
    auto rows=json_node_get_array(node);require(json_array_get_length(rows)<=256 && subject>0,"Native metadata inventory bound");
    std::set<uint64_t> seen;std::optional<WindowMetadata> result;
    for(guint i=0;i<json_array_get_length(rows);++i) {
        auto row=json_array_get_element(rows,i);require(row && JSON_NODE_HOLDS_OBJECT(row),"Native metadata window shape");auto window=json_node_get_object(row);
        Json::fields(window,{"incarnation","application","label","minimized"});
        const auto id=decimal(Json::text(window,"incarnation"));require(seen.insert(id).second,"Unique native metadata incarnation");
        auto title=metadataLabel(window,"label"),application=metadataLabel(window,"application");(void)Json::boolean(window,"minimized");
        if(id==subject)result=WindowMetadata{owner,id,revision,std::move(title),std::move(application),request};
    }
    require(result.has_value(),"Metadata cannot borrow a replacement incarnation");return *result;
}
inline WindowMetadata windowMetadata(Native& native,uint64_t subject) {
    const auto request=native.next();auto reply=native.control("{\"protocolVersion\":3,\"kind\":\"snapshot-request\",\"binding\":"+native.bindingJSON()+",\"requestId\":\""+std::to_string(request)+"\",\"minimumWatermark\":\"0\"}");
    return decodeWindowMetadata(reply,native.binding(),request,subject);
}
}
