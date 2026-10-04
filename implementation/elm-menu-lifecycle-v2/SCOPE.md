# Next menu lifecycle slice

Fresh derivative of `elm-context-menu-v1`; do not change its frozen evidence.
This is the next independent lane in the active full-desktop build loop. The
shared controller and native bar/popup integration remain owned by their lane.

Target gaps: ELM-RC-022 receipts/uncertainty and ELM-RC-023 bounded resources,
with the existing reliable-authority obligations. This slice does not implement
general popup focus/placement or create a second authoritative desktop model.

Behavioral oracles:

1. Dispatch A, dismiss its menu, complete B, then deliver A's correlated receipt.
   Only A's outstanding entry changes. Repeated or wrong-binding receipts cannot
   alter B, dispatch an effect, or manufacture a native observation.
2. Unknown A remains blocked across dismissal, fresh context, and broker frontend
   rebinding for the same compositor lifetime/session/window incarnation. Only a
   definitive authenticated receipt or separately specified reconciliation can
   release that operation, once.
3. Malformed, duplicate, overcapacity, overlong or unsupported provider data is
   refused without replacing the previously validated context. Actions are typed
   capabilities; titles, labels and arbitrary command strings convey no authority.
4. At the outstanding-operation limit, refuse new dispatch while preserving every
   uncertain entry. Never evict an unresolved command to make space. Bound retained
   invalidations and providers without reopening stale targets or replaying intents.
5. Compile and replay the actual Elm reducer and decoder. Keep native execution
   acceptance separate; a valid synthetic input cannot certify the native producer.

Choose and document finite bounds before implementing. Preserve lossless native
identity strings, no optimistic application state, and no retries on timeout.
Model changes follow the approved modeling workflow if that skill is invoked;
the earlier V1 model is not a proof of this extension.

The subsequent GUI lifecycle slice will exercise outside-click/capture loss and
application-owned menu delegation after agreeing on the integration controller's
native origin, publication, popup lease and widget epoch interfaces. Do not bypass
that controller or its native closed-lease barrier.
