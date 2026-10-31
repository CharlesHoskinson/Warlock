import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {createHost} from './index.js';
const source=fs.readFileSync(new URL('../runtime/vendor/elm.js',import.meta.url),'utf8').replace("_Platform_export({'Main'", "scope.__test={decode:$author$project$GeometryProjection$decoder,run:_Json_run,caps:$author$project$GeometryProjection$capabilitiesDecoder};_Platform_export({'Main'");
const sandbox={console,setTimeout,clearTimeout}; vm.createContext(sandbox); vm.runInContext(source,sandbox);
const messages=[], listeners={}; globalThis.location={origin:'https://test.invalid'}; globalThis.addEventListener=(name,fn)=>listeners[name]=fn;globalThis.removeEventListener=()=>{};
const frames=Object.fromEntries(['controller','bar','popup'].map(id=>[id,{postMessage:p=>messages.push(p)}]));
const host=createHost({frames});host.start();
function emit(packet){listeners.message({origin:location.origin,source:frames.controller,data:{bridgeVersion:1,epoch:0,frameId:'controller',kind:'native',payload:JSON.stringify(packet)}});}
emit({protocolVersion:3,kind:'host-ready'}); const binding=host.getSnapshot().binding;
emit({viewProtocol:1,kind:'view-commit',projection:{revision:'1',frame:{publication:'1',lease:'1',mode:'closed',bar:[],popup:[]}},focus:[],requests:[{kind:'geometry-attach',binding,requestId:'1'},{kind:'geometry-facts-request',binding,requestId:'2',minimumWatermark:'8'}]});
const packets=messages.map(x=>x.payload?.value).filter(Boolean), attached=packets.find(x=>x.kind==='geometry-attached'), facts=packets.find(x=>x.kind==='geometry-facts');
assert.ok(facts);assert.equal(facts.sequence,'9');
const {run,caps,decode}=sandbox.__test;const cap=run(caps)(attached.capabilities);assert.equal(cap.$,0,JSON.stringify(cap));const result=run(decode(3)(cap.a))(facts);assert.equal(result.$,0,JSON.stringify(result));
host.destroy();console.log('Real compiled Elm geometry decoder accepts emitted facts and watermark.');
