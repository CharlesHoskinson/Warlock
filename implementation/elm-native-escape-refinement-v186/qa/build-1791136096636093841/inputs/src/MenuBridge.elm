module MenuBridge exposing
    ( Model, UpdateResult, connectionLost, currentProvider, guardedAct, initial, menuEvent
    , locallyRefuseUnsent, menuSnapshot, nativeFrame, open, receiptCount, reconcileWithShell, preparedSnapshot, expirePrepared, advancePrepared, cancelSelection
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
import GeometryProjection
import Json.Decode as D
import Json.Encode as E
import Menu
import NativeProvider
import Provider
import ReceiptRouter
import Shell
import UnsentOperation
import UInt64 exposing (Counter)


type alias CapturedProvider =
    { snapshot : Provider.Snapshot, stamp : Shell.Stamp }


type Model
    = Model
        { menu : Menu.Model
        , router : ReceiptRouter.Model
        , provider : Maybe CapturedProvider
        , prepared : Maybe Prepared
        , preparedSerial : Counter
        }


type alias Prepared =
    { dispatch : Menu.Effect, local : Menu.IntentId, originalBinding : Menu.Binding
    , menuId : Menu.MenuId, action : Menu.Action, captured : CapturedProvider
    , legacyWindows : List ActionProjection.Window
    , geometryCaps : Maybe GeometryProjection.Capabilities
    , token : Counter, legacyRequest : Counter, geometryRequest : Maybe Counter
    , legacyReady : Bool, geometryReady : Bool
    }


type alias PreparedSnapshot =
    { token : Counter, legacyRequest : Counter, geometryRequest : Maybe Counter
    , legacyReady : Bool, geometryReady : Bool }


preparedSnapshot : Model -> Maybe PreparedSnapshot
preparedSnapshot (Model state) =
    state.prepared |> Maybe.map (\slot -> {token=slot.token,legacyRequest=slot.legacyRequest,geometryRequest=slot.geometryRequest,legacyReady=slot.legacyReady,geometryReady=slot.geometryReady})


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
    Model { menu = Menu.init, router = ReceiptRouter.empty, provider = Nothing, prepared = Nothing, preparedSerial = UInt64.zero }


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
    if state.prepared/=Nothing then model else
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
        Menu.Maximize -> Just Effects.Maximize
        Menu.RestoreGeometry -> Just Effects.RestoreGeometry
        _ -> Nothing


providerMatches : CapturedProvider -> Shell.Model -> Bool
providerMatches captured shell =
    shell.binding == Just (Provider.nativeBinding captured.snapshot)
        && Shell.capture shell == Just captured.stamp
        && (Provider.geometryObservation captured.snapshot |> Maybe.map .context) == (if Provider.geometryObservation captured.snapshot==Nothing then Nothing else shell.geometry |> Maybe.map .context)
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
        nativeBlocked =
            case ( shell.binding, shell.effects.observed, root ) of
                ( Just _, Just observed, Just family ) ->
                    ActionProjection.windows observed.scene
                        |> List.filter (\window -> ActionProjection.rootOf window.incarnation observed.scene == Just family)
                        |> List.any (\window -> Effects.blocked observed.context.lifetime window.incarnation shell.effects)
                _ ->
                    -- Without admitted ownership, no family may be inferred.
                    List.any (\transaction -> List.member transaction.status [Effects.Pending, Effects.Unknown]) shell.effects.unresolved
    in blocked || nativeBlocked


guardedAct : Shell.Stamp -> Effects.Operation -> Counter -> Shell.Model -> Model -> ( Shell.Model, List Shell.Effect, Maybe String )
guardedAct stamp action incarnation shell model =
    let blocked = blockedFor incarnation shell model
    in
    if blocked || preparedSnapshot model/=Nothing then
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
        Menu.Dismiss id ->
            case state.prepared of
                Just slot -> if slot.menuId==id then cancelPrepared "Selection canceled before dispatch" shell model else answer model shell [] Nothing
                Nothing -> answer (Model {state|menu=Tuple.first (Menu.update message state.menu)}) shell [] Nothing
        Menu.Invalidate binding ->
            case state.prepared of
                Just slot -> if slot.originalBinding==binding then cancelPrepared "Selection authority retired" shell model else answer (Model {state|menu=Tuple.first (Menu.update message state.menu)}) shell [] Nothing
                Nothing -> answer (Model {state|menu=Tuple.first (Menu.update message state.menu)}) shell [] Nothing
        Menu.OutputRetired output generation ->
            case state.prepared of
                Just slot -> if Menu.outputId (UInt64.string (Provider.presentationScope slot.captured.snapshot).outputId)==output && UInt64.string (Provider.nativeContext slot.captured.snapshot).output==generation then cancelPrepared "Selection output retired" shell model else answer (Model {state|menu=Tuple.first (Menu.update message state.menu)}) shell [] Nothing
                Nothing -> answer (Model {state|menu=Tuple.first (Menu.update message state.menu)}) shell [] Nothing
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
                        ( Just captured, Just _ ) ->
                            if Provider.getBinding captured.snapshot /= binding || not (providerMatches captured shell) || (Provider.actionProtocol action==2 && (shell.geometryExpected/=Nothing || shell.geometryAttachExpected/=Nothing)) then
                                rejected "Native window information changed; choose again"
                            else
                                case (state.prepared,UInt64.next state.preparedSerial,((Menu.snapshot state.menu).menu,shell.effects.observed)) of
                                    (Nothing,Just token,(Just view,Just observed)) ->
                                        let (refreshing,requests)=Shell.update Shell.Refresh shell
                                            needsGeometry=Provider.geometryObservation captured.snapshot/=Nothing
                                            closed=Tuple.first (Menu.update (Menu.Dismiss view.id) menu)
                                        in case refreshing.expected of
                                            Nothing -> rejected "Post-close window observation unavailable"
                                            Just legacyRequest ->
                                                if List.isEmpty requests || (needsGeometry && refreshing.geometryExpected==Nothing) then rejected "Post-close geometry observation unavailable" else
                                                let slot={dispatch=dispatch,local=local,originalBinding=binding,menuId=view.id,action=action,captured=captured,legacyWindows=ActionProjection.windows observed.scene,geometryCaps=shell.geometryCaps,token=token,legacyRequest=legacyRequest,geometryRequest=refreshing.geometryExpected,legacyReady=False,geometryReady=not needsGeometry}
                                                in answer (Model {state|menu=closed,prepared=Just slot,preparedSerial=token}) {refreshing|deferNotifications=True} (requests++[Shell.ArmPrepared token]) Nothing
                                    _ -> rejected "A prepared selection is already pending or exhausted"
                        _ -> rejected "Menu operation unavailable"
                [] -> answer updated shell [] Nothing
                _ -> answer model shell [] (Just "Invalid menu dispatch count")


connectionLost : Model -> Model
connectionLost (Model state) =
    let
        canceled = case state.prepared of
            Nothing -> state.menu
            Just slot -> Tuple.first (Menu.update (Menu.ReceiveFor slot.local slot.originalBinding (Menu.Refusal "Connection lost before dispatch")) state.menu)
        uncertain = Menu.markDisconnected canceled
        closed =
            case (Menu.snapshot uncertain).menu of
                Nothing -> uncertain
                Just view -> Tuple.first (Menu.update (Menu.Dismiss view.id) uncertain)
    in
    Model { state | menu = closed, prepared = Nothing }


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


{-| Reconcile only admitted native facts. A focus-only revision can replace an
open Ready menu with a freshly produced provider and new menu identity, provided
the native authority, output generation, canonical target and action table agree.
Old bindings are retired; unresolved requests and their receipt keys survive.
The captured provider retains the trusted presentation output/provider scope.
-}
reconcileWithShell : Shell.Model -> Model -> Model
reconcileWithShell shell ((Model state) as model) =
    if shell.phase == Shell.Detached then
        connectionLost model
    else if state.prepared/=Nothing then model
    else
        case state.provider of
            Nothing -> model
            Just captured ->
                case shell.effects.observed of
                    Nothing -> model
                    Just observed ->
                        let
                            previous = Provider.nativeContext captured.snapshot
                            liveRoot = ActionProjection.rootOf (Provider.incarnation captured.snapshot) observed.scene == Just (Provider.incarnation captured.snapshot)
                            sameAuthority = shell.binding == Just (Provider.nativeBinding captured.snapshot)
                                && observed.context.lifetime == previous.lifetime
                                && observed.context.epoch == previous.epoch
                                && observed.context.output == previous.output
                            changed = observed.context /= previous || not sameAuthority || not liveRoot
                                || (Provider.geometryObservation captured.snapshot |> Maybe.map .context) /= (if Provider.geometryObservation captured.snapshot==Nothing then Nothing else shell.geometry |> Maybe.map .context)
                            retired =
                                let (menu,_) = Menu.update (Menu.Invalidate (Provider.getBinding captured.snapshot)) state.menu
                                in Model {state | menu=menu}
                        in
                        if not changed then model else
                        case (Menu.snapshot state.menu).menu of
                            Just view ->
                                if view.status /= Menu.Ready || not sameAuthority || not liveRoot then retired
                                else if shell.expected/=Nothing || shell.geometryExpected/=Nothing || shell.geometryAttachExpected/=Nothing then model
                                else if not (Shell.available shell) then retired
                                else
                                let scope=Provider.presentationScope captured.snapshot
                                    sameGeometry fresh = case (Provider.geometryObservation captured.snapshot,Provider.geometryObservation fresh) of
                                        (Nothing,Nothing) -> True
                                        (Just previousFacts,Just currentFacts) -> previousFacts.windows==currentFacts.windows
                                            && previousFacts.binding==currentFacts.binding
                                            && previousFacts.context.lifetime==currentFacts.context.lifetime
                                            && previousFacts.context.epoch==currentFacts.context.epoch
                                            && previousFacts.context.output==currentFacts.context.output
                                        _ -> False
                                in case NativeProvider.fromShell {outputId=scope.outputId,providerId=scope.providerId,capabilityGeneration=observed.context.revision} (Provider.incarnation captured.snapshot) shell of
                                    Err _ -> retired
                                    Ok fresh ->
                                        if Provider.getItems fresh/=Provider.getItems captured.snapshot || Provider.title fresh/=Provider.title captured.snapshot || not (sameGeometry fresh) then retired
                                        else case providerStamp fresh of
                                            Err _ -> retired
                                            Ok stamp ->
                                                let refreshed=Menu.rebindReady view.id view.binding (Provider.getBinding fresh) (Provider.getItems fresh) state.menu
                                                in if ((Menu.snapshot refreshed).menu |> Maybe.map .binding)/=Just (Provider.getBinding fresh) then retired
                                                   else Model {state|menu=refreshed,provider=Just {snapshot=fresh,stamp=stamp}}
                            _ -> retired


cancelPrepared : String -> Shell.Model -> Model -> UpdateResult
cancelPrepared reason shell ((Model state) as model) =
    case state.prepared of
        Nothing -> answer model shell [] Nothing
        Just slot ->
            let cleared=refuse slot.local slot.originalBinding reason (Model {state|prepared=Nothing})
                (resumed,effects)=Shell.resumeNotifications shell
            in answer cleared resumed effects (Just reason)


cancelSelection : Counter -> Shell.Model -> Model -> UpdateResult
cancelSelection token shell ((Model state) as model) =
    case state.prepared of
        Just slot -> if slot.token==token then cancelPrepared "Selection canceled before dispatch" shell model else answer model shell [] Nothing
        Nothing -> answer model shell [] Nothing


expirePrepared : Counter -> Shell.Model -> Model -> UpdateResult
expirePrepared token shell ((Model state) as model) =
    case state.prepared of
        Just slot -> if slot.token==token then cancelPrepared "Window information took too long. Choose again." shell model else answer model shell [] Nothing
        Nothing -> answer model shell [] Nothing


compatiblePrepared : Prepared -> Shell.Model -> Bool
compatiblePrepared slot shell =
    let original=slot.captured.snapshot
        old=Provider.nativeContext original
        legacy=shell.effects.observed
        sameLegacy=legacy |> Maybe.map (\observed -> observed.context.lifetime==old.lifetime && observed.context.epoch==old.epoch && observed.context.output==old.output && UInt64.compare observed.context.revision old.revision/=LT && ActionProjection.windows observed.scene==slot.legacyWindows && ActionProjection.rootOf (Provider.incarnation original) observed.scene==Just (Provider.incarnation original)) |> Maybe.withDefault False
        sameGeometry=case (Provider.geometryObservation original,shell.geometry) of
            (Nothing,_) -> slot.geometryRequest==Nothing
            (Just before,Just after) -> before.binding==after.binding && before.context.lifetime==after.context.lifetime && before.context.epoch==after.context.epoch && before.context.output==after.context.output && UInt64.compare after.context.revision before.context.revision/=LT && UInt64.compare after.sequence before.sequence/=LT && not after.blocked && before.windows==after.windows
            _ -> False
    in shell.binding==Just (Provider.nativeBinding original) && shell.geometryCaps==slot.geometryCaps && sameLegacy && sameGeometry


advancePrepared : Shell.Msg -> Shell.Model -> Shell.Model -> Model -> UpdateResult
advancePrepared message previous shell ((Model state) as model) =
    case state.prepared of
        Nothing -> answer model shell [] Nothing
        Just slot ->
            if shell.phase==Shell.Detached || shell.phase==Shell.Exhausted || shell.binding/=Just (Provider.nativeBinding slot.captured.snapshot) then cancelPrepared "Selection disconnected or authority changed" shell model else
            let response=case message of
                    Shell.Incoming raw -> D.decodeValue (D.map3 (\kind native request -> (kind,native,request)) (D.field "kind" D.string) (D.field "binding" NativeBinding.decoder) (D.field "requestId" UInt64.decoder)) raw |> Result.toMaybe
                    _ -> Nothing
                legacyReady=slot.legacyReady || (response==Just ("action-projection",Provider.nativeBinding slot.captured.snapshot,slot.legacyRequest) && previous.expected==Just slot.legacyRequest && shell.expected==Nothing)
                geometryReady=slot.geometryReady || (case slot.geometryRequest of
                    Nothing -> True
                    Just request -> response==Just ("geometry-facts",Provider.nativeBinding slot.captured.snapshot,request) && previous.geometryExpected==Just request && shell.geometryExpected==Nothing)
                lostCorrelation=(not legacyReady && shell.expected/=Just slot.legacyRequest) || (not geometryReady && shell.geometryExpected/=slot.geometryRequest)
                updatedSlot={slot|legacyReady=legacyReady,geometryReady=geometryReady}
                updated=Model {state|prepared=Just updatedSlot}
            in if lostCorrelation then cancelPrepared "Post-close observation correlation changed" shell updated else
               if not (legacyReady && geometryReady && Shell.available shell) then answer updated shell [] Nothing else
               if not (compatiblePrepared updatedSlot shell) then cancelPrepared "Window state changed. Choose again." shell updated else
               let scope=Provider.presentationScope slot.captured.snapshot
                   generation=shell.effects.observed |> Maybe.map (.context >> .revision) |> Maybe.withDefault UInt64.zero
               in case NativeProvider.fromShell {outputId=scope.outputId,providerId=scope.providerId,capabilityGeneration=generation} (Provider.incarnation slot.captured.snapshot) shell of
                   Err reason -> cancelPrepared reason shell updated
                   Ok fresh ->
                       case operation slot.action of
                           Nothing -> cancelPrepared "Selected operation unavailable" shell updated
                           Just nativeOperation ->
                               let stamp=if Provider.actionProtocol slot.action==2 then Shell.captureGeometry shell else Shell.capture shell
                               in case stamp of
                                   Nothing -> cancelPrepared "Fresh native context unavailable" shell updated
                                   Just current ->
                                       let (issued,commands)=Shell.update (Shell.Act current nativeOperation (Provider.incarnation fresh)) shell
                                       in case commands of
                                           [Shell.Send command] ->
                                               case ReceiptRouter.registerPrepared slot.dispatch slot.captured.snapshot fresh command state.router of
                                                   Err reason -> cancelPrepared reason shell updated
                                                   Ok router -> answer (Model {state|prepared=Nothing,router=router}) {issued|deferNotifications=False} commands Nothing
                                           _ -> cancelPrepared "Native operation unavailable" shell updated


{-| Invoke only after Shell validates the exact issued Pending key against a
matched authenticated preflight-unsent certificate. No native receipt is made.
-}
locallyRefuseUnsent : UnsentOperation.Key -> Model -> Model
locallyRefuseUnsent proved ((Model state) as model) =
    let (router,message)=ReceiptRouter.locallyRefuseUnsent proved state.router
    in case message of
        Nothing -> model
        Just receipt ->
            let (menu,_)=Menu.update receipt state.menu
            in Model {state|router=router,menu=menu}
