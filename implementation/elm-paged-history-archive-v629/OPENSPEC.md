# Proposed OpenSpec change: scalable retirement archive

Status: proposed amendment only. Existing64-history capacity scenarios remain frozen history; production behavior is unchanged. Requirements are EARS contracts in requirements.json. Witnesses are symbolic prototype scenarios, not integrated acceptance.

## Requirement: ARC-001

The archive shall conserve the immutable exact full-origin Admission, Unknown, definitive receipt, original Prepared/Released proof and join, delivery attestation and predecessor migration evidence without inferring a terminal outcome from absence.

### Scenario: bounded executable witness for ARC-001

- GIVEN the private symbolic archive and exact-origin model
- WHEN unknownReleaseAndDeliveryTest, immutableMigrationAndCompactionTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Requirement: ARC-002

The archive shall bound live reservations, in-flight mutations, page bytes/entries, cache pages, index depth, cohort records and native queues independently of total retained historical record count.

### Scenario: bounded executable witness for ARC-002

- GIVEN the private symbolic archive and exact-origin model
- WHEN historyGrowsHotBoundedTest, hotExhaustionBeforeEffectTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Requirement: ARC-003

When a new effect is requested, the paired producer shall verify authoritative independent replay watermarks and retired origin/scope indexes and durably commit exact Admission plus reserved completion capacity before invoking the native effect.

### Scenario: bounded executable witness for ARC-003

- GIVEN the private symbolic archive and exact-origin model
- WHEN archivedKeyCannotReadmitTest, archiveQuotaRefusesBeforeEffectTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Requirement: ARC-004

When a generation is published, the writer shall synchronize event/index files and all containing directories before synchronizing the manifest and CURRENT/root directory and exposing success.

### Scenario: bounded executable witness for ARC-004

- GIVEN the private symbolic archive and exact-origin model
- WHEN pagesBeforeManifestTest, visibleManifestRestartBarrierTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Requirement: ARC-005

While a restarted generation has not passed validation and the archive-root synchronization barrier, the system shall keep recovered admissions reserved and refuse effect, unlink, release acknowledgement and historical delivery exposure.

### Scenario: bounded executable witness for ARC-005

- GIVEN the private symbolic archive and exact-origin model
- WHEN preparedUnlinkNeedsRestartBarrierTest, visibleManifestRestartBarrierTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Requirement: ARC-006

When power loss removes unsynchronized publication or admission removal, recovery shall use validated durable roots and exact remaining admissions without replaying any prior effect or lowering conserved watermarks.

### Scenario: bounded executable witness for ARC-006

- GIVEN the private symbolic archive and exact-origin model
- WHEN unsyncedManifestPowerLossTest, unlinkPowerLossRetainsReservationTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Requirement: ARC-007

When an exact live Unknown is released, the writer shall commit its Prepared proof/join, unlink and synchronize the exact admission, and commit Released before exposing a release or anchored delivery attestation.

### Scenario: bounded executable witness for ARC-007

- GIVEN the private symbolic archive and exact-origin model
- WHEN unknownReleaseAndDeliveryTest, noReleasedWithoutProofTest, unanchoredDeliveryRefusedTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Requirement: ARC-008

When late C admission evidence appears, the paired writer shall remove and synchronize an exact already Released/terminal key after the restart barrier and retain a different retired-scope origin as Unknown until its own qualified disposition.

### Scenario: bounded executable witness for ARC-008

- GIVEN the private symbolic archive and exact-origin model
- WHEN lateExactReleasedCAdmissionTest, lateOtherCRemainsBlockedTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Requirement: ARC-009

When migrating a prior store, the system shall verify and retain exact predecessor bytes, all full records, releases, sidecar certificates and independent watermarks before durably activating only paired schema7 producers.

### Scenario: bounded executable witness for ARC-009

- GIVEN the private symbolic archive and exact-origin model
- WHEN migrateBeforeEffectTest, immutableMigrationAndCompactionTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Requirement: ARC-010

When compacting indexes or collecting unreachable temporary/index pages, the system shall preserve all primary evidence and replay maxima and wait for durable replacement-root publication and reader-generation pin release.

### Scenario: bounded executable witness for ARC-010

- GIVEN the private symbolic archive and exact-origin model
- WHEN immutableMigrationAndCompactionTest, historyGrowsHotBoundedTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Requirement: ARC-011

If ownership, type, size, key, hash, generation, lock, quota, inode, counter, I/O or migration validation fails, the system shall refuse the new operation before effect and preserve uncertain live reservations without evicting historical evidence.

### Scenario: bounded executable witness for ARC-011

- GIVEN the private symbolic archive and exact-origin model
- WHEN archiveQuotaRefusesBeforeEffectTest, lockRefusesMutationTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Requirement: ARC-012

When a caller pages historical evidence, the system shall deliver bounded cursor batches and conserve original release anchors while correlating any new delivery certificate to its own current proof and accepted read pair.

### Scenario: bounded executable witness for ARC-012

- GIVEN the private symbolic archive and exact-origin model
- WHEN unknownReleaseAndDeliveryTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Requirement: ARC-013

The filesystem/native implementation shall preserve a common verified writer/admission lock order and shall not await native bind, request or output while holding storage locks.

### Scenario: bounded executable witness for ARC-013

- GIVEN the private symbolic archive and exact-origin model
- WHEN lockRefusesMutationTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Requirement: ARC-014

Where full S15 scaling is claimed, the integrated implementation shall pass sustained same-lifetime archive and migration tests with bounded measured resources and paired filesystem/C/frontend/native acceptance, including independent native grant history and frontend historical-slot limits.

### Scenario: bounded executable witness for ARC-014

- GIVEN the private symbolic archive and exact-origin model
- WHEN historyGrowsHotBoundedTest execute
- THEN their exact assertions SHALL pass and their declared scope SHALL remain partial
- AND actual byte/index/ownership/storage/C/native obligations SHALL remain open

## Required implementation scenarios beyond the prototype

### Scenario: sustained history beyond64 in one lifetime

- GIVEN one unchanged native lifetime and a bounded64 hot reservation/cache/cohort configuration
- WHEN >10,000 distinct legitimate terminal/release/delivery transactions complete with indexed historical lookups
- THEN every original full record, Unknown status, terminal receipt, anchor, predecessor and watermark SHALL remain retrievable
- AND resident memory and per-append page work SHALL remain within separately measured approved budgets
- AND no lifetime reset or record eviction SHALL occur

### Scenario: storage faults and migration

- GIVEN exact frozen v6/sidecar bytes and markers plus live/Prepared admissions
- WHEN failures occur at every file write/fsync/rename, directory fsync, unlink, root activation and reader-pin boundary
- THEN process-visible restart SHALL reestablish barriers before exposure
- AND independent power-loss testing SHALL permit loss only of uncommitted publication without old effect replay
- AND disk/inode exhaustion SHALL refuse new effects before Admission or retain persisted uncertain reservations after later faults

### Scenario: paired late C reader and paged historical delivery

- GIVEN the paired schema7 C/Python lock order and authenticated native proof transport
- WHEN late exact/different retired-scope admissions and historical cursor/delivery retries occur
- THEN exact released keys SHALL not resurrect, different keys SHALL stay reserved, and fresh certificates SHALL preserve original anchor identity
- AND no native bind or output wait SHALL occur while storage locks are held
