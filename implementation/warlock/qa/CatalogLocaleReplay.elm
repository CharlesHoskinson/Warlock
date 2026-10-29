port module CatalogLocaleReplay exposing (main)
import Catalog
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64
port outgoing : E.Value -> Cmd msg
row entry = E.object [("id",E.string (Catalog.id entry.identity)),("name",E.string entry.name),("genericName",E.string entry.genericName),("keywords",E.list E.string entry.keywords)]
result flags =
    case D.decodeValue (D.map2 Tuple.pair (D.field "snapshot" D.value) (D.field "queries" (D.list D.string))) flags of
        Err problem -> E.object [("ok",E.bool False),("error",E.string (D.errorToString problem))]
        Ok (raw,queries) ->
            case Catalog.decode raw of
                Err problem -> E.object [("ok",E.bool False),("error",E.string problem)]
                Ok snapshot ->
                    let scope=Catalog.scope snapshot
                        query text=E.object [("query",E.string text),("entries",E.list row (Catalog.search text snapshot))]
                    in E.object [("ok",E.bool True),("lifetime",E.string (UInt64.string scope.lifetime)),("generation",E.string (UInt64.string scope.generation)),("entries",E.list row (Catalog.entries snapshot)),("results",E.list query queries)]
main : Program D.Value () Never
main = Platform.worker {init=\flags -> ((),outgoing (result flags)),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
