var passed=0
function assert(v,label){if(!v)throw new Error(label);passed++}
function refused(fn,label){var caught=false;try{fn()}catch(e){caught=true}assert(caught,label)}
var a={address:"0x123",stableId:"18000000",pid:7}, b={address:"0x124",stableId:"18000001",pid:7}
var encoded=JSON.stringify([a,b])
function observed(home,gen,delegate,x) {
 var w={widgetGeneration:gen,delegateGeneration:delegate,screen:{name:"HEADLESS-1",width:1600,height:1000},monitor:{id:0,x:100,y:-30,width:1600,height:1000,scale:1},bar:{position:"bottom",x:0,y:960,width:1600,height:40},icon:{x:x,y:10,width:19,height:19},clip:{x:x,y:10,width:600,height:40},allocation:{width:32,height:40}}
 return {target:{visible:true,home:home,screenName:"HEADLESS-1",monitorX:100,monitorY:-30,rect:{x:100+x,y:940,width:19,height:19}},witness:w}
}
var g1=allocateGeneration(),g2=allocateGeneration(),d1=allocateGeneration(),d2=allocateGeneration(),calls=0
function widget(gen,home){return {motionWidgetGeneration:gen,motionTargetObservation:function(id){calls++;return observed(home,gen,id.address===a.address?d1:d2,id.address===a.address?20:60)}}}
var w1=widget(g1,false),w2=widget(g2,true),result=capture(encoded,[w1,w2])
assert(result.queryKind==="one-bulk-observation"&&result.members.length===2,"one bulk vector")
assert(calls===8,"two bounded actual samples per candidate")
assert(result.members[0].identity.address===a.address&&result.members[1].identity.address===b.address,"input order")
assert(result.members.every(function(r){return r.witness.widgetGeneration===g2&&r.target.home}),"home selected")
assert(result.members[0].witness.delegateGeneration!==result.members[1].witness.delegateGeneration,"per-member actual delegate")
refused(function(){capture(JSON.stringify([a,a]),[w1])},"exact duplicate")
refused(function(){capture(JSON.stringify([a,{address:a.address,stableId:b.stableId,pid:9}]),[w1])},"reused address")
refused(function(){capture(JSON.stringify([{address:a.address,stableId:1,pid:7}]),[w1])},"numeric stable")
refused(function(){capture(JSON.stringify([{address:a.address,stableId:a.stableId,pid:true}]),[w1])},"boolean pid")
refused(function(){capture(JSON.stringify([{address:a.address,stableId:a.stableId,pid:1.5}]),[w1])},"fractional pid")
refused(function(){capture(JSON.stringify([{address:a.address,stableId:a.stableId,pid:2147483648}]),[w1])},"pid overflow")
refused(function(){capture(JSON.stringify([{address:a.address,stableId:a.stableId,pid:7,override:{}}]),[w1])},"override key")
refused(function(){capture('[]',[w1])},"empty request")
refused(function(){capture(JSON.stringify(Array(513).fill(a)),[w1])},"request bound")
refused(function(){capture('[{"address":"0x123","address":"0x124","stableId":"18000000","pid":7}]',[w1])},"duplicate lexical field")
refused(function(){capture('[{"address":"0x123","stableId":"18000000","p\\u0069d":7}]',[w1])},"escaped field")
var oldCalls=calls
refused(function(){capture(JSON.stringify([a,a]),[{motionTargetObservation:function(){calls++}}])},"refuse before lookup")
assert(calls===oldCalls,"no lookup for refused request")
refused(function(){capture(JSON.stringify([a]),[w1,w1])},"duplicate widget")
var missing={motionWidgetGeneration:g1,motionTargetObservation:function(){return null}}
result=capture(JSON.stringify([a]),[missing]);assert(result.members[0].target===null&&result.members[0].witness===null,"missing honest")
var count=0,appears={motionWidgetGeneration:g1,motionTargetObservation:function(){return ++count===1?null:observed(true,g1,d1,20)}}
refused(function(){capture(JSON.stringify([a]),[appears])},"missing becomes visible invalidates")
count=0;var changed={motionWidgetGeneration:g1,motionTargetObservation:function(){return observed(true,g1,d1,20+(count++))}}
refused(function(){capture(JSON.stringify([a]),[changed])},"allocation changed")
var bad={motionWidgetGeneration:g1,motionTargetObservation:function(){var r=observed(true,g1,d1,20);r.target.rect.x++;return r}}
refused(function(){capture(JSON.stringify([a]),[bad])},"translation exact")
bad.motionTargetObservation=function(){var r=observed(true,g1,d1,20);r.witness.icon.width=NaN;return r}
refused(function(){capture(JSON.stringify([a]),[bad])},"nonfinite allocation")
bad.motionTargetObservation=function(){var r=observed(true,g1,d1,590);return r}
refused(function(){capture(JSON.stringify([a]),[bad])},"clipped allocation")
var tie=widget(g2,false);result=capture(JSON.stringify([a]),[w1,tie]);assert(result.members[0].witness.widgetGeneration===g1,"home tie source order")
var saved=nextGeneration;nextGeneration=9007199254740990;assert(allocateGeneration()===9007199254740991,"last representable generation");refused(allocateGeneration,"generation exhaustion");nextGeneration=saved
"batch policy assertions: "+passed
