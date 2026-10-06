#include "client_producer.hpp"
#include "preview-provider-bootstrap.h"
#include <iostream>
using namespace preview;using namespace preview::bridge;
static void output(const char* stage,const std::string& status){std::cout<<"{\"stage\":\""<<stage<<"\",\"status\":"<<status<<"}\n"<<std::flush;}
int main(int argc,char** argv){try {
    require(argc==4,"Exact config, subject and private control path");
    GError* error=nullptr;auto bootstrap=warlock_preview_bootstrap_open(argv[1],&error);require(bootstrap && !error,"Own exact native bootstrap");
    auto transport=static_cast<Native*>(warlock_preview_bootstrap_native_transport(bootstrap,&error));require(transport && !error,"Own actual native transport");
    ClientProducer producer(*transport,77,decimal(argv[2]),1,1);const auto job=producer.job();
    Wire acquire;auto captureEvents=producer.command("family:"+std::string(argv[2]),acquire.text("kind","acquire").begin("job").job(job).end().finish());
    Json events("{\"events\":"+captureEvents+"}");auto array=json_object_get_array_member(events.object(),"events");require(array && json_array_get_length(array)==2,"Real capture Offer and readiness");
    auto ready=Json::child(json_node_get_object(json_array_get_element(array,1)),"event");auto frame=Json::child(ready,"frame");
    const auto handle=std::string(Json::text(frame,"handle"));const auto expires=decimal(Json::text(frame,"expires"));
    auto encoded=json_node_to_string(json_object_get_member(ready,"frame"));require(encoded,"Exact native packet JSON");std::string release="{\"kind\":\"release\",\"frame\":"+std::string(encoded)+"}";g_free(encoded);
    auto& endpoint=producer.endpoint();ReceiptDelivery delivery(endpoint,job.binding,77);gsize size{};
    auto stream=endpoint.open(77,"elm-shell://preview/"+handle,&size,&error);require(stream && !error,"Own held actual GIO stream");
    std::array<uint8_t,4> bytes{};require(g_input_stream_read(stream,bytes.data(),bytes.size(),nullptr,&error)==4 && !error,"Initial native PNG read");
    output("ready",producer.status());bool denied=false;std::string prior;
    for(;;){
        std::ifstream control(argv[3]);std::string command;std::getline(control,command);require(bool(control) || control.eof(),"Private control read");
        if(command==prior || command=="hold" || command.empty()){::usleep(20000);continue;}prior=command;
        if(command=="deny") {
            require(!denied && stream,"One owned denial qualification");
            endpoint.native([&](auto& b){require(static_cast<bool>(b.fetch(1,job.binding,b.inspect().at(0).packet->token)),"Broker is still readable before independent native guard");});
            require(g_input_stream_read(stream,bytes.data(),bytes.size(),nullptr,&error)==-1 && error,"Actual held read denied by native authority before frontend denial");g_clear_error(&error);
            auto extra=endpoint.open(77,"elm-shell://preview/"+handle,&size,&error);require(!extra && error,"Actual new URI read denied independently");g_clear_error(&error);
            output("native-uri-denied-before-policy",producer.status());
            auto denial=producer.poll(1,1);Json wire("{\"events\":"+denial+"}");auto rows=json_object_get_array_member(wire.object(),"events");require(rows && json_array_get_length(rows)==1,"Exact known own native denial");
            auto event=Json::child(json_node_get_object(json_array_get_element(rows,0)),"event");require(std::string_view(Json::text(event,"kind"))=="source-denied" && decodeJob(Json::child(event,"job"))==job,"Actual native scope denial preserves original job");
            std::cout<<"{\"stage\":\"typed-denial\",\"events\":"<<denial<<",\"originalExpires\":\""<<expires<<"\"}\n"<<std::flush;
            require(g_input_stream_close(stream,nullptr,&error) && !error,"Actual held stream drain");g_object_unref(stream);stream=nullptr;
            require(producer.command("family:"+std::string(argv[2]),release)=="[]","Exact own physical cleanup request");denied=true;output("cleanup",producer.status());
        } else if(command=="poll") {require(denied,"Only retained cleanup polled");require(producer.poll(1,1)=="[]","No renewed capture or native deadline");output("polled",producer.status());}
        else if(command=="finish") {
            require(denied,"No false successful capture retirement");auto pending=delivery.pending(77);require(pending.size()==1,"One exact retained native terminal proof");
            Json proof(pending[0]);auto receipt=Json::child(proof.object(),"event");auto terminal=Json::child(receipt,"event");require(std::string_view(Json::text(terminal,"kind"))=="released" && decodeJob(Json::child(Json::child(terminal,"frame"),"job"))==job,"Native physical retirement before terminal proof");
            Wire ack;require(delivery.acknowledge(77,"family:"+std::string(argv[2]),ack.text("kind","acknowledge").begin("job").job(job).end().counter("sequence",decimal(Json::text(receipt,"sequence"))).finish()),"Exact physical terminal ACK");
            require(producer.empty() && producer.close(),"Own charge, readers and journal drained");output("complete",producer.status());warlock_preview_bootstrap_free(bootstrap);return 0;
        } else throw std::runtime_error("Unexpected private witness command");
    }
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
