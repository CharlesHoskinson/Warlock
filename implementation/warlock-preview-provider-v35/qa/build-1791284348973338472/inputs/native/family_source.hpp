#pragma once
#include "preview_wire.hpp"
#include <cmath>

namespace preview::bridge {
enum class FamilyPlane { Transparent, GeneratedBackdrop };
struct FamilyCrop { int32_t x{},y{};uint32_t width{},height{};double scale{}; };
struct FamilyMember { uint64_t id{},parent{},content{},order{},flags{};std::array<double,8> geometry{}; };
struct FamilyGradient { double angle{};uint64_t colors{}; };
struct FamilyStyle { uint64_t id{},flags{};std::array<double,18> channels{};std::array<FamilyGradient,6> gradients{}; };
struct FamilySourceObservation {
    Scope scope;uint64_t observation{},request{},maximumTransferBytes{};
    FamilyCrop crop;std::vector<FamilyMember> members;std::vector<FamilyStyle> styles;
    std::string wire;
    FamilyPlane plane{FamilyPlane::Transparent};std::optional<uint32_t> generatedColor{};
};
inline double familyNumber(JsonNode* node) {
    require(node && JSON_NODE_HOLDS_VALUE(node),"Native family number");
    const auto type=json_node_get_value_type(node);require(type==G_TYPE_INT64 || type==G_TYPE_DOUBLE,"Typed native family number");
    const double value=json_node_get_double(node);require(std::isfinite(value),"Finite native family number");return value;
}
inline JsonArray* familyArray(JsonObject* object,const char* name) {
    auto node=json_object_get_member(object,name);require(node && JSON_NODE_HOLDS_ARRAY(node),"Native family array");return json_node_get_array(node);
}
template<size_t Size> inline std::array<double,Size> familyNumbers(JsonObject* object,const char* name) {
    const auto values=familyArray(object,name);require(json_array_get_length(values)==Size,"Native family fixed vector");std::array<double,Size> result{};
    for(size_t i=0;i<Size;++i)result[i]=familyNumber(json_array_get_element(values,i));
    return result;
}
inline uint64_t familyInteger(JsonObject* object,const char* name,uint64_t maximum) {
    const auto value=Json::integer(object,name);require(value>=0 && static_cast<uint64_t>(value)<=maximum,"Native family integer range");return static_cast<uint64_t>(value);
}
inline int32_t familyPixel(JsonObject* object,const char* name) {
    const std::string_view text=Json::text(object,name);int32_t value{};const auto parsed=std::from_chars(text.data(),text.data()+text.size(),value);
    require(!text.empty() && parsed.ec==std::errc{} && parsed.ptr==text.data()+text.size() && std::to_string(value)==text,"Canonical signed native crop origin");return value;
}
inline FamilySourceObservation decodeFamilySource(const Json& reply,Binding owner,Id<Incarnation> subject,uint64_t request,FamilyPlane plane=FamilyPlane::Transparent) {
    const bool backdrop=plane==FamilyPlane::GeneratedBackdrop;
    auto object=reply.object();if(backdrop)Json::fields(object,{"protocolVersion","kind","binding","requestId","scope","maximumTransferBytes","previewEligible","scopeKind","members","styles","crop","generatedBackdrop"});else Json::fields(object,{"protocolVersion","kind","binding","requestId","scope","maximumTransferBytes","previewEligible","scopeKind","members","styles","crop"});
    require(Json::integer(object,"protocolVersion")==3 && std::string_view(Json::text(object,"kind"))==(backdrop?"preview-family-backdrop-crop-scope":"preview-family-style-crop-scope") && std::string_view(Json::text(object,"scopeKind"))==(backdrop?"native-generated-backdrop-family-crop-unqualified":"native-family-style-crop-channels-unqualified") && !Json::boolean(object,"previewEligible"),"Distinct unqualified native family source");
    require(owner.lifetime.value && owner.session.value && owner.frontend.value && subject.value && request && decodeBinding(Json::child(object,"binding"))==owner && reply.counter("requestId")==request,"Own native family envelope correlation");
    auto raw=Json::child(object,"scope");Json::fields(raw,{"binding","context","observation","clock","now","present","sourceLive","locked","gpuReady"});
    const auto context=decodeContext(Json::child(raw,"context"));Scope scope{decodeBinding(Json::child(raw,"binding")),context,{decimal(Json::text(raw,"clock"))},decimal(Json::text(raw,"now")),Json::boolean(raw,"present"),Json::boolean(raw,"sourceLive"),Json::boolean(raw,"locked"),Json::boolean(raw,"gpuReady")};
    require(scope.binding==owner && context.lifetime==owner.lifetime && context.incarnation==subject && scope.clock.value==owner.lifetime.value,"Own native family scope subject/clock");
    FamilySourceObservation result;result.plane=plane;
    if(backdrop) {
        auto color=Json::child(object,"generatedBackdrop");Json::fields(color,{"kind","colorARGB"});
        const auto value=decimal(Json::text(color,"colorARGB"));require(std::string_view(Json::text(color,"kind"))=="native-opaque-generated-color" && value<=UINT32_MAX && (value>>24)==255,"Typed opaque generated backdrop color");result.generatedColor=static_cast<uint32_t>(value);
    }
    result.scope=scope;result.request=request;result.observation=decimal(Json::text(raw,"observation"));result.maximumTransferBytes=reply.counter("maximumTransferBytes");
    require(result.maximumTransferBytes%4096==0 && result.maximumTransferBytes<=128ULL*1024*1024,"Original native transfer capacity");
    auto crop=Json::child(object,"crop");Json::fields(crop,{"pixelX","pixelY","width","height","scale"});result.crop={familyPixel(crop,"pixelX"),familyPixel(crop,"pixelY"),static_cast<uint32_t>(familyInteger(crop,"width",4096)),static_cast<uint32_t>(familyInteger(crop,"height",4096)),familyNumber(json_object_get_member(crop,"scale"))};
    require(result.crop.width && result.crop.height && result.crop.scale>0,"Positive native crop extent/scale");
    auto members=familyArray(object,"members");auto styles=familyArray(object,"styles");const auto count=json_array_get_length(members);
    require(count>0 && count<=256 && json_array_get_length(styles)==count,"Bounded exact native member/style domain");
    std::set<uint64_t> ids,styleIds;
    for(guint i=0;i<count;++i) {
        auto node=json_array_get_element(members,i);require(node && JSON_NODE_HOLDS_OBJECT(node),"Native family member object");auto row=json_node_get_object(node);Json::fields(row,{"incarnation","parent","content","renderOrder","flags","geometry"});
        FamilyMember member;member.id=decimal(Json::text(row,"incarnation"));member.content=decimal(Json::text(row,"content"));member.order=familyInteger(row,"renderOrder",INT32_MAX);member.flags=familyInteger(row,"flags",511);member.geometry=familyNumbers<8>(row,"geometry");
        auto parent=json_object_get_member(row,"parent");require(parent,"Native member parent field");if(!JSON_NODE_HOLDS_NULL(parent))member.parent=decimal(Json::text(row,"parent"));
        require(ids.insert(member.id).second && member.parent!=member.id,"Unique native family members");result.members.push_back(member);
        node=json_array_get_element(styles,i);require(node && JSON_NODE_HOLDS_OBJECT(node),"Native family style object");row=json_node_get_object(node);Json::fields(row,{"incarnation","flags","channels","gradients"});FamilyStyle style;style.id=decimal(Json::text(row,"incarnation"));style.flags=familyInteger(row,"flags",4095);style.channels=familyNumbers<18>(row,"channels");require(styleIds.insert(style.id).second,"Unique native family style identities");
        auto gradients=familyArray(row,"gradients");require(json_array_get_length(gradients)==6,"Native gradient shape");
        for(guint index=0;index<6;++index){node=json_array_get_element(gradients,index);require(node && JSON_NODE_HOLDS_OBJECT(node),"Native gradient object");row=json_node_get_object(node);Json::fields(row,{"angle","colors"});style.gradients[index]={familyNumber(json_object_get_member(row,"angle")),familyInteger(row,"colors",65536)};}
        result.styles.push_back(style);
    }
    require(ids==styleIds && ids.contains(subject.value),"Exact native family style membership");
    for(const auto& member:result.members) {
        uint64_t current=member.id;bool reached=false;
        for(size_t steps=0;steps<result.members.size();++steps) {
            auto row=std::find_if(result.members.begin(),result.members.end(),[&](const auto& value){return value.id==current;});require(row!=result.members.end(),"Native parent remains in family");
            if(current==subject.value){require(!row->parent,"Native family root remains root");reached=true;break;}
            require(row->parent,"Every native family member reaches root");current=row->parent;
        }
        require(reached,"Native family parent graph has no cycle");
    }
    gchar* encoded=json_to_string(json_parser_get_root(reply.parser),FALSE);require(encoded,"Native family source encoding");result.wire=encoded;g_free(encoded);
    return result;
}
inline FamilySourceObservation observeFamilySource(Native& native,Id<Incarnation> subject,FamilyPlane plane=FamilyPlane::Transparent) {
    Deadline deadline;const auto owner=native.binding();const auto request=native.next();
    Wire wire;wire.integer("protocolVersion",3).text("kind",plane==FamilyPlane::GeneratedBackdrop?"preview-family-backdrop-crop-scope-request":"preview-family-style-crop-scope-request").begin("binding").binding(owner).end().counter("requestId",request).counter("subjectIncarnation",subject.value);
    auto reply=native.controlWithin(wire.finish(),deadline);
    if(const auto denied=decodeSourceDenial(reply))throw ScopeDenied(owner,subject,request,*denied);
    if(std::string_view(Json::text(reply.object(),"kind"))=="refused") {
        Json::fields(reply.object(),{"protocolVersion","kind","reason"});
        if(std::string_view(Json::text(reply.object(),"reason"))==(plane==FamilyPlane::GeneratedBackdrop?"preview-family-backdrop-crop-unavailable":"preview-family-style-crop-unavailable"))throw ScopeDenied(owner,subject,request,SourceDenial::LayoutUnsupported);
    }
    auto result=decodeFamilySource(reply,owner,subject,request,plane);require(native.binding()==owner,"Native family grant still current");deadline.check();return result;
}
}
