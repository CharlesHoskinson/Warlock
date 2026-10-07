#include "capture-intent-source-fixture.hpp"
using namespace preview;
int main(int argc,char** argv){try{
 const std::string mode=argc>1?argv[1]:"capture-refused";Server server(mode);auto native=server.open();ImportedClients value(*native,256);auto& endpoint=value.endpoint();const auto binding=native->binding();
 check(endpoint.registerControlView(77,binding),"Original empty native capture model receiver");const auto epoch=endpoint.registeredView(77)->epoch;
 PreviewControlGrant grant{binding.lifetime.value,binding.session.value,binding.frontend.value,77,epoch};PreviewControlDelivery channel{};require(preview_control_delivery_init(&channel,grant),"Original capture prefix");ControlReservations bank(channel,1065);
 std::unique_ptr<ImportedControlAdmission> controls;endpoint.native([&](auto& broker){controls=std::make_unique<ImportedControlAdmission>(bank,grant,broker,256);});value.attachControlAdmission(*controls,grant);
 auto started=value.tryStartAtReceiver(77,epoch,1,{21},1,1);require(started.native.job.has_value(),"Original capture model job");const auto job=*started.native.job;
 auto command=[&](const char* kind,const Job& target){return Wire().text("kind",kind).begin("job").job(target).end().finish();};
 auto state=[&](int last){
  uint64_t captures=0;std::ifstream(server.root/"capture-count")>>captures;
  const auto original=value.captureIntent(1);bool unchanged=true,deadline=true;
  if(original){std::ifstream file(server.root/"capture-wire.json");const std::string wire((std::istreambuf_iterator<char>(file)),std::istreambuf_iterator<char>());unchanged=wire==original->command();deadline=original->deadline()==job.deadline && original->observed().scope.context==job.context && original->observed().scope.binding==job.binding;}
  auto rows=endpoint.native([](auto& broker){return broker.inspect();});require(rows.size()==1,"Original unresolved or terminal capture model record");
  const auto cancelled=rows[0].cleanup;
  std::cout<<Wire().integer("issued",bank.issued()).integer("delivered",channel.prefix.delivered).integer("confirmed",channel.confirmed)
   .boolean("intent",bool(original)).integer("captures",captures).integer("charge",endpoint.native([](auto& broker){return broker.charge();}))
   .boolean("terminal",rows[0].terminal).boolean("cancelled",cancelled).boolean("closed",false)
   .boolean("deadlineUnchanged",deadline).boolean("wireUnchanged",unchanged).integer("last",last).finish()<<'\n';
 };
 for(std::string event;std::getline(std::cin,event);){int last=0;
  try{
   if(event=="Acquire" || event=="Cancel"){
    const auto raw=command(event=="Acquire"?"acquire":"cancel",job);auto ticket=value.proposeJobControl(grant,1,"family:21",raw);require(ticket.has_value(),"Actual capture model ticket");
    const auto decision=preview_control_delivery_receive(&channel,grant,ticket->ticket.ordinal,ticket->ticket.wire.c_str(),ticket->ticket.wire.size());
    if(decision==PREVIEW_CONTROL_INVOKE){value.command(1,"family:21",raw);require(preview_control_delivery_complete(&channel,ticket->ticket.ordinal),"Actual capture model dispatcher return");last=1;}
    else last=decision==PREVIEW_CONTROL_REPEAT_RECEIPT?2:0;
   }else if(event=="RawRetry"){require(value.captureIntent(1).has_value(),"Raw retry witness follows original unknown attempt");value.command(1,"family:21",command("acquire",job));last=1;}
   else if(event=="Poll")last=value.pollRetirement(1)?1:0;
   else if(event=="Close")last=value.closeControlBinding(grant)?1:0;
   else if(event=="Confirm")last=preview_control_delivery_confirm(&channel,grant,channel.prefix.delivered)?1:0;
   else if(event=="BadJob"){auto wrong=job;wrong.request.value++;value.proposeJobControl(grant,1,"family:21",command("acquire",wrong));last=1;}
   else if(event=="ForeignReceiver"){auto foreign=grant;foreign.epoch++;value.proposeJobControl(foreign,1,"family:21",command("acquire",job));last=1;}
   else throw std::runtime_error("Unknown capture model event");
  }catch(const std::exception&){
   if(channel.prefix.inFlight){require(preview_control_delivery_complete(&channel,channel.prefix.delivered+1),"Actual failed capture dispatcher return");last=3;}else last=-1;
  }
  state(last);
 }
 server.finish();return 0;
}catch(const std::exception& exception){std::cerr<<exception.what()<<'\n';return 1;}}
