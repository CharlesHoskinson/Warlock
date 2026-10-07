#include "preview_client.hpp"
#include "preview_metadata.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
static unsigned checks;
#define CHECK(name,expression) do{++checks;if(!(expression)){std::cerr<<name<<'\n';return 1;}}while(false)
static const Binding own{{1},{2},{3}};
static std::string row(std::string id="4",bool minimized=false,std::string label="Actual window") {
    return "{\"incarnation\":\""+id+"\",\"application\":\"org.warlock.fixture\",\"label\":\""+label+"\",\"minimized\":"+(minimized?"true":"false")+"}";
}
static std::string snapshot(std::string rows="",std::string revision="9007199254740993") {
    return "{\"protocolVersion\":3,\"kind\":\"snapshot\",\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"},\"requestId\":\"5\",\"sequence\":\"7\",\"revision\":\""+revision+"\",\"windows\":["+rows+"]}";
}
static bool refused(const std::string& wire,Binding binding=own,uint64_t request=5) {
    try{Json reply(wire);(void)decodeWindowCatalog(reply,binding,request);return false;}catch(const std::exception&){return true;}
}
static std::string replace(std::string value,const std::string& from,const std::string& to) {
    const auto found=value.find(from);if(found==std::string::npos)throw std::runtime_error("Fixture replacement missing");value.replace(found,from.size(),to);return value;
}
int main() {
    const auto wire=snapshot(row()+","+row("9007199254740995",true));Json reply(wire);auto catalog=decodeWindowCatalog(reply,own,5);
    CHECK("lossless own native catalog identity",catalog.binding==own && catalog.request==5 && catalog.sequence==7 && catalog.revision==9007199254740993ULL);
    CHECK("complete distinct source inventory",catalog.windows.size()==2 && catalog.windows[0].subject==4 && catalog.windows[1].subject==9007199254740995ULL);
    CHECK("actual minimized Booleans retained",!catalog.windows[0].minimized && catalog.windows[1].minimized);
    CHECK("row correlation retained without a capture job",catalog.windows[1].binding==own && catalog.windows[1].delivery==5 && catalog.windows[1].revision==catalog.revision && catalog.windows[1].title=="Actual window");
    CHECK("single-source metadata retains minimized fact",decodeWindowMetadata(reply,own,5,9007199254740995ULL).minimized);
    Json empty(snapshot());CHECK("empty own catalog is valid metadata",decodeWindowCatalog(empty,own,5).windows.empty());
    bool missing=false;try{(void)decodeWindowMetadata(reply,own,5,6);}catch(const std::exception&){missing=true;}CHECK("missing subject cannot borrow metadata",missing);
    CHECK("foreign binding refused",refused(wire,{{1},{2},{9}}));CHECK("foreign request refused",refused(wire,own,6));
    CHECK("Boolean protocol refused",refused(replace(wire,"\"protocolVersion\":3","\"protocolVersion\":true")));
    CHECK("zero sequence refused",refused(replace(wire,"\"sequence\":\"7\"","\"sequence\":\"0\"")));
    CHECK("numeric revision refused",refused(replace(wire,"\"revision\":\"9007199254740993\"","\"revision\":9007199254740993")));
    CHECK("extra envelope field refused",refused(replace(wire,"\"windows\":","\"scope\":{},\"windows\":")));
    CHECK("duplicate incarnation refuses whole catalog",refused(snapshot(row()+","+row("4",true))));CHECK("zero incarnation refused",refused(snapshot(row("0"))));
    CHECK("noncanonical incarnation refused",refused(snapshot(row("04"))));CHECK("overflow incarnation refused",refused(snapshot(row("18446744073709551616"))));
    CHECK("extra window field refused",refused(snapshot(replace(row(),"\"minimized\":","\"clock\":\"1\",\"minimized\":"))));
    CHECK("string minimized refused",refused(snapshot(replace(row(),"\"minimized\":false","\"minimized\":\"false\""))));
    CHECK("oversized label refused",refused(snapshot(row("4",false,std::string(1025,'a')))));
    CHECK("decoded control character refused",refused(snapshot(row("4",false,"old\\nprivate"))));
    CHECK("foreign malformed row cannot bypass whole admission",refused(snapshot(row()+","+replace(row("6"),"\"minimized\":false","\"minimized\":1"))));
    Json unicode(snapshot(row("4",false,"Κατάλογος")));CHECK("valid UTF8 native title retained",decodeWindowCatalog(unicode,own,5).windows[0].title=="Κατάλογος");
    Json maximum(snapshot(row("18446744073709551615"),"18446744073709551615"));auto maxCatalog=decodeWindowCatalog(maximum,own,5);CHECK("maximum counters retained without arithmetic",maxCatalog.windows[0].subject==UINT64_MAX && maxCatalog.revision==UINT64_MAX);
    std::string rows;for(unsigned i=1;i<=256;++i){if(i>1)rows+=',';rows+=row(std::to_string(i));}Json bounded(snapshot(rows));CHECK("original256 inventory bound retained",decodeWindowCatalog(bounded,own,5).windows.size()==256);
    CHECK("257th record refused",refused(snapshot(rows+","+row("257"))));
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}
