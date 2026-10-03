module focus_setup {
  type Identity = {window:int, pid:int, start:int, session:int}
  type Setup = {owner:Identity, ack:bool, nativeFocus:int, pointerOwner:int, clear:bool, stable:bool}
  type Motion = {owner:Identity, focus:int, pointer:int, clear:bool, x:int, y:int, fresh:bool, exactTranslation:bool}
  type Event = Establish(Setup) | Move(Motion) | Change(Identity) | LoseFocus | Press
  pure val original = {window:1,pid:1,start:1,session:1}
  pure val goodSetup = {owner:original,ack:true,nativeFocus:1,pointerOwner:1,clear:true,stable:true}
  pure val good = {owner:original,focus:1,pointer:1,clear:true,x:10,y:10,fresh:true,exactTranslation:true}
  pure val second = {...good,x:20,y:20}
  var current:Identity
  var setup:bool
  var pending:bool
  var ready:bool
  var pressed:bool
  var cursorX:int
  var cursorY:int
  var firstX:int
  var firstY:int
  def valid(s:Setup):bool = s.owner==current and s.ack and s.nativeFocus==current.window
    and s.pointerOwner==current.window and s.clear and s.stable
  def validMove(m:Motion):bool = setup and m.owner==current and m.focus==current.window
    and m.pointer==current.window and m.clear and m.fresh and m.exactTranslation
    and (m.x!=cursorX or m.y!=cursorY)
  action init=all{current'=original,setup'=false,pending'=false,ready'=false,pressed'=false,
    cursorX'=10,cursorY'=10,firstX'=0,firstY'=0}
  action fire(e:Event):bool = match e {
    | Establish(s)=>all{current'=current,setup'=valid(s),pending'=false,ready'=false,pressed'=false,
        cursorX'=cursorX,cursorY'=cursorY,firstX'=0,firstY'=0}
    | Move(m)=>all{current'=current,setup'=(setup and validMove(m)),pending'=validMove(m),
        ready'=(validMove(m) and pending and m.x!=firstX and m.y!=firstY),pressed'=false,
        firstX'=if(pending and validMove(m))firstX else m.x,
        firstY'=if(pending and validMove(m))firstY else m.y,
        cursorX'=m.x,cursorY'=m.y}
    | Change(i)=>all{current'=i,setup'=false,pending'=false,ready'=false,pressed'=false,
        cursorX'=cursorX,cursorY'=cursorY,firstX'=0,firstY'=0}
    | LoseFocus=>all{current'=current,setup'=false,pending'=false,ready'=false,pressed'=false,
        cursorX'=cursorX,cursorY'=cursorY,firstX'=0,firstY'=0}
    | Press=>all{current'=current,setup'=setup,pending'=pending,ready'=ready,pressed'=ready,
        cursorX'=cursorX,cursorY'=cursorY,firstX'=firstX,firstY'=firstY}
  }
  val allProps = (ready implies setup and pending) and (pressed implies ready and setup)
  action step={nondet e=Set(Establish(goodSetup),Establish({...goodSetup,ack:false}),
    Establish({...goodSetup,nativeFocus:2}),Move(good),Move(second),
    Move({...second,focus:2}),Move({...second,owner:{...original,start:2}}),
    Move({...second,fresh:false}),Change({...original,session:2}),LoseFocus,Press).oneOf();fire(e)}
}
