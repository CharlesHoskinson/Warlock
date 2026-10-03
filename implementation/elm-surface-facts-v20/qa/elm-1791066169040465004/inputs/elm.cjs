const fs=require('fs'),assert=require('assert');
const app=require(process.argv[2]).Elm.Replay.init({flags:null});
const deadline=setTimeout(()=>{throw new Error('Trace decoder deadline');},5000);
function replay(message){return new Promise(resolve=>{const cb=value=>{app.ports.outgoing.unsubscribe(cb);resolve(value);};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(message);});}
(async()=>{
 const report=JSON.parse(fs.readFileSync(process.argv[3])),captures=[...Object.values(report.captures),...report.identityTracePackets.map(renderTrace=>({renderTrace}))];let checks=0;
 for(const capture of captures){const result=await replay(capture.renderTrace);assert(result.passed);assert.equal(result.summary.canonicalScene,false);checks++;}
 const original=captures[0].renderTrace,clone=()=>JSON.parse(JSON.stringify(original));
 const invalid=[];
 let value=clone();value.frames.push(value.frames[0]);invalid.push(value);
 value=clone();value.frames[0].frame=9007199254740993;invalid.push(value);
 value=clone();value.frames[0].frame='18446744073709551616';invalid.push(value);
 value=clone();value.frames[0].complete=true;value.frames[0].overflow=true;invalid.push(value);
 value=clone();value.frames[0].draws=Array(1025).fill(value.frames[0].draws[0]);invalid.push(value);
 value=clone();value.frames[0].draws[0].authority=null;value.frames[0].draws[0].incarnation='1';invalid.push(value);
 value=clone();value.kind='scene';invalid.push(value);
 value=clone();value.order=['1'];invalid.push(value);
 for(const malformed of invalid){assert.equal((await replay(malformed)).passed,false);checks++;}
 value=clone();value.frames[0].frame='18446744073709551615';assert((await replay(value)).passed);checks++;
 value=clone();value.frames[0].draws[0].retired=true;value.frames[0].draws[0].incarnation='1';
 const retired=await replay(value);assert(retired.passed);assert.equal(retired.summary.frames[0].usableDispatchTrace,false);checks++;
 fs.writeFileSync(process.argv[4],JSON.stringify({passed:true,checks,nativeCaptures:captures.length,malformedCases:invalid.length},null,2)+'\n');clearTimeout(deadline);
})();
