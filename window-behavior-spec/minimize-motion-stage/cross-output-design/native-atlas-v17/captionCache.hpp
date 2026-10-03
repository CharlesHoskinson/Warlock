#pragma once
#include <array>
#include <optional>
#include <string>
#include <utility>
namespace CaptionCache {
struct TitleKey {
 double scale=0,bufferWidth=0,bufferHeight=0;
 int pixelSize=0,weight=0,maxWidth=0,padding=0,buttonPadding=0;
 std::string text,font,align;
 std::array<double,4> color{};
 bool operator==(const TitleKey&)const=default;
};
struct IconKey {
 double scale=0,bufferWidth=0,bufferHeight=0,size=0;
 int pixelSize=0;
 bool userForeground=false;
 std::string text,font;
 std::array<double,4> foreground{},background{};
 bool operator==(const IconKey&)const=default;
};
template<class Key,class Texture> struct Raster {
 std::optional<Key> key;
 Texture texture{};
 bool matches(const Key& desired)const {return key && *key==desired && bool(texture);}
 void store(const Key& desired,Texture result){key=desired;texture=std::move(result);}
};
template<class F>class RestoreScope {
 F restore;bool active;
public:
 RestoreScope(F fn,bool enabled):restore(std::move(fn)),active(enabled){}
 RestoreScope(const RestoreScope&)=delete;
 ~RestoreScope(){if(active)restore();}
};
}
