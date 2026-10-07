#include "capture-resource-fd-source-fixture.hpp"
#include "preview-policy-driver.h"
using namespace preview;
static std::string bytes(const char* path) {std::ifstream file(path);std::ostringstream output;output<<file.rdbuf();require(file.good() || file.eof(),"Held driver bundle asset");return output.str();}
struct ForeignCall {WarlockPolicyDriver* driver;const char* input;guint64 epoch;bool ok{};GError* error{};};
static gpointer foreign(gpointer raw) {auto& c=*static_cast<ForeignCall*>(raw);c.ok=warlock_policy_driver_native(c.driver,c.epoch,c.input,&c.error);return nullptr;}
int main(int argc,char** argv) {try {
    require(argc==3,"Held original policy and native outbox assets");
    Server server("valid");GError* error=nullptr;char *initial=nullptr,*grant=nullptr;void* raw=nullptr;
    auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);check(bootstrap && !error,"Actual original Bootstrap");
    auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);require(transport && !error,"Actual original Native");
    auto& native=*static_cast<Native*>(transport);const auto binding=native.binding();
    gpointer popup=reinterpret_cast<gpointer>(uintptr_t(77));
    auto imported=warlock_imported_clients_open_controlled(transport,popup,21,1,1,&initial,&grant,&raw,&error);require(imported && initial && grant && raw && !error,"Actual controlled C source owner");
    require(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Actual borrowed original delivery");
    auto policy=bytes(argv[1]);auto outbox=bytes(argv[2]);const auto epoch=Json(grant).counter("receiverEpoch");uint64_t subject=21;
    auto refusal=[&](const std::string& candidate_policy,const std::string& candidate_outbox,const char* candidate_grant) {
        auto* rejected=warlock_policy_driver_new(candidate_policy.data(),candidate_policy.size(),candidate_outbox.data(),candidate_outbox.size(),imported,bootstrap,popup,candidate_grant,&error);
        check(!rejected && error,"Pre-grant driver failure returns no live custody");g_clear_error(&error);
        check(native.binding()==binding && native.previewControlClaimed(),"Pre-grant driver refusal preserves original controlled Native namespace");
    };
    refusal(policy,"throw new Error('held outbox pre-grant fault');",grant);
    refusal(policy,"nativePost('unexpected constructor callback');",grant);
    refusal("throw new Error('held worker pre-grant fault');",outbox,grant);
    auto wrong_grant=Wire().begin("binding").binding(binding).end().counter("receiverEpoch",epoch+1).integer("capacity",1065).finish();
    refusal(policy,outbox,wrong_grant.c_str());
    auto* driver=warlock_policy_driver_new(policy.data(),policy.size(),outbox.data(),outbox.size(),imported,bootstrap,popup,grant,&error);require(driver && !error,"Actual native-owned policy/transport driver");
    std::cout<<"{\"events\":"<<initial<<",\"grant\":"<<grant<<",\"epoch\":\""<<epoch<<"\",\"preGrantFaultChecks\":"<<passed<<"}"<<std::endl;g_free(initial);
    auto* original_policy=warlock_policy_driver_policy(driver,&error);require(original_policy && !error,"Original persistent policy identity");
    std::string line;
    while(std::getline(std::cin,line)) {
        require(line.size()<=16*1024*1024,"Original bounded fixture input");Json request(line);auto* object=request.object();const auto op=std::string(Json::text(object,"op"));bool ok=false,progressed=false;std::string result="null";char* text=nullptr;
        if(op=="native")ok=warlock_policy_driver_native(driver,request.counter("epoch"),Json::text(object,"events"),&error);
        else if(op=="presentation")ok=warlock_policy_driver_presentation(driver,Json::text(object,"value"),&error);
        else if(op=="large-presentation") {const auto length=Json::integer(object,"length");require(length>0 && length<=15*1024*1024,"Bounded native-generated input for aggregate custody fixture");auto value=std::string("{\"padding\":\"")+std::string(length,'x')+"\"}";ok=warlock_policy_driver_presentation(driver,value.c_str(),&error);}
        else if(op=="quarantine")ok=warlock_policy_driver_quarantine(driver,request.counter("epoch"),&error);
        else if(op=="step") {gboolean advanced=FALSE;ok=warlock_policy_driver_step(driver,&advanced,&error);progressed=advanced;}
        else if(op=="inspect") {ok=warlock_policy_driver_inspect(driver,&text,&error);if(text){result=text;g_free(text);}}
        else if(op=="visual") {auto* worker=warlock_policy_driver_policy(driver,&error);if(worker)ok=warlock_preview_policy_visual_projection(worker,&text,&error);if(text){result=text;g_free(text);}}
        else if(op=="foreign-native") {ForeignCall call{driver,Json::text(object,"events"),request.counter("epoch")};auto* thread=g_thread_new("foreign-driver",foreign,&call);g_thread_join(thread);ok=call.ok;error=call.error;}
        else if(op=="duplicate-driver") {auto* duplicate=warlock_policy_driver_new(policy.data(),policy.size(),outbox.data(),outbox.size(),imported,bootstrap,popup,grant,&error);require(!duplicate && error,"Another policy cannot bind original native owner");ok=false;}
        else if(op=="terminal") {ok=warlock_preview_bootstrap_pending(bootstrap,popup,&text,&error);if(text){result=text;g_free(text);}}
        else if(op=="seed") {auto identity="family:"+std::to_string(subject);ok=warlock_imported_clients_detachment_inventory(imported,popup,identity.c_str(),&text,&error);if(text){result=text;g_free(text);}}
        else if(op=="poll") {auto* delivery=warlock_preview_bootstrap_delivery(bootstrap,popup,&error);if(delivery)ok=warlock_imported_clients_retirement_poll(imported,delivery,popup,&text,&error);if(text){result=text;g_free(text);}}
        else if(op=="pending") {auto* delivery=warlock_preview_bootstrap_delivery(bootstrap,popup,&error);if(delivery)ok=warlock_imported_clients_detachment_pending(imported,delivery,popup,&text,&error);if(text){result=text;g_free(text);}}
        else if(op=="native-status") {
            auto* endpoint=static_cast<uri::Endpoint*>(raw);
            result=endpoint->native([&](auto& broker){auto rows=broker.inspect();Wire wire;wire.text("records",std::to_string(rows.size())).text("charge",std::to_string(broker.charge()));uint64_t captures=0;std::ifstream(server.root/"capture-count")>>captures;wire.text("captures",std::to_string(captures));if(!rows.empty())wire.begin("job").job(rows.front().job).end().boolean("terminal",rows.front().terminal);return wire.finish();});ok=true;
        } else if(op=="retired-subject") {
            std::ofstream(server.root/"retired-through")<<subject;
            auto identity="family:"+std::to_string(subject);
            ok=warlock_imported_clients_retirement_observe(imported,popup,identity.c_str(),&text,&error);if(text){result=text;g_free(text);}
        } else if(op=="retirement-pending") {
            auto* delivery=warlock_preview_bootstrap_delivery(bootstrap,popup,&error);
            if(delivery)ok=warlock_imported_clients_retirement_pending(imported,delivery,popup,&text,&error);if(text){result=text;g_free(text);}
        } else if(op=="readiness") {
            gboolean ready=FALSE;ok=warlock_policy_driver_retirement_ready(driver,&ready,&error);
            result=std::string("{\"ready\":")+(ready?"true":"false")+"}";
        } else if(op=="retire-probe") {
            ok=warlock_policy_driver_retire(driver,&error);require(!ok && error,"Original unsettled realm retirement refused");
        } else if(op=="retire") {
            ok=warlock_policy_driver_retire(driver,&error);
            if(ok){imported=nullptr;raw=nullptr;require(native.binding()==binding && !native.previewControlClaimed(),"Strict C realm retirement preserves original Native");
                require(warlock_policy_driver_policy(driver,&error)==original_policy && !error,"Retirement preserves exact original policy pointer");}
        } else if(op=="next-realm") {
            require(!imported && !raw && !native.previewControlClaimed(),"Original realm retired before actual later claim");
            subject=22;char* events=nullptr;g_free(grant);grant=nullptr;
            imported=warlock_imported_clients_open_controlled(transport,popup,subject,2,2,&events,&grant,&raw,&error);
            require(imported && events && grant && raw && !error,"Actual later C namespace");
            require(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Later original Bootstrap delivery");
            result=std::string("{\"events\":")+events+",\"grant\":"+grant+"}";g_free(events);ok=true;
        } else if(op=="reopen-probe") {
            auto* previous=driver;
            ok=warlock_policy_driver_reopen(&driver,outbox.data(),outbox.size(),imported,bootstrap,popup,grant,&error);
            require(!ok && error && driver==previous,"Open realm cannot transfer original policy");
        } else if(op=="bad-reopen") {
            auto* previous=driver;const auto variant=std::string(Json::text(object,"variant"));std::string candidate=grant,source=outbox;
            if(variant=="old-epoch")replace(candidate,"\"receiverEpoch\":\"2\"","\"receiverEpoch\":\"1\"");
            else if(variant=="foreign-binding")replace(candidate,"\"frontend\":\""+std::to_string(binding.frontend.value)+"\"","\"frontend\":\"1\"");
            else if(variant=="outbox")source="throw new Error('pre-transfer outbox fault');";
            else require(false,"Closed reopen refusal stimulus");
            ok=warlock_policy_driver_reopen(&driver,source.data(),source.size(),imported,bootstrap,popup,candidate.c_str(),&error);
            require(!ok && error && previous==driver,"Pre-transfer refusal keeps original driver");
            GError* observed=nullptr;require(warlock_policy_driver_policy(driver,&observed)==original_policy && !observed,"Pre-transfer refusal keeps same policy");
        } else if(op=="reopen") {
            ok=warlock_policy_driver_reopen(&driver,outbox.data(),outbox.size(),imported,bootstrap,popup,grant,&error);
            if(ok)require(warlock_policy_driver_policy(driver,&error)==original_policy && !error && native.binding()==binding,"Later realm reuses exact original policy/Native");
        } else if(op=="close-probe") {ok=warlock_policy_driver_close(driver,&error);require(!ok && error,"Original unsettled driver cannot normally close");}
        else if(op=="finish") {
            require(warlock_policy_driver_close(driver,&error) && !error,"Exact original policy/input/ticket/native physical/confirmed close");driver=nullptr;imported=nullptr;raw=nullptr;
            require(native.binding()==binding && !native.previewControlClaimed(),"Original Native grant unchanged after strict driver close");
            RetirementCursor cursor;require(observeIncarnationRetirement(native,{subject},cursor).state==IncarnationState::Active,"Original synthetic native subject remains Active");
            warlock_preview_bootstrap_free(bootstrap);server.finish();g_free(grant);std::cout<<"{\"finished\":true,\"normalOwnedPeerExit\":true,\"nativeGrantResets\":0}"<<std::endl;return 0;
        } else require(false,"Closed actual driver fixture union");
        std::cout<<"{\"ok\":"<<(ok?"true":"false")<<",\"refused\":"<<(error?"true":"false")<<",\"code\":"<<(error?error->code:0)<<",\"progressed\":"<<(progressed?"true":"false")<<",\"result\":"<<result<<"}"<<std::endl;g_clear_error(&error);
    }
    require(false,"Explicit normal driver and native realm close required");
}catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}}

