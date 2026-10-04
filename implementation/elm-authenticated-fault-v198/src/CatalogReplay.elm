port module CatalogReplay exposing (main)
import Catalog
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) _ ->
    let snapshot = D.decodeValue (D.field "snapshot" D.value) raw |> Result.mapError D.errorToString |> Result.andThen Catalog.decode
        output = case snapshot of
            Err error -> E.object [("passed",E.bool False),("error",E.string error)]
            Ok catalog ->
                let request = D.decodeValue (D.field "request" UInt64.decoder) raw |> Result.withDefault UInt64.zero
                    entry = D.decodeValue (D.field "entry" D.string) raw |> Result.withDefault ""
                    intent = Catalog.lookup entry catalog |> Maybe.andThen (\value -> Catalog.intent request value.identity catalog)
                in E.object [("passed",E.bool True),("entries",E.list (\value -> E.object [("id",E.string (Catalog.id value.identity)),("name",E.string value.name),("iconHint",E.string value.iconHint)]) (Catalog.entries catalog)),("intent",intent |> Maybe.withDefault E.null)]
    in ((),outgoing output)}
