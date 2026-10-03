module maintenance {
 var loaded:bool
 var nonce:int
 var expected:int
 var prepared:int
 var retired:bool
 var held:bool
 var dirty:bool
 var watch:bool
 var grabs:bool
 var reader:bool
 var initialReader:bool
 var stable:bool
 var approved:bool
 var success:bool
 var unloads:int
 var locked:bool
 action initialize(readerIntent:bool):bool=all{loaded'=false,nonce'=0,expected'=0,prepared'=0,retired'=false,held'=false,dirty'=false,watch'=false,grabs'=false,reader'=readerIntent,initialReader'=readerIntent,stable'=true,approved'=true,success'=false,unloads'=0,locked'=true}
 action init=initialize(false)
 pure def quiet(h:bool,d:bool):bool=not(h) and not(d)
 action load=all{stable,approved,locked,not(loaded),loaded'=true,nonce'=nonce+1,expected'=expected,prepared'=0,retired'=false,held'=held,dirty'=dirty,watch'=false,grabs'=false,reader'=reader,initialReader'=initialReader,stable'=stable,approved'=approved,success'=true,unloads'=unloads,locked'=locked}
 action snapshot=all{loaded,expected'=nonce,loaded'=loaded,nonce'=nonce,prepared'=prepared,retired'=retired,held'=held,dirty'=dirty,watch'=watch,grabs'=grabs,reader'=reader,initialReader'=initialReader,stable'=stable,approved'=approved,success'=success,unloads'=unloads,locked'=locked}
 action activity(h:bool,d:bool):bool=all{loaded,not(retired),held'=h,dirty'=d,watch'=true,grabs'=true,loaded'=loaded,nonce'=nonce,expected'=expected,prepared'=prepared,retired'=retired,reader'=reader,initialReader'=initialReader,stable'=stable,approved'=approved,success'=success,unloads'=unloads,locked'=locked}
 action prepare=all{loaded,loaded'=loaded,nonce'=nonce,expected'=expected,prepared'=if(stable and expected==nonce and quiet(held,dirty))nonce else prepared,retired'=(retired or (stable and expected==nonce and quiet(held,dirty))),watch'=if(stable and expected==nonce and quiet(held,dirty))false else watch,grabs'=if(stable and expected==nonce and quiet(held,dirty))false else grabs,held'=held,dirty'=dirty,reader'=reader,initialReader'=initialReader,stable'=stable,approved'=approved,success'=(stable and expected==nonce and quiet(held,dirty)),unloads'=unloads,locked'=locked}
 action replacement=all{loaded,not(held),not(dirty),nonce'=nonce+1,expected'=expected,prepared'=0,retired'=false,watch'=false,grabs'=false,held'=false,dirty'=false,loaded'=loaded,reader'=reader,initialReader'=initialReader,stable'=stable,approved'=approved,success'=false,unloads'=unloads,locked'=locked}
 action unload=all{loaded,locked,stable,approved,retired,prepared==nonce,expected==nonce,loaded'=false,nonce'=nonce,expected'=expected,prepared'=prepared,retired'=retired,watch'=watch,grabs'=grabs,held'=held,dirty'=dirty,reader'=reader,initialReader'=initialReader,stable'=stable,approved'=approved,success'=true,unloads'=unloads+1,locked'=locked}
 action idle=all{loaded'=loaded,nonce'=nonce,expected'=expected,prepared'=prepared,retired'=retired,watch'=watch,grabs'=grabs,held'=held,dirty'=dirty,reader'=reader,initialReader'=initialReader,stable'=stable,approved'=approved,success'=success,unloads'=unloads,locked'=locked}
 action step=any{load,snapshot,activity(true,false),activity(false,true),activity(false,false),prepare,replacement,unload,idle}
 val safe=(retired implies (not(watch) and not(grabs) and not(held) and not(dirty))) and reader==initialReader and (prepared>0 implies retired)
 run defaultPassiveTest=init.then(load).then(all{assert(not(watch) and not(grabs) and not(reader)),idle})
 run staleNonceRefusalTest=init.then(load).then(snapshot).then(replacement).then(activity(false,false)).then(prepare).then(all{assert(not(success) and watch and grabs and not(retired)),idle})
 run heldRefusalPreservesTest=init.then(load).then(snapshot).then(activity(true,false)).then(prepare).then(all{assert(not(success) and held and watch and grabs and not(retired)),idle})
 run lockRefusalPreservesTest=init.then(load).then(snapshot).then(activity(false,true)).then(prepare).then(all{assert(not(success) and dirty and watch and grabs and not(retired)),idle})
 run trueRetirementTest=init.then(load).then(snapshot).then(activity(false,false)).then(prepare).then(all{assert(success and retired and not(watch) and not(grabs)),idle})
 run normalUnloadTest=init.then(load).then(snapshot).then(prepare).then(unload).then(all{assert(not(loaded) and unloads==1),idle})
 run sameArtifactReloadNewNonceTest=init.then(load).then(snapshot).then(prepare).then(unload).then(load).then(all{assert(nonce==2 and not(retired) and expected==1),idle})
 run enabledIntentPreservedTest=initialize(true).then(load).then(snapshot).then(prepare).then(unload).then(load).then(all{assert(reader and initialReader and not(grabs)),idle})
}
