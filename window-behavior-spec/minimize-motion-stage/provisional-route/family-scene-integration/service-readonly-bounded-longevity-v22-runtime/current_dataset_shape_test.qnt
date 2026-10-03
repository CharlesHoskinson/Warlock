module current_dataset_shape_test {
 import current_dataset_shape.* from "./current_dataset_shape"
 action check(b:bool):bool=all{assert(b),s'=s}
 action reply=fire(Check(header)).then(fire(Connect)).then(fire(Reply))
 run validTypedFreshFlowTest=init.then(reply).then(fire(Confirm({...header,serial:1}))).then(fire(Consume)).then(check(s.bytesNow and allProps))
 run booleanFalseEpochAliasIsNotIntegerZeroTest=init.then(fire(Check({...header,epoch:0,epochTyped:false}))).then(check(s.fault and s.phase==0))
 run booleanFalseSerialAliasIsNotIntegerZeroTest=init.then(fire(Check({...header,serial:0,serialTyped:false}))).then(check(s.fault and s.phase==0))
 run floatVersionEqualityIsNotTypedIntegerVersionTest=init.then(fire(Check({...header,version:2,versionTyped:false}))).then(check(s.fault))
 run falseLikeFaultIsNotLiteralFalseTest=init.then(fire(Check({...header,faultFalse:false}))).then(check(s.fault))
 run incompleteFieldSetCannotAuthorizeConnectionTest=init.then(fire(Check({...header,fieldsComplete:false}))).then(fire(Connect)).then(check(s.fault and s.phase==0))
 run validReplacementCurrentBindingDirectoryPredecessorRefusesTest=init.then(all{nondet n=Set(1,2,3).oneOf();fire(Check({...header,binding:if(n==1)2 else 1,directory:if(n==2)2 else 1,predecessor:if(n==3)2 else 1}))}).then(check(s.fault))
 run inconsistentActiveArchiveCoverageRefusesTest=init.then(fire(Check({...header,countConsistent:false}))).then(check(s.fault))
 run postDiskTypeLossCannotReturnBytesTest=init.then(reply).then(fire(Confirm({...header,epochTyped:false}))).then(fire(Consume)).then(check(s.fault and not(s.bytesNow)))
 run cachedValidHeaderCannotClearTerminalRefusalTest=init.then(fire(Check({...header,epochTyped:false}))).then(fire(Check(header))).then(fire(Connect)).then(fire(Reply)).then(fire(Confirm(header))).then(fire(Consume)).then(check(s.fault and not(s.bytesNow)))
 run integerSizeFloatAliasRefusesCurrentConnectionTest=init.then(fire(Check({...header,binding:1,bindingTyped:false}))).then(fire(Connect)).then(check(s.fault and s.phase==0))
 run integerSourceBoolAliasRefusesHistoricalProjectionTest=init.then(fire(HistoricalProjection({...header,binding:1,bindingTyped:false}))).then(check(s.fault and not(s.historicalShapeAccepted)))
 run integerSourceFloatAliasRefusesHistoricalProjectionTest=init.then(fire(HistoricalProjection({...header,bindingTyped:false}))).then(check(s.fault and not(s.historicalShapeAccepted)))
 run postDiskSourceTypeLossCannotReturnBytesTest=init.then(reply).then(fire(Confirm({...header,bindingTyped:false}))).then(fire(Consume)).then(check(s.fault and not(s.bytesNow)))
 run validTypedHistoricalShapeIsNotNativeOrReturnedByteAuthorityTest=init.then(fire(HistoricalProjection(header))).then(check(s.historicalShapeAccepted and not(s.bytesNow) and s.nativeEffects==0))
}
