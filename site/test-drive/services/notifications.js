import {packet, read, registerRead, mutate} from './common.js';
export const notifications = {service:'9',revision:'1',available:true,reason:'',entries:[{id:'1',incarnation:'1',producer:':1.7',app:'Calendar',summary:'Meeting soon',body:'Bring your notes',state:'live',actions:[{key:'open',label:'Open meeting'}]},{id:'2',incarnation:'2',producer:':1.8',app:'Mail',summary:'Build complete',body:'The build is ready to review.',state:'expired',actions:[]},{id:'3',incarnation:'3',producer:':1.9',app:'System',summary:'Battery low',body:'Connect power to continue.',state:'live',urgency:2,actions:[{key:'details',label:'Show details'}]},{id:'4',incarnation:'4',producer:':1.10',app:'Calendar',summary:'Earlier reminder',body:'The action is no longer available.',state:'unavailable',actions:[]}]};
export function registerNotifications(host) {
  registerRead(host,'notification-request','notification-snapshot','notifications',notifications);
  host.registerService('notification-effect',(request,ctx)=>{
    const i=request.intent, current=read(ctx,'notifications',notifications);
    const entry=current.entries.find(e=>e.id===i?.id && e.incarnation===i.incarnation && e.producer===i.producer && e.state==='live');
    const allowed=i?.service===current.service && entry && ((i.verb==='invoke' && entry.actions.some(a=>a.key===i.action)) || (i.verb==='dismiss' && i.action===''));
    const saved=allowed && mutate(ctx,'notifications',notifications,current.revision,s=>{const e=s.entries.find(item=>item.id===i.id && item.incarnation===i.incarnation); e.state=i.verb==='invoke'?'invoked':'dismissed'; e.actions=[]; return s;});
    if(!ctx.signal.aborted) ctx.reply(packet(request,'notification-outcome',{status:saved?'Dispatched':'Refused',snapshot:saved || read(ctx,'notifications',notifications)}));
  });
}
