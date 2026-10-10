#include "preview_icons.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
using namespace preview::icons;
int main(int argc,char** argv) try {
    if(argc!=3)throw std::runtime_error("Mode and private fixture root required");
    const std::string mode=argv[1];const std::filesystem::path root=argv[2];
    g_setenv("XDG_DATA_HOME",root.c_str(),TRUE);
    std::filesystem::create_directories(root/"applications");
    auto image=gdk_pixbuf_new(GDK_COLORSPACE_RGB,TRUE,8,48,48);
    gdk_pixbuf_fill(image,0x00ffffff);GError* error=nullptr;
    const auto artwork=(root/"own.png").string();
    if(!gdk_pixbuf_save(image,artwork.c_str(),"png",&error,nullptr))throw std::runtime_error(error->message);
    g_object_unref(image);
    const auto directArtwork=(root/"direct.png").string();
    image=gdk_pixbuf_new(GDK_COLORSPACE_RGB,TRUE,8,48,48);gdk_pixbuf_fill(image,0xff00ffff);
    if(!gdk_pixbuf_save(image,directArtwork.c_str(),"png",&error,nullptr))throw std::runtime_error(error->message);
    g_object_unref(image);
    auto desktop=[&](const std::string& id,const std::string& windowClass,const std::string& icon) {
        std::ofstream file(root/"applications"/(id+".desktop"));
        file<<"[Desktop Entry]\nType=Application\nName=Owned fixture\nExec=/usr/bin/true\nStartupWMClass="<<windowClass<<"\nIcon="<<icon<<"\n";
    };
    desktop("org.warlock.Owned","WarlockIconFixture",artwork);
    if(mode=="direct") {
        desktop("WarlockIconFixture","DifferentClass",directArtwork);
        desktop("org.warlock.Other","WarlockIconFixture",artwork);
    }
    if(mode=="ambiguous")desktop("org.warlock.Other","WarlockIconFixture",artwork);
    if(mode=="missing")desktop("org.warlock.Owned","WarlockIconFixture","warlock-nonexistent-icon");
    if(!gtk_init_check(nullptr,nullptr))throw std::runtime_error("Actual GTK display required");
    const auto query=mode=="invalid"?"../WarlockIconFixture":mode=="unknown"?"WarlockUnknownFixture":"WarlockIconFixture";
    auto result=resolveApplication(query);
    if(!result)throw std::runtime_error("No GTK resolved icon");
    const bool own=mode=="direct" || mode=="class";
    if(result->kind!=(own?"application":"generic"))throw std::runtime_error("Wrong application/generic resolution");
    auto generic=resolveApplication("WarlockUnknownFixture");
    if(!generic)throw std::runtime_error("Generic icon unavailable");
    if(own) {
        gchar* bytes=nullptr;gsize length=0;
        if(!g_file_get_contents((mode=="direct"?directArtwork:artwork).c_str(),&bytes,&length,&error))throw std::runtime_error(error->message);
        const bool exact=result->png==std::vector<uint8_t>(reinterpret_cast<uint8_t*>(bytes),reinterpret_cast<uint8_t*>(bytes)+length);g_free(bytes);
        if(!exact)throw std::runtime_error("Application artwork differs from owned PNG");
    } else if(result->png!=generic->png)throw std::runtime_error("Ambiguous/invalid icon borrows artwork");
    std::cout<<"{\"passed\":true,\"mode\":\""<<mode<<"\",\"kind\":\""<<result->kind<<"\",\"bytes\":"<<result->png.size()<<"}\n";
    return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
