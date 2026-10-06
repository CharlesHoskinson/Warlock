#include "family_frame.hpp"
#include <iostream>

int main(){using namespace preview;using namespace preview::bridge;try {
    unsigned checks=0;auto check=[&](bool value){require(value,"Native family frame correlation control");++checks;};
    FamilyCapture c{{{1},{2},{3}},{{1},{4},{5},{6},{7},{8},{9}},10,100,200,320,240,16,4096,0,{-35,17,320,240,1.5}};
    stylecropfd::Header h{};h[fd::Magic]=fd::MAGIC;h[fd::Version]=3;h[fd::Lifetime]=1;h[fd::Session]=2;h[fd::Frontend]=3;h[fd::Request]=11;h[fd::Capture]=10;h[fd::Subject]=4;h[fd::Output]=5;h[fd::Completed]=100;h[fd::Now]=101;h[fd::Width]=320;h[fd::Height]=240;h[fd::Bytes]=16;h[fd::Charge]=4096;h[fd::Transfer]=12;h[fd::CRC]=0;h[fd::Privacy]=6;h[fd::Rendering]=7;h[fd::Scene]=8;h[fd::Content]=9;h[fd::Flags]=131;h[fd::Deadline]=200;h[fd::Expires]=500;h[stylecropfd::PixelX]=std::bit_cast<uint64_t>(int64_t{-35});h[stylecropfd::PixelY]=17;h[stylecropfd::Scale]=std::bit_cast<uint64_t>(1.5);
    check(familyFrameMatches(h,c));
    for(auto word:{fd::Magic,fd::Version,fd::Status,fd::Lifetime,fd::Session,fd::Frontend,fd::Capture,fd::Subject,fd::Output,fd::Completed,fd::Width,fd::Height,fd::Bytes,fd::Charge,fd::CRC,fd::Privacy,fd::Rendering,fd::Scene,fd::Content,fd::Deadline}){auto bad=h;++bad[word];check(!familyFrameMatches(bad,c));}
    for(auto flags:{0ULL,3ULL,7ULL,11ULL,35ULL,67ULL,128ULL,129ULL,130ULL,255ULL}){auto bad=h;bad[fd::Flags]=flags;check(!familyFrameMatches(bad,c));}
    for(auto word:{stylecropfd::PixelX,stylecropfd::PixelY,stylecropfd::Scale}){auto bad=h;++bad[word];check(!familyFrameMatches(bad,c));}
    {auto bad=h;bad[fd::Now]=c.deadline;check(!familyFrameMatches(bad,c));}
    {auto bad=h;bad[fd::Expires]=bad[fd::Now];check(!familyFrameMatches(bad,c));}
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"nativeAcceptance\":false}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
