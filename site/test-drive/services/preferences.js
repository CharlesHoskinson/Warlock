import {packet, read, registerRead, mutate} from './common.js';
export const settings = {schema:2,revision:'1',values:{theme:'night',textScale:100,effectsOff:false,reducedTransparency:false}};
export const motion = {schema:1,revision:'1',override:null};
export const shortcuts = {schema:1,revision:'1',choices:{applications:'keep',system:'keep',notifications:'keep'}};
const row=(defaultChord,alternateChord)=>({defaultChord,alternateChord,defaultAvailable:true,alternateAvailable:true,active:'keep'});
export const inventory={fingerprint:'a'.repeat(64),applications:row('SUPER + ALT + SPACE','SUPER + CTRL + ALT + SPACE'),system:row('SUPER + ESCAPE','SUPER + CTRL + ESCAPE'),notifications:row('SUPER + SHIFT + ALT + comma','SUPER + CTRL + ALT + comma')};
export function registerPreferences(host) {
  registerRead(host,'shell-settings-request','shell-settings','settings',settings);
  registerRead(host,'motion-preferences-request','motion-preferences','motionPreferences',motion);
  for (const [kind,response,name,fallback,valid] of [
    ['shell-settings-write','shell-settings-outcome','settings',settings,p=>p?.schema===2 && ['night','dawn','high-contrast'].includes(p.values?.theme) && [100,125,150,200].includes(p.values?.textScale) && typeof p.values.effectsOff==='boolean' && typeof p.values.reducedTransparency==='boolean'],
    ['motion-preferences-write','motion-preferences-outcome','motionPreferences',motion,p=>p?.schema===1 && [null,'full','reduced'].includes(p.override)]
  ]) host.registerService(kind,(request,ctx)=>{
    if(ctx.signal.aborted) return;
    const p=request.proposal;
    const saved=valid(p) && mutate(ctx,name,fallback,p.revision,()=>structuredClone(p));
    ctx.reply(packet(request,response,{status:saved?'Saved':'Refused',snapshot:saved || read(ctx,name,fallback)}));
    if(saved && name==='settings') ctx.transact(world=>{ world.appearance=structuredClone(saved.values); return world; });
  });
  host.registerService('motion-profile-set',(request,ctx)=>{
    if(ctx.signal.aborted || !['full','reduced'].includes(request.profile)) return;
    ctx.transact(world=>{world.motion={profile:request.profile,reduced:request.profile==='reduced'}; return world;});
    ctx.reply(packet(request,'motion-profile',{profile:request.profile}));
  });
  host.registerService('shortcut-preferences-request',(request,ctx)=>ctx.reply(packet(request,'shortcut-preferences',{snapshot:read(ctx,'shortcutPreferences',shortcuts),inventory:read(ctx,'shortcutInventory',inventory)})));
  host.registerService('shortcut-preferences-write',(request,ctx)=>{
    if(ctx.signal.aborted) return;
    const p=request.proposal?.preferences, inv=read(ctx,'shortcutInventory',inventory);
    const valid=p?.schema===1 && request.proposal.fingerprint===inv.fingerprint && ['applications','system','notifications'].every(k=>['keep','default','alternate'].includes(p.choices?.[k]) && (p.choices[k]==='keep' || inv[k][p.choices[k]+'Available']));
    const saved=valid && mutate(ctx,'shortcutPreferences',shortcuts,p.revision,()=>structuredClone(p));
    if(saved) ctx.transact(world=>{ const effective=structuredClone(world.services?.shortcutInventory ?? inventory); for(const key of ['applications','system','notifications']) effective[key].active=saved.choices[key]; world.services={...world.services,shortcutInventory:effective}; return world; });
    const observed=read(ctx,'shortcutInventory',inventory);
    const applied=saved && ['applications','system','notifications'].every(key=>observed[key].active===saved.choices[key]);
    if(!ctx.signal.aborted) ctx.reply(packet(request,'shortcut-preferences-outcome',{status:saved?(applied?'Saved':'Stored'):'Refused',snapshot:saved || read(ctx,'shortcutPreferences',shortcuts),inventory:observed}));
  });
}
