module viewport_geometry {
  type Key = {lifetime:int, session:int, surface:int, layout:int, basis:int, clock:int}
  type Sample = {key:Key, sequence:int, trusted:bool, buttons:int,
    mouse:bool, primary:bool, exactHit:bool, unchanged:bool, finite:bool,
    timestamp:int, prepared:int, modifiers:int, clear:bool,
    pointX:int, pointY:int, clientX:int, clientY:int, inside:bool}
  type Event = Move(Sample) | Change(Key) | Invalidate | Press
  pure val original = {lifetime:1,session:1,surface:1,layout:1,basis:1,clock:1}
  pure val empty = {key:original,sequence:0,trusted:false,buttons:0,
    mouse:true,primary:true,exactHit:false,unchanged:false,finite:true,
    timestamp:0,prepared:0,modifiers:0,clear:true,
    pointX:0,pointY:0,clientX:0,clientY:0,inside:false}
  pure def valid(s:Sample,k:Key):bool = s.key==k and s.sequence>0
    and s.trusted and s.buttons==0 and s.mouse and s.primary and s.exactHit
    and s.unchanged and s.finite and s.inside and s.modifiers==0 and s.clear
    and s.timestamp>=s.prepared and s.prepared>0
  pure def agrees(a:Sample,b:Sample):bool = a.key==b.key
    and b.sequence>a.sequence and a.pointX!=b.pointX and a.pointY!=b.pointY
    and a.pointX-a.clientX==b.pointX-b.clientX
    and a.pointY-a.clientY==b.pointY-b.clientY
  var current:Key
  var first:Sample
  var last:Sample
  var pending:bool
  var ready:bool
  var pressed:bool
  action init=all{current'=original,first'=empty,last'=empty,pending'=false,ready'=false,pressed'=false}
  action fire(event:Event):bool = match event {
    | Move(s)=>all{current'=current,last'=s,pressed'=false,
        first'=if(pending and valid(s,current) and agrees(first,s))first else s,
        pending'=valid(s,current),ready'=(pending and valid(first,current)
          and valid(s,current) and agrees(first,s))}
    | Change(k)=>all{current'=k,first'=empty,last'=empty,pending'=false,ready'=false,pressed'=false}
    | Invalidate=>all{current'=current,first'=empty,last'=empty,pending'=false,ready'=false,pressed'=false}
    | Press=>all{current'=current,first'=first,last'=last,pending'=pending,ready'=ready,pressed'=ready}
  }
  pure val good={...empty,sequence:1,trusted:true,exactHit:true,unchanged:true,timestamp:2,prepared:1,
    pointX:300,pointY:400,clientX:120,clientY:163,inside:true}
  pure val second={...good,sequence:2,pointX:360,pointY:440,clientX:180,clientY:203}
  val allProps = (ready implies pending and valid(first,current) and valid(last,current) and agrees(first,last))
    and (pressed implies ready)
  action step={nondet e=Set(Move(good),Move(second),Move({...second,trusted:false}),
    Move({...second,clientX:181}),Move({...second,buttons:1}),
    Move({...second,key:{...original,lifetime:2}}),Change(original),
    Change({...original,session:2}),Invalidate,Press).oneOf();fire(e)}
}
