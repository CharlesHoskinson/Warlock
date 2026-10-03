# Binding order clarification

The original contract's bootstrap lifetime binding is raw evidence, not the model Bind event. The first authorized Bind contains the complete RuntimeLease owner token after actual lease creation. An authorized owner token is never augmented or replaced. The runtime records source/bootstrap fields with usable=false and rawEvidenceOnly=true.

Source-bearing methods decorated by contextlib are inspected through their actual __wrapped__ business function. Generated dataclass methods and standard-library supplied methods are excluded from candidate business-source enumeration; linked product classes and their actual event/prepare/commit/native/context callbacks are checked separately.

## Fresh restart data probe

The frozen V20 recovery query desktop uses the original Keeper-owned read-only
helpers before NativeFactory.bind_journal creates its new ReadonlyIPC. A restart
with no new actor otherwise has zero rows. The collector requires a real current
nonempty ledger, so each observer performs one explicit QA service-owned
OwnedCommands fixed `hyprctl clients -j` observation after complete lease/module
binding and RuntimeService construction, before service.run/API listening. It
uses the existing 0.6 second absolute request bound, actual adapter peer/EOF/FD/
source/lease/durable guards and returned byte hash. No helper/native effect or
settlement decision follows from these bytes. This is the model's existing
Queries event with a genuinely registered current batch, not a fabricated row or
old-data reuse. Original baseline and fault oracles/deadlines remain exact.
