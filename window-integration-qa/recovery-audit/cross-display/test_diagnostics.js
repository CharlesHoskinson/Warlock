// Exercises the actual staged diagnostic functions with two independent widgets.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const staged=process.argv[2];
const text=fs.readFileSync(staged,'utf8');
const helpers=text.slice(text.indexOf('  function diagnosticState()'),text.indexOf('  IpcHandler {'));
const contexts=[];
function widget(id,name,x,bottom) {
  const context={root:{monitors:[{id,name,x,y:0,width:1920,height:1080,scale:1.5}],currentMonitor:id,
    barScreen:{name,width:1280,height:720},barWindow:{width:1280,height:26,contentItem:{}},
    bar:{position:bottom?'bottom':'top'},fileDragActive:true,fileDragOnTaskbar:true,
    fileDragStamp:100,filePreviewKey:'',dragEntries:2,dragGroupKey:'g',dragActivated:false,
    groups:[{displayKey:'display',key:'app',windows:[{address:'own-'+id,pid:7,stableId:'stable'}]}],
    widthFor:()=>38,menuMode:false,popupGroup:null,wheelEvents:0,selectedWindowIndex:0,
    menuItems:[],currentDesktop:'1',popupOpen:false,popupIndex:0,keyboardMode:false,taskbarSettings:{}},
    taskDrop:{width:38,height:26},taskRepeater:{itemAt:()=>({height:26,mapToItem:()=>({x:500,y:0})})},
    windowRepeater:{itemAt:()=>null},popupFlickable:{contentY:0,height:0,contentHeight:0},popupKeyCatcher:{activeFocus:false}};
  vm.createContext(context);vm.runInContext(helpers,context);
  context.root.diagnosticState=context.diagnosticState;context.root.diagnosticStates=context.diagnosticStates;
  contexts.push(context);return context.root;
}
const first=widget(0,'physical',0,false),second=widget(1,'headless',1600,true);
for(const context of contexts)context.root.bar.moduleWidgets=()=>[first,second];
const all=JSON.parse(JSON.stringify(first.diagnosticStates()));
assert.equal(all.length,2);assert.deepEqual(all.map(s=>s.currentMonitor),[0,1]);
assert.equal(all[1].screenName,'headless');assert.equal(all[1].monitorGeometry.x,1600);
assert.equal(all[1].monitorGeometry.width,1280);assert.equal(all[1].barOffset.y,694);
assert.deepEqual(all[1].taskbarItems[0].windows,['own-1']);assert.equal(all[1].taskbarItems[0].height,26);
assert.equal(first.fileDragActive,true);assert.equal(second.fileDragActive,true);
assert.equal(first.popupOpen,false);assert.equal(second.popupOpen,false);
// Existing state fields keep their values; additive queries use no focus/action API.
assert.equal(all[0].dragEntries,2);assert.equal(all[0].displayMode,'all');assert.equal(all[0].combineMode,'always');
assert(!helpers.includes('runArgs('));assert(!helpers.includes('openGroup('));assert(!helpers.includes('activate'));
console.log('PASS actual diagnostic helper: two outputs, fractional geometry, bottom bar offset, preserved state and no actions');
