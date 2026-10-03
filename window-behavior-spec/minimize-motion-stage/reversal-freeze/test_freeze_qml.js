// Executes the staged QML's actual JavaScript, including epoch and input holds.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync(__dirname+'/widget_v65/WindowMotion.qml','utf8');
function block(file,start){const open=file.indexOf('{',start);let depth=1,i=open+1;for(;depth;i++){if(file[i]==='{')depth++;if(file[i]==='}')depth--}return file.slice(open,i)}
function method(file,name){const start=file.indexOf('  function '+name+'(');assert(start>=0,name);return '('+file.slice(start,file.indexOf('{',start))+block(file,start)+')'}
function fixture(){
 const owner={barScreen:{name:'DP-1'},reducedMotion:false,appGroups:[{windows:[{address:'0x10',stableId:'stable10',pid:100},{address:'0x20',stableId:'stable20',pid:200}]}]},signals=[];
 const root={owner,requests:[],objects:{},epochs:{},visible:true,contentItem:{},signal(...a){signals.push(a)}};
 const context=vm.createContext({root,owner,Image:{Ready:1},Object,Date,motionFrame:{createObject(parent,args){
  return {modelData:args.modelData,previousFrame:args.previousFrame,routeProgress:0,imageStatus:1,visible:true,heldFor:'',localHold:false,
   holdTimeout:{running:false,stop(){this.running=false},restart(){this.running=true}},
   currentRect(){const r={};for(const f of ['x','y','width','height'])r[f]=this.modelData.from[f]+(this.modelData.to[f]-this.modelData.from[f])*this.routeProgress;return r},
   stop(){this.stopped=true},play(){this.played=true},dispose(){this.disposed=true;this.holdTimeout.stop()}}
 }}});
 for(const n of ['requests','objects','epochs'])Object.defineProperty(context,n,{get(){return root[n]},set(v){root[n]=v}});
 for(const n of ['sameIdentity','liveIdentity','collectEpochs','epochAllows','remember','freeze','holdCaptured','begin','start','cancel','reduce','visualState']){root[n]=vm.runInContext(method(source,n),context).bind(root);context[n]=root[n]}
 return {root,owner,signals,context};
}
function request(token,operation='minimize',pid=100,id='stable10'){return {token:'session-'+token,operation,identity:['0x10',id,pid],rect:{x:80,y:90,width:640,height:380},target:{screenName:'DP-1',rect:{x:950,y:10,width:19,height:19}}}}
function freeze(token,previous){return {...request(token,'restore'),previousToken:'session-'+previous}}
let count=0;function test(name,body){body();count++;console.log('PASS '+name)}
test('freeze/current rectangle retained exactly at new begin',()=>{
 const {root}=fixture();assert(root.begin(request(1)));root.start(request(1));const old=root.objects['0x10'];old.routeProgress=.37;
 const rect=old.currentRect(),ack=root.freeze(freeze(2,1));assert.deepEqual(ack.rect,rect);assert.equal(old.heldFor,'session-2');assert(old.stopped);
 assert(root.begin(request(2,'restore')));assert.deepEqual(root.objects['0x10'].modelData.from,rect);assert.equal(root.objects['0x10'].previousFrame,old);
});
test('old readiness start begin and cancel cannot overwrite reservation',()=>{
 const {root}=fixture();root.begin(request(1));root.objects['0x10'].routeProgress=.43;root.freeze(freeze(2,1));
 assert.equal(root.start(request(1)),false);assert.equal(root.begin(request(1)),false);root.cancel(request(1));assert(root.objects['0x10']);
 assert(root.begin(request(2,'restore')));assert.equal(root.begin(request(1)),false);
});
test('multiple reservations retain source and reject stale freeze',()=>{
 const {root}=fixture();root.begin(request(1));const old=root.objects['0x10'];old.routeProgress=.52;
 root.freeze(freeze(2,1));const ack=root.freeze(freeze(3,2));assert.equal(ack.routeProgress,.52);assert.equal(old.heldFor,'session-3');
 assert.equal(root.freeze(freeze(2,1)),null);assert.equal(root.begin(request(2,'restore')),false);assert(root.begin(request(3)));
});
test('reservation without a loaded image rejects its delayed old begin',()=>{
 const {root}=fixture();assert(root.freeze(freeze(2,1)).accepted);assert.equal(root.begin(request(1)),false);assert(root.begin(request(2,'restore')));
});
test('different PID/stable ID cannot freeze or adopt old image',()=>{
 const {root,owner}=fixture();root.begin(request(1));const old=root.objects['0x10'];assert.equal(root.freeze({...freeze(2,1),identity:['0x10','other',100]}),null);
 assert.equal(root.freeze({...freeze(2,1),identity:['0x10','stable10',101]}),null);assert(!old.stopped);
 owner.appGroups[0].windows[0].pid=101;assert(root.begin(request(3,'restore',101)));assert.deepEqual(root.objects['0x10'].modelData.from,request(3).target.rect);
});
test('failed preparation cancels held token and clears old request',()=>{
 const {root}=fixture();root.begin(request(1));const old=root.objects['0x10'];root.freeze(freeze(2,1));root.cancel(freeze(2,1));
 assert(old.disposed);assert.equal(root.requests.length,0);assert.equal(Object.keys(root.objects).length,0);assert.equal(root.begin(request(2,'restore')),false);
});
test('reduced motion removes hold and signals latest token',()=>{
 const {root,signals}=fixture();root.begin(request(1));root.freeze(freeze(2,1));root.reduce();assert.equal(root.requests.length,0);assert.equal(Object.keys(root.objects).length,0);
 assert.deepEqual(signals,[['fail','session-2']]);
});
test('input hold is captured identity guarded and service replaces timeout',()=>{
 const {root}=fixture();root.begin(request(1));const item=root.objects['0x10'];assert(!root.holdCaptured({address:'0x10',stableId:'stale',pid:100}));
 assert(root.holdCaptured({address:'0x10',stableId:'stable10',pid:100}));assert(item.localHold);assert(item.holdTimeout.running);assert(!root.start(request(1)));
 root.freeze(freeze(2,1));assert(!item.localHold);assert(!item.holdTimeout.running);assert.equal(item.heldFor,'session-2');
});
test('restarted service session rejects older session callbacks',()=>{
 const {root}=fixture();root.begin(request(1));root.cancel(request(1));assert(root.begin({...request(1,'restore'),token:'new-1'}));assert(!root.begin(request(20)));
});
test('caption/taskbar action holds pixels before spawning helper',()=>{
 const file=fs.readFileSync(__dirname+'/widget_v65/Windows.qml','utf8'),calls=[];
 const context=vm.createContext({groups:[{windows:[{address:'0x10',stableId:'stable10',pid:100}]}],homeDir:'/tmp/fake',windowMotion:{holdCaptured(w){calls.push(['hold',w.stableId])}},runArgs(args){calls.push(['exec',args])},popupOpen:true});
 vm.runInContext(method(file,'windowAction'),context)('restore','0x10');assert.equal(calls[0][0],'hold');assert.equal(calls[1][0],'exec');assert.equal(calls[1][1][3],'stable10');
});
test('actual asynchronous readiness handler cannot revive a held image',()=>{
 const start=source.indexOf('onStatusChanged:');const body=block(source,start);let restarted=0,disposed=0;
 const context=vm.createContext({status:1,Image:{Ready:1,Error:2},signaled:false,heldFor:'session-2',localHold:false,previousFrame:{dispose(){disposed++}},readiness:{restart(){restarted++}},root:{signal(){throw Error('unexpected signal')}},modelData:request(1)});
 vm.runInContext(body,context);assert.equal(restarted,0);assert.equal(disposed,0);
 context.heldFor='';context.localHold=true;vm.runInContext(body,context);assert.equal(restarted,0);
 context.localHold=false;vm.runInContext(body,context);assert.equal(restarted,1);assert.equal(disposed,1);
});
test('independent family frame survives peer hold/cancel',()=>{
 const {root}=fixture();root.begin(request(1));const peer={...request(2),identity:['0x20','stable20',200]};root.begin(peer);
 const item=root.objects['0x20'];root.freeze(freeze(3,1));root.cancel(freeze(3,1));assert.equal(root.objects['0x20'],item);assert(!item.disposed);
});
test('hidden screen/reduced preparation rejects without replacing prior frame',()=>{
 const {root,owner}=fixture();root.begin(request(1));const item=root.objects['0x10'];
 assert(!root.begin({...request(2),target:{screenName:'other'}}));owner.reducedMotion=true;assert(!root.begin(request(2)));
 assert.equal(root.objects['0x10'],item);assert(!item.stopped);
});
test('live cancelled token stays rejected after long idle across minimized state',()=>{
 const {root,owner,context}=fixture();root.begin(request(1));root.cancel(request(1));
 owner.appGroups[0].windows[0].workspace={name:'special:win-minimized'};
 context.Date={now(){return 600000}};root.collectEpochs();assert(root.epochs['0x10']);assert(!root.begin(request(1)));
 assert.equal(root.requests.length,0);assert.equal(Object.keys(root.objects).length,0);
});
test('all retired live sessions remain rejected after more than eight restarts',()=>{
 const {root}=fixture();root.begin(request(1));root.cancel(request(1));
 for(let i=0;i<12;i++){const next={...request(1),token:'restart'+i+'-1'};assert(root.begin(next));root.cancel(next)}
 root.collectEpochs();assert(!root.begin(request(40)));assert.equal(root.requests.length,0);
});
test('closed/reused epoch is collected but stale begin cannot create a layer',()=>{
 const {root,owner}=fixture();root.begin(request(1));root.cancel(request(1));owner.appGroups[0].windows[0].pid=101;
 root.collectEpochs();assert(!root.epochs['0x10']);assert(!root.begin(request(20)));assert.equal(root.requests.length,0);assert.equal(Object.keys(root.objects).length,0);
 assert(root.begin(request(1,'restore',101)));
});
test('loading replacement acknowledges actually visible ancestor snapshot',()=>{
 const {root}=fixture();const first={...request(1),image:'/private/one.png',nativeRect:request(1).rect,wholeWindow:true};root.begin(first);
 const ancestor=root.objects['0x10'];ancestor.routeProgress=.42;root.freeze(freeze(2,1));root.begin({...request(2,'restore'),image:'/private/two.png'});
 const loading=root.objects['0x10'];loading.imageStatus=0;loading.visible=false;
 const ack=root.freeze(freeze(3,2));assert.equal(ack.snapshot.image,'/private/one.png');assert.equal(ack.snapshot.whole,true);assert.deepEqual(ack.snapshot.nativeRect,first.nativeRect);assert(ack.visible);
});
console.log(count+' actual QML freeze/input/epoch scenarios passed');
