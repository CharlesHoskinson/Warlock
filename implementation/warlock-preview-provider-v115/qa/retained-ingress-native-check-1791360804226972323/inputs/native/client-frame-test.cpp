#include "client_frame.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
int main(){try{
 unsigned checks=0;auto check=[&](bool ok){require(ok,"Client frame admission control");++checks;};
 ClientCapture c{{{1},{2},{3}},{{1},{4},{5},{6},{7},{8},{9}},10,100,200,320,240,16,4096,0};
 fd::Header h{};h[fd::Magic]=fd::MAGIC;h[fd::Version]=1;h[fd::Status]=0;
 h[fd::Lifetime]=1;h[fd::Session]=2;h[fd::Frontend]=3;h[fd::Request]=11;h[fd::Capture]=10;h[fd::Subject]=4;h[fd::Output]=5;
 h[fd::Completed]=100;h[fd::Now]=101;h[fd::Width]=320;h[fd::Height]=240;h[fd::Bytes]=16;h[fd::Charge]=4096;h[fd::Transfer]=12;
 h[fd::CRC]=0;h[fd::Privacy]=6;h[fd::Rendering]=7;h[fd::Scene]=8;h[fd::Content]=9;h[fd::Flags]=11;h[fd::Deadline]=200;h[fd::Expires]=500;
 check(clientFrameMatches(h,c));check(!fd::imageHeader(h));check(!fd::imageHeaderFor(h,fd::SourcePlane::Monitor));
 for(auto word:{fd::Magic,fd::Version,fd::Status,fd::Lifetime,fd::Session,fd::Frontend,fd::Capture,fd::Subject,fd::Output,fd::Completed,fd::Width,fd::Height,fd::Bytes,fd::Charge,fd::CRC,fd::Privacy,fd::Rendering,fd::Scene,fd::Content,fd::Deadline}){auto bad=h;++bad[word];check(!clientFrameMatches(bad,c));}
 for(auto flags:{0ULL,3ULL,4ULL,7ULL,8ULL,9ULL,10ULL,15ULL,27ULL}){auto bad=h;bad[fd::Flags]=flags;check(!clientFrameMatches(bad,c));}
 {auto bad=h;bad[fd::Now]=200;check(!clientFrameMatches(bad,c));}
 {auto monitor=h;monitor[fd::Flags]=7;check(fd::imageHeaderFor(monitor,fd::SourcePlane::Monitor));check(!clientFrameMatches(monitor,c));}
 const std::array<uint8_t,16> png{137,80,78,71,13,10,26,10,1,2,3,4,5,6,7,8};
 {fd::Mapped mapping(fd::seal(png),h,4096,fd::SourcePlane::ClientMain);check(mapping.png().size()==16 && mapping.charge()==4096);check(mapping.close() && mapping.png().empty() && mapping.charge()==4096);check(mapping.close());}
 bool refused=false;try{fd::Mapped wrong(fd::seal(png),h,4096);}catch(const std::invalid_argument&){refused=true;}check(refused);
 refused=false;try{fd::Mapped wrong(fd::seal(png),h,15,fd::SourcePlane::ClientMain);}catch(const std::invalid_argument&){refused=true;}check(refused);
 std::cout<<"{\"passed\":true,\"checks\":"<<checks<<"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
