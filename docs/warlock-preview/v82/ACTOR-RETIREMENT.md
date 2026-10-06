# Next implementation slice: native incarnation retirement

Audit of held GUI81 found lifetime growth in:

- imported-clients.cpp: subjects vector assigns entry by index+1 and never removes.
- imported_admission.hpp: current intent and bounded predecessor maps never remove.
- imported_clients.hpp: frame map never removes a settled job.
- demand.hpp: slots remain after physical and terminal settlement.
- preview_broker.hpp: actor request floors remain after exact acknowledgment.
- preview_uri.hpp/.cpp: registered receiver entry sets only grow.
- preview_delivery.hpp: retained subject map deliberately requires prior membership.

These structures correctly preserve replay and cleanup obligations, but exhaust
the256 cap over a long session. Neither increasing the cap nor erasing on close
establishes bounded, safe turnover. The proposed additive EARS/OpenSpec contract
is openspec/changes/warlock-preview-actor-retirement (3requirements/12scenarios).

The owning plugin17 authority issues incarnation by ++incarnation, refuses
UINT64_MAX exhaustion, and removes old members in forget(). Its snapshot is
mapped-window metadata; absence cannot prove permanent retirement. Implement
a separate authenticated native retirement-state observation first, derived
from the issuance frontier and still-owned members in the same native lifetime.
It is factual lifetime observation, not a new UI policy. Do not make capture
eligible or release any resources from this observation alone.

Then implement nonreused entry serials and removal serialized with receiver,
reader, delivery and demand operations only after exact backend/physical/final
ACK retirement. Refuse replay of absent old serials with a compact frontier;
retain floors for live actors. Carry native facts into the existing Elm owner
without dropping unsettled jobs. Qualify actual turnover beyond256windows and
one neighbor's counter continuity in one host. All original release gates remain.
