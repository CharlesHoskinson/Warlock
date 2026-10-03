// Actual extracted QML JavaScript function, controlled provider/allocation data.
// No Qt/QQuickWindow/installed-QS/native semantics are claimed.
const fs=require('fs');
const source=fs.readFileSync(process.argv[2],'utf8');
const from=source.indexOf('    function diagnosticState() {');
const to=source.indexOf('    function sync()',from);
if(from<0||to<0)throw Error('Exact diagnostic source boundaries required');
const method=source.slice(from,to);
const rows=[];
for(const scenario of ['open','closed','getter-mutation']){
 let windowGeneration=6,calls=[],generationRead=0;
 const root={},pinPopup={},toggleButton={};
 const nativeWindow={contentItem:{}};
 toggleButton.QsWindow={window:nativeWindow};toggleButton.mapToItem=(item,x,y)=>{
  if(item!==nativeWindow.contentItem||x!==0||y!==0)throw Error('Actual arguments changed');return{x:0,y:0};
 };
 Object.defineProperty(toggleButton,'width',{get(){generationRead++;if(scenario==='getter-mutation')windowGeneration=60;return 220;}});
 toggleButton.height=30;toggleButton.visible=true;
 const toggleMouse={enabled:true},invocation=null,lastReceipt=null;
 const menuState={nonce:1,open:scenario!=='closed',status:'ready',target:{address:'0x123',stableId:'18000000',pid:7},token:{},sent:false};
 const names=['menu','row','popup','attached','content','window','nativeRoot'];
 const meta=()=>({schema:'qml-engine-metadata-v1',kind:'metadata-only; no widget/input authority',engineGeneration:1,engineEpoch:1,providerGeneration:1,processId:11,processStart:'777',configSHA256:'f'.repeat(64)});
 const NativeLifetime={Lifetime:{engineScope(){calls.push('engine');return meta();},observePopup(menu,row,popup,core){
  if(menu!==root||row!==toggleButton||popup!==pinPopup||core!==Quickshell)throw Error('Lexical tuple was substituted');
  calls.push('popup');let v=meta();delete v.kind;v.schema='qml-popup-lifetime-v1';v.relationship='lexical-pin-popup-existing-attached-native-content';v.nativeWindowBound=true;v.diagnostics={};v.allocations={};v.contexts={};
  names.forEach((n,i)=>{v.allocations[n]=n==='window'?windowGeneration:i+1;v.contexts[n]={generation:i<3?i+11:0,present:i<3,enginePresent:i<3};});return v;
 }}};const Quickshell={};
 const obtain=new Function('NativeLifetime','root','toggleButton','pinPopup','Quickshell','menuState','toggleMouse','invocation','lastReceipt',method+'\nreturn diagnosticState();');
 const value=obtain(NativeLifetime,root,toggleButton,pinPopup,Quickshell,menuState,toggleMouse,invocation,lastReceipt);
 if(generationRead!==1||calls.join(',')!==(scenario==='closed'?'engine,engine':'engine,popup,popup,engine'))throw Error('Getter/provider ordering changed');
 if(scenario==='getter-mutation'&&value.popupBefore.allocations.window===value.popupAfter.allocations.window)throw Error('Mutation hidden');
 if(scenario==='closed'&&(value.popupBefore!==null||value.popupAfter!==null))throw Error('Closed menu claimed native popup');
 rows.push({scenario,value,exactLexicalArguments:true,sourceBoundFunction:true,controlledDataNotNativeAuthority:true});
}
process.stdout.write(JSON.stringify(rows));
