port module PinsReplay exposing (main)
import Binding
import Catalog
import Desktop
import Json.Decode as D
import Json.Encode as E
import Launch
import Pins
import Platform
import Shell
import Surface
import UInt64
port outgoing : E.Value -> Cmd msg
one = UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero
bindingValue = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
binding = D.decodeValue Binding.decoder bindingValue |> Result.toMaybe
catalog = E.object [("catalogProtocol",E.int 2),("lifetime",E.string "1"),("generation",E.string "1"),("entries",E.list identity (List.map (\(id,name) -> E.object [("id",E.string id),("name",E.string name),("iconHint",E.string ""),("wmclass",E.string ""),("genericName",E.string ""),("keywords",E.list E.string [])]) [("warlock-files","Files"),("warlock-editor","Editor")]))]
base =
    let m=Desktop.initial
        w=m.windows
        s=w.shell
    in {m|open=True,applications=Catalog.decode catalog |> Result.toMaybe,pins=Pins.observe (Just {revision=one,identities=[]}) Pins.initial,launch=Launch.init |> Launch.bind (E.encode 0 bindingValue) |> Launch.catalog catalog,windows={w|shell={s|binding=binding,phase=Shell.Ready}}}
apply build model = Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (build stamp) model) |> Maybe.withDefault (model,[])
save revision state = saveReceipt state |> Tuple.first
saveReceipt (model,effects) =
    let wire=effects |> List.filterMap (\e -> case e of
            Desktop.Send value -> Just value
            _ -> Nothing) |> List.head
        proposal=wire |> Maybe.andThen (D.decodeValue (D.field "proposal" Pins.decoder) >> Result.toMaybe)
        frame snapshot request = E.object [("protocolVersion",E.int 3),("kind",E.string "taskbar-pins-outcome"),("binding",bindingValue),("requestId",E.string request),("status",E.string "Saved"),("preferences",Pins.encode snapshot)]
    in case (wire,proposal) of
        (Just value,Just p) ->
            let request=D.decodeValue (D.field "requestId" D.string) value |> Result.withDefault "0"
            in Desktop.update (Desktop.Incoming (frame {p|revision=UInt64.next p.revision |> Maybe.withDefault p.revision} request)) model
        _ -> (model,[])
main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ s -> (s,Cmd.none),subscriptions=\_ -> Sub.none}
result =
    let first=apply (\stamp -> Desktop.TogglePin stamp "warlock-files") base
        savedFirst=save 2 first
        second=apply (\stamp -> Desktop.TogglePin stamp "warlock-editor") savedFirst
        savedSecond=save 3 second
        moved=apply (\stamp -> Desktop.MovePin stamp "warlock-editor" -1) savedSecond
        savedMoved=save 4 moved
        order=Desktop.pinIdentities savedMoved
        restartedBase={base|open=False,pins=Pins.initial,expected=Just one}
        snapshot=savedMoved.pins.snapshot |> Maybe.map Pins.encode |> Maybe.withDefault E.null
        restarted=Desktop.update (Desktop.Incoming (E.object [("protocolVersion",E.int 3),("kind",E.string "application-catalog"),("binding",bindingValue),("requestId",E.string "1"),("snapshot",catalog),("preferences",snapshot)])) restartedBase |> Tuple.first
        stale=Desktop.capture base |> Maybe.map (\stamp -> Desktop.update (Desktop.TogglePin stamp "warlock-files") savedMoved) |> Maybe.withDefault (savedMoved,[])
        launchAction=Surface.resolve one one (E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string "bar"),("publication",E.string "1"),("lease",E.string "1"),("id",E.string "bar:pin:warlock-editor")]) restarted
        launched=launchAction |> Maybe.map (\msg -> Desktop.update msg restarted) |> Maybe.withDefault (restarted,[])
        requests=Tuple.second launched |> List.filterMap (\e -> case e of
            Desktop.Send value -> D.decodeValue (D.field "kind" D.string) value |> Result.toMaybe
            _ -> Nothing)
        pending=Tuple.first moved
        staleReceipt=Desktop.update (Desktop.Incoming (E.object [("protocolVersion",E.int 3),("kind",E.string "taskbar-pins-outcome"),("binding",bindingValue),("requestId",E.string "999"),("status",E.string "Saved"),("preferences",snapshot)])) pending
        unknownReceipt=Desktop.update (Desktop.Incoming (E.object [("protocolVersion",E.int 3),("kind",E.string "taskbar-pins-outcome"),("binding",bindingValue),("requestId",E.string "3"),("status",E.string "Unknown"),("preferences",E.null)])) pending
        writes effects = List.filterMap (\effect -> case effect of
            Desktop.Send value -> Just value
            _ -> Nothing) effects
        focus effects = List.filterMap (\effect -> case effect of
            Desktop.Focus target -> Just target
            _ -> Nothing) effects
        invalid=apply (\stamp -> Desktop.TogglePin stamp "removed-identity") savedMoved
        boundary=apply (\stamp -> Desktop.MovePin stamp "warlock-editor" -1) savedMoved
    in E.object [("checks",E.object [("pinWritesOnce",E.bool (List.length (Tuple.second first)==1 && (Tuple.first first).pins.pending/=Nothing)),("doesNotClaimSaveBeforeReceipt",E.bool (Desktop.pinIdentities (Tuple.first first)==[])),("pinOrderConfirmed",E.bool (Desktop.pinIdentities savedSecond==["warlock-files","warlock-editor"])),("reorderConfirmed",E.bool (order==["warlock-editor","warlock-files"])),("restartPreservesExactIdentitiesAndOrder",E.bool (Desktop.pinIdentities restarted==order)),("staleActionRejected",E.bool (Tuple.first stale==savedMoved && List.isEmpty (Tuple.second stale))), ("staleReceiptRejected",E.bool (Tuple.first staleReceipt==pending && List.isEmpty (Tuple.second staleReceipt))), ("missingEntryCannotBePinned",E.bool (Tuple.first invalid==savedMoved && List.isEmpty (Tuple.second invalid))), ("boundaryReorderNoWrite",E.bool (List.isEmpty (Tuple.second boundary))), ("zeroWindowPinLaunchesOnce",E.bool (requests==["application-launch"] && not (Tuple.first launched).open)),("unknownReceiptNeverWrites",E.bool (List.isEmpty (writes (Tuple.second unknownReceipt)) && (Tuple.first unknownReceipt).pins.pending/=Nothing)),("currentPinReceiptRestoresSearchFocus",E.bool (focus (Tuple.second (saveReceipt first))==["launcher-search"])),("unknownReceiptKeepsRecoveryReachable",E.bool (focus (Tuple.second unknownReceipt)==["launcher-search"]))]),("restartedFrame",Surface.packet one one restarted)]
