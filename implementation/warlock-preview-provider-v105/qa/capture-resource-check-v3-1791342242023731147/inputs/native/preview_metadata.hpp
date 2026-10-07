#pragma once
#include "preview_wire.hpp"
#include <algorithm>
#include <vector>
namespace preview::bridge {
struct WindowMetadata {Binding binding;uint64_t subject,revision;std::string title,application;uint64_t delivery;bool minimized=false;};
// Catalog identity is metadata authority only. No scope, clock, capture job,
// resource owner or denial is inferred from inventory membership.
struct WindowCatalog {Binding binding;uint64_t request,sequence,revision;std::vector<WindowMetadata> windows;};
inline std::string metadataLabel(JsonObject* object,const char* name) {
    std::string value=Json::text(object,name);
    require(value.size()<=1024 && g_utf8_validate(value.data(),value.size(),nullptr),"Native metadata label bound/UTF8");
    for(const char* p=value.c_str();*p;p=g_utf8_next_char(p))require(!g_unichar_iscntrl(g_utf8_get_char(p)),"Native metadata control characters");
    return value;
}
inline WindowCatalog decodeWindowCatalog(const Json& reply,const Binding& owner,uint64_t request) {
    auto object=reply.object();Json::fields(object,{"protocolVersion","kind","binding","requestId","sequence","revision","windows"});
    require(Json::integer(object,"protocolVersion")==3 && std::string_view(Json::text(object,"kind"))=="snapshot" && decodeBinding(Json::child(object,"binding"))==owner && reply.counter("requestId")==request,"Own native metadata response identity");
    const auto sequence=reply.counter("sequence"),revision=reply.counter("revision");
    auto node=json_object_get_member(object,"windows");require(node && JSON_NODE_HOLDS_ARRAY(node),"Native metadata window array");
    auto rows=json_node_get_array(node);require(json_array_get_length(rows)<=256,"Native metadata inventory bound");
    std::set<uint64_t> seen;WindowCatalog result{owner,request,sequence,revision,{}};result.windows.reserve(json_array_get_length(rows));
    for(guint i=0;i<json_array_get_length(rows);++i) {
        auto row=json_array_get_element(rows,i);require(row && JSON_NODE_HOLDS_OBJECT(row),"Native metadata window shape");auto window=json_node_get_object(row);
        Json::fields(window,{"incarnation","application","label","minimized"});
        const auto id=decimal(Json::text(window,"incarnation"));require(seen.insert(id).second,"Unique native metadata incarnation");
        auto title=metadataLabel(window,"label"),application=metadataLabel(window,"application");const auto minimized=Json::boolean(window,"minimized");
        result.windows.push_back({owner,id,revision,std::move(title),std::move(application),request,minimized});
    }
    return result;
}
inline WindowMetadata decodeWindowMetadata(const Json& reply,const Binding& owner,uint64_t request,uint64_t subject) {
    require(subject>0,"Native metadata inventory bound");const auto catalog=decodeWindowCatalog(reply,owner,request);
    auto found=std::find_if(catalog.windows.begin(),catalog.windows.end(),[&](const auto& row){return row.subject==subject;});
    require(found!=catalog.windows.end(),"Metadata cannot borrow a replacement incarnation");return *found;
}
inline WindowCatalog windowCatalog(Native& native) {
    const auto request=native.next();auto reply=native.control("{\"protocolVersion\":3,\"kind\":\"snapshot-request\",\"binding\":"+native.bindingJSON()+",\"requestId\":\""+std::to_string(request)+"\",\"minimumWatermark\":\"0\"}");
    return decodeWindowCatalog(reply,native.binding(),request);
}
inline WindowMetadata windowMetadata(Native& native,uint64_t subject) {
    require(subject>0,"Native metadata inventory bound");const auto catalog=windowCatalog(native);
    auto found=std::find_if(catalog.windows.begin(),catalog.windows.end(),[&](const auto& row){return row.subject==subject;});
    require(found!=catalog.windows.end(),"Metadata cannot borrow a replacement incarnation");return *found;
}
}
