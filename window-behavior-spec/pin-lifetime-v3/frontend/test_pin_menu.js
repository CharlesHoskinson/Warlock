var checks=0;
function check(v){checks++;if(!v)throw Error("Pin menu assertion "+checks);}
var w={address:"0x1234",stableId:"abcd",pid:123}, other={address:"0x4567",stableId:"7b",pid:234};
var t={address:w.address,stableId:"abcd",pid:w.pid,session:"private",compositorPid:432,compositorStart:"123",incarnation:"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",epoch:"1",generation:"1"};
function reply(token){return {result:"captured",nativeWrites:0,nativeCompletionClaimed:false,automaticRetries:0,publicIdentity:w,captured:token};}
var s=create();open(s,w);check(captured(s,1,w,0,reply(t)));check(s.status==="ready");var action=invoke(s);check(s.sent && action.token===s.token);check(invoke(s)===null);check(action.token.address===w.address);
var receipt={result:"complete",nativeCompletionClaimed:true,automaticRetries:0,captured:t,rawNativeResult:{ok:true,captured:t}};check(completed(s,action,0,receipt));check(s.status==="complete");
s=create();open(s,w);captured(s,1,w,0,reply(t));action=invoke(s);open(s,other);check(!completed(s,action,0,receipt));check(s.status==="capturing");
s=create();open(s,w);dismiss(s);check(!captured(s,1,w,0,reply(t)));check(invoke(s)===null);
s=create();open(s,w);open(s,other);check(!captured(s,1,w,0,reply(t)));check(s.token===null);
s=create();open(s,w);check(!captured(s,1,other,0,reply(t)));check(s.token===null);
s=create();open(s,w);var bad=Object.assign({},t,{pid:true});check(!captured(s,1,w,0,reply(bad)));check(s.status==="capture-refused");
s=create();open(s,w);bad=Object.assign({},t,{generation:"18446744073709551616"});check(!captured(s,1,w,0,reply(bad)));
s=create();open(s,w);bad=Object.assign({},t,{stableId:"10000000000000000"});check(!captured(s,1,w,0,reply(bad)));
s=create();open(s,w);check(!captured(s,1,w,1,reply(t)));check(invoke(s)===null);
s=create();open(s,w);captured(s,1,w,0,reply(t));action=invoke(s);check(!completed(s,action,3,{result:"uncertain",nativeCompletionClaimed:false}));check(invoke(s)===null);
s=create();open(s,w);captured(s,1,w,0,reply(t));action=invoke(s);var foreign=Object.assign({},t,{generation:"2"});check(!completed(s,action,0,Object.assign({},receipt,{captured:foreign})));
s=create();var failed=false;try{open(s,Object.assign({},w,{stableId:9007199254740992}));}catch(e){failed=true;}check(failed);
s=create();s.nonce=Number.MAX_SAFE_INTEGER;failed=false;try{open(s,w);}catch(e){failed=true;}check(failed);
s=create();open(s,w);var mutable=Object.assign({},t);captured(s,1,w,0,reply(mutable));mutable.generation="9";check(s.token.generation==="1");
checks+" actual Qt QJSEngine pin menu assertions PASS";
