#define main retained_original_channel_fixture
#include "actor-retirement-channel-test-v2.cpp"
#undef main

int main(){try {
    Server server("turnover");GError* error=nullptr;
    auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);
    check(bootstrap && !error,"Actual original fair-poll bootstrap");
    auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);
    check(transport && !error,"Actual authenticated Native transport");
    auto& native=*static_cast<Native*>(transport);auto popup=reinterpret_cast<gpointer>(uintptr_t(77));
    char* events=nullptr;void* raw=nullptr;
    auto owner=warlock_imported_clients_open_dynamic(transport,popup,21,1,1,&events,&raw,&error);
    check(owner && events && raw && !error,"Original dynamic owner");g_free(events);events=nullptr;
    auto& endpoint=*static_cast<preview::uri::Endpoint*>(raw);
    check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Original receipt attachment");
    auto delivery=warlock_preview_bootstrap_delivery(bootstrap,popup,&error);
    check(delivery && !error,"Original delivery capability");
    WarlockImportedAdmission admission=WARLOCK_IMPORTED_INVALID;
    check(warlock_imported_clients_enroll(owner,popup,23,1,1,&admission,&events,&error) && events && !error && admission==WARLOCK_IMPORTED_STARTED,"Second original native actor");g_free(events);events=nullptr;
    check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error) && !error,"Original receiver extends without replacement");
    const auto jobs=endpoint.native([](auto& broker){return broker.inspect();});
    check(jobs.size()==2,"Two actual original physical reservations");const auto original=jobs[0].job;
    std::ofstream(server.root/"retired-through")<<23;
    auto ready=[&](uint64_t subject) {
        const auto identity="family:"+std::to_string(subject);
        check(warlock_imported_clients_retirement_observe(owner,popup,identity.c_str(),&events,&error) && events && !error,"Actual native observation under original receiver");
        Json envelope("{\"rows\":"+std::string(events)+"}");g_free(events);events=nullptr;
        auto rows=json_object_get_array_member(envelope.object(),"rows");check(rows && json_array_get_length(rows)==1,"Exact retained original observation");
        auto fact=json_node_get_object(json_array_get_element(rows,0));
        auto command=Wire().text("kind","retire-ready").begin("binding").binding(native.binding()).end().counter("subject",subject)
            .text("observationRequest",Json::text(fact,"request")).text("observationSequence",Json::text(fact,"sequence")).finish();
        const auto before=native.next();
        check(warlock_imported_clients_retirement_control(owner,delivery,popup,identity.c_str(),command.c_str(),&events,&error) && events && !error && std::string_view(events)=="[]","Readiness retained while physical owner blocks");g_free(events);events=nullptr;
        check(native.next()==before+1,"Physical barrier causes no native query");
    };
    ready(21);ready(23);
    auto terminal=[&](uint64_t entry) {
        return endpoint.native([&](auto& broker){auto rows=broker.inspect();auto row=std::find_if(rows.begin(),rows.end(),[&](const auto& r){return r.entry==entry;});require(row!=rows.end(),"Original exact job");
            auto result=broker.producerRefused(entry,row->job);check(result.status==preview::Result::Status::Complete && !result.receipts.empty(),"Actual terminal producer proof");return result.receipts.back();});
    };
    auto acknowledge=[&](const preview::Receipt& proof) {
        const auto identity="family:"+std::to_string(proof.job.context.incarnation.value);
        auto command=Wire().text("kind","acknowledge").begin("job").job(proof.job).end().counter("sequence",proof.sequence.value).finish();
        check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,identity.c_str(),command.c_str(),&error) && !error,"Exact original terminal proof acknowledgment");
    };
    acknowledge(terminal(1));const auto secondProof=terminal(2);
    check(endpoint.registerView(78,native.binding(),{1}),"Actual second receiver blocks only first actor");
    auto poll=[&](uint64_t queryCount) {
        const auto before=native.next();
        check(warlock_imported_clients_retirement_poll(owner,delivery,popup,&events,&error) && events && !error,"Actual original native polling path");
        std::string result=events;g_free(events);events=nullptr;
        check(native.next()==before+1+queryCount,"Exact per-call native query count");return result;
    };
    check(poll(0)=="[]","Receiver-blocked first candidate remains intact");
    check(poll(0)=="[]","Unacknowledged terminal proof blocks second candidate without query");
    acknowledge(secondProof);
    check(poll(0)=="[]","One-candidate polling does not query eligible neighbor in first actor turn");
    const auto second=poll(1);Json completion("{\"rows\":"+second+"}");
    auto completedRows=json_object_get_array_member(completion.object(),"rows");
    check(completedRows && json_array_get_length(completedRows)==1 && std::string_view(Json::text(Json::child(json_node_get_object(json_array_get_element(completedRows,0)),"fact"),"subject"))=="23","Eligible neighbor completes on its next fair turn");
    check(endpoint.native([&](auto& broker){return broker.actorCount()==1 && broker.requestFloor(1)==1 && broker.inspect().empty();}),"Blocked original actor and request floor survive neighbor removal");
    auto confirm=[&](const std::string& wire,const char* identity) {
        Json packet("{\"rows\":"+wire+"}");auto rows=json_object_get_array_member(packet.object(),"rows");auto row=json_node_get_object(json_array_get_element(rows,0));
        auto command=Wire().text("kind","retire-delivery-ack").begin("binding").binding(native.binding()).end().text("deliveryOrdinal",Json::text(row,"deliveryOrdinal")).finish();
        check(warlock_imported_clients_retirement_control(owner,delivery,popup,identity,command.c_str(),&events,&error) && events && !error && std::string_view(events)=="[]","Exact retained completion processing acknowledgment");g_free(events);events=nullptr;
    };
    confirm(second,"family:23");
    auto foreignPopup=reinterpret_cast<gpointer>(uintptr_t(78));const auto beforeForeign=native.next();
    check(!warlock_imported_clients_retirement_poll(owner,delivery,foreignPopup,&events,&error) && !events && error,"Foreign popup cannot poll readiness");g_clear_error(&error);
    check(native.next()==beforeForeign+1,"Foreign receiver cannot query native");
    endpoint.unregisterView(78);const auto first=poll(1);Json firstPacket("{\"rows\":"+first+"}");
    auto firstRows=json_object_get_array_member(firstPacket.object(),"rows");check(firstRows && json_array_get_length(firstRows)==1,"First actor completes after original receiver clears");
    auto firstFact=Json::child(json_node_get_object(json_array_get_element(firstRows,0)),"fact");
    check(std::string_view(Json::text(firstFact,"subject"))=="21" && std::string_view(Json::text(firstFact,"requestFloor"))=="1" && original.context.incarnation.value==21,"Original actor identity and floor remain exact");
    check(!warlock_imported_clients_empty(owner) && !warlock_imported_clients_close(owner,&error) && error,"Physically empty owner retains final delivery close barrier");g_clear_error(&error);
    check(poll(0)==first,"Empty readiness poll retries byte-identical final without new query");
    confirm(first,"family:21");check(poll(0)=="[]","Confirmed delivery empties without resetting cursor or native prefix");
    check(warlock_imported_clients_empty(owner) && warlock_imported_clients_close(owner,&error) && !error,"Normal close after all original barriers and confirmations");
    warlock_preview_bootstrap_free(bootstrap);server.finish();
    std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"normalOwnedExit\":true,\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
