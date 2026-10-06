module popup {
  var popupExists: bool
  var identity: int
  var nextIdentity: int
  var applied: int
  var x: int
  var y: int
  var valid: bool
  var epoch: int
  var command: str
  var changed: bool
  action init = all { popupExists'=false, identity'=0, nextIdentity'=2,
    applied'=0, x'=0, y'=0, valid'=true, epoch'=2, command'="reset", changed'=true }
  action create = all { not(popupExists), valid, popupExists'=true, identity'=nextIdentity,
    nextIdentity'=nextIdentity+1, applied'=1, x'=291, y'=211,
    valid'=true, epoch'=epoch+1, command'="popup-create", changed'=true }
  action yellow = all { popupExists, valid, applied==1, popupExists'=popupExists, identity'=identity,
    nextIdentity'=nextIdentity, applied'=applied+1, x'=x, y'=y,
    valid'=valid, epoch'=epoch+1, command'="popup-yellow", changed'=true }
  action reposition = all { popupExists, valid, x==291, popupExists'=popupExists, identity'=identity,
    nextIdentity'=nextIdentity, applied'=applied+1, x'=101, y'=81,
    valid'=valid, epoch'=epoch+1, command'="popup-reposition", changed'=true }
  action destroy = all { popupExists, valid, popupExists'=false, identity'=0,
    nextIdentity'=nextIdentity, applied'=0, x'=0, y'=0,
    valid'=valid, epoch'=epoch+1, command'="popup-destroy", changed'=true }
  action inspect = all { popupExists'=popupExists, identity'=identity, nextIdentity'=nextIdentity,
    applied'=applied, x'=x, y'=y, valid'=valid, epoch'=epoch,
    command'="inspect", changed'=false }
  action malformed = all { valid, popupExists'=popupExists, identity'=identity,
    nextIdentity'=nextIdentity, applied'=applied, x'=x, y'=y,
    valid'=false, epoch'=epoch+1, command'="duplicate-root", changed'=true }
  action recover = all { not(valid), popupExists'=popupExists, identity'=identity,
    nextIdentity'=nextIdentity, applied'=applied, x'=x, y'=y,
    valid'=true, epoch'=epoch+1, command'="recover", changed'=true }
  val safe = epoch>=2 and nextIdentity>=2 and
    (popupExists implies (identity>1 and identity<nextIdentity and applied>=1)) and
    (not(popupExists) implies (identity==0 and applied==0))
  action checked = all { assert(safe), inspect }
  run rootStableTest = init.then(checked).then(checked)
  run popupCommitTest = init.then(create).then(checked).then(yellow).then(checked).then(destroy)
  run popupMoveTest = init.then(create).then(reposition).then(checked).then(destroy)
  run popupReplacementTest = init.then(create).then(yellow).then(destroy).then(create).then(checked).then(destroy)
  run malformedRefusalTest = init.then(create).then(malformed).then(checked).then(recover).then(checked).then(destroy)
}
