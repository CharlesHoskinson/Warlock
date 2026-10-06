#include "preview_png.hpp"
#include <png.h>
#include <iostream>
using namespace preview;
using namespace preview::capture;
static void require(bool value,const char* name) {if(!value)throw std::runtime_error(name);}
static std::vector<uint8_t> decode(std::span<const uint8_t> encoded,uint32_t w,uint32_t h) {
    png_image image{};image.version=PNG_IMAGE_VERSION;
    require(png_image_begin_read_from_memory(&image,encoded.data(),encoded.size()),"libpng accepts independent PNG");
    struct Free {png_image& image;~Free(){png_image_free(&image);}} free{image};
    require(image.width==w && image.height==h,"decoded dimensions");image.format=PNG_FORMAT_RGBA;
    std::vector<uint8_t> out(PNG_IMAGE_SIZE(image));
    require(png_image_finish_read(&image,nullptr,out.data(),0,nullptr),"libpng completes PNG decoding");return out;
}
int main(){try {
 size_t count=0;auto check=[&](bool v,const char* name){require(v,name);++count;std::cerr<<"PASS "<<name<<'\n';};
 const auto p=*plan(2,2);
 check(!plan(0,1) && !plan(1,0) && !plan(4097,1) && !plan(1,4097) && !plan(UINT32_MAX,UINT32_MAX),"bounded dimensions and overflow rejection");
 check(p.peak==p.pixels*2+p.png && p.stride==8,"GPU CPU PNG preflight charge");
 std::vector<uint8_t> raw={0,0,255,255,99,22,11,0,7,7,7,7,255,0,0,255,64,32,16,128,9,9,9,9};
 const std::vector<uint8_t> expected={255,0,0,255,128,64,32,128,0,0,255,255,0,0,0,0};
 auto bytes=encodeRgba(raw,2,2,12,true,true);
 check(bytes.size()==p.png,"exact planned PNG allocation");
 check(decode(bytes,2,2)==expected,"bottom-up padded premultiplied samples decode correctly");
 auto normal=encodeRgba(expected,2,2,8,false,false);
 check(decode(normal,2,2)==expected,"top-down straight-alpha samples decode correctly");
 bool bad=false;try{encodeRgba(raw,2,2,7,false,false);}catch(const std::invalid_argument&){bad=true;}check(bad,"short stride rejected");
 bad=false;try{encodeRgba(std::span<const uint8_t>(raw).first(19),2,2,12,false,false);}catch(const std::invalid_argument&){bad=true;}check(bad,"short source span rejected");
 bad=false;try{encodeRgba(raw,0,2,12,false,false);}catch(const std::invalid_argument&){bad=true;}check(bad,"invalid encoder dimensions rejected");
 std::vector<uint8_t> large(257*73*4);for(size_t i=0;i<large.size();++i)large[i]=static_cast<uint8_t>((i*37+i/29)%256);
 auto blocks=encodeRgba(large,257,73,257*4,false,false);
 check(decode(blocks,257,73)==large,"multiple stored-deflate blocks decode correctly");
 auto corrupt=blocks;corrupt[corrupt.size()/2]^=1;
 png_image malformed{};malformed.version=PNG_IMAGE_VERSION;bool accepted=png_image_begin_read_from_memory(&malformed,corrupt.data(),corrupt.size());if(accepted){malformed.format=PNG_FORMAT_RGBA;std::vector<uint8_t> scratch(PNG_IMAGE_SIZE(malformed));accepted=png_image_finish_read(&malformed,nullptr,scratch.data(),0,nullptr);}png_image_free(&malformed);
 check(!accepted,"independent decoder detects corrupted data");
 Budget tight(p.peak-1,2);check(!tight.reserve(p.peak) && tight.used()==0 && tight.items()==0,"budget refusal precedes allocation");
 Budget limited(p.peak*3,1);{auto ticket=limited.reserve(p.peak);check(ticket.has_value(),"budget reservation admitted");check(!limited.reserve(p.peak),"global item bound enforced");}check(limited.used()==0 && limited.items()==0,"reservation rollback releases charge");
 Budget budget(p.peak*2,2);
 uri::Endpoint endpoint({1,3,2,p.peak*2},2,1,[](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{1},2};});
 Scope scope{{{1},{1},{1}},{{1},{1},{1},{1},{1},{1},{1}},{1},1};Job job{scope.binding,scope.context,{1},{1},{1},4};Token token{};
 endpoint.native([&](Broker& broker){require(broker.enroll(1,scope,p.peak),"actual broker enrollment");require(broker.acquire(1,scope.binding,job).status==Result::Status::Admitted,"actual broker admission before image allocation");auto ticket=budget.reserve(p.peak);require(ticket.has_value(),"native producer reservation");std::unique_ptr<const Buffer> image=std::make_unique<const OwnedPng>(std::move(*ticket),encodeRgba(raw,2,2,12,true,true),2,2);auto result=broker.allocate(1,job,image,10);require(!image && result.receipts.size()==1,"native broker adopts encoded ownership");token=result.receipts[0].packet->token;broker.producerComplete(1,job);});
 check(endpoint.registerView(1,scope.binding,{1}),"native view enrolled for valid image");
 auto input=endpoint.open(1,uri::encode(token),nullptr,nullptr);check(input!=nullptr,"native PNG stream opens");
 std::vector<uint8_t> streamed;std::array<uint8_t,11> chunk{};for(;;){const auto n=g_input_stream_read(input,chunk.data(),chunk.size(),nullptr,nullptr);require(n>=0,"native stream read succeeds");if(!n)break;streamed.insert(streamed.end(),chunk.begin(),chunk.begin()+n);}
 check(decode(streamed,2,2)==expected,"actual GInputStream image independently decodes");
 // Mutating/forgetting source raster cannot alter the separately owned result.
 raw.clear();raw.shrink_to_fit();auto stopped=scope;stopped.sourceLive=false;stopped.context.scene={2};
 endpoint.native([&](Broker& broker){require(broker.observe(1,stopped,p.peak),"native fixture observes source stop");});
 auto historical=endpoint.open(1,uri::encode(token),nullptr,nullptr);check(historical!=nullptr,"valid owned PNG survives fixture source stop");std::vector<uint8_t> retained;for(;;){const auto n=g_input_stream_read(historical,chunk.data(),chunk.size(),nullptr,nullptr);require(n>=0,"historical native stream read succeeds");if(!n)break;retained.insert(retained.end(),chunk.begin(),chunk.begin()+n);}check(decode(retained,2,2)==expected,"original source storage destroyed but historical PNG pixels unchanged");g_object_unref(historical);
 endpoint.native([&](Broker& broker){broker.cancel(1,scope.binding,job);});
 check(g_input_stream_read(input,chunk.data(),1,nullptr,nullptr)==-1,"revocation rejects existing valid image reader");
 endpoint.native([&](Broker& broker){check(!broker.consumerComplete(1,job),"live reader blocks physical image retirement");broker.destroy(1,job);});
 check(budget.used()==p.peak,"reader retains producer reservation");
 g_object_unref(input);check(budget.used()==p.peak,"reader finalization does not grant consumer fence");
 endpoint.native([&](Broker& broker){check(broker.consumerComplete(1,job),"native consumer completion after reader release");auto result=broker.destroy(1,job);check(result.status==Result::Status::Complete,"actual native image physically retired");require(!result.receipts.empty(),"physical release proof");require(broker.acknowledge(1,scope.binding,job,result.receipts.back().sequence),"acknowledge physical release proof");});
 check(budget.used()==0 && budget.items()==0,"retired image releases producer budget");
 std::cout<<"{\"passed\":true,\"checks\":"<<count<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
