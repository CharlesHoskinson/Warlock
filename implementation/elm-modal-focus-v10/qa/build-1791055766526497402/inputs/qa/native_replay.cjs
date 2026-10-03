'use strict';
const fs=require('fs'),assert=require('node:assert/strict');
const {Elm}=require(process.env.ELM_REPLAY),input=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const app=Elm.Replay.init({flags:null});const timer=setTimeout(()=>{throw Error('Native replay timeout');},5000);
app.ports.results.subscribe(report=>{
 clearTimeout(timer);assert.ok(!report.error,report.error);
 const steps=report.cases[0].steps;
 assert.equal(steps.length,input.operations.length);
 input.operations.forEach((operation,index)=>{
  if(operation.op!=='observe')return;
  const actual=steps[index],expected=operation.event;
  assert.equal(actual.phase,'Coherent');assert.equal(actual.projection.sequence,expected.sequence);
  assert.equal(actual.projection.revision,expected.revision);assert.deepEqual(actual.projection.windows,expected.windows);
 });
 const receipt={passed:true,scope:'Actual native projection snapshots accepted by compiled nullable-state Elm reducer',transitions:steps.length,steps};
 fs.writeFileSync(process.argv[3],JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({passed:true,transitions:steps.length}));process.exit(0);
});app.ports.transcripts.send([{name:'native-authority-projection',operations:input.operations}]);
