module exit_ack {
 var requested: bool
 var ack: bool
 var quit: bool
 var exited: bool
 var localVFS: bool
 var activated: bool
 action init = all {requested'=false,ack'=false,quit'=false,exited'=false,localVFS'=true,activated'=false}
 action request = all {not(quit),not(exited),requested'=true,ack'=ack,quit'=quit,exited'=exited,localVFS'=localVFS,activated'=activated}
 action acknowledge = all {requested,not(quit),not(exited),requested'=requested,ack'=true,quit'=quit,exited'=exited,localVFS'=localVFS,activated'=activated}
 val canQuit = not(exited) and (not(requested) or ack)
 action stop = all {canQuit,requested'=requested,ack'=ack,quit'=true,exited'=exited,localVFS'=localVFS,activated'=activated}
 action exit = all {quit,requested'=requested,ack'=ack,quit'=quit,exited'=true,localVFS'=localVFS,activated'=activated}
 action fileInit = all {requested'=requested,ack'=ack,quit'=quit,exited'=exited,localVFS'=localVFS,activated'=not(localVFS)}
 action step = any {request,acknowledge,stop,exit,fileInit}
 val safeOrder = (quit and requested) implies ack
 val responseTruth = ack implies requested
 val exitedOrder = exited implies quit
 val noDaemon = localVFS implies not(activated)
 val invariants = safeOrder and responseTruth and exitedOrder and noDaemon
}
