module popup_layer_composition_v2 {
 type Tuple={pid:int,start:int,config:int,engine:int,epoch:int,provider:int,objects:List[int],contexts:List[int],present:List[bool],engines:List[bool],nativeBound:bool}
 type Input={sequence:int,code:int,state:int,time:int,layer:int,point:int,surface:bool,resource:bool,symbol:int,cancelled:bool}
 type Event=Sample({before:Tuple,after:Tuple,metadata:bool,row:bool,layer:int,point:int,nonce:int,owner:int})|Press({tuple:Tuple,nonce:int,owner:int,route:int})|Episode({prefix:bool,events:List[Input],tuple:Tuple,nonce:int,owner:int})|Effect({tuple:Tuple,nonce:int,owner:int,callback:bool,receipt:bool,native:bool,preserved:bool})|Accept|Change|WriteIntent|ProducerExit
 type State={tuple:Tuple,nonce:int,owner:int,layer:int,point:int,current:bool,witnessed:bool,pressed:bool,route:int,delivered:bool,effect:bool,accepted:bool}
 val slots=Set(0,1,2,3,4,5,6)
 val lexical=Set(0,1,2)
 val good:Tuple={pid:11,start:10,config:1,engine:1,epoch:1,provider:1,objects:[1,2,3,4,5,6,7],contexts:[11,12,13,0,0,0,0],present:[true,true,true,false,false,false,false],engines:[true,true,true,false,false,false,false],nativeBound:true}
 pure def valid(t:Tuple):bool=all{t.pid>0,t.start>0,t.config>0,t.engine>0,t.epoch>0,t.provider>0,t.nativeBound,t.objects.length()==7,t.contexts.length()==7,t.present.length()==7,t.engines.length()==7,
  slots.forall(i=>t.objects.nth(i)>0 and t.contexts.nth(i)>=0 and t.present.nth(i)==(t.contexts.nth(i)>0) and t.engines.nth(i)==t.present.nth(i)),
  lexical.forall(i=>t.present.nth(i)),slots.forall(i=>slots.forall(j=>i==j or t.objects.nth(i)!=t.objects.nth(j)))}
 var s:State
 action init=s'={tuple:good,nonce:0,owner:0,layer:0,point:0,current:false,witnessed:false,pressed:false,route:0,delivered:false,effect:false,accepted:false}
 def bound(t:Tuple,n:int,o:int):bool=s.current and s.witnessed and valid(t) and t==s.tuple and n==s.nonce and o==s.owner
 def episode(v:List[Input]):bool=if(v.length()!=2)false else {
  val a=v.nth(0);val b=v.nth(1);val code=if(s.route==1)272 else 28;
  all{a.sequence>0,b.sequence==a.sequence+1,a.code==code,b.code==code,a.state==1,b.state==0,a.time>=0,b.time>=0,a.time<=4294967295,b.time<=4294967295,
   a.layer==s.layer,b.layer==s.layer,a.surface,b.surface,not(a.cancelled),not(b.cancelled),
   if(s.route==1)a.point==s.point and b.point==s.point else a.resource and b.resource and a.symbol==65293 and b.symbol==65293}
 }
 action fire(e:Event):bool={s'=match e {
 |Sample(v)=>{...s,tuple:v.before,nonce:v.nonce,owner:v.owner,layer:v.layer,point:v.point,current:valid(v.before) and v.before==v.after and v.metadata and v.row and v.layer>0 and v.nonce>0 and v.owner>0,witnessed:valid(v.before) and v.before==v.after and v.metadata and v.row and v.layer>0 and v.nonce>0 and v.owner>0,pressed:false,delivered:false,effect:false,accepted:false}
 |Press(v)=>if(bound(v.tuple,v.nonce,v.owner) and Set(1,2).contains(v.route)){...s,pressed:true,route:v.route,delivered:false,effect:false,accepted:false}else {...s,current:false,accepted:false}
 |Episode(v)=>{...s,delivered:bound(v.tuple,v.nonce,v.owner) and s.pressed and v.prefix and episode(v.events),accepted:false}
 |Effect(v)=>{...s,effect:bound(v.tuple,v.nonce,v.owner) and s.pressed and v.callback and v.receipt and v.native and v.preserved,accepted:false}
 |Accept=>{...s,accepted:s.current and s.witnessed and s.pressed and s.delivered and s.effect}
 |Change=>{...s,current:false,witnessed:false,delivered:false,effect:false,accepted:false}
 |WriteIntent=>s
 |ProducerExit=>s
 }}
 val allProps=s.accepted implies all{s.current,s.witnessed,s.pressed,s.delivered,s.effect,valid(s.tuple),s.owner>0,s.nonce>0}
 val down:Input={sequence:1,code:272,state:1,time:0,layer:9,point:10,surface:true,resource:true,symbol:65293,cancelled:false}
 val up:Input={...down,sequence:2,state:0}
 action check(v:bool):bool=all{assert(v),s'=s}
 action sample(t:Tuple,u:Tuple):bool=fire(Sample({before:t,after:u,metadata:true,row:true,layer:9,point:10,nonce:1,owner:1}))
 action ready(r:int):bool=sample(good,good).then(fire(Press({tuple:good,nonce:1,owner:1,route:r})))
 action deliver(v:List[Input]):bool=fire(Episode({prefix:true,events:v,tuple:good,nonce:1,owner:1}))
 action effect(t:Tuple,n:int,o:int):bool=fire(Effect({tuple:t,nonce:n,owner:o,callback:true,receipt:true,native:true,preserved:true}))
 action done=effect(good,1,1).then(fire(Accept))
 action step={nondet b=Set(true,false).oneOf();nondet n=Set(0,1,2).oneOf();nondet t=Set(good,{...good,epoch:2},{...good,nativeBound:false},{...good,objects:[1,2,3,4,5,6,8]},{...good,contexts:[11,12,13,14,0,0,0],present:[true,true,true,true,false,false,false],engines:[true,true,true,true,false,false,false]}).oneOf();nondet e=Set(Sample({before:t,after:good,metadata:b,row:b,layer:9,point:10,nonce:n,owner:n}),Press({tuple:t,nonce:n,owner:n,route:n}),Episode({prefix:b,events:[down,up],tuple:t,nonce:n,owner:n}),Effect({tuple:t,nonce:n,owner:n,callback:b,receipt:b,native:b,preserved:b}),Accept,Change,WriteIntent,ProducerExit).oneOf();fire(e)}
 run pointerPositiveTest=init.then(ready(1)).then(deliver([down,up])).then(done).then(check(s.accepted))
 run returnPositiveTest=init.then(ready(2)).then(deliver([{...down,code:28},{...up,code:28}])).then(done).then(check(s.accepted))
 run getterEpochChangeTest=init.then(sample(good,{...good,epoch:2})).then(check(not(s.witnessed)))
 run getterNativeWindowGenerationTest=init.then(sample(good,{...good,objects:[1,2,3,4,5,8,7]})).then(check(not(s.witnessed)))
 run getterContextPresenceTest=init.then(sample(good,{...good,contexts:[11,12,13,14,0,0,0],present:[true,true,true,true,false,false,false],engines:[true,true,true,true,false,false,false]})).then(check(not(s.witnessed)))
 run missingLexicalContextTest=init.then(sample({...good,contexts:[0,12,13,0,0,0,0],present:[false,true,true,false,false,false,false],engines:[false,true,true,false,false,false,false]},good)).then(check(not(s.witnessed)))
 run duplicateAllocationTest=init.then(sample({...good,objects:[1,2,3,4,5,6,6]},good)).then(check(not(s.witnessed)))
 run nullNativeWindowTest=init.then(sample({...good,nativeBound:false},good)).then(check(not(s.witnessed)))
 run engineMetadataOnlyTest=init.then(fire(Press({tuple:good,nonce:1,owner:1,route:1}))).then(deliver([down,up])).then(done).then(check(not(s.accepted)))
 run intentCannotReleaseTest=init.then(ready(1)).then(fire(WriteIntent)).then(fire(ProducerExit)).then(done).then(check(not(s.accepted)))
 run pendingOnlyDownTest=init.then(ready(1)).then(deliver([down])).then(done).then(check(not(s.accepted)))
 run wrongSequenceTest=init.then(ready(1)).then(deliver([down,{...up,sequence:3}])).then(done).then(check(not(s.accepted)))
 run wrongLayerTest=init.then(ready(1)).then(deliver([down,{...up,layer:8}])).then(done).then(check(not(s.accepted)))
 run wrongIntegerPointTest=init.then(ready(1)).then(deliver([down,{...up,point:11}])).then(done).then(check(not(s.accepted)))
 run popupCancellationRefusedTest=init.then(ready(1)).then(deliver([{...down,cancelled:true},up])).then(done).then(check(not(s.accepted)))
 run replacedPrefixTest=init.then(ready(1)).then(fire(Episode({prefix:false,events:[down,up],tuple:good,nonce:1,owner:1}))).then(done).then(check(not(s.accepted)))
 run wrongReturnSymbolTest=init.then(ready(2)).then(deliver([{...down,code:28,symbol:65307},{...up,code:28}])).then(done).then(check(not(s.accepted)))
 run missingKeyboardResourceTest=init.then(ready(2)).then(deliver([{...down,code:28,resource:false},{...up,code:28}])).then(done).then(check(not(s.accepted)))
 run stalePopupAfterInputTest=init.then(ready(1)).then(deliver([down,up])).then(effect({...good,objects:[1,2,3,4,5,6,8]},1,1)).then(fire(Accept)).then(check(not(s.accepted)))
 run changedOwnerAfterInputTest=init.then(ready(1)).then(deliver([down,up])).then(effect(good,1,2)).then(fire(Accept)).then(check(not(s.accepted)))
 run changedNonceAfterInputTest=init.then(ready(1)).then(deliver([down,up])).then(effect(good,2,1)).then(fire(Accept)).then(check(not(s.accepted)))
 run actualEpisodeCannotReplaceEffectTest=init.then(ready(1)).then(deliver([down,up])).then(fire(Accept)).then(check(not(s.accepted)))
 run invalidationAfterAcceptTest=init.then(ready(1)).then(deliver([down,up])).then(done).then(fire(Change)).then(check(not(s.accepted)))
}
