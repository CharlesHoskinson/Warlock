// Executes the candidate's actual QML JavaScript functions with offline doubles.
const assert=require('node:assert/strict');const fs=require('node:fs');const vm=require('node:vm');
const file=fs.readFileSync(process.env.MOTION_QML_SOURCE || __dirname+'/widget_v62/WindowMotion.qml','utf8');
function method(name) {
 const begin=file.indexOf('  function '+name+'(');assert(begin>=0,name);
 const open=file.indexOf('{',begin);let depth=1,i=open+1;
 for(;depth && i<file.length;i++){if(file[i]==='{')depth++;if(file[i]==='}')depth--}
 return '('+file.slice(begin,i).trim()+')';
}
const live=[];
function frame(request,previous){return {modelData:request,previousFrame:previous,rectangle:request.from,imageStatus:1,routeProgress:0,visible:true,
 currentRect(){return this.rectangle},stop(){this.stopped=true},play(){this.played=true},dispose(){this.disposed=true}}}
const owner={barScreen:{name:'DP-1'},reducedMotion:false};
const root={owner,visible:true,requests:[],objects:{},contentItem:{},signal(){}};
const context=vm.createContext({root,owner,Image:{Ready:1},Object,motionFrame:{createObject(parent,args){const item=frame(args.modelData,args.previousFrame);live.push(item);return item}}});
for(const name of ['begin','start','cancel','reduce','intent','visualState'])root[name]=vm.runInContext(method(name),context).bind(root);
// QML function names resolve properties lexically; expose QML property accessors.
for(const name of ['requests','objects'])Object.defineProperty(context,name,{get(){return root[name]},set(v){root[name]=v},configurable:true});
function request(token,op,address='0x10',pid=100,id='stable10') {return {token,operation:op,identity:[address,id,pid],
 rect:{x:80,y:90,width:640,height:380},target:{screenName:'DP-1',rect:{x:950,y:10,width:19,height:19}}}}
assert(root.begin(request('one','minimize')));root.start(request('one','minimize'));
const first=root.objects['0x10'];first.rectangle={x:470,y:53,width:340,height:195};first.routeProgress=.5;
const state=root.visualState();assert.equal(state[0].routeProgress,.5);assert.deepEqual(state[0].rect,first.rectangle);assert.equal(state[0].imageReady,true);assert.equal(state[0].visible,true);
assert(root.begin(request('two','restore')));
const second=root.objects['0x10'];assert.deepEqual(second.modelData.from,first.rectangle);assert(first.stopped);
assert.equal(second.previousFrame,first);assert(!first.disposed);assert(!root.start(request('one','minimize')));
root.cancel(request('one','minimize'));assert.equal(root.objects['0x10'],second);
assert.equal(root.intent({address:'0x10',stableId:'stable10',pid:100}),'restore');
assert(root.begin(request('peer','minimize','0x20',200,'stable20')));
assert.equal(root.objects['0x10'],second); // A peer never destroys/restarts this frame.
assert(root.start(request('two','restore')));assert(second.played);
root.cancel(request('two','restore'));assert(second.disposed);assert(root.objects['0x20']);
owner.reducedMotion=true;assert(!root.begin(request('reduced','restore','0x20',200,'stable20')));
root.reduce();assert.equal(root.requests.length,0);assert.equal(Object.keys(root.objects).length,0);
owner.reducedMotion=false;
assert(root.begin(request('new','restore','0x10',101,'reused')));
assert.deepEqual(root.objects['0x10'].modelData.from,request('new','restore').target.rect);
assert.equal(root.intent({address:'0x10',stableId:'stable10',pid:100}),'');
console.log('Actual QML motion functions: reversal continuity, pixel retention, token guards, independent frames, reduced motion and reuse passed.');
