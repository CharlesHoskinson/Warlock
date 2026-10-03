// Test the actual installed QML relay function with transport/geometry fixtures.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const base=path.join(process.env.HOME,'.config/omarchy/plugins/hoskinson.windows');
const manifest=JSON.parse(fs.readFileSync(path.join(base,'manifest.json'),'utf8'));
const source=fs.readFileSync(path.join(base,manifest.entryPoints.barWidget),'utf8');
const start=source.indexOf('  function externalFileDrag('),end=source.indexOf('  Timer {id:filePreviewDelay',start);
assert(start>=0&&end>start,'installed relay missing');
const timer=()=>({starts:0,stops:0,restart(){this.starts++},stop(){this.stops++}});
function fixture(){
  const c={fileDragStamp:-1,fileDragActive:false,fileDragOnTaskbar:false,popupOpen:false,menuMode:false,keyboardMode:false,currentMonitor:0,dragEntries:0,filePreviewWindow:null,filePreviewKey:'',monitors:[{id:0,x:1000,y:200}],bar:{position:'top'},barScreen:{width:1600,height:1000},barWindow:{width:1600,height:26,contentItem:{}},tasksFlickable:{width:100,height:26,mapToItem(){return{x:10,y:0}}},windowRepeater:{count:0,itemAt(){return null}},beginDragGroup(x){this.chosenX=x},stopDragHover(){this.stopped=(this.stopped||0)+1},fileDragWatchdog:timer(),filePreviewDelay:timer(),closeDelay:timer()};
  c.beginDragGroup=x=>{c.chosenX=x};c.stopDragHover=()=>{c.stopped=(c.stopped||0)+1};
  c.root=c;vm.createContext(c);vm.runInContext(source.slice(start,end),c);return c;
}
let c=fixture();c.externalFileDrag(true,1030,213,0,100);
assert(c.fileDragOnTaskbar&&c.chosenX===20&&c.dragEntries===1,'screen offset routing');
c.externalFileDrag(false,0,0,-1,99);assert(c.fileDragActive&&c.fileDragStamp===100,'old end cancelled newer drag');
c.externalFileDrag(false,0,0,-1,101);assert(!c.fileDragActive&&!c.fileDragOnTaskbar&&c.filePreviewWindow===null,'end cleanup');
c.externalFileDrag(true,1030,213,0,100);assert(!c.fileDragActive,'late move revived cancelled drag');
c=fixture();c.externalFileDrag(true,1030,213,1,100);assert(!c.fileDragOnTaskbar,'foreign monitor hovered local icon');
c=fixture();c.bar.position='bottom';c.externalFileDrag(true,1030,1187,0,100);assert(c.fileDragOnTaskbar,'bottom bar routing');
c=fixture();c.popupOpen=true;const w={address:'0xabc',pid:40,stableId:70};
c.windowRepeater={count:1,itemAt(){return {modelData:w,width:120,height:149,QsWindow:{window:{}},mapToItem(){return{x:20,y:100}}}}};
c.externalFileDrag(true,1030,320,0,100);assert(c.filePreviewWindow.address==='0xabc'&&c.filePreviewDelay.starts===1,'preview identity capture');
c.externalFileDrag(true,1030,320,0,101);assert(c.filePreviewDelay.starts===1,'heartbeat reset preview dwell');
c.externalFileDrag(true,1030,500,0,102);assert(c.filePreviewWindow===null,'exit left preview armed');
c=fixture();c.popupOpen=true;c.menuMode=true;c.externalFileDrag(false,0,0,-1,1);assert(c.popupOpen,'idle relay dismissed unrelated menu');
console.log('Installed QML drag relay: 10 transport/geometry/identity assertions passed');
