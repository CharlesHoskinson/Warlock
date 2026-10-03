module physical_keyboard {
 type Event=Plan({valid:bool,physical:bool})|Connect({live:bool,peer:bool})|KeymapReady({valid:bool,eof:bool})|Press|Release|Advance|Change|Error|Finish
 var planned:bool
 var connected:bool
 var mapped:bool
 var live:bool
 var failed:bool
 var held:bool
 var index:int
 var presses:int
 var releases:int
 var complete:bool
 action init=all{planned'=false,connected'=false,mapped'=false,live'=true,failed'=false,held'=false,index'=0,presses'=0,releases'=0,complete'=false}
 action fire(e:Event):bool=all{
  planned'=(planned or match e{|Plan(v)=>v.valid and v.physical and not(connected) and presses==0|_=>false}),
  connected'=(connected or match e{|Connect(v)=>planned and not(failed) and live and v.live and v.peer|_=>false}),
  mapped'=(mapped or match e{|KeymapReady(v)=>connected and planned and not(failed) and live and v.valid and v.eof|_=>false}),
  live'=(live and e!=Change),
  failed'=(failed or e==Error or e==Change or match e{|Plan(v)=>not(v.valid and v.physical)or connected or presses>0|Connect(v)=>not(planned and live and v.live and v.peer)|KeymapReady(v)=>not(connected and planned and live and v.valid and v.eof)|Press=>not(planned and connected and mapped and live and not(held)and index<11)|Release=>not(held and live)|Advance=>held or presses!=releases or presses!=index+1 or index>=11|Finish=>held or index!=11 or presses!=11 or releases!=11|_=>false}),
  held'=if(e==Press and planned and connected and mapped and live and not(failed)and not(held)and index<11)true else if(e==Release and held and live)false else held,
  presses'=if(e==Press and planned and connected and mapped and live and not(failed)and not(held)and index<11)presses+1 else presses,
  releases'=if(e==Release and held and live)releases+1 else releases,
  index'=if(e==Advance and not(held) and presses==releases and presses==index+1 and not(failed))index+1 else index,
  complete'=(e==Finish and not(failed)and live and not(held)and index==11 and presses==11 and releases==11)
 }
 val allProps=all{releases<=presses,presses-releases<=1,index<=releases,index>=0,index<=11,presses>0 implies planned and connected and mapped,complete implies not(failed)and live and not(held)and presses==releases and index==11}
 action step={nondet b=Set(true,false).oneOf();nondet e=Set(Plan({valid:b,physical:true}),Plan({valid:true,physical:b}),Connect({live:b,peer:true}),Connect({live:true,peer:b}),KeymapReady({valid:b,eof:true}),Press,Release,Advance,Change,Error,Finish).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),planned'=planned,connected'=connected,mapped'=mapped,live'=live,failed'=failed,held'=held,index'=index,presses'=presses,releases'=releases,complete'=complete}
 action ready=fire(Plan({valid:true,physical:true})).then(fire(Connect({live:true,peer:true}))).then(fire(KeymapReady({valid:true,eof:true})))
 action pair=fire(Press).then(fire(Release)).then(fire(Advance))
}
