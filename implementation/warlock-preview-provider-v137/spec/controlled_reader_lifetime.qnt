module controlled_reader_lifetime {
 import host_realm_lifecycle.* from "./host_realm_lifecycle"
 type Reader=Absent|HeldCurrent|HeldRevoked|Released
 var reader:Reader
 var probed:bool
 var closes:int
 action initReader=all{init,reader'=Absent,probed'=false,closes'=0}
 action event(e:Event)=all{
  if(e==ClosePopup and reader==HeldCurrent) reader'=HeldRevoked else reader'=reader,
  probed'=probed,closes'=closes,
  if(e==Drain and (reader==HeldCurrent or reader==HeldRevoked)) s'={...s,code:1} else fire(e)
 }
 action hold=all{
  s'=s,probed'=probed,closes'=closes,
  if(reader==Absent and s.native and s.initialized and s.current and not(s.uncertain)) reader'=HeldCurrent else reader'=reader
 }
 action probe=all{s'=s,reader'=reader,closes'=closes,probed'=(reader==HeldRevoked and not(s.uncertain)) or probed}
 action release=all{
  s'=s,probed'=probed,
  if(reader==HeldRevoked and probed and not(s.uncertain)) all{reader'=Released,closes'=closes+1} else all{reader'=reader,closes'=closes}
 }
 action admitted=event(OpenIntent).then(event(DOMReady)).then(event(Admit)).then(event(Initialize)).then(event(Apply))
 action step=any{hold,probe,release,nondet e=Set(OpenIntent,DOMReady,Admit,Initialize,Apply,ClosePopup,Drain,Retire,Replace,StaleCallback,Unknown).oneOf();event(e)}
 val readerSafety=all{safety,closes>=0,closes<=1,(reader==HeldCurrent or reader==HeldRevoked) implies s.duty,reader==HeldRevoked implies not(s.current)}
}
