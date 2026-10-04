module join {
 var s:{projection:bool,geometry:bool,pending:bool,binding:bool,output:bool,target:bool,live:bool,unknown:bool,age:int,effects:int}
 action init = s'={projection:false,geometry:false,pending:true,binding:true,output:true,target:true,live:true,unknown:false,age:0,effects:0}
 val ready = s.projection and s.geometry and s.pending and s.binding and s.output and s.live and not(s.unknown) and s.age<2000
 action settle = if(ready) s'={...s,pending:false,effects:s.effects+1} else s'=s
 action projection = (s'={...s,projection:true}).then(settle)
 action geometry = (s'={...s,geometry:true}).then(settle)
 action cancel = s'={...s,pending:false}
 action bindingChange = s'={...s,binding:false}
 action outputChange = s'={...s,output:false}
 action retire = s'={...s,target:false}
 action disconnect = s'={...s,live:false,pending:false}
 action unknown = s'={...s,unknown:true}
 action expire = s'={...s,age:2000,pending:false}
 action step = any {projection,geometry,cancel,bindingChange,outputChange,retire,disconnect,unknown,expire,settle}
 val safety = s.effects<=1 and (s.effects==0 or not(s.pending))
 run projectionFirstTest = init.then(projection).then(all {assert(s.effects==0 and s.pending),s'=s}).then(geometry).then(all {assert(s.effects==1 and not(s.pending)),s'=s})
 run geometryFirstTest = init.then(geometry).then(all {assert(s.effects==0 and s.pending),s'=s}).then(projection).then(all {assert(s.effects==1),s'=s})
 run duplicateTest = init.then(projection).then(geometry).then(geometry).then(projection).then(all {assert(s.effects==1),s'=s})
 run bindingChangeTest = init.then(projection).then(bindingChange).then(geometry).then(all {assert(s.effects==0),s'=s})
 run outputChangeTest = init.then(projection).then(outputChange).then(geometry).then(all {assert(s.effects==0),s'=s})
 run retiredTargetTest = init.then(projection).then(retire).then(geometry).then(all {assert(s.effects==0),s'=s})
 run deadlineTest = init.then(projection).then(expire).then(geometry).then(all {assert(s.effects==0),s'=s})
 run cancellationTest = init.then(projection).then(cancel).then(geometry).then(all {assert(s.effects==0),s'=s})
 run disconnectTest = init.then(projection).then(disconnect).then(geometry).then(all {assert(s.effects==0),s'=s})
 run unknownTest = init.then(projection).then(unknown).then(geometry).then(all {assert(s.effects==0),s'=s})
}
