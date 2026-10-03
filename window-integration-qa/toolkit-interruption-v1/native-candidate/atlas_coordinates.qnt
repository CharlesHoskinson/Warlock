module atlas_coordinates {
 type State={nativeX:int,offset:int,atlasX:int,quadX:int,damageX:int,roundX:int,normalized:bool,published:bool}
 type Event=Normalize | ProjectOnly | ClipOnly | Publish
 var s:State
 action init=s'={nativeX:200,offset:196,atlasX:4,quadX:200,damageX:200,roundX:200,normalized:false,published:false}
 action fire(e:Event):bool={s'=match e {
  | Normalize=>{...s,quadX:s.atlasX,damageX:s.atlasX,roundX:s.atlasX,normalized:true}
  | ProjectOnly=>{...s,quadX:s.atlasX,normalized:false}
  | ClipOnly=>{...s,damageX:s.atlasX,normalized:false}
  | Publish=>if(s.quadX==s.atlasX and s.damageX==s.atlasX and s.roundX==s.atlasX and s.normalized){...s,published:true} else s
 }}
 val completePixelsRequireSingleDomain=s.published implies (s.quadX==s.atlasX and s.damageX==s.atlasX and s.roundX==s.atlasX)
 val nativeUnchanged=s.nativeX==200 and s.offset==196
 val allProps=completePixelsRequireSingleDomain and nativeUnchanged
 action step={nondet e=Set(Normalize,ProjectOnly,ClipOnly,Publish).oneOf();fire(e)}
}
