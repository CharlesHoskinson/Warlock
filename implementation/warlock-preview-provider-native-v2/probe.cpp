#include "preview_wire.hpp"
#include "preview-provider-bootstrap.h"
#include <iostream>
using namespace preview::bridge;
int main(int argc,char** argv){try{
 require(argc==3,"Config and native subject required");GError* error=nullptr;
 auto owner=warlock_preview_bootstrap_open(argv[1],&error);require(owner && !error,"Actual own C bootstrap enrollment");
 char* bytes=nullptr;require(warlock_preview_bootstrap_enrollment(owner,&bytes,&error) && !error,"Actual typed native enrollment metadata");
 Json enrolled(bytes);g_free(bytes);auto metadata=enrolled.object();auto binding=decodeBinding(Json::child(metadata,"binding"));
 const auto provider=Json::child(metadata,"provider"),core=Json::child(metadata,"compositor");
 require(Json::integer(provider,"pid")==getpid() && decimal(Json::text(provider,"start"))==processStart(getpid()),"Actual native child PID/start metadata");
 require(!Json::boolean(metadata,"loadedPluginAttested") && std::string_view(Json::text(core,"executableSHA256"))=="bda6ce0094961c285673589afa2b61fe2b97321a1d86b248823b482122fec0f5","Verified owning core is separate from plugin attestation");
 const auto subject=decimal(argv[2]);uint64_t previous=0;
 for(unsigned i=0;i<2;i++){
  bytes=nullptr;require(warlock_preview_bootstrap_scope(owner,subject,&bytes,&error) && !error,"Actual correlated native scope");
  Json observed(bytes);g_free(bytes);auto root=observed.object(),scope=Json::child(root,"scope");
  require(decodeBinding(Json::child(root,"binding"))==binding && decodeBinding(Json::child(scope,"binding"))==binding && decodeContext(Json::child(scope,"context")).incarnation.value==subject,"Own provider scope binding and incarnation");
  const auto request=decimal(Json::text(root,"requestId"));require(request==i+1 && decimal(Json::text(scope,"observation"))>previous,"Actual correlated request and fresh native observation");previous=decimal(Json::text(scope,"observation"));
  require(!Json::boolean(root,"previewEligible") && std::string_view(Json::text(root,"scopeKind"))=="root-surface-commit-monitor-plane-unqualified" && decimal(Json::text(scope,"clock"))==binding.lifetime.value && decimal(Json::text(root,"maximumTransferBytes"))%4096==0,"Actual root-monitor scope remains ineligible and owns native clock");
 }
 warlock_preview_bootstrap_free(owner);Wire report;report.boolean("passed",true).integer("checks",5).integer("providerPID",getpid()).begin("binding").binding(binding).end().boolean("previewEligible",false);std::cout<<report.finish()<<'\n';return 0;
}catch(const std::exception& e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
