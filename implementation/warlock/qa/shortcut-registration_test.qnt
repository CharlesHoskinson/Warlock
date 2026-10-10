module ShortcutRegistrationTest {
 import ShortcutRegistration.* from "./shortcut-registration"
 run freeDefaultAfterConfigurationTest = init.then(finishReload).then(verify(defaultReady))
 run defaultConflictPreservesForeignTest = init.then(foreignConflict("default")).then(finishReload).then(verify(state.installed == Keep and state.foreign == Set("existing", "default")))
 run explicitKeepSurvivesReloadTest = init.then(finishReload).then(submit(Keep)).then(apply).then(receipt).then(beginReload).then(finishReload).then(verify(keptAfterReload and state.installed == Keep and state.writes == 1))
 run selectedAlternateSurvivesReloadTest = init.then(finishReload).then(submit(Alternate)).then(apply).then(receipt).then(beginReload).then(finishReload).then(verify(alternateAfterReload and state.writes == 1))
 run reloadRetiresOldFingerprintTest = init.then(finishReload).then(submit(Alternate)).then(beginReload).then(finishReload).then(refuse).then(verify(state.desired == Default and state.writes == 0))
 run unknownReloadDoesNotResubmitTest = init.then(finishReload).then(submit(Alternate)).then(apply).then(loseReceipt).then(beginReload).then(finishReload).then(verify(unknownAfterReload and state.submissions == 1)).then(read).then(verify(state.writes == 1))
 run newConflictDoesNotOverwriteForeignTest = init.then(finishReload).then(submit(Alternate)).then(apply).then(receipt).then(beginReload).then(foreignConflict("alternate")).then(finishReload).then(verify(state.desired == Alternate and state.installed == Keep and state.foreign == Set("existing", "alternate")))
}
