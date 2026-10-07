'use strict';
const assert=require('node:assert/strict');require(process.argv[2]);let checks=0;
const binding={lifetime:'18446744073709551615',session:'9007199254740993',frontend:'9007199254740994'};
const value={previewProtocol:3,kind:'preview-proposals',binding,receiverEpoch:'18446744073709551615',entries:[{identity:'binding:'+Object.values(binding).join(':'),commands:[{kind:'reconcile',binding}]}]};
function same(a,b,m){assert.deepEqual(a,b,m);checks++;}function refused(v,m){assert.throws(()=>WarlockNativePreviewProposals(v),TypeError,m);checks++;}
const wires=WarlockNativePreviewProposals(value);same(wires.length,1);same(JSON.parse(wires[0]),value,'Original policy envelope preserved');same(Object.isFrozen(wires),true);same(JSON.parse(wires[0]).controlOrdinal,undefined,'Renderer never issues an ordinal');
const two={...value,entries:[value.entries[0],{identity:'family:21',commands:[{kind:'cancel',job:{request:'1'}}]}]};
same(WarlockNativePreviewProposals(two).map(w=>JSON.parse(w).entries[0]),two.entries,'Original policy order and command bodies preserved');
same(WarlockNativePreviewProposals({...value,entries:[]}),[]);
for(const v of [null,[],{}, {...value,extra:true},{...value,controlOrdinal:'1'},{...value,kind:'preview-commands'},{...value,previewProtocol:true},{...value,binding:{...binding,extra:true}}])refused(v,'Exact closed header fields');
for(const receiverEpoch of ['0','01',1,true,'18446744073709551616','-1','1.0','',null])refused({...value,receiverEpoch},'Lossless positive native epoch');
for(const lifetime of ['0','01',1,'18446744073709551616'])refused({...value,binding:{...binding,lifetime}},'Lossless native binding');
for(const entries of [null,{},[null],[{}],[{identity:'family:21',commands:[]}],[{identity:'family:21',commands:[{},{}]}],[{identity:'family:21',commands:[null]}],[{identity:'family:21',commands:[[]]}],[{identity:'family:21',commands:[{}],extra:true}],[{identity:'',commands:[{}]}],[{identity:'é'.repeat(257),commands:[{}]}]])refused({...value,entries},'Bounded singleton original native command rows');
const full={...value,entries:Array.from({length:1065},()=>value.entries[0])};same(WarlockNativePreviewProposals(full).length,1065,'Original native queue bound');refused({...value,entries:[...full.entries,value.entries[0]]},'Native quota bound refuses excess');
refused({...value,entries:[value.entries[0],{identity:'family:21',commands:[{kind:'oversized',text:'é'.repeat(2048)}]}]},'Validate whole packetization before returning any original wire');
same(value.receiverEpoch,'18446744073709551615');same(value.entries.length,1,'Pure packetization does not mutate Elm output');
console.log(JSON.stringify({passed:true,checks,nativeIssuerOnly:true,purePacketization:true,nativeAcceptance:false,fullReleaseAccepted:false}));
