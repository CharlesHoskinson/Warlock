module MenuBridge exposing
    ( Model, UpdateResult, connectionLost, currentProvider, guardedAct, initial, menuEvent
    , menuSnapshot, nativeFrame, open, receiptCount
    )

{-| Adapt validated window menus to the one existing Shell engine.

This adapter never allocates native request IDs, creates native outcomes, or
manufactures observed application state. Successful dispatch first registers the
engine-generated command and closes the presentation menu while retaining its
operation ledger. The caller must publish that closed popup and the returned
command together in the native controller's atomic surface-commit; sending the
command while a logical native popup remains open is not supported.

Call nativeFrame only for authenticated broker frames, before/independently of
Shell's current transaction processing. Every controller Shell.Act route,
including taskbar actions, must use guardedAct so Unknown cannot be bypassed.
-}

import ActionProjection
import Binding as NativeBinding
import Effects
import Json.Decode as D
import Json.Encode as E
import Menu
import Provider
import ReceiptRouter
import Shell
import UInt64 exposing (Counter)


type alias CapturedProvider =
    { snapshot : Provider.Snapshot, stamp : Shell.Stamp }


type Model
    = Model
        { menu : Menu.Model
        , router : ReceiptRouter.Model
        , provider : Maybe CapturedProvider
        }


type alias UpdateResult =
    { bridge : Model
    , shell : Shell.Model
    , effects : List Shell.Effect
    , error : Maybe String
    }


answer : Model -> Shell.Model -> List Shell.Effect -> Maybe String -> UpdateResult
answer bridge shell effects error =
    { bridge = bridge, shell = shell, effects = effects, error = error }


initial : Model
initial =
    Model { menu = Menu.init, router = ReceiptRouter.empty, provider = Nothing }


menuSnapshot : Model -> Menu.Snapshot
menuSnapshot (Model state) =
    Menu.snapshot state.menu


receiptCount : Model -> Int
receiptCount (Model state) =
    ReceiptRouter.count state.router


currentProvider : Model -> Maybe Provider.Snapshot
currentProvider (Model state) =
    Maybe.map .snapshot state.provider


providerStamp : Provider.Snapshot -> Result String Shell.Stamp
providerStamp provider =
    let
        context = Provider.nativeContext provider
    in
    D.decodeValue Shell.stampDecoder
        (E.object
            [ ( "binding", NativeBinding.encode (Provider.nativeBinding provider) )
            , ( "output", E.string (UInt64.string context.output) )
            , ( "revision", E.string (UInt64.string context.revision) )
            ]
        )
        |> Result.mapError (\_ -> "Invalid native menu stamp")


open : Provider.Snapshot -> Model -> Model
open provider ((Model state) as model) =
    case providerStamp provider of
        Err _ -> model
        Ok stamp ->
            let
                before = Menu.snapshot state.menu
                ( menu, _ ) = Menu.update (Provider.toOpen provider) state.menu
            in
            if (Menu.snapshot menu).menu == before.menu then
                model
            else
                Model { state | menu = menu, provider = Just { snapshot = provider, stamp = stamp } }


refuse : Menu.IntentId -> Menu.Binding -> String -> Model -> Model
refuse local binding reason (Model state) =
    let ( menu, _ ) = Menu.update (Menu.ReceiveFor local binding (Menu.Refusal reason)) state.menu
    in Model { state | menu = menu }


operation : Menu.Action -> Maybe Effects.Operation
operation action =
    case action of
        Menu.Minimize -> Just Effects.Minimize
        Menu.Restore -> Just Effects.Restore
        _ -> Nothing


providerMatches : CapturedProvider -> Shell.Model -> Bool
providerMatches captured shell =
    shell.binding == Just (Provider.nativeBinding captured.snapshot)
        && Shell.capture shell == Just captured.stamp
        && (shell.effects.observed |> Maybe.map .context) == Just (Provider.nativeContext captured.snapshot)
        && (shell.effects.observed |> Maybe.andThen
            (\observed -> ActionProjection.rootOf (Provider.incarnation captured.snapshot) observed.scene))
            == Just (Provider.incarnation captured.snapshot)


blockedFor : Counter -> Shell.Model -> Model -> Bool
blockedFor incarnation shell (Model state) =
    let
        root = shell.effects.observed |> Maybe.andThen (\observed -> ActionProjection.rootOf incarnation observed.scene)
        blocked =
            case ( shell.binding, root ) of
                ( Just native, Just family ) ->
                    Menu.hasOutstandingFor
                        (Menu.windowId (NativeBinding.authorityIdentity native) (UInt64.string family))
                        state.menu
                _ -> (Menu.snapshot state.menu).outstanding > 0
    in blocked


guardedAct : Shell.Stamp -> Effects.Operation -> Counter -> Shell.Model -> Model -> ( Shell.Model, List Shell.Effect, Maybe String )
guardedAct stamp action incarnation shell model =
    let blocked = False
    in
    if blocked then
        ( shell, [], Just "A menu operation for this window family awaits reconciliation" )
    else
        let ( next, effects ) = Shell.update (Shell.Act stamp action incarnation) shell
        in ( next, effects, if List.isEmpty effects then Just "Native operation unavailable" else Nothing )


menuEvent : Menu.Msg -> Shell.Model -> Model -> UpdateResult
menuEvent message shell ((Model state) as model) =
    case message of
        Menu.ReceiveFor _ _ _ ->
            answer model shell [] (Just "Native outcomes require an authenticated frame")
        Menu.Open _ _ ->
            answer model shell [] (Just "Menu opening requires a validated provider")
        _ ->
            let
                preblocked =
                    case ( message, state.provider ) of
                        ( Menu.Activate _ _ _, Just captured ) ->
                            blockedFor (Provider.incarnation captured.snapshot) shell model
                        _ -> False
                ( menu, effects ) = Menu.update message state.menu
                updated = Model { state | menu = menu }
            in
            if preblocked then
                answer model shell [] (Just "A menu operation for this window family awaits reconciliation")
            else case effects of
                [ ((Menu.Dispatch local binding action) as dispatch) ] ->
                    let
                        rejected reason = answer (refuse local binding reason updated) shell [] (Just reason)
                    in
                    case ( state.provider, operation action ) of
                        ( Just captured, Just nativeOperation ) ->
                            if Provider.getBinding captured.snapshot /= binding || not (providerMatches captured shell) then
                                rejected "Native window information changed; choose again"
                            else
                                -- This local intent has just become Pending. Do
                                -- not pass it through guardedAct, which protects
                                -- unrelated controller routes against that ledger.
                                let ( prepared, commands ) = Shell.update
                                        (Shell.Act captured.stamp nativeOperation (Provider.incarnation captured.snapshot)) shell
                                in
                                case commands of
                                    [ (Shell.Send command) ] ->
                                        case ReceiptRouter.register dispatch captured.snapshot command state.router of
                                            Err _ -> rejected "Native menu command could not be registered"
                                            Ok router ->
                                                let
                                                    closed =
                                                        case (Menu.snapshot menu).menu of
                                                            Nothing -> menu
                                                            Just view -> Tuple.first (Menu.update (Menu.Dismiss view.id) menu)
                                                in
                                                answer (Model { state | menu = closed, router = router }) prepared commands Nothing
                                    _ -> rejected "Native operation unavailable"
                        _ -> rejected "Menu operation unavailable"
                [] -> answer updated shell [] Nothing
                _ -> answer model shell [] (Just "Invalid menu dispatch count")


connectionLost : Model -> Model
connectionLost (Model state) =
    let
        uncertain = Menu.markDisconnected state.menu
        closed =
            case (Menu.snapshot uncertain).menu of
                Nothing -> uncertain
                Just view -> Tuple.first (Menu.update (Menu.Dismiss view.id) uncertain)
    in
    Model { state | menu = closed }


nativeFrame : String -> Model -> ( Model, Maybe String )
nativeFrame raw ((Model state) as model) =
    case D.decodeString (D.field "kind" D.string) raw of
        Err _ -> ( model, Just "Invalid native frame" )
        Ok "host-disconnected" -> ( connectionLost model, Nothing )
        Ok "effect-outcome" ->
            let ( router, receipt, error ) = ReceiptRouter.accept raw state.router
            in
            case receipt of
                Nothing -> ( model, error )
                Just message ->
                    let ( menu, _ ) = Menu.update message state.menu
                    in ( Model { state | menu = menu, router = router }, error )
        Ok _ -> ( model, Nothing )
