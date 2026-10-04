const fs=require('fs');
const {Elm}=require(process.argv[2]);
const samples=JSON.parse(fs.readFileSync(process.argv[3]));
const worker=Elm.GeometryBoundsReplay.init({flags:null});
const timer=setTimeout(()=>{throw Error('Compiled decoder response missing');},10000);
worker.ports.outgoing.subscribe(actual=>{
 clearTimeout(timer);
 if(actual.length!==samples.length)throw Error('Sample count');
 for(let i=0;i<samples.length;i++)if(actual[i]!==samples[i].expected)throw Error(samples[i].name+' expected '+samples[i].expected+' observed '+actual[i]);
 fs.writeFileSync(process.argv[4],JSON.stringify({passed:true,checks:samples.length,actual}));
});
worker.ports.incoming.send(samples);
