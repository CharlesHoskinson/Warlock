module mapping_identity {
  var fdPinned: bool
  var pathExact: bool
  var bytesExact: bool
  var backingDevice: int
  var backingInode: int
  var calibrated: bool
  var remoteDevice: int
  var remoteInode: int
  var accepted: bool
  action init = all { fdPinned'=false, pathExact'=true, bytesExact'=true,
    backingDevice'=30, backingInode'=7, calibrated'=false,
    remoteDevice'=0, remoteInode'=0, accepted'=false }
  action pin = all { pathExact, bytesExact, fdPinned'=true,
    pathExact'=pathExact, bytesExact'=bytesExact, backingDevice'=backingDevice,
    backingInode'=backingInode, calibrated'=false, remoteDevice'=remoteDevice,
    remoteInode'=remoteInode, accepted'=false }
  action calibrate = all { fdPinned, pathExact, bytesExact, calibrated'=true,
    fdPinned'=fdPinned, pathExact'=pathExact, bytesExact'=bytesExact,
    backingDevice'=backingDevice, backingInode'=backingInode,
    remoteDevice'=remoteDevice, remoteInode'=remoteInode, accepted'=false }
  action observe = {
    nondet dev = Set(30,58).oneOf()
    nondet ino = Set(7,8).oneOf()
    all { remoteDevice'=dev, remoteInode'=ino, fdPinned'=fdPinned,
      pathExact'=pathExact, bytesExact'=bytesExact, backingDevice'=backingDevice,
      backingInode'=backingInode, calibrated'=calibrated, accepted'=false }
  }
  action replace = all { pathExact'=false, fdPinned'=fdPinned, bytesExact'=bytesExact,
    backingDevice'=backingDevice, backingInode'=backingInode, calibrated'=calibrated,
    remoteDevice'=remoteDevice, remoteInode'=remoteInode, accepted'=false }
  action mutate = all { bytesExact'=false, fdPinned'=fdPinned, pathExact'=pathExact,
    backingDevice'=backingDevice, backingInode'=backingInode, calibrated'=calibrated,
    remoteDevice'=remoteDevice, remoteInode'=remoteInode, accepted'=false }
  action accept = all { fdPinned, pathExact, bytesExact, calibrated,
    remoteDevice==backingDevice, remoteInode==backingInode, accepted'=true,
    fdPinned'=fdPinned, pathExact'=pathExact, bytesExact'=bytesExact,
    backingDevice'=backingDevice, backingInode'=backingInode, calibrated'=calibrated,
    remoteDevice'=remoteDevice, remoteInode'=remoteInode }
  action stutter = all { fdPinned'=fdPinned, pathExact'=pathExact, bytesExact'=bytesExact,
    backingDevice'=backingDevice, backingInode'=backingInode, calibrated'=calibrated,
    remoteDevice'=remoteDevice, remoteInode'=remoteInode, accepted'=accepted }
  action step = any { pin, calibrate, observe, replace, mutate, accept, stutter }
  val invariant = accepted implies all { fdPinned, pathExact, bytesExact, calibrated,
    remoteDevice==backingDevice, remoteInode==backingInode }
  run calibratedBtrfsCanAcceptTest = init.then(pin).then(calibrate)
    .then(all { remoteDevice'=30, remoteInode'=7, fdPinned'=fdPinned, pathExact'=pathExact,
      bytesExact'=bytesExact, backingDevice'=backingDevice, backingInode'=backingInode,
      calibrated'=calibrated, accepted'=false }).then(accept).then(all { assert(accepted and invariant), stutter })
  run noCalibrationCannotAcceptTest = init.then(pin).then(observe).then(all { assert(not(calibrated) and not(accepted)), stutter })
  run statDeviceNeverSubstitutesTest = init.then(pin).then(calibrate)
    .then(all { remoteDevice'=58, remoteInode'=7, fdPinned'=fdPinned, pathExact'=pathExact,
      bytesExact'=bytesExact, backingDevice'=backingDevice, backingInode'=backingInode,
      calibrated'=calibrated, accepted'=false }).then(all { assert(remoteDevice!=backingDevice and not(accepted)), stutter })
  run changedPathCannotAcceptTest = init.then(pin).then(calibrate).then(replace).then(all { assert(not(pathExact) and not(accepted)), stutter })
  run changedBytesCannotAcceptTest = init.then(pin).then(calibrate).then(mutate).then(all { assert(not(bytesExact) and not(accepted)), stutter })
}
