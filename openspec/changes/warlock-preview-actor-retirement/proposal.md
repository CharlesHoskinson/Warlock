# Retire permanently closed preview actors

The current dynamic bridge keeps every introduced subject in its C vector,
ImportedIntentLedger, ImportedClients frame map, Coordinator slots, Broker
actors, receiver membership and ReceiptDelivery subject map. The256-subject
limit therefore bounds lifetime introductions rather than concurrent owners.

Add authenticated native incarnation-retirement evidence, then reclaim these
records together only after their physical and terminal obligations are empty.
Use monotonically issued entry serials to refuse reused old entry identifiers
without an unbounded tombstone map. Native incarnation identity must remain
permanent within the compositor lifetime; catalog omission is insufficient.
The existing immutable Elm policy receives exact typed retirement facts and
retains any unsettled work until its original proofs arrive.

This is proposed implementation work, not accepted runtime behavior. Original
source/ABI identities, deadlines, request floors and S01–S16 release gates stay
unchanged. The existing fixed two-subject path retains its behavior.
