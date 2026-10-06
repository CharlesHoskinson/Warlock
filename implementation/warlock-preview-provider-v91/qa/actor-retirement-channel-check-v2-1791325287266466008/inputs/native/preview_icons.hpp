#pragma once
#include "preview_metadata.hpp"
#include <gtk/gtk.h>
#include <gio/gdesktopappinfo.h>
#include <functional>
#include <mutex>
namespace preview::icons {
using namespace preview::bridge;
struct Asset {std::vector<uint8_t> png;std::string kind;};
std::optional<Asset> resolveApplication(const std::string& application);
struct Record {WindowMetadata metadata;uint64_t privacy;std::string token;Asset asset;unsigned readers{};bool revoked{};};
struct State {
    std::mutex lock;uint64_t view;Binding binding;uint64_t subject;
    std::function<bool(const Record&)> authorize;
    std::vector<std::shared_ptr<Record>> records;unsigned readers{};
};
class Endpoint {
    std::shared_ptr<State> state_;
public:
    Endpoint(uint64_t view,Binding binding,uint64_t subject,std::function<bool(const Record&)> authorize);
    std::optional<std::string> issue(const WindowMetadata&,const Scope&,Asset);
    GInputStream* open(uint64_t view,std::string_view uri,gsize* length,GError**);
    bool close();unsigned readers();std::string status();
};
}
