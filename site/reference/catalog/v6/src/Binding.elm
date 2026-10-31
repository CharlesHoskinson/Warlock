module Binding exposing (Binding, decoder, encode, replaces, matchesContext, authorityIdentity, sameLifetime)

import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type Binding = Binding Counter Counter Counter
nonzero : D.Decoder Counter
nonzero = UInt64.decoder |> D.andThen (\v -> if v == UInt64.zero then D.fail "Zero identity" else D.succeed v)
decoder : D.Decoder Binding
decoder = D.keyValuePairs D.value |> D.andThen (\fields ->
    if List.sort (List.map Tuple.first fields) /= ["frontend","lifetime","session"] then D.fail "Binding fields"
    else D.map3 Binding (D.field "lifetime" nonzero) (D.field "session" nonzero) (D.field "frontend" nonzero))
encode : Binding -> E.Value
encode (Binding lifetime session frontend) = E.object [("lifetime",E.string (UInt64.string lifetime)),("session",E.string (UInt64.string session)),("frontend",E.string (UInt64.string frontend))]
replaces : Binding -> Binding -> Bool
replaces (Binding life session frontend) (Binding oldLife oldSession oldFrontend) = life /= oldLife || session /= oldSession || UInt64.compare frontend oldFrontend == GT
matchesContext : Counter -> Counter -> Binding -> Bool
matchesContext life epoch (Binding lifetime _ frontend) = life == lifetime && epoch == frontend

authorityIdentity : Binding -> String
authorityIdentity (Binding lifetime _ _) = UInt64.string lifetime

sameLifetime : Counter -> Binding -> Bool
sameLifetime life (Binding lifetime _ _) = life == lifetime
