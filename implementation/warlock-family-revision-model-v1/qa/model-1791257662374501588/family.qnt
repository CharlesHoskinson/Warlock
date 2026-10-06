module family {
  var present: bool
  var linked: bool
  var modal: bool
  var identity: int
  var nextIdentity: int
  var content: int
  var x: int
  var y: int
  var invalid: int
  var epoch: int
  var command: str
  var changed: bool
  action init = all {present'=false,linked'=false,modal'=false,identity'=0,nextIdentity'=2,
    content'=0,x'=0,y'=0,invalid'=0,epoch'=2,command'="reset",changed'=true}
  action create = all {not(present),invalid==0,present'=true,linked'=true,modal'=true,
    identity'=nextIdentity,nextIdentity'=nextIdentity+1,content'=1,x'=192,y'=168,
    invalid'=0,epoch'=epoch+1,command'="modal-create",changed'=true}
  action paint = all {present,linked,invalid==0,present'=present,linked'=linked,modal'=modal,
    identity'=identity,nextIdentity'=nextIdentity,content'=content+1,x'=x,y'=y,
    invalid'=invalid,epoch'=epoch+1,command'="modal-yellow",changed'=true}
  action move = all {present,linked,invalid==0,x==192,present'=present,linked'=linked,modal'=modal,
    identity'=identity,nextIdentity'=nextIdentity,content'=content,x'=260,y'=190,
    invalid'=invalid,epoch'=epoch+1,command'="modal-move",changed'=true}
  action parent(value:bool):bool = all {present,invalid==0,linked!=value,
    present'=present,linked'=value,modal'=modal,identity'=identity,nextIdentity'=nextIdentity,
    content'=content,x'=x,y'=y,invalid'=invalid,epoch'=epoch+1,
    command'=if(value)"modal-reparent" else "modal-unparent",changed'=true}
  action hint(value:bool):bool = all {present,linked,invalid==0,modal!=value,
    present'=present,linked'=linked,modal'=value,identity'=identity,nextIdentity'=nextIdentity,
    content'=content,x'=x,y'=y,invalid'=invalid,epoch'=epoch+1,
    command'=if(value)"modal-set" else "modal-unset",changed'=true}
  action destroy = all {present,invalid==0,present'=false,linked'=false,modal'=false,
    identity'=0,nextIdentity'=nextIdentity,content'=0,x'=0,y'=0,invalid'=0,
    epoch'=epoch+1,command'="modal-destroy",changed'=true}
  action inspect = all {present'=present,linked'=linked,modal'=modal,identity'=identity,
    nextIdentity'=nextIdentity,content'=content,x'=x,y'=y,invalid'=invalid,epoch'=epoch,
    command'="inspect",changed'=false}
  action malformed(code:int):bool = all {present,linked,invalid==0,
    present'=present,linked'=linked,modal'=modal,identity'=identity,nextIdentity'=nextIdentity,
    content'=content,x'=x,y'=y,invalid'=code,epoch'=epoch+1,
    command'=if(code==1)"cycle" else "over-capacity",changed'=true}
  action recover = all {invalid>0,present'=present,linked'=linked,modal'=modal,
    identity'=identity,nextIdentity'=nextIdentity,content'=content,x'=x,y'=y,
    invalid'=0,epoch'=epoch+1,command'="recover",changed'=true}
  val safe = epoch>=2 and nextIdentity>=2 and invalid>=0 and invalid<=2 and
    (present implies (identity>1 and identity<nextIdentity and content>=1)) and
    (not(present) implies (identity==0 and content==0 and not(linked)))
  action checked = all {assert(safe),inspect}
  run familyStableTest = init.then(checked).then(checked)
  run familyPaintTest = init.then(create).then(checked).then(paint).then(checked).then(destroy)
  run familyGeometryTest = init.then(create).then(move).then(checked).then(destroy)
  run familyLinkTest = init.then(create).then(parent(false)).then(checked).then(parent(true)).then(checked).then(destroy)
  run familyHintTest = init.then(create).then(hint(false)).then(checked).then(hint(true)).then(checked).then(destroy)
  run familyReplacementTest = init.then(create).then(destroy).then(create).then(checked).then(destroy)
  run familyCycleRefusalTest = init.then(create).then(malformed(1)).then(checked).then(recover).then(checked).then(destroy)
  run familyCapacityRefusalTest = init.then(create).then(malformed(2)).then(checked).then(recover).then(checked).then(destroy)
}
