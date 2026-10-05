# Host enrollment and scope for the in-process native producer

The actual shared host now exports preview_host_enrollment and
preview_host_source_scope through its existing own C bootstrap. Both require the
GTK owner thread, clear failed output and preserve the original native request
correlation and IPC budget. Opening a second same-PID Native hello would replace
the frontend epoch and invalidate the retained host grant; these APIs avoid it.
The backend's ordinary desktop grant remains separate.

Protected full33-command optimized Elm/C/C++ build passed at
qa/build-1791231646780910186/report.json, including79 real grant/scope/C API
checks,41 physical delivery checks,23 actual compiled Presenter/live Broker ACK
checks and23 retained GIO ownership checks. All49 Elm policy modules and the
Broker/demand/delivery/native client headers are unchanged from qualifiedv5.
The v5 explicitly selected Quint evidence remains applicable to those unchanged
headers; no new model run is claimed here.

The added producer-facing host wrappers are compiled but need actual runtime
qualification. Eligible compositor-owned client/family source capture, whole
host WebKit receipt delivery and ordered ownership/restart/shutdown integration
remain open. Native492 scope remains falseeligible/unqualified; no production
capture or original S09 acceptance follows from these APIs. The mandatory
release gates and Omarchy command/shortcut compatibility requirements remain.
