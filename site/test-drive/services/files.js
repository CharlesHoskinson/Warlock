import {packet, read, registerRead, mutate} from './common.js';
export const files = {service:'9',revision:'1',available:true,reason:'',peer:{pid:'20',start:'40',instance:'owned1',target:'home',visible:true}};
export function registerFiles(host) {
  registerRead(host,'files-request','files-snapshot','files',files);
  host.registerService('files-open',(request,ctx)=>{
    const i=request.intent, current=read(ctx,'files',files);
    const target=typeof i?.target==='string' ? i.target.trim() : '';
    const valid=current.available && i.service===current.service && target.length<=512 && /^(home|coll:(recent|images|videos|documents|downloads|large|screenshots)|\/[^\x00-\x1f\x7f]*|~(?:\/[^\x00-\x1f\x7f]*)?)$/.test(target);
    const normalized=target.startsWith('~') ? '/home/demo'+target.slice(1) : target.startsWith('/') ? '/'+target.split('/').reduce((parts,part)=>{if(part==='..') parts.pop(); else if(part && part!=='.') parts.push(part); return parts;},[]).join('/') : target;
    // The observed target has its own decoder boundary after home expansion.
    const observedValid=normalized.length<=512 && !/[\x00-\x1f\x7f]/.test(normalized);
    const saved=valid && observedValid && mutate(ctx,'files',files,i.revision,s=>({...s,peer:{...(s.peer || files.peer),target:normalized,visible:true}}));
    if(!ctx.signal.aborted) { ctx.reply(packet(request,'files-outcome',{status:saved?'Opened':'Refused',snapshot:saved || read(ctx,'files',files)})); if(saved) host.dispatchInput?.({kind:'files',action:'open',target:normalized,peer:structuredClone(saved.peer)}); }
  });
}
