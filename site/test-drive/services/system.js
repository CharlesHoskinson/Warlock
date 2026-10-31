import {packet, read, registerRead, mutate} from './common.js';
export const system = {service:'9',revision:'1',volume:{percent:50,muted:false,label:'Simulated audio'},network:{enabled:true,state:'connected',permission:'yes'},power:{suspend:'yes',reboot:'yes',poweroff:'no'},session:{name:'Simulated session',state:'active',locked:false}};
export function registerSystem(host) {
  registerRead(host,'system-menu-request','system-menu-snapshot','system',system);
  host.registerService('system-menu-effect',(request,ctx)=>{
    const i=request.intent, current=read(ctx,'system',system);
    // Submission of a power or logout request does not observe a state change.
    // Validate against the serialized world without advancing its revision.
    if (['suspend','reboot','poweroff','session-logout'].includes(i?.operation)) {
      let accepted=false, snapshot=current;
      const transacted=ctx.transact(world=>{
        snapshot=structuredClone(world.services?.system ?? system);
        accepted=i.service===snapshot.service && i.revision===snapshot.revision && i.value===0 &&
          (i.operation==='session-logout'
            ? !!snapshot.session && snapshot.session.state!=='closing'
            : !!snapshot.power && ['yes','challenge'].includes(snapshot.power[i.operation]));
        return world;
      });
      if(!ctx.signal.aborted) ctx.reply(packet(request,'system-menu-outcome',{status:transacted && accepted?'Submitted':'Refused',snapshot}));
      return;
    }
    const saved=i?.service===current.service && mutate(ctx,'system',system,i.revision,s=>{
      const v=i.value;
      switch(i.operation) {
        case 'volume-set': if(!s.volume || !Number.isInteger(v) || v<0 || v>100) return null; s.volume.percent=v; break;
        case 'volume-mute': if(!s.volume || ![0,1].includes(v)) return null; s.volume.muted=!!v; break;
        case 'network-enable': if(!s.network || !['yes','auth'].includes(s.network.permission) || ![0,1].includes(v)) return null; s.network.enabled=!!v; s.network.state=v?'connected':'disconnected'; break;
        case 'session-lock': if(!s.session || v!==0) return null; s.session.locked=true; break;
        default: return null;
      } return s;
    });
    if(!ctx.signal.aborted) ctx.reply(packet(request,'system-menu-outcome',{status:saved?'Committed':'Refused',snapshot:saved || read(ctx,'system',system)}));
  });
}
