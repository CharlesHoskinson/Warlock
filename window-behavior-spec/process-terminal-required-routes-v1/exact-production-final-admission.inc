 {
  std::lock_guard admission(faultMutex);bound();
  const bool matchedPending=std::any_of(queuedFaults.begin(),queuedFaults.end(),[&](const auto&fault){return fault.first==scope.objects[3]&&fault.second==scope.lease;});
  if(matchedPending||faultOverflow.load()||r->fault){invalidate();throw Refused("Matched pending fault/overflow forbids terminal retirement");}
  if(!r->job||!r->job->joined||!r->started||!r->historical||!r->exited||!r->normal||!r->out||!r->err||!r->gone)throw Refused("Terminal closure lost before admission commit");
  const auto selected=rows.find(r->arm.process);
  r->current=false;r->kernel=false;r->accepted=false;r->normalLife=true;r->receipt=true;history.push_back(r);rows.erase(selected);
 }