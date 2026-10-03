module caption_cache {
 type Key={scale:int,width:int,config:int,text:int}
 type Cache={key:Key,texture:int}
 type State={wanted:Key,normal:Cache,other:Cache,scope:bool,saved:Cache,active:Cache,serial:int,used:bool,beforeNormal:Cache,beforeOther:Cache}
 type Event=Scale(int) | Resize(int) | Config | Title | Move | Draw | ExportBegin | ExportDraw | ExportEnd
 val emptyKey={scale:0,width:0,config:0,text:0}
 var s:State
 action init=s'={wanted:{scale:1,width:200,config:1,text:1},normal:{key:emptyKey,texture:0},other:{key:emptyKey,texture:0},scope:false,saved:{key:emptyKey,texture:0},active:{key:emptyKey,texture:0},serial:0,used:false,beforeNormal:{key:emptyKey,texture:0},beforeOther:{key:emptyKey,texture:0}}
 action fire(e:Event):bool={
  val b={...s,used:false,beforeNormal:s.normal,beforeOther:s.other}
  s'=match e {
   | Scale(n)=>{...b,wanted:{...s.wanted,scale:n}}
   | Resize(n)=>{...b,wanted:{...s.wanted,width:n}}
   | Config=>{...b,wanted:{...s.wanted,config:s.wanted.config+1}}
   | Title=>{...b,wanted:{...s.wanted,text:s.wanted.text+1}}
   | Move=>b
   | Draw=>if(s.scope)b else if(s.normal.key==s.wanted){...b,used:true} else {...b,used:true,normal:{key:s.wanted,texture:s.serial+1},serial:s.serial+1}
   | ExportBegin=>if(s.scope)b else {...b,scope:true,saved:s.normal,active:s.normal}
   | ExportDraw=>if(not(s.scope))b else if(s.active.key==s.wanted)b else {...b,active:{key:s.wanted,texture:s.serial+1},serial:s.serial+1}
   | ExportEnd=>if(not(s.scope))b else {...b,scope:false,normal:s.saved,active:{key:emptyKey,texture:0}}
  }
 }
 val currentRasterOnNormalUse=s.used implies s.normal.key==s.wanted
 val exportCannotMutateNormal=s.scope implies s.normal==s.saved
 val otherDecorationUnchanged=s.other==s.beforeOther
 val allProps=currentRasterOnNormalUse and exportCannotMutateNormal and otherDecorationUnchanged
 action step={nondet e=Set(Scale(1),Scale(2),Resize(200),Resize(410),Config,Title,Move,Draw,ExportBegin,ExportDraw,ExportEnd).oneOf();fire(e)}
}
