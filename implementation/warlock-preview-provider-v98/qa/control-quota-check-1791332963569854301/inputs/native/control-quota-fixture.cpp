#include "imported_control_admission.hpp"
#include "preview_delivery.hpp"
#include "client_producer.hpp"
#include <iostream>
using namespace preview;using namespace preview::bridge;
struct Bytes final:uri::Payload {
    std::array<uint8_t,8> data{137,80,78,71,13,10,26,10};
    uint64_t charge()const noexcept override{return data.size();}
    std::span<const uint8_t> png()const noexcept override{return data;}
};
int main(){try {
    const Binding binding{{17},{18},{19}};const Scope scope{binding,{{17},{21},{1},{1},{1},{1},{1}},{17},10,true,true,false,true};
    uri::Endpoint endpoint({16,8,2,128*1024*1024},1,2,[](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{17},10};});
    require(endpoint.enableDemand({{16,8,2,128*1024*1024},{17},{17},1}) && endpoint.registerControlView(77,binding),"Native enrollment before actual admission");
    const PreviewControlGrant grant{17,18,19,77,endpoint.registeredView(77)->epoch};PreviewControlDelivery channel{};
    require(preview_control_delivery_init(&channel,grant),"Original native receiver grant");ControlReservations bank(channel,105);
    std::unique_ptr<ImportedControlAdmission> controls;
    endpoint.native([&](auto& broker){controls=std::make_unique<ImportedControlAdmission>(bank,grant,broker,16);});
    ImportedIntentLedger ledger(binding,16);ImportedStartAttempt started;
    endpoint.nativeDemandView(77,[&](auto& queue,uri::View* view){started=controls->reserveIntent(queue,ledger,grant,view,1,scope,4096,1,1,2000000010);});
    require(started.native.job.has_value(),"Actual guarded original native job");const auto job=*started.native.job;
    ReceiptDelivery delivery(endpoint,binding,77);std::optional<Packet> packet;std::vector<Receipt> proofs;
    std::unique_ptr<GInputStream,void(*)(GInputStream*)> reader(nullptr,[](GInputStream* value){g_object_unref(value);});uint64_t invocations=0;bool closed=false;
    auto send=[&](std::string text){std::cout<<text<<'\n'<<std::flush;};
    SourceObservation observed{scope,1,4096,1,SourceObservation::Kind::UnqualifiedClientMain,false};
    send("{\"seed\":"+clientSeed(observed,1,1)+",\"request\":"+clientRequest(job)+",\"jobQuota\":5,\"actorQuota\":2,\"reconciliationQuota\":1}");
    std::string line;
    while(std::getline(std::cin,line)) {
        Json request(line);auto object=request.object();const std::string op=Json::text(object,"op");
        if(op=="command") {
            Json::fields(object,{"op","body"});const std::string body=Json::text(object,"body");Json entry(body);auto fields=entry.object();Json::fields(fields,{"identity","commands"});
            const std::string identity=Json::text(fields,"identity");require(identity=="family:21","Exact native quota subject");
            auto array=json_object_get_array_member(fields,"commands");require(array && json_array_get_length(array)==1,"One compiled Elm command");
            auto command=json_node_get_object(json_array_get_element(array,0));require(command,"Actual command object");
            auto raw=json_to_string(json_array_get_element(array,0),FALSE);std::string commandWire(raw);g_free(raw);
            const std::string kind=Json::text(command,"kind");uint64_t slot=0;
            if(kind=="acknowledge") {
                Json::fields(command,{"kind","job","sequence"});require(decodeJob(Json::child(command,"job"))==job,"Original native ACK job");
                const auto sequence=decimal(Json::text(command,"sequence"));
                require(!proofs.empty() && proofs.size()<=2,"Actual original terminal proof bound");
                for(size_t i=0;i<proofs.size();++i)if(proofs[i].sequence.value==sequence)slot=4+i;
                require(slot,"ACK must reference an actual retained native terminal proof");
            }else {
                const auto decoded=decodeClientCommand(identity,commandWire,job,packet);
                slot=decoded==ClientCommand::Acquire?1:decoded==ClientCommand::Cancel?2:3;
            }
            auto ticket=bank.issue(grant,controls->jobReservation(1),slot,body);require(ticket.has_value(),"Pre-admission quota remains available for actual Elm cleanup");
            require(bank.ownsTicket(grant,ticket->ordinal,ticket->wire),"Actual original native issued ticket before dispatcher");
            auto decision=preview_control_delivery_receive(&channel,grant,ticket->ordinal,ticket->wire.c_str(),ticket->wire.size());
            std::string events="[]";bool effectReturned=false;
            if(decision==PREVIEW_CONTROL_INVOKE) {
                ++invocations;
                if(slot==1) {
                    endpoint.native([&](auto& broker){
                        std::unique_ptr<const Buffer> bytes=std::make_unique<Bytes>();auto offer=broker.allocate(1,job,bytes,2000001010);
                        require(offer.receipts.size()==1 && offer.receipts[0].packet && !bytes,"Actual Broker owns fixture bytes");const auto before=*offer.receipts[0].packet;
                        auto ready=broker.producerComplete(1,job);require(ready.receipts.size()==1 && ready.receipts[0].packet,"Single native producer completion");packet=*ready.receipts[0].packet;
                        events="["+frameEvent("offer",before)+","+frameEvent("fence",*packet)+"]";
                    });
                    GError* error=nullptr;gsize length=0;reader.reset(endpoint.open(77,uri::encode(packet->token),&length,&error));
                    require(reader && !error && length==8,"Actual held URI reader retains native Broker storage");effectReturned=true;
                }else if(slot==2) {
                    endpoint.native([&](auto& broker){broker.cancel(1,binding,job);
                        require(!broker.consumerComplete(1,job) && broker.destroy(1,job).receipts.empty(),"Actual URI reader prevents terminal proof before release");});effectReturned=true;
                }else if(slot==3) {
                    endpoint.native([&](auto& broker){broker.release(1,binding,job,packet->token);});
                    require(bool(reader),"Actual original URI reader");reader.reset();
                    endpoint.native([&](auto& broker){require(broker.consumerComplete(1,job),"Actual reader retired before native consumer completion");
                        auto result=broker.destroy(1,job);proofs=result.receipts;require(proofs.size()==2 && proofs[0].kind==Receipt::Kind::Released && proofs[1].kind==Receipt::Kind::Cancelled,"Actual two-proof cancellation/release worst case");
                        const auto repeated=broker.cancel(1,binding,job);require(repeated.receipts.size()==1 && broker.inspect()[0].proofs.size()==2,"Repeated cancellation cannot add another terminal proof");});
                    effectReturned=true;
                    auto pending=delivery.pending(77);events="[";for(const auto& value:pending){if(events.size()>1)events+=",";events+=value;}events+="]";
                }else effectReturned=delivery.acknowledge(77,identity,commandWire);
                require(preview_control_delivery_complete(&channel,ticket->ordinal),"Dispatcher receipt remains separate from actual effect result");
            }else require(decision==PREVIEW_CONTROL_REPEAT_RECEIPT,"Exact original ticket cannot reenter its handler");
            Wire response;auto prefix=response.text("ticket",ticket->wire).integer("decision",decision).text("delivered",std::to_string(channel.prefix.delivered)).integer("invocations",invocations).boolean("effectReturned",effectReturned).finish();
            prefix.pop_back();send(prefix+",\"events\":"+events+"}");
        }else if(op=="confirm") {
            Json::fields(object,{"op","ordinal"});const bool accepted=preview_control_delivery_confirm(&channel,grant,decimal(Json::text(object,"ordinal")));
            send(Wire().boolean("accepted",accepted).boolean("prefixConfirmed",preview_control_delivery_confirmed(&channel)).finish());
        }else if(op=="status" || op=="exit-fixture") {
            Json::fields(object,{"op"});size_t records=0;uint64_t charge=0;
            endpoint.native([&](auto& broker){records=broker.recordCount();charge=broker.charge();});
            send(Wire().integer("records",records).integer("readers",endpoint.readers()).text("charge",std::to_string(charge)).integer("invocations",invocations).text("issued",std::to_string(bank.issued())).text("reserved",std::to_string(bank.reserved())).integer("tickets",bank.ticketCount()).boolean("prefixConfirmed",preview_control_delivery_confirmed(&channel)).boolean("transportEmpty",bank.transportEmpty()).boolean("fullCloseAllowed",false).finish());
            if(op=="exit-fixture") {
                require(!records && !endpoint.readers() && !charge && preview_control_delivery_confirmed(&channel),"Normal fixture exit after actual URI/Broker/control settlement");
                // Synthetic actor and unused transport reservations are fixtures;
                // this is process teardown, never real native actor/host close.
                closed=true;break;
            }
        }else require(false,"Closed native fixture operation union");
    }
    require(closed && !reader,"Explicit normal owned fixture exit");return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
