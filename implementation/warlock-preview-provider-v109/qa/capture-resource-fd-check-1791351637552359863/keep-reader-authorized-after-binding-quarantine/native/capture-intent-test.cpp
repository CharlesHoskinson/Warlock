#include "capture-intent-source-fixture.hpp"
using namespace preview;
int main(){try{
 for(const auto* mode:{"capture-refused","capture-malformed","capture-fd-missing"}) {
  Server server(mode);auto native=server.open();ImportedClients value(*native,256);auto& endpoint=value.endpoint();const auto binding=native->binding();
  check(endpoint.registerControlView(77,binding),"Original empty actual capture receiver");const auto epoch=endpoint.registeredView(77)->epoch;
  PreviewControlGrant grant{binding.lifetime.value,binding.session.value,binding.frontend.value,77,epoch};PreviewControlDelivery channel{};
  check(preview_control_delivery_init(&channel,grant),"Original native capture control prefix");ControlReservations bank(channel,1065);
  std::unique_ptr<ImportedControlAdmission> controls;endpoint.native([&](auto& broker){controls=std::make_unique<ImportedControlAdmission>(bank,grant,broker,256);});value.attachControlAdmission(*controls,grant);
  auto started=value.tryStartAtReceiver(77,epoch,1,{21},1,1);check(started.native.job.has_value(),"Original capture job admission");const auto job=*started.native.job;
  check(!value.captureIntent(1),"No capture intent before native preparation");
  const auto command=Wire().text("kind","acquire").begin("job").job(job).end().finish();auto ticket=value.proposeJobControl(grant,1,"family:21",command);
  check(ticket && preview_control_delivery_receive(&channel,grant,ticket->ticket.ordinal,ticket->ticket.wire.c_str(),ticket->ticket.wire.size())==PREVIEW_CONTROL_INVOKE,"Actual original native acquisition ticket");
  check(denied([&]{value.command(1,"family:21",command);}),"Original capture exception reaches owning handler");
  check(preview_control_delivery_complete(&channel,ticket->ticket.ordinal),"Dispatcher return does not fabricate capture success");
  const auto original=value.captureIntent(1);check(original && original->observed().scope.binding==job.binding && original->observed().scope.context==job.context && original->deadline()==job.deadline,"Original request and deadline retained across capture exception");
  std::ifstream file(server.root/"capture-wire.json");const std::string wire((std::istreambuf_iterator<char>(file)),std::istreambuf_iterator<char>());
  check(original->command()==wire,"Retained native capture intent equals exact bytes received by original core");Json captured(wire);
  check(captured.counter("requestId")==original->request() && captured.counter("deadlineNs")==job.deadline,"Original assigned native capture serial remains lossless");
  check(denied([&]{value.command(1,"family:21",command);}) && value.proposeJobControl(grant,1,"family:21",command)->ticket.wire==ticket->ticket.wire,"Unknown acquisition cannot become a second native attempt");
  const auto cancel=Wire().text("kind","cancel").begin("job").job(job).end().finish();auto cancelled=value.proposeJobControl(grant,1,"family:21",cancel);
  check(cancelled && preview_control_delivery_confirm(&channel,grant,ticket->ticket.ordinal) &&
   preview_control_delivery_receive(&channel,grant,cancelled->ticket.ordinal,cancelled->ticket.wire.c_str(),cancelled->ticket.wire.size())==PREVIEW_CONTROL_INVOKE,"Original cancellation retains native ticket ordering");
  value.command(1,"family:21",cancel);check(preview_control_delivery_complete(&channel,cancelled->ticket.ordinal) && preview_control_delivery_confirm(&channel,grant,cancelled->ticket.ordinal),"Cancellation transport confirmed independently");
  check(!value.pollRetirement(1) && !value.closeControlBinding(grant) && !value.empty(),"Unknown backend ownership prevents false physical retirement or binding close");
  check(endpoint.native([](auto& broker){auto rows=broker.inspect();return rows.size()==1 && !rows[0].terminal && rows[0].proofs.empty() && broker.charge()==4096;}),"Unresolved attempt retains original Broker charge without fabricated final proof");
  uint64_t attempts=0;std::ifstream(server.root/"capture-count")>>attempts;check(attempts==1,"Exactly one original capture request reached core");
  check(value.captureIntent(1)->command()==original->command(),"Cancellation and polling preserve original unknown intent");
  server.finish();
 }
 std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"nativeAcceptance\":false,\"normalOwnedExit\":true,\"retainedUnknownCases\":3}\n";return 0;
}catch(const std::exception& exception){std::cerr<<exception.what()<<'\n';return 1;}}
