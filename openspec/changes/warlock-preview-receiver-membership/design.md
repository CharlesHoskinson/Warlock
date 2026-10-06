# Design

The single URI Endpoint serializes membership checks with physical reader access. Extension authenticates the same native receiver and binding, validates every new actor against the Broker own native scope, and commits a bounded union atomically. It preserves epoch and old membership. Each held reader still checks its own binding, token, native source and clock on every read; extension cannot bypass revocation.

ImportedClients supports a bounded inventory of at most256 distinct native actors while retaining its original two-actor default for prior qualification. Actor inventory bounds and physical budgets remain distinct: two live items,128MiB,8 records,4 readers,2 views. Old actor floors and outstanding jobs are retained; new distinct actors receive their own native request domain. Capacity feedback is local scheduling state, not a fabricated job or terminal refusal. Original captured jobs/resources retire through actual producers, reader drain, physical destruction and exact ACK.

The next integration step enrolls actual ordinary subjects from the picker/catalog intersection under a genuine own native capture grant. This packet neither promotes unqualified source eligibility nor wires experimental scope into ordinary captures. Actual owning-ABI native qualification remains required after these changed sources.
