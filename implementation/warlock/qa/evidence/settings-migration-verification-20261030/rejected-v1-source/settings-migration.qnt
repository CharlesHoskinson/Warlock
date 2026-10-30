// Source proposal only; untypechecked and unrun. No OS crash-durability proof.
module settings_migration {
  type Phase = Idle | BackupTemp | BackupFlushed | BackupExisting | BackupLinked | BackupUnlinked | BackupReady | ActiveTemp | ActiveFlushed | ActiveVisible | Complete | Stopped
  type Outcome = NoneYet | ReadOnly | Refused | Raised | Unknown | Saved | RestartRead | RestartRefused
  type State = { phase: Phase, outcome: Outcome, legacy: bool, active: int,
    old: int, backup: int, initialBackup: int, backupLinks: int, backupSafe: bool,
    backupSynced: bool, backupFileSynced: bool, activeFileSynced: bool,
    activeDirSynced: bool, readObserved: bool, renameOccurred: bool,
    restartBlocked: bool, activeSafe: bool, schemaValid: bool, broken: bool }
  // 1 = exact raw legacy bytes, 2 = complete current-schema bytes, 3 = foreign.
  // backup 0 = absent. The values are opaque identities, not serialized schemas.
  var s: State
  pure def canBegin(x: State): bool = x.phase == Idle and x.activeSafe and x.schemaValid and (x.outcome == NoneYet or x.outcome == ReadOnly or x.outcome == RestartRead)
  pure def backupValid(x: State): bool = x.backup == 0 or (x.backup == x.old and x.backupSafe and x.backupLinks == 1)
  pure def withRead(x: State): State = {...x, outcome: ReadOnly, readObserved: true}
  action init: bool = s' = {phase: Idle, outcome: NoneYet, legacy: true, active: 1,
    old: 1, backup: 0, initialBackup: 0, backupLinks: 0, backupSafe: true, backupSynced: false,
    backupFileSynced: false, activeFileSynced: false, activeDirSynced: false,
    readObserved: false, renameOccurred: false, restartBlocked: false, activeSafe: true, schemaValid: true, broken: false}
  action readLegacy: bool = all {canBegin(s), s.legacy, s' = withRead(s)}
  // Fixture selections only, before any save; no implicit migration.
  action currentSchema: bool = all {s.phase == Idle, s.outcome == NoneYet, s' = {...s, legacy: false, active: 2}}
  action existingExact: bool = all {s.phase == Idle, s.outcome == NoneYet, s.active == 1, s.backup == 0,
    s' = {...s, backup: 1, initialBackup: 1, backupLinks: 1, backupSafe: true}}
  action existingForeign: bool = all {s.phase == Idle, s.outcome == NoneYet, s.active == 1, s.backup == 0,
    s' = {...s, backup: 3, initialBackup: 3, backupLinks: 1, backupSafe: true}}
  action existingUnsafe: bool = all {s.phase == Idle, s.outcome == NoneYet, s.active == 1, s.backup == 0,
    s' = {...s, backup: 1, initialBackup: 1, backupLinks: 2, backupSafe: false}}
  action unsafeActiveFixture: bool = all {s.phase == Idle, s.outcome == NoneYet, s' = {...s, activeSafe: false}}
  action invalidSchemaFixture: bool = all {s.phase == Idle, s.outcome == NoneYet, s' = {...s, schemaValid: false}}
  action rejectActive: bool = all {s.phase == Idle, (not(s.activeSafe) or not(s.schemaValid)), s' = {...s, outcome: Refused}}
  action invalid: bool = all {canBegin(s), s' = {...s, outcome: Refused}}
  action casConflict: bool = all {canBegin(s), s' = {...s, outcome: Refused}}
  action noChange: bool = all {canBegin(s), s' = {...s, outcome: Refused}}
  action rejectBackup: bool = all {canBegin(s), s.active == 1, not(backupValid(s)), s' = {...s, outcome: Refused}}
  action begin: bool = all {canBegin(s), (s.active == 2 or backupValid(s)),
    s' = {...s, phase: if (s.active == 2) BackupReady else if (s.backup == 0) BackupTemp else BackupExisting}}
  action flushBackup: bool = all {s.phase == BackupTemp, s' = {...s, phase: BackupFlushed, backupFileSynced: true}}
  action linkBackup: bool = all {s.phase == BackupFlushed, s' = {...s, phase: BackupLinked, backup: s.old, backupLinks: 2}}
  action unlinkBackupTemp: bool = all {s.phase == BackupLinked, s' = {...s, phase: BackupUnlinked, backupLinks: 1}}
  action syncExistingFile: bool = all {s.phase == BackupExisting, s' = {...s, phase: BackupUnlinked, backupFileSynced: true}}
  action syncBackupDirectory: bool = all {s.phase == BackupUnlinked,
    s' = {...s, phase: BackupReady, backupFileSynced: true, backupSynced: true}}
  action writeActive: bool = all {s.phase == BackupReady, s' = {...s, phase: ActiveTemp}}
  action flushActive: bool = all {s.phase == ActiveTemp, s' = {...s, phase: ActiveFlushed, activeFileSynced: true}}
  action renameActive: bool = all {s.phase == ActiveFlushed, s.activeFileSynced,
    (not(s.legacy) or (s.backup == s.old and s.backupSynced and s.backupFileSynced and s.backupLinks == 1)),
    s' = {...s, phase: ActiveVisible, active: 2, renameOccurred: true}}
  action syncActiveDirectory: bool = all {s.phase == ActiveVisible,
    s' = {...s, phase: Complete, outcome: Saved, activeDirSynced: true}}
  // Pre-rename system failure propagates OSError, it does not return a Refused tuple.
  action preRenameFault: bool = all {Set(BackupTemp, BackupFlushed, BackupExisting, BackupUnlinked, BackupReady, ActiveTemp, ActiveFlushed).contains(s.phase),
    s' = {...s, phase: Stopped, outcome: Raised}}
  // Crash or failed repeated unlink can leave published backup with two links.
  action linkedInterrupt: bool = all {s.phase == BackupLinked,
    s' = {...s, phase: Stopped, outcome: Raised, backupSafe: false}}
  action postRenameFault: bool = all {s.phase == ActiveVisible,
    s' = {...s, phase: Stopped, outcome: Unknown}}
  // Restart reads only active file; it does not validate the backup on read.
  action restartRead: bool = all {s.phase == Stopped, s.activeSafe, s.schemaValid, (s.active == 1 or s.active == 2),
    s' = {...s, phase: Idle, outcome: RestartRead, readObserved: true}}
  action restartSaveRefusesLinks: bool = all {s.phase == Idle, s.outcome == RestartRead, s.active == 1, s.backupLinks == 2,
    s' = {...s, outcome: RestartRefused, restartBlocked: true}}
  // Crash after unsynced active rename may recover either complete directory entry.
  action crashBeforeBarrierOld: bool = all {s.phase == ActiveVisible,
    s' = {...s, phase: Stopped, outcome: Unknown, active: if (s.legacy) 1 else 2}}
  // Explicit intentionally broken historical behavior; excluded from step.
  action brokenActivate: bool = all {canBegin(s), s.legacy, s.backup == 0,
    s' = {...s, active: 2, renameOccurred: true, broken: true, phase: Complete, outcome: Saved}}
  val completeActive: bool = s.active == 1 or s.active == 2
  val originalBeforeActivation: bool = (s.legacy and s.renameOccurred) implies (s.backup == s.old and s.backupSynced and s.backupFileSynced)
  val savedAfterBarrier: bool = (s.outcome == Saved) implies s.activeDirSynced
  val backupNeverOverwritten: bool = s.initialBackup != 0 implies s.backup == s.initialBackup
  val twoLinkRecoverable: bool = (s.backupLinks == 2) implies s.backup == s.old and s.active == s.old
  action step: bool = any {readLegacy, currentSchema, existingExact, existingForeign, existingUnsafe,
    unsafeActiveFixture, invalidSchemaFixture, rejectActive, invalid, casConflict, noChange, rejectBackup, begin, flushBackup, linkBackup,
    unlinkBackupTemp, syncExistingFile, syncBackupDirectory, writeActive, flushActive, renameActive,
    syncActiveDirectory, preRenameFault, linkedInterrupt, postRenameFault, restartRead,
    restartSaveRefusesLinks, crashBeforeBarrierOld}
}
