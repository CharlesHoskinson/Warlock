module ReceiptRouter exposing (Model, accept, count, empty, register)

{-| Correlation only: retain mappings before the existing broker sends a command.
This module does not allocate native intents or execute/retry operations. Call
accept only for frames delivered by the authenticated broker. Decoding a JSON
frame cannot authenticate its sender. Native observation remains separate.
-}

import Binding as NativeBinding
import Char
import Json.Decode as D
import Menu
import Provider
import UInt64 exposing (Counter)

type alias Context = { lifetime : Counter, epoch : Counter, output : Counter, revision : Counter }
type Operation = Minimize | Restore | Maximize | RestoreGeometry
type alias Intent = { request : Counter, generation : Counter, incarnation : Counter, operation : Operation, context : Context }
type alias Key = { native : NativeBinding.Binding, intent : Intent, protocol : Int }
type alias Entry = { local : Menu.IntentId, binding : Menu.Binding, key : Key }
type Model = Model (List Entry)

empty : Model
empty = Model []

count : Model -> Int
count (Model entries) = List.length entries

safeError : D.Error -> String
safeError error = case error of
    D.Failure reason _ -> String.left 256 reason
    D.Field _ nested -> safeError nested
    D.Index _ nested -> safeError nested
    D.OneOf alternatives -> List.head alternatives |> Maybe.map safeError |> Maybe.withDefault "Invalid native frame"

strict : List String -> D.Decoder a -> D.Decoder a
strict fields body = D.keyValuePairs D.value |> D.andThen (\pairs ->
    if List.sort (List.map Tuple.first pairs)==List.sort fields then body else D.fail "Receipt fields")

positive : D.Decoder Counter
positive = UInt64.decoder |> D.andThen (\value -> if value==UInt64.zero then D.fail "Zero native identity" else D.succeed value)

version : D.Decoder ()
version = D.field "protocolVersion" D.int |> D.andThen (\value -> if value==3 then D.succeed () else D.fail "Native protocol")

effectVersion : D.Decoder ()
effectVersion = D.field "effectProtocol" D.int |> D.andThen (\value -> if List.member value [1,2] then D.succeed () else D.fail "Effect protocol")

kind : String -> D.Decoder ()
kind expected = D.field "kind" D.string |> D.andThen (\value -> if value==expected then D.succeed () else D.fail "Native message kind")

operation : D.Decoder Operation
operation = D.string |> D.andThen (\value -> case value of
    "minimize" -> D.succeed Minimize
    "restore" -> D.succeed Restore
    "maximize" -> D.succeed Maximize
    "restore-geometry" -> D.succeed RestoreGeometry
    _ -> D.fail "Unsupported native menu operation")

context : D.Decoder Context
context = strict ["lifetime","epoch","output","revision"] (D.map4 Context
    (D.field "lifetime" positive) (D.field "epoch" positive) (D.field "output" positive) (D.field "revision" positive))

intent : D.Decoder Intent
intent = strict ["request","generation","incarnation","operation","context"] (D.map5 Intent
    (D.field "request" positive) (D.field "generation" positive) (D.field "incarnation" positive)
    (D.field "operation" operation) (D.field "context" context))

key : D.Decoder Key
key = D.map3 Key (D.field "binding" NativeBinding.decoder) (D.field "intent" intent) (D.field "effectProtocol" D.int)
    |> D.andThen (\value -> if value.protocol==(if value.intent.operation==Maximize || value.intent.operation==RestoreGeometry then 2 else 1) then D.succeed value else D.fail "Operation protocol mismatch")

command : D.Decoder Key
command = strict ["protocolVersion","kind","effectProtocol","binding","intent"]
    (D.map4 (\_ _ _ value -> value) version (kind "window-effect") effectVersion key)

register : Menu.Effect -> Provider.Snapshot -> D.Value -> Model -> Result String Model
register (Menu.Dispatch local binding action) provider value ((Model entries) as model) =
    case D.decodeValue command value of
        Err error -> Err (safeError error)
        Ok native ->
            let expectedOperation = case action of
                    Menu.Minimize -> Just Minimize
                    Menu.Restore -> Just Restore
                    Menu.Maximize -> Just Maximize
                    Menu.RestoreGeometry -> Just RestoreGeometry
                    _ -> Nothing
                eligible = List.any (\item -> item.enabled && item.action==action) (Provider.getItems provider)
            in if binding/=Provider.getBinding provider || not eligible
                || Just native.intent.operation/=expectedOperation
                || native.native/=Provider.nativeBinding provider
                || native.intent.context/=Provider.actionContext action provider
                || native.protocol/=Provider.actionProtocol action
                || native.intent.incarnation/=Provider.incarnation provider then
                    Err "Native command does not match frozen menu action"
               else if List.any (\entry -> entry.local==local || entry.key==native
                    || (entry.key.native==native.native && entry.key.intent.request==native.intent.request)) entries then
                    Err "Native/local operation already registered"
               else if List.length entries>=Menu.maxOutstanding then Err "Receipt registry capacity"
               else Ok (Model ({local=local,binding=binding,key=native}::entries))

utf8Bytes : String -> Int
utf8Bytes = String.foldl (\character total -> let code=Char.toCode character in
    total+(if code<=127 then 1 else if code<=2047 then 2 else if code<=65535 then 3 else 4)) 0

receipt : D.Decoder (Key, Menu.Outcome)
receipt = strict ["protocolVersion","kind","effectProtocol","binding","intent","status","reason","revision","outputGeneration"]
    (D.map8 (\_ _ _ native status reason _ _ -> (native,case status of
        "Committed" -> Menu.Committed
        "Refused" -> Menu.Refusal reason
        _ -> Menu.Uncertain))
        version (kind "effect-outcome") effectVersion key
        (D.field "status" D.string |> D.andThen (\value -> if List.member value ["Committed","Refused","Unknown"] then D.succeed value else D.fail "Native outcome"))
        (D.field "reason" D.string |> D.andThen (\value -> if String.length value<=256 then D.succeed value else D.fail "Native reason bound"))
        (D.field "revision" positive) (D.field "outputGeneration" positive))

accept : String -> Model -> (Model, Maybe Menu.Msg, Maybe String)
accept raw ((Model entries) as model) =
    if String.length raw>16384 || utf8Bytes raw>16384 then (model,Nothing,Just "Native receipt byte bound") else
    case D.decodeString receipt raw of
        Err error -> (model,Nothing,Just (safeError error))
        Ok (native,outcome) ->
            case List.head (List.filter (\entry -> entry.key==native) entries) of
                Nothing -> (model,Nothing,Just "Unknown or mismatched native receipt")
                Just entry ->
                    let next = if outcome==Menu.Uncertain then model else Model (List.filter (\item -> item.local/=entry.local) entries)
                    in (next,Just (Menu.ReceiveFor entry.local entry.binding outcome),Nothing)
