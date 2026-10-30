// Source proposal only; untypechecked and unrun. No OS crash-durability proof.
module settings_migration {
  type Phase = Idle | BackupTemp | BackupFlushed | BackupExisting | BackupLinked | BackupUnlinked | BackupReady | ActiveTemp | ActiveFlushed | ActiveVisible | Complete | Stopped
  type Outcome = NoneYet | ReadOnly | Refused | Raised | Unknown | Saved | RestartRead | RestartRefused
  type State = { phase: Phase, outcome: Outcome, legacy: bool, active: int, previousActive: int,
    old: int, backup: int, initialBackup: int, backupLinks: int, backupSafe: bool,
    backupSynced: bool, backupFileSynced: bool, activeFileSynced: bool,
    activeDirSynced: bool, readObserved: bool, renameOccurred: bool,
    restartBlocked: bool, activeSafe: bool, schemaValid: bool, broken: bool,
    fixtureOpen: bool, publishedBackup: bool }
  // 1 = exact raw legacy bytes, 2 = current-schema old/new migration image,
  // 3 = foreign backup, 4 = changed complete current-schema image.
  // backup 0 = absent. The values are opaque identities, not serialized schemas.
  var s: State
  pure def canBegin(x: State): bool = x.phase == Idle and x.activeSafe and x.schemaValid and (x.outcome == NoneYet or x.outcome == ReadOnly or x.outcome == RestartRead)
  pure def backupValid(x: State): bool = x.backup == 0 or (x.backup == x.old and x.backupSafe and x.backupLinks == 1)
  pure def withRead(x: State): State = {...x, outcome: ReadOnly, readObserved: true, fixtureOpen: false}
  action init: bool = s' = {phase: Idle, outcome: NoneYet, legacy: true, active: 1, previousActive: 1,
    old: 1, backup: 0, initialBackup: 0, backupLinks: 0, backupSafe: true, backupSynced: false,
    backupFileSynced: false, activeFileSynced: false, activeDirSynced: false,
    readObserved: false, renameOccurred: false, restartBlocked: false, activeSafe: true, schemaValid: true, broken: false, fixtureOpen: true, publishedBackup: false}
  action readLegacy: bool = all {canBegin(s), s.active == 1, s' = withRead(s)}
  action readCurrent: bool = all {canBegin(s), s.active != 1, s' = withRead(s)}
  // Fixture selections only, before any save; no implicit migration.
  action currentSchema: bool = all {s.fixtureOpen, s' = {...s, legacy: false, active: 2, previousActive: 2, old: 2, fixtureOpen: false}}
  action existingExact: bool = all {s.fixtureOpen,
    s' = {...s, backup: 1, initialBackup: 1, backupLinks: 1, backupSafe: true, fixtureOpen: false}}
  action existingForeign: bool = all {s.fixtureOpen,
    s' = {...s, backup: 3, initialBackup: 3, backupLinks: 1, backupSafe: true, fixtureOpen: false}}
  action existingUnsafe: bool = all {s.fixtureOpen,
    s' = {...s, backup: 1, initialBackup: 1, backupLinks: 2, backupSafe: false, fixtureOpen: false}}
  action unsafeActiveFixture: bool = all {s.fixtureOpen, s' = {...s, activeSafe: false, fixtureOpen: false}}
  action invalidSchemaFixture: bool = all {s.fixtureOpen, s' = {...s, schemaValid: false, fixtureOpen: false}}
  action rejectActive: bool = all {s.phase == Idle, (not(s.activeSafe) or not(s.schemaValid)), s' = {...s, outcome: Refused, fixtureOpen: false}}
  // Schema 2 can legitimately coexist with an unrelated unsafe old backup.
  action currentWithUnsafeBackup: bool = all {s.fixtureOpen,
    s' = {...s, legacy: false, active: 2, previousActive: 2, old: 2, backup: 3, initialBackup: 3,
      backupLinks: 2, backupSafe: false, fixtureOpen: false}}
  action invalid: bool = all {canBegin(s), s' = {...s, outcome: Refused, fixtureOpen: false}}
  action casConflict: bool = all {canBegin(s), s' = {...s, outcome: Refused, fixtureOpen: false}}
  action noChange: bool = all {canBegin(s), s' = {...s, outcome: Refused, fixtureOpen: false}}
  action rejectBackup: bool = all {canBegin(s), s.active == 1, not(backupValid(s)), s' = {...s, outcome: Refused, fixtureOpen: false}}
  action begin: bool = all {canBegin(s), (s.active != 1 or backupValid(s)),
    s' = {...s, phase: if (s.active != 1) BackupReady else if (s.backup == 0) BackupTemp else BackupExisting, fixtureOpen: false}}
  action flushBackup: bool = all {s.phase == BackupTemp, s' = {...s, phase: BackupFlushed, backupFileSynced: true}}
  action linkBackup: bool = all {s.phase == BackupFlushed, s' = {...s, phase: BackupLinked, backup: s.old, backupLinks: 2, publishedBackup: true}}
  action unlinkBackupTemp: bool = all {s.phase == BackupLinked, s' = {...s, phase: BackupUnlinked, backupLinks: 1}}
  action syncExistingFile: bool = all {s.phase == BackupExisting, s' = {...s, phase: BackupUnlinked, backupFileSynced: true}}
  action syncBackupDirectory: bool = all {s.phase == BackupUnlinked,
    s' = {...s, phase: BackupReady, backupFileSynced: true, backupSynced: true}}
  action writeActive: bool = all {s.phase == BackupReady, s' = {...s, phase: ActiveTemp}}
  action flushActive: bool = all {s.phase == ActiveTemp, s' = {...s, phase: ActiveFlushed, activeFileSynced: true}}
  action renameActive: bool = all {s.phase == ActiveFlushed, s.activeFileSynced,
    (not(s.legacy) or (s.backup == s.old and s.backupSynced and s.backupFileSynced and s.backupLinks == 1)),
    s' = {...s, phase: ActiveVisible, active: if (s.active == 1) 2 else 4, previousActive: s.active, renameOccurred: true}}
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
  action restartRead: bool = all {s.phase == Stopped, s.activeSafe, s.schemaValid, (s.active == 1 or s.active == 2 or s.active == 4),
    s' = {...s, phase: Idle, outcome: RestartRead, readObserved: true}}
  action restartSaveRefusesLinks: bool = all {s.phase == Idle, s.outcome == RestartRead, s.active == 1, s.backupLinks == 2,
    s' = {...s, outcome: RestartRefused, restartBlocked: true}}
  // Crash after unsynced active rename may recover either complete directory entry.
  action crashBeforeBarrierOld: bool = all {s.phase == ActiveVisible,
    s' = {...s, phase: Stopped, outcome: Unknown, active: s.previousActive}}
  // Explicit intentionally broken historical behavior; excluded from step.
  action brokenActivate: bool = all {canBegin(s), s.legacy, s.backup == 0,
    s' = {...s, active: 2, renameOccurred: true, broken: true, phase: Complete, outcome: Saved, fixtureOpen: false}}
  val completeActive: bool = s.active == 1 or s.active == 2 or s.active == 4
  val originalBeforeActivation: bool = (s.legacy and s.renameOccurred) implies (s.backup == s.old and s.backupSynced and s.backupFileSynced)
  val savedAfterBarrier: bool = (s.outcome == Saved) implies s.activeDirSynced
  val backupNeverOverwritten: bool = s.initialBackup != 0 implies s.backup == s.initialBackup
  val twoLinkRecoverable: bool = (s.publishedBackup and s.backupLinks == 2) implies s.backup == s.old and s.active == s.old
  action step: bool = any {readLegacy, readCurrent, currentSchema, existingExact, existingForeign, existingUnsafe,
    unsafeActiveFixture, invalidSchemaFixture, currentWithUnsafeBackup, rejectActive, invalid, casConflict, noChange, rejectBackup, begin, flushBackup, linkBackup,
    unlinkBackupTemp, syncExistingFile, syncBackupDirectory, writeActive, flushActive, renameActive,
    syncActiveDirectory, preRenameFault, linkedInterrupt, postRenameFault, restartRead,
    restartSaveRefusesLinks, crashBeforeBarrierOld}
}
