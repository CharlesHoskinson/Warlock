var tests=[];
function assert(value,name){if(!value)throw Error(name);tests.push(name);}
function event(type){return {type:type,target:{id:'draft',value:'old',selectionStart:3,selectionEnd:3},isTrusted:true,key:'-',code:'Escape',keyCode:189,which:189,charCode:0,timeStamp:12,altKey:false,ctrlKey:false,metaKey:false,shiftKey:false,repeat:false,isComposing:false,defaultPrevented:false};}
function send(e,phase){listeners[e.type+':'+phase].forEach(function(fn){fn(e);});}
var s=window.qaKeyboardDiagnostic;
var first=event('keydown');send(first,'capture');first.defaultPrevented=true;send(first,'bubble');
assert(s.entries.length===2,'capture and bubble both observed');
assert(s.entries[0].eventToken===s.entries[1].eventToken,'same actual object token');
assert(!s.entries[0].defaultPrevented&&s.entries[1].defaultPrevented,'capture versus bubble default snapshots');
assert(s.entries[0].key==='-'&&s.entries[0].code==='Escape','key and code distinct exact raw fields');
assert(s.entries[0].timestamp===12&&s.entries[0].timeOrigin===100&&s.entries[0].handled===200,'original time and page separately saved');
assert(Object.isFrozen(s.entries[0])&&Object.isFrozen(s.entries[0].modifiers)&&Object.isFrozen(s.entries[0].selection),'primitive row snapshots immutable');
assert(first.defaultPrevented===true&&first.target.value==='old','observer does not repair event or value');
var orphan=event('keyup');send(orphan,'bubble');assert(s.entries[2].eventToken===null&&!s.entries[2].captureExists,'orphan bubble never invents capture');
var next=event('keydown');send(next,'capture');send(next,'bubble');assert(s.entries[3].eventToken!==s.entries[0].eventToken,'different event objects never joined by metadata');
var synthetic=event('keyup');synthetic.isTrusted=false;send(synthetic,'capture');send(synthetic,'bubble');assert(s.entries[5].trusted===false,'synthetic stays synthetic');
var before=event('beforeinput');before.data='-';before.inputType='insertText';send(before,'capture');send(before,'bubble');assert(s.entries[7].data==='-'&&s.entries[7].inputType==='insertText','beforeinput raw data and type');
var input=event('input');input.data='-';input.inputType='insertText';input.target.value='old-';input.target.selectionStart=4;input.target.selectionEnd=4;send(input,'capture');send(input,'bubble');assert(s.entries[9].value==='old-'&&s.entries[9].selection[0]===4,'actual input state snapshot');
var unsupported=event('compositionstart');delete unsupported.key;delete unsupported.repeat;send(unsupported,'capture');send(unsupported,'bubble');assert(s.entries[11].key===null&&s.entries[11].repeat===null,'missing metadata stays null');
var altered=event('keydown');send(altered,'capture');altered.key='c';send(altered,'bubble');assert(s.entries[14].key==='c'&&!s.entries[14].captureIdentityMatches,'changed metadata preserved with failed pairing qualification');
var page=event('keydown');send(page,'capture');performance.timeOrigin=101;send(page,'bubble');assert(!s.entries[16].captureIdentityMatches,'page change refuses old pairing');
var noTarget=event('keyup');noTarget.target=null;send(noTarget,'capture');send(noTarget,'bubble');assert(s.entries[17].target===null&&s.entries[17].value===null,'missing target remains missing');
var repeat=event('keydown');repeat.repeat=true;repeat.isComposing=true;send(repeat,'capture');send(repeat,'bubble');assert(s.entries[19].repeat&&s.entries[19].isComposing,'repeat and composition observed');
var invalid=event('keydown');invalid.keyCode=true;invalid.altKey=0;send(invalid,'capture');assert(s.entries[s.entries.length-1].keyCode===null&&s.entries[s.entries.length-1].modifiers[0]===null,'boolean/numeric metadata never coerced');
for(var i=0;i<300;i++){var e=event('keydown');send(e,'capture');send(e,'bubble');}
assert(s.entries.length===512&&s.dropped>0&&s.entries[0].sequence>1,'bounded history with explicit truncation');
assert(s.entries.every(function(row,index){return index===0||row.sequence===s.entries[index-1].sequence+1;}),'monotonic sample sequence after truncation');
var count=s.entries.length;s.sequence=Number.MAX_SAFE_INTEGER;send(event('keydown'),'capture');assert(s.exhausted&&s.entries.length===count,'safe integer exhaustion stops only diagnostics');
var testResult={result:'pass',cpuCases:tests.length,nativeGuiExecuted:false,realDomEventProof:false};
