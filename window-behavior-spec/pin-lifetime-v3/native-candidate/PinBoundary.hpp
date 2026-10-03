#pragma once
#include "PinAction.hpp"
namespace PinAction {
// Adapter invocation metadata survives a throwing post-action observation.
// An exception cannot manufacture a no-write refusal after an owning call.
template<class Adapter>Report executeConservative(Adapter&adapter,const Snapshot&before){
 Report report;report.before=before;report.after=before;report.desired=!before.pinned;
 try{
  report=execute(adapter);report.actionsInvoked=adapter.invoked;
  if(!report.ok&&!adapter.invoked)report.phase=Phase::Validate;
  return report;
 }
 catch(const std::exception&error){report.phase=adapter.phase;report.actionsInvoked=adapter.invoked;report.reason=std::string("Native observation failed: ")+error.what();}
 catch(...){report.phase=adapter.phase;report.actionsInvoked=adapter.invoked;report.reason="Unknown native observation failure";}
 return report;
}
}
