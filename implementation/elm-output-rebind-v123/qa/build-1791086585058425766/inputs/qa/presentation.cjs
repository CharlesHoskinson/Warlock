const fs=require('fs'),assert=require('assert'),{Elm}=require(process.argv[2]);const app=Elm.PresentationReplay.init({flags:null});
const deadline=setTimeout(()=>{throw Error('Presentation replay deadline');},5000);
const c={id:'entry:app',domId:'entry-scope',label:'Open App',ariaLabel:'Open App',detail:'',enabled:true};
const frame={surfaceProtocol:2,publication:'9007199254740993',lease:'4',mode:'applications',status:'Idle',bar:[],popup:[c]};
const present=frame=>({kind:'present',frame}),action=(change={})=>({kind:'action',action:{surfaceProtocol:2,surface:'popup',kind:'surface-action',publication:frame.publication,lease:'4',id:c.id,...change}});
function replay(events){return new Promise(resolve=>{const cb=value=>{app.ports.outgoing.unsubscribe(cb);resolve(value);};app.ports.outgoing.subscribe(cb);app.ports.incoming.send(events);});}
(async()=>{let cases=[];async function check(name,events,verify){const rows=await replay(events);verify(rows.at(-1));cases.push({name,rows});}
await check('lossless admitted callback',[present(frame),action()],last=>assert.equal(last.action.publication,frame.publication));
await check('malformed frame retires controls',[present(frame),present({}),action()],last=>assert.equal(last.action,null));
await check('malformed frame cannot reset publication watermark',[present(frame),present({}),present({...frame,publication:'1'}),action({publication:'1'})],last=>assert.equal(last.publication,null));
await check('new frame recovers after malformed',[present(frame),present({}),present({...frame,publication:'9007199254740994'})],last=>assert.equal(last.publication,'9007199254740994'));
await check('older lease rejected despite newer publication',[present(frame),present({...frame,publication:'9007199254740994',lease:'3'})],last=>assert.equal(last.publication,frame.publication));
await check('retired callback suppressed after new presentation',[present(frame),present({...frame,publication:'9007199254740994'}),action()],last=>assert.equal(last.action,null));
for(const [name,mutation] of [['wrong surface',{surface:'bar'}],['extra Exec',{exec:'/bin/sh'}],['arbitrary id',{id:'/bin/sh'}],['numeric counter',{publication:1}],['zero lease',{lease:'0'}]])await check('callback rejected '+name,[present(frame),action(mutation)],last=>assert.equal(last.action,null));
await check('disabled item cannot emit callback',[present({...frame,popup:[{...c,enabled:false}]}),action()],last=>assert.equal(last.action,null));
fs.writeFileSync(process.argv[3],JSON.stringify({passed:true,checks:cases.length,cases},null,2)+'\n');clearTimeout(deadline);})();
