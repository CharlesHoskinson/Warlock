module callback_fixture_completion {
 type State={failed:bool,callbackStarted:bool,receipts:int,elapsed:int,expired:bool,accepted:bool,sendRefused:bool,normalCloseRefused:bool}
 type Event=Failure|StartCallback|ReturnCallback|Duplicate|Tick|Inspect|Send|Close
 var s:State
 action init=s'={failed:false,callbackStarted:false,receipts:0,elapsed:0,expired:false,accepted:false,sendRefused:false,normalCloseRefused:false}
 action fire(e:Event):bool=s'=match e {
 | Failure=>{...s,failed:true}
 | StartCallback=>if(s.failed){...s,callbackStarted:true}else s
 | ReturnCallback=>if(s.callbackStarted and s.receipts==0){...s,receipts:1}else s
 | Duplicate=>if(s.receipts>0){...s,receipts:s.receipts+1,accepted:false}else s
 | Tick=>{...s,elapsed:s.elapsed+1,expired:s.expired or s.elapsed+1>=20}
 | Inspect=>{...s,accepted:s.failed and s.receipts==1 and not(s.expired) and s.elapsed<20}
 | Send=>{...s,sendRefused:s.failed}
 | Close=>{...s,normalCloseRefused:s.failed}
 }
 val allProps=s.receipts>=0 and (s.accepted implies s.failed and s.receipts==1)
 action step={nondet e=Set(Failure,StartCallback,ReturnCallback,Duplicate,Tick,Inspect,Send,Close).oneOf();fire(e)}
}
