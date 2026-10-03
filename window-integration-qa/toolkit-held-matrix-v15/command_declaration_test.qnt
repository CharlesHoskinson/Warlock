module command_declaration_test {
 import command_declaration.* from "./command_declaration"
 run originalMutableDeclarationComparisonRejectsRealNormalJobTest=init.then(fire(Submit)).then(fire(Rebind)).then(fire(Start)).then(fire(OldCommandComparison)).then(all { s'=s, assert(s.failed and s.launchedArgv==1 and s.declaration==2) })
 run declaredBindingChangeDoesNotChangeLaunchedArgvTest=init.then(fire(Submit)).then(fire(Rebind)).then(fire(Start)).then(fire(NormalExit)).then(fire(Drain)).then(all { s'=s, assert(s.accepted and s.launchedArgv==1 and s.requestDeclaration==1 and s.declaration==2 and allProps) })
 run declaredFieldCannotInferMissingNativeStartTest=init.then(fire(Submit)).then(fire(Rebind)).then(fire(NormalExit)).then(fire(Drain)).then(all { s'=s, assert(s.failed and not(s.accepted)) })
 run actualExit120StillRefusesRegardlessOfBindingTest=init.then(fire(Submit)).then(fire(Rebind)).then(fire(Start)).then(fire(BadExit)).then(fire(Drain)).then(all { s'=s, assert(s.failed and not(s.accepted)) })
 run sourceIdentityMutationCannotGainDeclarationExceptionTest=init.then(fire(Submit)).then(fire(Rebind)).then(fire(Start)).then(fire(SourceChanged)).then(fire(NormalExit)).then(fire(Drain)).then(all { s'=s, assert(s.failed and not(s.accepted)) })
}
