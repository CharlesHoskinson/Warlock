"""Extend original 207 C/JSC controls with an independent pure visual decoder."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v117')
s=(root/'qa/persistent-policy-native-roundtrip.js').read_text()
old="require(process.argv[5]);let lastPolicyEnvelope;";assert s.count(old)==1
s=s.replace(old,old+"\nconst {Elm:DecoderElm}=require(process.argv[6]);const codec=DecoderElm.NativePreviewVisualReplay.init();let awaitingCodec;let visualChecks=0;\ncodec.ports.outgoing.subscribe(v=>{assert(awaitingCodec);const resolve=awaitingCodec;awaitingCodec=null;resolve(v);});\nfunction decodeProjection(value){return new Promise((resolve,reject)=>{assert(!awaitingCodec);const timer=setTimeout(()=>reject(Error('Original three-second visual decoder timeout')),3000);awaitingCodec=v=>{clearTimeout(timer);resolve(v);};codec.ports.incoming.send({kind:'projection',domain:{binding:value.binding,receiverEpoch:value.receiverEpoch},value});});}\n")
old="if(result.commands.kind==='preview-proposals')lastPolicyEnvelope=result.commands;return result;}";assert s.count(old)==1
new="""if(result.commands.kind==='preview-proposals')lastPolicyEnvelope=result.commands;
 if(result.visuals!==null){const decoded=await decodeProjection(result.visuals);assert(decoded.accepted,'Actual optimized worker emits typed original visual projection');assert.deepEqual(decoded.value,result.visuals,'Pure decoder preserves exact projection');visualChecks+=2;
  for(const row of result.visuals.previews){const policy=result.models.find(item=>item.identity===row.identity);if(row.visual.kind==='lifecycle'){assert(policy?.active && policy.model);assert.equal(row.visual.state,policy.model.state);visualChecks+=2;
    if(row.visual.frame!==null){assert.equal('elm-shell://preview/'+row.visual.frame,policy.model.image);visualChecks++;}}
  }
 }
 return result;}""";s=s.replace(old,new)
s=s.replace('realmEpochs:2,nativeGrantResets:0,','visualProjectionChecks:visualChecks,pureRendererDecoderInstances:1,rendererWindowPolicyInstances:0,realmEpochs:2,nativeGrantResets:0,')
p=root/'qa/persistent-policy-visual-roundtrip.js';assert not p.exists();p.write_text(s)
s=(root/'qa/persistent-policy-native-check-v3.py').read_text().replace('persistent-policy-native-check-v3-','persistent-policy-visual-native-check-').replace('qa/persistent-policy-native-roundtrip.js','qa/persistent-policy-visual-roundtrip.js').replace('qa/persistent-policy-native-check-v3.py','qa/persistent-policy-visual-native-check.py')
old=" flags=shlex.split(run('flags'";assert s.count(old)==1
s=s.replace(old," decoder=out/'visual-decoder.js';run('optimized-visual-decoder',[str(root/held['compiler']),'make','src/NativePreviewVisualReplay.elm','--optimize','--output='+str(decoder)],dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')))\n"+old)
old="str(out/'inputs/assets/native-preview-proposals.js')]))";assert s.count(old)==1;s=s.replace(old,"str(out/'inputs/assets/native-preview-proposals.js'),str(decoder)]))")
s=s.replace("assert e['passed'] and e['nativeOwnedJavaScriptCore']", "assert e['passed'] and e['checks']==207 and e['visualProjectionChecks']>0 and e['rendererWindowPolicyInstances']==0 and e['pureRendererDecoderInstances']==1 and e['nativeOwnedJavaScriptCore']")
s=s.replace("'scope':'Actual one native-owned", "'scope':'Original207 controls remain unchanged with additive actual optimized worker visual projection roundtripped through a separately compiled pure DTO decoder, never another window policy. No real renderer/DOM/WebKit projection delivery or ordering proof. Actual one native-owned")
ast.parse(s);p=root/'qa/persistent-policy-visual-native-check.py';assert not p.exists();p.write_text(s);print(p)
