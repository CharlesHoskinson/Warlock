#include "captionCache.hpp"
#include <cassert>
#include <functional>
#include <iostream>
#include <memory>
#include <vector>
using namespace CaptionCache;
int main(){
 int checks=0;
 TitleKey k{1,200,28,12,400,180,5,3,"title","sans","left",{1,.5,0,1}};
 Raster<TitleKey,std::shared_ptr<int>> r;r.store(k,std::make_shared<int>(1));
 std::vector<std::function<void(TitleKey&)>> titleChanges={
 [](auto& x){x.scale=1.5;},[](auto& x){x.bufferWidth++;},[](auto& x){x.bufferHeight++;},[](auto& x){x.pixelSize++;},[](auto& x){x.weight++;},[](auto& x){x.maxWidth++;},[](auto& x){x.padding++;},[](auto& x){x.buttonPadding++;},[](auto& x){x.text+="new";},[](auto& x){x.font+="new";},[](auto& x){x.align="right";},[](auto& x){x.color[0]+=.1;},[](auto& x){x.color[1]+=.1;},[](auto& x){x.color[2]+=.1;},[](auto& x){x.color[3]-=.1;}};
 for(const auto& change:titleChanges){auto other=k;change(other);assert(!r.matches(other));++checks;}
 auto normal=r;{auto saved=r;RestoreScope guard([&]{r=saved;},true);auto x=k;x.scale=1.5;r.store(x,std::make_shared<int>(2));assert(r.matches(x));}assert(r.key==normal.key && r.texture==normal.texture);++checks;
 try{auto saved=r;RestoreScope guard([&]{r=saved;},true);auto x=k;x.scale=2;r.store(x,std::make_shared<int>(3));throw 1;}catch(int){}assert(r.key==normal.key && r.texture==normal.texture);++checks;
 for(double scale:{1.,1.5,1.}){auto x=k;x.scale=scale;if(!r.matches(x))r.store(x,std::make_shared<int>(4));assert(r.key->scale==scale);++checks;}
 auto unchanged=r.texture;assert(r.matches(k));assert(r.texture==unchanged);++checks;
 IconKey icon{1,18,18,18,11,true,"X","sans",{0,0,0,1},{1,0,0,1}};
 Raster<IconKey,std::shared_ptr<int>> a,b;a.store(icon,std::make_shared<int>(5));b.store(icon,std::make_shared<int>(6));auto before=a;
 std::vector<std::function<void(IconKey&)>> iconChanges={
 [](auto& x){x.scale=1.5;},[](auto& x){x.bufferWidth++;},[](auto& x){x.bufferHeight++;},[](auto& x){x.size++;},[](auto& x){x.pixelSize++;},[](auto& x){x.userForeground=false;},[](auto& x){x.text="+";},[](auto& x){x.font="mono";},[](auto& x){x.foreground[0]+=.1;},[](auto& x){x.foreground[1]+=.1;},[](auto& x){x.foreground[2]+=.1;},[](auto& x){x.foreground[3]-=.1;},[](auto& x){x.background[0]-=.1;},[](auto& x){x.background[1]+=.1;},[](auto& x){x.background[2]+=.1;},[](auto& x){x.background[3]-=.1;}};
 for(const auto& change:iconChanges){auto other=icon;change(other);assert(!a.matches(other));++checks;}
 auto second=icon;second.scale=1.5;b.store(second,std::make_shared<int>(7));assert(a.key==before.key && a.texture==before.texture);++checks;
 std::cout<<checks<<" actual caption/icon cache key and scope checks PASS\n";
}
