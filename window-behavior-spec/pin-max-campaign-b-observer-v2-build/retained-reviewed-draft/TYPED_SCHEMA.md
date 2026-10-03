# Typed observation schema1

The exact draft decoder is `decode_observation.py`; the exact draft producer is `campaign_b_observer.cpp`. Unknown/additional JSON keys, duplicate keys, non-JSON constants, bad UTF-8, bool/int aliases and float/int aliases refuse. Maximum raw response128KiB. Ordinary native floats are finite decimal STRINGS represented with17 significant digits; no JSON numeric coercion is permitted. Pointer tokens are canonical lowercase `0x` hex strings; stable IDs canonical lowercase hexadecimal strings without prefix; generations/operations/sequence/start/observedNs decimal uint64 strings. These are observations of current objects, not durable authority.

Envelope exact fields:
`schema queryKind queryProperties ignoreOwner hitOwner corePolicyBuild compositorPid compositorPgid compositorStart session sequence observedNs ok error body postBody`.

- schema: exact integer1; queryKind exact `metadata` or `windowAtStimulus` matching the requested entry.
- root PID/PGID: positive exact integers; start: positive uint64 string from a single actual /proc/self/stat read; session: actual compositor environment instance signature. Successful responses require equality with the independently selected actual root tuple and reviewed policy SHA.
- observedNs: start-of-call steady-clock represented integer, not frame/presentation/cadence time.
- sequence: monotonically increasing successful-query counter within this loaded plugin instance; exhaustion refuses. Outer caller must reject reuse/regression/reload without fresh binding. It does not establish historical lineage.
- metadata: queryProperties/ignoreOwner/hitOwner allnull.
- windowAtStimulus: queryProperties exact selected mask19/27/147/83/3; ignoreOwner exact selected public tuple only when ignoreSelected true; hitOwner actual returned public tuple ornull.
- successful ok is exacttrue/errornull/body and postBody complete type-exact equal metadata. Partial or changed data never gives oktrue. Failure okfalse/error nonempty retains already completed body/postBody and query evidence; missing phases remain null. Decoder refuses ALL failures without treating preserved partial data as usable.

Metadata exact fields:
`owner mapped hidden acceptsInput noFocus priorityFocus pinned floating internalMode clientMode fullscreenHandler target space workspace output logicalBox visualBox restoreValid restoreGeneration restoreLogicalBox restoreVisualBox restoreFloating restoreLayoutHandled restoreTarget restoreLayoutTarget restoreSpace restoreOrigin restoreManaged ownedUnpinReady group groupMembers cursor coreFocus scroll transfer`.

- owner={address,stableId,pid}; exact requested public tuple; actual mappedtrue. Root receipt/controller's complete incarnation/epoch/generation/member capture remains separately mandatory and is not fabricated here.
- boolean fields exact bool; mode fields exact integers0..3 (native NONE/MAX/FULLSCREEN combinations remain actual stored values).
- fullscreenHandler,target,space,workspace,output positive pointer strings retained/rechecked within the synchronous observation. Not cross-process leases.
- logical/visual/restoration boxes four finite represented scalars. Zero default restore boxes remain raw invalid projection data, not usable geometry. restoreValid requires positive generation and exact current restoreLayoutTarget==target/restoreSpace==space. All existing public projection fields are retained; restoreFloating/restoreLayoutHandled do not authorize native writes.
- group zero pointer iff no members, otherwise complete bounded unique actual public member tuples ≤64; each mapped in producer. cursor two represented scalars. coreFocus nullable publictuple, NOT Seat acceptance.
- scroll null for non-scrolling/floating selected target; otherwise exact fields `owner controller selectedData selectedColumn offset direction columns`. Offset finite decimalstring/direction exactinteger0..3. Columns complete1..64 unique pointer IDs, each exact `{column,width,rows}` with positive represented width. At most256 total unique data/target rows. Each row exact `{data,target,owner,size,layoutBox}`; size positive finite decimalstring. Selected data occurs exactly once in selected column and has current target. Raw controller strip mapping is checked before getters. No private stored restore claim.
- transfer null or exact `{operation,generation,accepted,actualModesKnown,beforeInternal,beforeClient,actualInternal,actualClient,target,space,workspace,output,reason}`. Positive integerstring operation/generation; booleans exact; modes exactinteger0..3; pointer strings (positive if actualModesKnown); bounded nonempty reason. Accepted requires actualModesKnown. A refused outcome stays refused, and a null outcome stays unreached. Comparison against before operation/current receipt/expected destination is a case predicate, not a decoder inference.

The consumer must persist raw bytes before any assertion, validate actual source/root binding before/after, invoke this decoder for the exact query kind, require complete unchanged product capture and actual distinct Seat/protocol evidence where applicable, then use the unchanged strict case predicate. Typed decode is not effect/native/job/cancellation/recovery authority. No acceptance/build/load is claimed by this packet.
