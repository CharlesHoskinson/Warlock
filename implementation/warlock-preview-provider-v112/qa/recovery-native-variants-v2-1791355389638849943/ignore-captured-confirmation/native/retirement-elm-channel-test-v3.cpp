// Reuse the exact held synthetic authenticated socket peer and its original
// fixture functions. This is a C/native/compiled-Elm protocol test, not native
// compositor destruction or captured-resource qualification.
#define main retained_original_channel_fixture
#include "actor-retirement-channel-test-v2.cpp"
#undef main

static void output(const std::string& stage,const std::string& events="[]",const std::string& extra="") {
    std::cout<<"{\"stage\":\""<<stage<<"\",\"events\":"<<events<<extra<<"}"<<std::endl;
}
int main(){try {
    Server server("turnover");GError* error=nullptr;
    auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);
    check(bootstrap && !error,"Actual original bootstrap for Elm retirement channel");
    auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);
    check(transport && !error,"Own authenticated Native transport");
    auto& native=*static_cast<Native*>(transport);
    auto popup=reinterpret_cast<gpointer>(uintptr_t(77));char* events=nullptr;void* raw=nullptr;
    auto owner=warlock_imported_clients_open_dynamic(transport,popup,21,1,1,&events,&raw,&error);
    check(owner && events && raw && !error,"Original dynamic imported owner");
    std::string seeds=events;g_free(events);events=nullptr;
    auto& endpoint=*static_cast<preview::uri::Endpoint*>(raw);
    check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Original journal attachment");
    auto journal=warlock_preview_bootstrap_delivery(bootstrap,popup,&error);
    check(journal && !error,"Original delivery capability");
    WarlockImportedAdmission admission=WARLOCK_IMPORTED_INVALID;
    check(warlock_imported_clients_enroll(owner,popup,22,1,1,&admission,&events,&error) && events && !error && admission==WARLOCK_IMPORTED_STARTED,"Retained native neighbor enrollment");
    std::string second=events;g_free(events);events=nullptr;
    check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error) && !error,"Original receiver extended for neighbor");
    seeds.pop_back();if(seeds.size()>1 && second.size()>2)seeds+=",";seeds+=second.substr(1);
    auto jobs=endpoint.native([](auto& broker){return broker.inspect();});
    check(jobs.size()==2,"Two exact original untouched reservations");
    const auto first=jobs[0].job,neighbor=jobs[1].job;
    const auto channel=Wire().text("kind","native-actor-retirement-channel").begin("binding").binding(native.binding()).end().finish();
    const auto job=Wire().begin("job").job(first).end().finish();
    Json jobEnvelope(job);const auto actualJob=json_to_string(json_object_get_member(jobEnvelope.object(),"job"),FALSE);
    output("start",seeds,",\"channel\":"+channel+",\"job\":"+actualJob);g_free(actualJob);
    auto pending=[&] {
        char* text=nullptr;
        check(warlock_imported_clients_retirement_pending(owner,journal,popup,&text,&error) && text && !error,"Exact original pending completion");
        std::string result=text;g_free(text);return result;
    };
    auto terminal=[&](uint64_t entry) {
        endpoint.native([&](auto& broker){auto rows=broker.inspect();auto row=std::find_if(rows.begin(),rows.end(),[&](const auto& value){return value.entry==entry;});
            require(row!=rows.end(),"Original known reservation");auto result=broker.producerRefused(entry,row->job);
            check(result.status==preview::Result::Status::Complete && !result.receipts.empty(),"Original actual terminal producer proof");});
    };
    bool stopped=false;std::string line;
    while(std::getline(std::cin,line)) {
        require(line.size()<=65536,"Bounded fixture command input");Json input(line);
        const auto op=std::string_view(Json::text(input.object(),"op"));
        if(op=="observe") {
            std::ofstream(server.root/"retired-through")<<21;
            check(warlock_imported_clients_retirement_observe(owner,popup,"family:21",&events,&error) && events && !error,"Actual native observation delivered to compiled Elm");
            output("observed",events);g_free(events);events=nullptr;
        }else if(op=="terminal") {
            check(endpoint.native([](auto& broker){return broker.recordCount()==2 && broker.activeItems()==1;}),"Actual cancellation already physically settled its original untouched producer");
            check(warlock_preview_bootstrap_pending(bootstrap,popup,&events,&error) && events && !error,"Actual terminal journal delivery to compiled Elm");
            output("terminal",events);g_free(events);events=nullptr;
        }else if(op=="controls") {
            auto rows=json_object_get_array_member(input.object(),"entries");require(rows && json_array_get_length(rows)<=8,"Bounded actual Elm controls");
            std::string emitted="[]";
            for(guint i=0;i<json_array_get_length(rows);++i) {
                auto row=json_node_get_object(json_array_get_element(rows,i));const auto identity=Json::text(row,"identity");
                auto commands=json_object_get_array_member(row,"commands");require(commands,"Actual Elm command array");
                for(guint j=0;j<json_array_get_length(commands);++j) {
                    auto command=json_array_get_element(commands,j);auto object=json_node_get_object(command);auto wire=json_to_string(command,FALSE);
                    const auto kind=std::string_view(Json::text(object,"kind"));
                    if(kind=="acknowledge") {
                        check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,identity,wire,&error) && !error,"Compiled Elm exact terminal ACK first");
                    }else if(kind=="retire-ready" || kind=="retire-delivery-ack") {
                        check(warlock_imported_clients_retirement_control(owner,journal,popup,identity,wire,&events,&error) && events && !error,"Actual compiled Elm retirement control");
                        if(std::string_view(events)!="[]") {emitted=events;}
                        g_free(events);events=nullptr;
                    }else {
                        check(kind=="cancel","Only exact cancellation precedes terminal proof in this fixture");
                        check(warlock_imported_clients_command(owner,identity,wire,&events,&error) && events && !error,"Actual Elm cancellation preserves native reservation");
                        check(std::string_view(events)=="[]","Cancellation alone is not terminal proof");g_free(events);events=nullptr;
                    }
                    g_free(wire);
                }
            }
            output("controlled",emitted);
        }else if(op=="pending") {
            output("pending",pending());
        }else if(op=="drain-neighbor") {
            check(endpoint.native([&](auto& broker){auto rows=broker.inspect();return rows.size()==1 && rows[0].job==neighbor && broker.requestFloor(2)==1;}),"Original neighbor job and counter survived compiled Elm retirement");
            terminal(2);
            check(warlock_preview_bootstrap_pending(bootstrap,popup,&events,&error) && events && !error,"Neighbor exact terminal proof retained");
            output("neighbor-terminal",events);g_free(events);events=nullptr;
        }else if(op=="check-close") {
            check(!warlock_imported_clients_empty(owner),"Transport journal keeps physically empty owner nonempty");
            check(!warlock_imported_clients_close(owner,&error) && error,"Pending completion prevents owner close after physical drain");g_clear_error(&error);
            output("drained",pending());
        }else if(op=="finish") {
            check(pending()=="[]" && warlock_imported_clients_empty(owner),"Compiled Elm ACK releases only retained final delivery");
            check(warlock_imported_clients_close(owner,&error) && !error,"Confirmed native owner closes normally");owner=nullptr;
            warlock_preview_bootstrap_free(bootstrap);server.finish();stopped=true;
            output("complete","[]",",\"passed\":true,\"checks\":"+std::to_string(passed)+",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false");break;
        }else require(false,"Known fixture operation");
    }
    require(stopped,"Explicit normal C/native/Elm fixture completion");return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 2;}}
