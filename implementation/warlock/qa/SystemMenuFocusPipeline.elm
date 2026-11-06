port module SystemMenuFocusPipeline exposing (main)

{-| Draft source-level observation through the real SurfaceController entrypoint.
The attached/snapshot records are synthetic replay inputs, not native receipts.
-}
import Desktop
import Json.Decode as D
import Json.Encode as E
import Platform
import Surface
import SurfaceController as Controller
import SystemMenu
import UInt64

port outgoing : E.Value -> Cmd msg

counter value =
    D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero

binding =
    E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]

attached =
    E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",binding)]

pointerIdle owner =
    E.object [("protocolVersion",E.int 3),("kind",E.string "pointer-ownership"),("ownershipProtocol",E.int 1),("binding",owner),("requestId",E.string "1"),("serial",E.string "1"),("state",E.string "idle"),("owner",E.null)]

foreignBinding =
    E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "2")]

snapshot =
    E.object
        [("service",E.string "9"),("revision",E.string "1")
        ,("volume",E.object [("percent",E.int 100),("muted",E.bool False),("label",E.string "Warlock private audio")])
        ,("network",E.null)
        ,("power",E.object [("suspend",E.string "yes"),("reboot",E.string "yes"),("poweroff",E.string "no")])
        ,("session",E.object [("name",E.string "Warlock private session"),("state",E.string "active"),("locked",E.bool False)])]

loaded request =
    E.object [("protocolVersion",E.int 3),("kind",E.string "system-menu-snapshot"),("binding",binding),("requestId",E.string (UInt64.string request)),("snapshot",snapshot)]

send message model =
    Controller.update (Controller.Interaction message) model

dispatch make model =
    Desktop.capture (Controller.desktop model)
        |> Maybe.map (\stamp -> send (make stamp) model)
        |> Maybe.withDefault (model,[])

focus effects =
    List.filterMap (\effect -> case effect of
        Controller.DesktopEffect (Desktop.Focus target) -> Just target
        _ -> Nothing) effects

published effects =
    List.filterMap (\effect -> case effect of
        Controller.Publish frame -> Just frame
        _ -> Nothing) effects

matches expected identity model =
    Surface.controls (Controller.desktop model)
        |> List.filter (\control -> control.id==identity && control.enabled && control.domId==expected)
        |> List.length
        |> (==) 1

result =
    let
        (attachedModel,_) = send (Desktop.Incoming attached) Controller.initial
        (blockedOpen,blockedEffects) = dispatch Desktop.OpenSystemMenu attachedModel
        (foreignIdle,_) = send (Desktop.Incoming (pointerIdle foreignBinding)) attachedModel
        (foreignOpen,foreignEffects) = dispatch Desktop.OpenSystemMenu foreignIdle
        (ready,_) = send (Desktop.Incoming (pointerIdle binding)) foreignIdle
        (opened,_) = dispatch Desktop.OpenSystemMenu ready
        request = (Controller.desktop opened).systemMenuExpected |> Maybe.withDefault UInt64.zero
        (read,_) = send (Desktop.Incoming (loaded request)) opened
        current = D.decodeValue SystemMenu.decoder snapshot |> Result.toMaybe
        intent = current |> Maybe.map (\value -> SystemMenu.intent value SystemMenu.Reboot 0)
        (confirmation,confirmationEffects) = intent |> Maybe.map (\value -> dispatch (\stamp -> Desktop.SystemChange stamp value) read) |> Maybe.withDefault (read,[])
        (cancelled,cancelEffects) = dispatch Desktop.CancelSystemChange confirmation
        stale = Desktop.capture (Controller.desktop read) |> Maybe.map (\stamp -> send (Desktop.CancelSystemChange stamp) confirmation) |> Maybe.withDefault (confirmation,[])
        (validAfterStale,validEffects) = dispatch Desktop.CancelSystemChange (Tuple.first stale)
        (duplicate,duplicateEffects) = dispatch Desktop.CancelSystemChange cancelled
        confirmId = "applications:{\"lifetime\":\"1\",\"session\":\"1\",\"frontend\":\"1\"}:5:system:cancel"
        closeId = "applications:{\"lifetime\":\"1\",\"session\":\"1\",\"frontend\":\"1\"}:6:system:close"
        readModel = Controller.desktop read
        exactModels = case intent of
            Nothing -> False
            Just selected ->
                let expectedConfirm = {readModel | systemMenuConfirmation=Just selected,presentation=Just (counter "5")}
                    expectedCancel = {expectedConfirm | systemMenuConfirmation=Nothing,presentation=Just (counter "6")}
                in Controller.desktop confirmation==expectedConfirm && Controller.desktop cancelled==expectedCancel
        sameFrame expected effects = case published effects of
            [frame] -> E.encode 0 frame == E.encode 0 (Controller.frame expected)
            _ -> False
        checks =
            [("missingPointerObservationRefusesOpen", Controller.desktop blockedOpen==Controller.desktop attachedModel && List.isEmpty blockedEffects)
            ,("foreignIdleRefusesThenCurrentIdleAllows", Controller.desktop foreignOpen==Controller.desktop foreignIdle && List.isEmpty foreignEffects && (Controller.desktop opened).systemMenuOpen && (Controller.desktop opened).systemMenuExpected/=Nothing)
            ,("confirmationPublishesSuccessorAndFocus", intent/=Nothing && focus confirmationEffects==[confirmId] && matches confirmId "system:cancel" confirmation && sameFrame confirmation confirmationEffects)
            ,("cancellationPublishesSuccessorAndFocus", focus cancelEffects==[closeId] && matches closeId "control:close" cancelled && sameFrame cancelled cancelEffects)
            ,("literalFullModelsAndOrderedEffects", exactModels && confirmationEffects==[Controller.Publish (Controller.frame confirmation),Controller.DesktopEffect (Desktop.Focus confirmId)] && cancelEffects==[Controller.Publish (Controller.frame cancelled),Controller.DesktopEffect (Desktop.Focus closeId)])
            ,("staleThenValid", Controller.desktop (Tuple.first stale)==Controller.desktop confirmation && List.isEmpty (Tuple.second stale) && Controller.desktop validAfterStale==Controller.desktop cancelled && focus validEffects==[closeId] && sameFrame validAfterStale validEffects)
            ,("duplicateCancelRefused", Controller.desktop duplicate==Controller.desktop cancelled && List.isEmpty duplicateEffects)
            ,("unavailableNetworkDisabled", Surface.controls (Controller.desktop read) |> List.any (\c -> c.id=="system:network:state" && c.label=="Network unavailable" && not c.enabled && c.message==Nothing))
            ,("observedVolumeDisplayed", Surface.controls (Controller.desktop read) |> List.any (\c -> String.startsWith "Volume 100%" c.label))]
    in
    E.object [("checks",E.object (List.map (\(name,ok) -> (name,E.bool ok)) checks)),("confirmationFrame",Controller.frame confirmation),("cancelFrame",Controller.frame cancelled)]

main =
    Platform.worker {init=\() -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
