port module FeedbackContextReplay exposing (main)

{-| ELM-UI-007 component fixture. This calls the owning Desktop query update and
Surface projection; typed window receipts are fixture state, not native evidence.
Seed 20261031 generates 96 bounded query/publication variants. No native effect
interpreter or second policy implementation is present in this worker.
-}

import Binding
import Catalog
import Desktop
import Effects
import Json.Decode as D
import Json.Encode as E
import Platform
import PointerOwnership as Pointer
import Shell
import Surface
import SurfaceRenderer
import UInt64


port outgoing : E.Value -> Cmd msg


main : Program () () Never
main =
    Platform.worker
        { init = \_ -> ( (), outgoing (E.list identity (fixedRows ++ generatedRows ++ lifecycleRows)) )
        , update = \_ state -> ( state, Cmd.none )
        , subscriptions = \_ -> Sub.none
        }


one : UInt64.Counter
one =
    UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero


counter : String -> UInt64.Counter
counter value =
    D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero


binding : Maybe Binding.Binding
binding =
    D.decodeValue Binding.decoder
        (E.object [ ( "lifetime", E.string "1" ), ( "session", E.string "1" ), ( "frontend", E.string "1" ) ])
        |> Result.toMaybe


pointer : Pointer.Model
pointer =
    case binding of
        Nothing ->
            Pointer.initial

        Just current ->
            D.decodeValue Pointer.decoder
                (E.object
                    [ ( "protocolVersion", E.int 3 )
                    , ( "kind", E.string "pointer-ownership" )
                    , ( "ownershipProtocol", E.int 1 )
                    , ( "binding", Binding.encode current )
                    , ( "requestId", E.string "1" )
                    , ( "serial", E.string "1" )
                    , ( "state", E.string "idle" )
                    , ( "owner", E.null )
                    ]
                )
                |> Result.map (\snapshot -> Pointer.receive (Just current) snapshot Pointer.initial)
                |> Result.withDefault Pointer.initial


catalog : Maybe Catalog.Snapshot
catalog =
    Catalog.decode
        (E.object
            [ ( "catalogProtocol", E.int 1 )
            , ( "lifetime", E.string "1" )
            , ( "generation", E.string "1" )
            , ( "entries"
              , E.list identity
                    [ E.object
                        [ ( "id", E.string "editor.desktop" )
                        , ( "name", E.string "Editor" )
                        , ( "iconHint", E.string "editor" )
                        , ( "wmclass", E.string "Editor" )
                        ]
                    ]
              )
            ]
        )
        |> Result.toMaybe


type alias Context =
    { name : String, query : String, guidance : String }


contexts : List Context
contexts =
    [ { name = "loading", query = "Ed", guidance = "Loading applications…" }
    , { name = "unavailable", query = "retained draft", guidance = "Application list unavailable. Refresh to try again." }
    , { name = "no-match", query = "no-such-application", guidance = "No matching applications. Change your search or Refresh." }
    , { name = "blank", query = "", guidance = "Type to search applications." }
    , { name = "matching", query = "Ed", guidance = "Choose a matching application." }
    ]


states : List (Maybe Effects.Status)
states =
    [ Just Effects.Pending, Just Effects.Refused, Just Effects.Unknown, Just Effects.Cancelled, Just Effects.Committed, Nothing ]


stateName : Maybe Effects.Status -> String
stateName status =
    status |> Maybe.map Effects.statusName |> Maybe.withDefault "None"


fixedRows : List E.Value
fixedRows =
    List.concatMap
        (\open ->
            List.concatMap
                (\context -> List.map (\status -> row False one open context status) states)
                contexts
        )
        [ True, False ]


generatedRows : List E.Value
generatedRows =
    let
        next seed =
            modBy 2147483647 (seed * 48271)

        walk remaining seed rows =
            if remaining == 0 then
                List.reverse rows

            else
                let
                    value =
                        next seed

                    context =
                        { name = "no-match"
                        , query = "draft-" ++ String.fromInt value ++ "-λ"
                        , guidance = "No matching applications. Change your search or Refresh."
                        }

                    status =
                        List.drop (modBy (List.length states) value) states |> List.head |> Maybe.withDefault Nothing

                    publication =
                        counter (String.fromInt (remaining + 10))
                in
                walk (remaining - 1) value (row True publication True context status :: rows)
    in
    walk 96 20261031 []


lifecycleRows : List E.Value
lifecycleRows =
    let
        matching =
            { name = "matching", query = "Ed", guidance = "Choose a matching application." }

        longQuery =
            { name = "long-query", query = String.repeat 256 "x", guidance = "No matching applications. Change your search or Refresh." }
    in
    [ rowWith True False False one True matching (Just Effects.Committed)
    , rowWith True False False one True matching Nothing
    , rowWith False True False one True matching (Just Effects.Unknown)
    , row False one True longQuery (Just Effects.Unknown)
    ]


row : Bool -> UInt64.Counter -> Bool -> Context -> Maybe Effects.Status -> E.Value
row =
    rowWith False False


rowWith : Bool -> Bool -> Bool -> UInt64.Counter -> Bool -> Context -> Maybe Effects.Status -> E.Value
rowWith older detached generated publication open context status =
    let
        intent =
            { request = if older then counter "2" else one
            , generation = counter "9007199254740993"
            , incarnation = counter "18446744073709551614"
            , operation = Effects.Restore
            , context = { lifetime = one, epoch = one, output = one, revision = one }
            }

        transaction =
            status |> Maybe.map (\value -> { intent = intent, status = value, effectProtocol = 1 })

        effects =
            { connected = not detached
            , observed = Nothing
            , request = intent.request
            , generation = intent.generation
            , transaction = transaction
            , unresolved =
                if older then
                    [ { intent = { intent | request = one, generation = counter "9007199254740992" }, status = Effects.Unknown, effectProtocol = 1 } ]

                else
                    transaction |> Maybe.map (\value -> if List.member value.status [ Effects.Pending, Effects.Unknown ] then [ value ] else []) |> Maybe.withDefault []
            }

        base =
            Desktop.initial

        windows =
            base.windows

        shell =
            windows.shell

        model =
            { base
                | windows = { windows | shell = { shell | binding = if detached then Nothing else binding, effects = effects, phase = if detached then Shell.Detached else Shell.Ready, notice = "Ready" } }
                , open = open
                , query = if open then "previous query" else context.query
                , applications = if context.name == "unavailable" then Nothing else catalog
                , expected = if context.name == "loading" then Just one else Nothing
                , presentation = Just publication
                , pointer = pointer
            }

        priorStamp =
            Desktop.capture model

        ( edited, commands ) =
            if open then
                priorStamp |> Maybe.map (\stamp -> Desktop.update (Desktop.SearchQuery stamp context.query) model) |> Maybe.withDefault ( model, [] )

            else
                ( model, [] )

        ( stale, staleCommands ) =
            if open then
                priorStamp |> Maybe.map (\stamp -> Desktop.update (Desktop.SearchQuery stamp "untrusted stale query") edited) |> Maybe.withDefault ( edited, [] )

            else
                ( edited, [] )

        frame =
            Surface.packet publication one edited

        closedFrame =
            Surface.packet publication one { edited | open = False }

        decoded =
            case SurfaceRenderer.decode frame of
                Ok _ ->
                    True

                Err _ ->
                    False

        feedback =
            if older then
                Just "Window action awaits native confirmation. Refresh status only reads observations; it does not retry the action."

            else case status of
                Just Effects.Pending ->
                    Just "Restore: applying to selected window…"

                Just Effects.Refused ->
                    Just "Restore: refused for selected window. Refresh window status, then choose again."

                Just Effects.Unknown ->
                    Just ("Restore: not confirmed for selected window." ++ (if detached then " Reconnect to read window status; the action will not be repeated." else " Check your windows; Refresh only reads status."))

                Just Effects.Cancelled ->
                    Just "Restore: cancelled for selected window."

                _ ->
                    Nothing
    in
    E.object
        [ ( "name", E.string ((if older then "retained" else if detached then "detached" else if generated then "generated-" ++ UInt64.string publication else if open then "open" else "closed") ++ "-" ++ context.name ++ "-" ++ stateName status) )
        , ( "status", E.string (stateName status) )
        , ( "state", E.string (stateName status) )
        , ( "open", E.bool open )
        , ( "generated", E.bool generated )
        , ( "older", E.bool older )
        , ( "detached", E.bool detached )
        , ( "context", E.string context.name )
        , ( "expectedGuidance", E.string context.guidance )
        , ( "guidance", E.string context.guidance )
        , ( "expectedQuery", E.string context.query )
        , ( "query", E.string context.query )
        , ( "feedback", feedback |> Maybe.map E.string |> Maybe.withDefault E.null )
        , ( "forbidden", E.list E.string (if feedback == Nothing then [ "Restore: applying", "Restore: not confirmed", "Restore: refused", "Restore: cancelled" ] else []) )
        , ( "setupReady", E.bool (binding /= Nothing && catalog /= Nothing && priorStamp /= Nothing && not (Pointer.blocked binding model.pointer) && one /= UInt64.zero && intent.generation /= UInt64.zero && intent.incarnation /= UInt64.zero) )
        , ( "queryEdited", E.bool (edited.query == context.query && (not open || model.query /= edited.query)) )
        , ( "frameDecodes", E.bool decoded )
        , ( "frame", frame )
        , ( "repeatFrame", Surface.packet publication one edited )
        , ( "closedFrame", closedFrame )
        , ( "queryEffects", E.int (List.length commands) )
        , ( "staleQuery", E.string stale.query )
        , ( "staleEffectsCount", E.int (List.length staleCommands) )
        , ( "effectsBeforeQuery", Effects.encode model.windows.shell.effects )
        , ( "effectsAfterQuery", Effects.encode edited.windows.shell.effects )
        , ( "effectsAfterStale", Effects.encode stale.windows.shell.effects )
        , ( "unresolvedBeforeQuery", encodeTransactions model.windows.shell.effects.unresolved )
        , ( "unresolvedAfterQuery", encodeTransactions edited.windows.shell.effects.unresolved )
        , ( "unresolvedAfterStale", encodeTransactions stale.windows.shell.effects.unresolved )
        , ( "intent", Effects.encodeIntent intent )
        , ( "unresolved", E.int (List.length edited.windows.shell.effects.unresolved) )
        ]


encodeTransactions : List Effects.Transaction -> E.Value
encodeTransactions =
    E.list (\transaction -> E.object [ ( "intent", Effects.encodeIntent transaction.intent ), ( "status", E.string (Effects.statusName transaction.status) ), ( "effectProtocol", E.int transaction.effectProtocol ) ])
