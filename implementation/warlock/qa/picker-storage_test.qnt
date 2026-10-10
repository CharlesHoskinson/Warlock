module pickerStorageTests {
  import pickerStorage.* from "./picker-storage"
  action check(ok:bool):bool=all{assert(ok and safety),s'=s}
  run twoFamiliesShareNoBackingTest=init.then(allocate(1)).then(finish(1)).then(offerDescriptor(1,1)).then(allocate(2)).then(finish(2)).then(offerDescriptor(2,2)).then(check(s.held==Set(1,2) and s.deliveries==2))
  run thirdBackingRefusesTest=init.then(allocate(1)).then(allocate(2)).then(allocate(3)).then(check(s.refused and s.held==Set(1,2)))
  run unsealedCannotExportTest=init.then(allocate(1)).then(offerDescriptor(1,1)).then(check(s.reply==0 and s.exported==Set()))
  run foreignJobCannotBorrowTest=init.then(allocate(1)).then(finish(1)).then(offerDescriptor(1,2)).then(check(s.reply==0 and s.deliveries==0))
  run exportDoesNotAddBackingTest=init.then(allocate(1)).then(finish(1)).then(offerDescriptor(1,1)).then(check(s.held.size()==1 and s.mapped==Set(1)))
  run retirementWaitsForActualMappingCloseTest=init.then(allocate(1)).then(finish(1)).then(offerDescriptor(1,1)).then(releaseExport(1,1)).then(retireProducer(1,1)).then(check(s.held==Set(1) and s.exported==Set(1) and s.refused))
  run exportReleaseKeepsProducerChargeTest=init.then(allocate(1)).then(finish(1)).then(offerDescriptor(1,1)).then(close(1)).then(releaseExport(1,1)).then(check(s.held==Set(1) and s.exported==Set()))
  run exactRetirementDoesNotEraseOtherFamilyTest=init.then(allocate(1)).then(finish(1)).then(offerDescriptor(1,1)).then(allocate(2)).then(finish(2)).then(offerDescriptor(2,2)).then(close(1)).then(releaseExport(1,1)).then(retireProducer(1,1)).then(check(s.held==Set(2) and s.exported==Set(2)))
  run foreignReleaseCannotRetireBackingTest=init.then(allocate(1)).then(finish(1)).then(offerDescriptor(1,1)).then(close(1)).then(releaseExport(1,2)).then(retireProducer(1,2)).then(check(s.held==Set(1) and s.exported==Set(1)))
  run duplicateExportCannotReplayTest=init.then(allocate(1)).then(finish(1)).then(offerDescriptor(1,1)).then(close(1)).then(releaseExport(1,1)).then(offerDescriptor(1,1)).then(check(s.reply==0 and s.deliveries==1))
  run revokedKeepsChargeButDeniesDescriptorTest=init.then(allocate(1)).then(finish(1)).then(revoke).then(offerDescriptor(1,1)).then(check(s.held==Set(1) and s.reply==0))
  run privateCaptureFailureFreesOnlyItsBackingTest=init.then(allocate(1)).then(allocate(2)).then(retireProducer(1,1)).then(allocate(3)).then(check(s.held==Set(2,3)))
}
