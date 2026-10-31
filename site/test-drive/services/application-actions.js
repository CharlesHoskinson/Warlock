import {packet, read, mutate} from './common.js';
import {catalog} from './catalog.js';

// Actions belong to a catalog identity; they are never borrowed from another app.
export const actionFixtures = {
  'warlock-editor': {name:'Warlock Editor', actions:[{id:'desktop:Alpha',label:'New document',kind:'desktop'},{id:'recent:owned',label:'Open recent document',kind:'recent'}]},
  'warlock-browser': {name:'Browser', actions:[{id:'desktop:NewWindow',label:'New window',kind:'desktop'}]},
  'warlock-terminal': {name:'Terminal', actions:[{id:'desktop:NewWindow',label:'New terminal',kind:'desktop'}]}
};
const unavailable = entry => ({service:'9',revision:'1',entry,name:'',available:false,reason:'Application actions are unavailable.',actions:[]});
function snapshotFor(ctx, entry) {
  const currentCatalog=read(ctx,'catalog',catalog);
  const declared=currentCatalog.entries.find(item=>item.id===entry);
  const fixture=actionFixtures[entry];
  if (!declared || !fixture || declared.name!==fixture.name) return unavailable(entry);
  const stored=ctx.readWorld().services?.applicationActions?.[entry];
  return structuredClone(stored ?? {service:'9',revision:'1',entry,name:declared.name,available:true,reason:'',actions:fixture.actions});
}
export function registerApplicationActions(host) {
  host.registerService('jump-list-request',(request,ctx)=> {
    if (!ctx.signal.aborted) ctx.reply(packet(request,'jump-list-snapshot',{snapshot:snapshotFor(ctx,request.entry)}));
  });
  host.registerService('jump-list-effect',(request,ctx)=> {
    const i=request.intent, snapshot=snapshotFor(ctx,i.entry);
    const valid=snapshot.available && i.service===snapshot.service && i.revision===snapshot.revision && snapshot.actions.some(action=>action.id===i.action);
    let saved=null;
    if (valid && !ctx.signal.aborted && !['unknown','refusal','stale','connection-loss'].includes(ctx.fault)) {
      const all=ctx.readWorld().services?.applicationActions ?? {};
      // Check the identity and revision again inside the serialized transaction.
      ctx.transact(world=>{
        const active=world.services?.catalog ?? catalog;
        const declared=active.entries.find(item=>item.id===i.entry);
        const current=world.services?.applicationActions?.[i.entry] ?? snapshot;
        if (!declared || declared.name!==snapshot.name || current.service!==i.service || current.revision!==i.revision || !current.actions.some(action=>action.id===i.action)) return world;
        saved={...current,revision:(BigInt(current.revision)+1n).toString()};
        world.services={...world.services,applicationActions:{...all,...world.services?.applicationActions,[i.entry]:saved}};
        return world;
      });
    }
    if (ctx.signal.aborted) return;
    ctx.reply(packet(request,'jump-list-outcome',{status:saved?'Submitted':'Refused',snapshot:saved || snapshot}));
    // A separate simulated world observation follows a successful submission.
    if (saved && !ctx.signal.aborted) host.dispatchInput?.({kind:'application',action:'launch',intent:{entry:i.entry}});
  });
}
