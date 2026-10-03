# Preserved native input-hole failure

The frozen V20 pair captured the actual GTK input-region hole and continued to
paint the peer correctly, but pointer press/release inside the hole reached the
peer instead of the lower owner. The native campaign failed
`inputHolePointerPassesToLowerOwner`; cleanup passed. Evidence is preserved in
`qa/native-1791066638746559471/report.json`, including actual client events.
No native acceptance is claimed. A separate retained V22 input-region experiment
also failed pass-through to a lower maximized window. V23 repairs window selection
in a fresh core derivative and preserves both original failures.
