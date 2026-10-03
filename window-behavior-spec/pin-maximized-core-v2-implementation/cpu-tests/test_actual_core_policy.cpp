#include "desktop/state/pin/NativePinState.hpp"
#include "layout/algorithm/tiled/scrolling/ScrollingFullscreenHandler.hpp"
#include "desktop/state/FocusState.hpp"
#include <cassert>
#include <iostream>
using namespace Desktop::Pin;
int main() {
 int checks=0;auto check=[&](bool v){++checks;assert(v);};
 SAdmission max{true,true,true,true,false,true,1,1};check(admitsNative(max));
 for(int i=0;i<5;++i){auto s=max;switch(i){case 0:s.live=false;break;case 1:s.visible=false;break;case 2:s.normalSpace=false;break;case 3:s.restoreKnown=false;break;case 4:s.targetExact=false;}check(!admitsNative(s));}
 for(int mode:{-1,2,3}){auto s=max;s.internalMode=mode;check(!admitsNative(s));s=max;s.clientMode=mode;check(!admitsNative(s));}
 auto normal=max;normal.internalMode=0;check(!admitsNative(normal));normal.restoreOrigin=true;check(admitsNative(normal));
 check(retainsMaxPin(true,1,0,0));check(retainsMaxPin(true,0,1,1));check(!retainsMaxPin(false,1,0,0));check(!retainsMaxPin(true,1,2,1));
 check(preservesProtectedPeer(true,1));check(!preservesProtectedPeer(true,2));check(!preservesProtectedPeer(false,1));
 SFocusAcceptance accepted{true,true,true,true,true,true};check(acceptsFocus(accepted));
 for(int i=0;i<6;++i){auto s=accepted;switch(i){case 0:s.coreOwnerExact=false;break;case 1:s.coreSurfaceExact=false;break;case 2:s.seatSurfaceExact=false;break;case 3:s.keyboardPresent=false;break;case 4:s.guardsCurrent=false;break;case 5:s.ownerCurrent=false;}check(!acceptsFocus(s));}
 auto ordinary=orderBand({{1,-1},{2,-1},{3,-1}});check(ordinary&&*ordinary==std::vector<size_t>({0,1,2}));
 auto family=orderBand({{1,-1},{2,0},{3,-1},{4,1},{5,-1}});check(family&&*family==std::vector<size_t>({2,0,1,3,4}));
 auto reverse=*family;std::reverse(reverse.begin(),reverse.end());check(reverse==std::vector<size_t>({4,3,1,0,2}));
 check(!orderBand({{1,-1},{1,-1}}));check(!orderBand({{0,-1}}));check(!orderBand({{1,0}}));check(!orderBand({{1,1},{2,0}}));check(!orderBand({{1,2}}));
 std::vector<SBandNode> limit;for(int i=0;i<512;++i)limit.push_back({uintptr_t(i+1),-1});check(orderBand(limit)->size()==512);limit.push_back({513,-1});check(!orderBand(limit));
 std::cout<<checks<<" actual compiled core admission/focus/shared render-hit band checks passed\n";
 std::cout<<"ABI sizes/alignments: ";
#define ABI(TYPE) std::cout<<#TYPE<<"="<<sizeof(TYPE)<<":"<<alignof(TYPE)<<" ";
 ABI(SNativeMaxRestore) ABI(SNativeMaxTransfer) ABI(SNativeTransferOutcome) ABI(SNativeMaxProjection) ABI(Desktop::SWindowFocusResult)
 ABI(Fullscreen::IFullscreenHandler) ABI(Fullscreen::ScrollingFullscreenHandler::SFullscreenScrollState)
 ABI(Fullscreen::ScrollingFullscreenHandler::SNativeScrollRestore)
 std::cout<<"\n";
}
