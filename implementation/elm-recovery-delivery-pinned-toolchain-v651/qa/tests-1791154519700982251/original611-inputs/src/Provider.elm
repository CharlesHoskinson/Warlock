module Provider exposing
    ( NativeContext, Snapshot, capabilityGeneration, decode, decodeString, decoder
    , getBinding, getItems, incarnation, menuBinding, nativeBinding, nativeContext
    , providerId, presentationScope, title, toOpen, withGeometry, actionContext, actionProtocol, geometryObservation
    )

{-| Validated, bounded protocol-1 window-menu provider data.

This is a decoder, not a capability producer or native authority. It admits only
the closed window-action vocabulary. Application, Files, selection and background
providers require separate declared schemas; their fields/actions are rejected.
Menu authority includes the complete native binding and provider generations;
window identity uses lifetime/session/incarnation and survives frontend rebinding.
JSON parsing does not retain duplicate raw object keys; this decoder does not
claim to detect those. It rejects duplicate row IDs, typed actions and capability
entries after parsing. The transport allows 64 rows; this first window vocabulary
has only nine distinct typed actions (including both AlwaysOnTop boolean values).
-}

import Binding as NativeBinding
import Char
import Json.Decode as D
import Json.Encode as E
import Menu
import GeometryProjection
import Set
import UInt64 exposing (Counter)


type Snapshot
    = Snapshot
        { binding : Menu.Binding
        , items : List Menu.Item
        , title : String
        , providerId : Counter
        , capabilityGeneration : Counter
        , context : Context
        , incarnation : Counter
        , geometry : Maybe GeometryProjection.Snapshot
        }


type alias Context =
    { native : NativeBinding.Binding
    , lifetime : Counter
    , session : Counter
    , frontend : Counter
    , revision : Counter
    , outputId : Counter
    , outputGeneration : Counter
    }


type alias NativeContext =
    { lifetime : Counter, epoch : Counter, output : Counter, revision : Counter }


type alias Target =
    { lifetime : Counter, session : Counter, incarnation : Counter }


type alias Entry =
    { id : String, item : Menu.Item, kind : String }


type alias Raw =
    { provider : Counter
    , capabilitiesGeneration : Counter
    , context : Context
    , target : Target
    , heading : String
    , capabilities : List String
    , entries : List Entry
    }


maximumBytes : Int
maximumBytes =
    16384


utf8Bytes : String -> Int
utf8Bytes value =
    String.foldl
        (\character total ->
            let
                code = Char.toCode character
            in
            total + (if code <= 127 then 1 else if code <= 2047 then 2 else if code <= 65535 then 3 else 4)
        )
        0
        value


validUnicode : String -> Bool
validUnicode value =
    case String.uncons value of
        Nothing -> True
        Just (character, rest) ->
            let
                units = String.fromChar character
                code = Char.toCode character
                valid =
                    if String.length units == 1 then
                        code < 55296 || code > 57343
                    else if String.length units == 2 then
                        -- Elm combines a high surrogate before validating its
                        -- partner. Check that second UTF-16 unit independently.
                        case String.uncons (String.dropLeft 1 units) of
                            Just (second, _) ->
                                let low = Char.toCode second in
                                low >= 56320 && low <= 57343 && code >= 65536 && code <= 1114111
                            Nothing -> False
                    else
                        -- A terminal high surrogate can become high+"undefined"
                        -- in Elm's kernel; Char.toCode alone cannot reject it.
                        False
            in
            if valid then validUnicode rest else False


strict : List String -> D.Decoder a -> D.Decoder a
strict fields body =
    D.keyValuePairs D.value
        |> D.andThen
            (\pairs ->
                if List.sort (List.map Tuple.first pairs) == List.sort fields then body
                else D.fail "Unexpected provider fields"
            )


nonzero : D.Decoder Counter
nonzero =
    UInt64.decoder
        |> D.andThen (\counter -> if counter == UInt64.zero then D.fail "Zero provider identity" else D.succeed counter)


boundedList : Int -> D.Decoder a -> D.Decoder (List a)
boundedList limit body =
    -- JSON values arrive allocated; this checks the first forbidden index before
    -- decoding per-row records. The string entry point also bounds raw bytes.
    D.value |> D.andThen
        (\value ->
            case D.decodeValue (D.index limit D.value) value of
                Ok _ -> D.fail "Provider array bound"
                Err _ -> D.list body
        )


textDecoder : D.Decoder String
textDecoder =
    D.string |> D.andThen
        (\value ->
            let
                forbidden character =
                    let code = Char.toCode character in
                    code < 32 || (code >= 127 && code <= 159) || (code >= 55296 && code <= 57343)
            in
            if String.length value > 256 || not (validUnicode value) || String.isEmpty (String.trim value) || String.any forbidden value then
                D.fail "Invalid provider label/title"
            else D.succeed value
        )


nativeDecoder : D.Decoder NativeBinding.Binding
nativeDecoder =
    D.map3
        (\lifetime session frontend -> E.object
            [ ("lifetime", E.string (UInt64.string lifetime))
            , ("session", E.string (UInt64.string session))
            , ("frontend", E.string (UInt64.string frontend))
            ])
        (D.field "lifetime" nonzero)
        (D.field "session" nonzero)
        (D.field "frontend" nonzero)
        |> D.andThen
            (\value -> case D.decodeValue NativeBinding.decoder value of
                Ok native -> D.succeed native
                Err _ -> D.fail "Native provider binding"
            )


contextDecoder : D.Decoder Context
contextDecoder =
    strict ["lifetime", "session", "frontend", "revision", "outputId", "outputGeneration"]
        (D.map7 Context nativeDecoder
            (D.field "lifetime" nonzero)
            (D.field "session" nonzero)
            (D.field "frontend" nonzero)
            (D.field "revision" nonzero)
            (D.field "outputId" nonzero)
            (D.field "outputGeneration" nonzero))


targetDecoder : D.Decoder Target
targetDecoder =
    strict ["lifetime", "session", "incarnation"]
        (D.map3 Target (D.field "lifetime" nonzero)
            (D.field "session" nonzero) (D.field "incarnation" nonzero))


actionKinds : List String
actionKinds =
    ["Restore", "Minimize", "Move", "Size", "Maximize", "Close", "ExitFullscreen", "AlwaysOnTop"]


kindDecoder : D.Decoder String
kindDecoder =
    D.string |> D.andThen
        (\kind -> if List.member kind actionKinds then D.succeed kind else D.fail "Unsupported window action")


actionDecoder : D.Decoder ( String, Menu.Action )
actionDecoder =
    D.field "kind" kindDecoder |> D.andThen
        (\kind ->
            let
                plain action = strict ["kind"] (D.succeed (kind, action))
            in
            case kind of
                "Restore" -> plain Menu.Restore
                "Minimize" -> plain Menu.Minimize
                "Move" -> plain Menu.Move
                "Size" -> plain Menu.Size
                "Maximize" -> plain Menu.Maximize
                "Close" -> plain Menu.Close
                "ExitFullscreen" -> plain Menu.ExitFullscreen
                "AlwaysOnTop" -> strict ["kind", "checked"]
                    (D.map (\checked -> (kind, Menu.AlwaysOnTop checked)) (D.field "checked" D.bool))
                _ -> D.fail "Unsupported window action"
        )


entryDecoder : D.Decoder Entry
entryDecoder =
    strict ["id", "label", "enabled", "action"]
        (D.map4
            (\identity label enabled (kind, action) ->
                { id = UInt64.string identity
                , item = {label = label, enabled = enabled, action = action}
                , kind = kind
                })
            (D.field "id" nonzero)
            (D.field "label" textDecoder)
            (D.field "enabled" D.bool)
            (D.field "action" actionDecoder))


envelopeDecoder : D.Decoder Snapshot
envelopeDecoder =
    let
        version = D.field "protocolVersion" D.int |> D.andThen
            (\number -> if number == 1 then D.succeed () else D.fail "Provider protocol version")
        body = D.map7 Raw
            (D.field "providerId" nonzero)
            (D.field "capabilityGeneration" nonzero)
            (D.field "binding" contextDecoder)
            (D.field "target" targetDecoder)
            (D.field "title" textDecoder)
            (D.field "capabilities" (boundedList 8 kindDecoder))
            (D.field "items" (boundedList 64 entryDecoder))
    in
    strict ["protocolVersion", "providerId", "capabilityGeneration", "binding", "target", "title", "capabilities", "items"]
        (D.map2 (\_ raw -> raw) version body)
        |> D.andThen
            (\raw ->
                let
                    identities = List.map .id raw.entries
                    coherent = raw.target.lifetime == raw.context.lifetime && raw.target.session == raw.context.session
                    duplicateIds = List.length identities /= Set.size (Set.fromList identities)
                    actions = List.map (.item >> .action) raw.entries
                    uniqueActions = List.foldl (\action seen -> if List.member action seen then seen else action :: seen) [] actions
                    duplicateActions = List.length actions /= List.length uniqueActions
                    duplicateCapabilities = List.length raw.capabilities /= Set.size (Set.fromList raw.capabilities)
                    unsupportedEnabled = List.any (\entry -> entry.item.enabled && not (List.member entry.kind raw.capabilities)) raw.entries
                    authority = E.encode 0 (E.list identity
                        [ NativeBinding.encode raw.context.native
                        , E.string (UInt64.string raw.provider)
                        , E.string (UInt64.string raw.capabilitiesGeneration)
                        ])
                in
                if not coherent || duplicateIds || duplicateActions || duplicateCapabilities || unsupportedEnabled then
                    D.fail "Incoherent provider identity/capabilities"
                else
                    D.succeed (Snapshot
                        { binding = Menu.binding
                            { authority = authority
                            , revision = UInt64.string raw.context.revision
                            , output = Menu.outputId (UInt64.string raw.context.outputId)
                            , outputGeneration = UInt64.string raw.context.outputGeneration
                            , target = Menu.Window (Menu.windowId (NativeBinding.authorityIdentity raw.context.native) (UInt64.string raw.target.incarnation))
                            }
                        , items = List.map .item raw.entries
                        , title = raw.heading
                        , providerId = raw.provider
                        , capabilityGeneration = raw.capabilitiesGeneration
                        , context = raw.context
                        , incarnation = raw.target.incarnation
                        , geometry = Nothing
                        })
            )


decoder : D.Decoder Snapshot
decoder =
    -- Value callers cannot recover the original wire spacing/escapes. Bound the
    -- canonical encoded value too; decodeString additionally checks raw UTF-8.
    D.value |> D.andThen
        (\value -> envelopeDecoder |> D.andThen
            (\validated ->
                -- Reject unknown/deep/cyclic shapes through the closed bounded
                -- decoder before serializing any accepted incoming JSON value.
                if utf8Bytes (E.encode 0 value) > maximumBytes then
                    D.fail "Provider encoded byte bound"
                else D.succeed validated))


decode : D.Value -> Result String Snapshot
decode value =
    D.decodeValue decoder value |> Result.mapError errorSummary


errorSummary : D.Error -> String
errorSummary error =
    -- Json.Decode.errorToString serializes the rejected value. A malformed port
    -- object can be cyclic/deep, so public entry points omit that value entirely.
    case error of
        D.Field field nested -> "Provider field " ++ field ++ ": " ++ errorSummary nested
        D.Index index nested -> "Provider index " ++ String.fromInt index ++ ": " ++ errorSummary nested
        D.OneOf _ -> "Provider alternatives rejected"
        D.Failure reason _ -> String.left 256 reason


decodeString : String -> Result String Snapshot
decodeString value =
    if String.length value > maximumBytes || not (validUnicode value) || utf8Bytes value > maximumBytes then Err "Provider raw UTF-8 byte bound"
    else D.decodeString decoder value |> Result.mapError errorSummary


getBinding : Snapshot -> Menu.Binding
getBinding (Snapshot value) = value.binding


menuBinding : Snapshot -> Menu.Binding
menuBinding = getBinding


nativeBinding : Snapshot -> NativeBinding.Binding
nativeBinding (Snapshot value) = value.context.native


nativeContext : Snapshot -> NativeContext
nativeContext (Snapshot value) =
    -- In this window-provider protocol outputGeneration is the native effect
    -- context's output version. outputId identifies the presentation output;
    -- it is never substituted for that version at the native commit boundary.
    { lifetime = value.context.lifetime
    , epoch = value.context.frontend
    , output = value.context.outputGeneration
    , revision = value.context.revision
    }


incarnation : Snapshot -> Counter
incarnation (Snapshot value) = value.incarnation


getItems : Snapshot -> List Menu.Item
getItems (Snapshot value) = value.items


title : Snapshot -> String
title (Snapshot value) = value.title


providerId : Snapshot -> String
providerId (Snapshot value) = UInt64.string value.providerId


capabilityGeneration : Snapshot -> String
capabilityGeneration (Snapshot value) = UInt64.string value.capabilityGeneration


toOpen : Snapshot -> Menu.Msg
toOpen (Snapshot value) = Menu.Open value.binding value.items


presentationScope : Snapshot -> {outputId : Counter, providerId : Counter}
presentationScope (Snapshot value) =
    {outputId=value.context.outputId,providerId=value.providerId}

geometryObservation : Snapshot -> Maybe GeometryProjection.Snapshot
geometryObservation (Snapshot state) = state.geometry

actionProtocol : Menu.Action -> Int
actionProtocol action = if action==Menu.Maximize || action==Menu.RestoreGeometry then 2 else 1

actionContext : Menu.Action -> Snapshot -> NativeContext
actionContext action ((Snapshot state) as snapshot) =
    if actionProtocol action==2 then state.geometry |> Maybe.map .context |> Maybe.withDefault (nativeContext snapshot) else nativeContext snapshot

withGeometry : GeometryProjection.Capabilities -> GeometryProjection.Snapshot -> Snapshot -> Result String Snapshot
withGeometry caps observed ((Snapshot state) as snapshot) =
    if observed.binding/=state.context.native || observed.context.output/=state.context.outputGeneration then Err "Geometry/legacy authority mismatch" else
    case GeometryProjection.window state.incarnation observed of
        Nothing -> Err "Geometry target missing"
        Just window ->
            let legacyRestore=List.filter (\item -> item.action==Menu.Restore) state.items |> List.head
                legacyMinimize=List.filter (\item -> item.action==Menu.Minimize) state.items |> List.head
                supported op=caps.effects && List.member op caps.operations
                restoreGeometry=supported "restore-geometry" && not window.minimized
                ready=List.any .enabled state.items && not observed.blocked && window.eligible && not window.fixedSize
                restore=if restoreGeometry then {label="Restore",action=Menu.RestoreGeometry,enabled=ready && window.restoreGeometry && window.nativeMode==GeometryProjection.Maximized && window.placementKnown}
                    else Maybe.withDefault {label="Restore",action=Menu.Restore,enabled=False} legacyRestore
                minimize=Maybe.withDefault {label="Minimize",action=Menu.Minimize,enabled=False} legacyMinimize
                items=[restore,minimize]++(if supported "maximize" then [{label="Maximize",action=Menu.Maximize,enabled=ready && window.maximize && not window.minimized && window.nativeMode==GeometryProjection.Ordinary}] else [])
                authority=E.encode 0 (E.list identity [E.string (E.encode 0 (NativeBinding.encode state.context.native) ++ ":" ++ UInt64.string state.providerId ++ ":" ++ UInt64.string state.capabilityGeneration ++ ":" ++ UInt64.string state.context.revision),E.string (UInt64.string observed.context.revision),E.string (UInt64.string observed.context.output),E.list E.string caps.operations])
            in Ok (Snapshot {state|items=items,geometry=Just observed,binding=Menu.binding {authority=authority,revision=UInt64.string observed.context.revision,output=Menu.outputId (UInt64.string state.context.outputId),outputGeneration=UInt64.string observed.context.output,target=Menu.Window (Menu.windowId (NativeBinding.authorityIdentity state.context.native) (UInt64.string state.incarnation))}})
