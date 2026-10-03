module maintenance {
 var stable:bool
 var approved:bool
 var loaded:bool
 var quiet:bool
 var retired:bool
 var subscribed:bool
 var prepared:bool
 var unloads:int
 var safeUnloads:int
 action init=all{stable'=true,approved'=false,loaded'=false,quiet'=false,retired'=false,subscribed'=false,prepared'=false,unloads'=0,safeUnloads'=0}
 action approve=all{approved'=true,stable'=stable,loaded'=loaded,quiet'=quiet,retired'=retired,subscribed'=subscribed,prepared'=prepared,unloads'=unloads,safeUnloads'=safeUnloads}
 action load=all{approved,stable,not(loaded),loaded'=true,retired'=false,subscribed'=false,prepared'=false,approved'=approved,stable'=stable,quiet'=quiet,unloads'=unloads,safeUnloads'=safeUnloads}
 action subscribe=all{loaded,not(retired),subscribed'=true,approved'=approved,stable'=stable,loaded'=loaded,quiet'=quiet,retired'=retired,prepared'=prepared,unloads'=unloads,safeUnloads'=safeUnloads}
 action release=all{quiet'=true,approved'=approved,stable'=stable,loaded'=loaded,retired'=retired,subscribed'=subscribed,prepared'=prepared,unloads'=unloads,safeUnloads'=safeUnloads}
 action prepare=all{loaded,stable,prepared'=quiet,retired'=(retired or quiet),subscribed'=if(quiet)false else subscribed,approved'=approved,stable'=stable,loaded'=loaded,quiet'=quiet,unloads'=unloads,safeUnloads'=safeUnloads}
 action replaceTarget=all{stable'=false,approved'=approved,loaded'=loaded,quiet'=quiet,retired'=retired,subscribed'=subscribed,prepared'=prepared,unloads'=unloads,safeUnloads'=safeUnloads}
 action unload=all{stable,loaded,prepared,retired,loaded'=false,unloads'=unloads+1,safeUnloads'=safeUnloads+1,approved'=approved,stable'=stable,quiet'=quiet,retired'=retired,subscribed'=subscribed,prepared'=prepared}
 action idle=all{stable'=stable,approved'=approved,loaded'=loaded,quiet'=quiet,retired'=retired,subscribed'=subscribed,prepared'=prepared,unloads'=unloads,safeUnloads'=safeUnloads}
 action step=any{approve,load,subscribe,release,prepare,replaceTarget,unload}
 val allProps=unloads==safeUnloads and (retired implies not(subscribed)) and (prepared implies retired)
 run falsePreparePreservesSubscriptionTest=init.then(approve).then(load).then(subscribe).then(prepare).then(all{assert(not(prepared) and subscribed and not(retired)),idle})
 run truePrepareRetiresTest=init.then(approve).then(load).then(subscribe).then(release).then(prepare).then(all{assert(prepared and retired and not(subscribed)),idle})
 run normalUnloadRequiresRetirementTest=init.then(approve).then(load).then(release).then(prepare).then(unload).then(all{assert(not(loaded) and unloads==1),idle})
 run targetReplacementPreservesRetiredTest=init.then(approve).then(load).then(release).then(prepare).then(replaceTarget).then(all{assert(retired and prepared and loaded and not(stable)),idle})
}
