# Retry exhaustion contract

EARS: When a matching unavailable projection reaches the UInt64 request ceiling, the shell shall enter Exhausted, clear the expected projection and queued retry, emit zero requests, and preserve independent geometry and effect state.

EARS: While disposition is deferred or transport is refused, the shell shall retain the retry without sending it. When disposition resumes with no other fence, it shall issue one fresh projection read. When the backend disconnects, the shell shall revoke the retry and outstanding observation slots.

OpenSpec scenario: Given request counter18446744073709551615, projection58 and independent geometry59, when one matching scene-changed terminal arrives, then Exhausted has no expected projection and no queued retry, geometry59 and effects remain unchanged, and zero commands issue. Duplicate terminals do not revive it.

OpenSpec scenario: Given a deferred matching terminal, when notifications resume, then one fresh read60 issues while geometry59 remains; subsequent duplicate terminals issue zero commands. Disconnect revokes both observation slots.

The Quint counter ceiling60 is an abstraction for finite exhaustion. Compiled Elm checks separately exercise the actual UInt64 ceiling. Native acceptance is separate.
