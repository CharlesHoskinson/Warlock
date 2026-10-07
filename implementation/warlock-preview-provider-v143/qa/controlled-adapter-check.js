'use strict';
const assert=require('assert'),fs=require('fs'),vm=require('vm');
const posted=[],frames=[],initializations=[];let checks=0,dom=null,receipts=[];
const check=(value,message)=>{checks++;assert.ok(value,message);};
const same=(a,b,message)=>{checks++;assert.deepStrictEqual(a,b,message);};
const port=()=>({send(){},listeners:[],subscribe(fn){this.listeners.push(fn);},unsubscribe(fn){this.listeners=this.listeners.filter(x=>x!==fn);}});
const admission={ports:{presentation:port(),requestAction:port(),actions:port()}};
const renderer={ports:{visualSnapshots:port(),acceptedSnapshots:port(),surfaceActions:port()}};
const nodes=new Map();
const nativeNode={id:'app',replaceChildren(child){nodes.set(child.id,child);},contains(){return true;}};
nodes.set('app',nativeNode);nodes.set('native-preview-admission-mount',{id:'native-preview-admission-mount'});
const document={getElementById:name=>nodes.get(name)||null,querySelector:()=>dom,createElement:()=>({id:''}),activeElement:null};
const context={window:{webkit:{messageHandlers:{native:{postMessage(value){posted.push(JSON.parse(value));}}}}},document,
 requestAnimationFrame(fn){frames.push(fn);},Elm:{
 NativePreviewAdmission:{init(options){initializations.push({kind:'admission',options});nodes.delete(options.node.id);return admission;}},
 NativePreviewRenderer:{init(options){initializations.push({kind:'renderer',options});nodes.delete(options.node.id);return renderer;}},
 Popup:{init(){throw new Error('A second window policy must never initialize');}}}};
context.window.window=context.window;
vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8'),context,{filename:process.argv[2]});
function drain(){for(let count=0;frames.length;count++){assert.ok(count<100);frames.shift()();}}
function node(publication,lease){return {dataset:{publication,lease},contains(){return true;}};}
same(posted,[{surfaceProtocol:2,kind:'presentation-ready'}],'Placeholder announces only original presentation readiness');
same(initializations.map(x=>x.kind),['admission'],'Only presentation placeholder initializes before native admission');
check(document.getElementById('app')===nativeNode && !document.getElementById('native-preview-admission-mount'),'Outer native-owned container survives Elm replacing the admission mount');
const original={publication:'10',lease:'3'};dom=node('10','3');context.window.receivePresentation(original);drain();
same(posted.at(-1),{surfaceProtocol:2,kind:'presentation-applied',publication:'10',lease:'3'},'Actual adapter binds placeholder DOM stamp after two RAF callbacks');
context.window.receivePresentation(original);dom=node('11','4');const before=posted.length;drain();same(posted.length,before,'Wrong DOM stamp cannot acknowledge the old presentation');
dom=node('10','3');context.window.receivePresentation(original);
const grant={channelProtocol:1,kind:'native-preview-renderer-grant',rendererLease:'1',sequenceFloor:'0',receiverEpoch:'1',binding:{lifetime:'7'}};
check(context.window.initializeNativePreviewRenderer(grant),'Native fixed initialization accepted once');
check(!context.window.initializeNativePreviewRenderer({...grant,rendererLease:'2'}),'Another native initialization cannot reset an existing receiver');
same(initializations.map(x=>x.kind),['admission','renderer'],'One pure receiver initializes and no browser window policy exists');
check(document.getElementById('app')===nativeNode && !document.getElementById('native-preview-renderer-mount'),'Outer container also survives pure Elm renderer mount replacement');
check(initializations[1].options.flags===grant,'Exact initial native grant reaches pure receiver flags');
same(admission.ports.actions.listeners.length,0,'Retired placeholder action subscription is removed');
drain();same(posted.length,before,'Old admission RAF is invalidated when renderer initializes');
renderer.ports.visualSnapshots.send=packet=>{
 for(const fn of renderer.ports.acceptedSnapshots.listeners)fn({channelProtocol:1,kind:'native-preview-projection-accepted',binding:grant.binding,receiverEpoch:packet.receiverEpoch,rendererLease:packet.rendererLease,visualSequence:packet.visualSequence});
};
const packet=sequence=>({rendererLease:'1',receiverEpoch:'1',visualSequence:String(sequence),visual:{surface:original}});
context.window.receiveNativeVisualProjection(packet(1));same(posted.length,before,'Decode receipt is held until DOM/RAF application');drain();
same(posted.at(-2).visualSequence,'1','Current exact visual receipt posted after original DOM stamp');
same(posted.at(-1),{surfaceProtocol:2,kind:'presentation-applied',publication:'10',lease:'3'},'Pure display updates retain original GTK presentation acknowledgment');
const prior=posted.length;context.window.receiveNativeVisualProjection(packet(2));context.window.receiveNativeVisualProjection(packet(3));drain();
same(posted.length,prior+2,'Only latest visual completion survives asynchronous supersession');same(posted.at(-2).visualSequence,'3','Old visual RAF cannot acknowledge a newer projection');
dom=node('11','4');const wrong=posted.length;context.window.receiveNativeVisualProjection(packet(4));drain();same(posted.length,wrong,'Wrong DOM publication/lease cannot produce an applied visual receipt');
dom=null;context.window.receiveNativeVisualProjection({rendererLease:'1',receiverEpoch:'1',visualSequence:'5',visual:{surface:null}});drain();
same(posted.at(-1).visualSequence,'5','Concealed projection requires absence of popup DOM');
context.window.receivePresentation(original);drain();same(posted.at(-1).visualSequence,'5','Raw presentation cannot bypass the pure visual channel after initialization');
console.log(JSON.stringify({passed:true,checks,rendererInitializations:1,browserWindowPolicies:0,syntheticPortsAndDOM:true,actualElmReceiver:false,actualWebKit:false,physicalRevealQualified:false,nativeAcceptance:false,fullReleaseAccepted:false}));
