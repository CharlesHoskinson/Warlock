port module LauncherVisibilityReplay exposing (main)

import Binding
import Catalog
import Desktop
import Json.Decode as D
import Json.Encode as E
import Launch
import NativePointerFixture
import Platform
import Shell
import Surface
import UInt64

port outgoing : E.Value -> Cmd msg

one = UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero
bindingWire = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
entry = E.object [("id",E.string "z-exact"),("name",E.string "Files"),("iconHint",E.string ""),("wmclass",E.string ""),("genericName",E.string "File manager"),("keywords",E.list E.string ["folders"])]
catalog = E.object [("catalogProtocol",E.int 2),("lifetime",E.string "1"),("generation",E.string "1"),("entries",E.list identity [entry])]
base =
    let initial=Desktop.initial
        windows=initial.windows
        shell=windows.shell
        binding=D.decodeValue Binding.decoder bindingWire |> Result.toMaybe
        host=binding |> Maybe.map (Binding.encode >> E.encode 0) |> Maybe.withDefault ""
    in NativePointerFixture.ready {initial | open=True,applications=Catalog.decode catalog |> Result.toMaybe,windows={windows | shell={shell | binding=binding,phase=Shell.Ready}},launch=Launch.init |> Launch.bind host |> Launch.catalog catalog}

query = E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-query"),("surface",E.string "popup"),("publication",E.string "1"),("lease",E.string "1"),("id",E.string "control:search"),("query",E.string "files")]
action = E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string "popup"),("publication",E.string "1"),("lease",E.string "1"),("id",E.string "entry:z-exact"),("trigger",E.string "keyboard")]
applySurface raw model = Surface.resolve one one raw model |> Maybe.map (\msg -> Desktop.update msg model) |> Maybe.withDefault (model,[])
sends effects = List.filterMap (\effect -> case effect of
    Desktop.Send wire -> Just wire
    _ -> Nothing) effects
status model = D.decodeValue (D.field "status" D.string) (Surface.packet one one model) |> Result.withDefault ""
field name raw = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
replace name value raw = D.decodeValue (D.keyValuePairs D.value) raw |> Result.map (List.map (\(key,old) -> (key,if key==name then value else old)) >> E.object) |> Result.withDefault E.null
outcome intent state reason = E.object [("protocolVersion",E.int 3),("kind",E.string "application-launch-outcome"),("binding",bindingWire),("outcome",E.object [("catalogProtocol",E.int 1),("kind",E.string "launch-outcome"),("intent",intent),("status",E.string state),("reason",E.string reason)])]

result =
    let
        (searched,searchEffects)=applySurface query base
        selected=Surface.resolve one one action searched
        (pending,effects)=selected |> Maybe.map (\msg -> Desktop.update msg searched) |> Maybe.withDefault (searched,[])
        sent=sends effects
        command=List.head sent |> Maybe.withDefault E.null
        intent=field "intent" command
        (repeated,repeatedEffects)=selected |> Maybe.map (\msg -> Desktop.update msg pending) |> Maybe.withDefault (pending,[])
        (bad,badEffects)=Desktop.update (Desktop.Incoming (outcome (replace "request" (E.string "2") intent) "Submitted" "native-submission-accepted")) pending
        (malformed,malformedEffects)=Desktop.update (Desktop.Incoming (outcome intent "Submitted" "stale-catalog")) pending
        acceptedWire=outcome intent "Submitted" "native-submission-accepted"
        refusedWire=outcome intent "Refused" "stale-catalog"
        (accepted,acceptedEffects)=Desktop.update (Desktop.Incoming acceptedWire) pending
        (acceptedAgain,acceptedAgainEffects)=Desktop.update (Desktop.Incoming acceptedWire) accepted
        (refused,refusedEffects)=Desktop.update (Desktop.Incoming refusedWire) pending
        (refusedAgain,refusedAgainEffects)=Desktop.update (Desktop.Incoming refusedWire) refused
        unknown = Launch.pending pending.launch |> Maybe.map (\token -> Desktop.update (Desktop.Deadline token) pending |> Tuple.first) |> Maybe.withDefault pending
        (unknownRepeat,unknownEffects)=selected |> Maybe.map (\msg -> Desktop.update msg unknown) |> Maybe.withDefault (unknown,[])
        (closed,closeEffects)=Desktop.capture pending |> Maybe.map (\stamp -> Desktop.update (Desktop.CloseApplications stamp) pending) |> Maybe.withDefault (pending,[])
        (closedRefused,closedRefusedEffects)=Desktop.update (Desktop.Incoming refusedWire) closed
        nonApps={ searched | open=False }
        (otherPending,otherEffects)=Launch.select "z-exact" nonApps.launch |> Maybe.map (\selection -> Desktop.update (Desktop.Start selection) nonApps) |> Maybe.withDefault (nonApps,[])
        otherIntent=sends otherEffects |> List.head |> Maybe.map (field "intent") |> Maybe.withDefault E.null
        (otherRefused,otherRefusedEffects)=Desktop.update (Desktop.Incoming (outcome otherIntent "Refused" "stale-catalog")) otherPending
        wrongBinding=replace "binding" (replace "session" (E.string "2") bindingWire) refusedWire
        (wrongBound,wrongBoundEffects)=Desktop.update (Desktop.Incoming wrongBinding) pending
        staleAction=replace "publication" (E.string "2") action
        staleLease=replace "lease" (E.string "2") action
        pendingControls=Surface.controls pending
        checks =
            [ ("queryThroughSurface",searched.query=="files" && List.isEmpty searchEffects)
            , ("currentKeyboardControlResolved",selected/=Nothing)
            , ("oneIdentityBoundRequest",List.length sent==1 && D.decodeValue (D.field "kind" D.string) command==Ok "application-launch" && D.decodeValue (D.at ["binding","lifetime"] D.string) command==Ok "1" && D.decodeValue (D.at ["binding","session"] D.string) command==Ok "1" && D.decodeValue (D.at ["binding","frontend"] D.string) command==Ok "1" && D.decodeValue (D.at ["intent","request"] D.string) command==Ok "1" && D.decodeValue (D.at ["intent","lifetime"] D.string) command==Ok "1" && D.decodeValue (D.at ["intent","generation"] D.string) command==Ok "1" && D.decodeValue (D.at ["intent","entry"] D.string) command==Ok "z-exact")
            , ("pendingVisibleApplications",pending.open && pending.query=="files" && Surface.mode pending=="applications" && status pending=="Opening application…" && List.any (\row -> row.id=="control:search" && row.enabled) pendingControls && List.any (\row -> row.id=="control:refresh" && row.enabled) pendingControls && List.any (\row -> row.id=="entry:z-exact" && not row.enabled) pendingControls)
            , ("staleSurfaceAuthorityRejected",Surface.resolve one one staleAction searched==Nothing && Surface.resolve one one staleLease searched==Nothing)
            , ("wrongBindingCannotSettle",Launch.status wrongBound.launch=="Pending" && wrongBound.open && List.isEmpty wrongBoundEffects)
            , ("unknownCannotRepeat",Launch.status unknown.launch=="Unknown" && Launch.status unknownRepeat.launch=="Unknown" && List.isEmpty (sends unknownEffects))
            , ("explicitCloseNotReopenedByRefusal",not closed.open && closed.query=="files" && not closedRefused.open && closedRefused.query=="files" && Launch.status closedRefused.launch=="Refused" && List.isEmpty (sends closeEffects) && List.isEmpty closedRefusedEffects)
            , ("nonApplicationsRefusalRecovers",not otherPending.open && List.length (sends otherEffects)==1 && otherRefused.open && Launch.status otherRefused.launch=="Refused" && List.isEmpty otherRefusedEffects)
            , ("pendingRepeatedSubmitNoRequest",Launch.status pending.launch=="Pending" && Launch.status repeated.launch=="Pending" && List.isEmpty (sends repeatedEffects))
            , ("mismatchedCannotSettle",Launch.status bad.launch=="Pending" && List.isEmpty badEffects)
            , ("invalidCannotSettle",Launch.status malformed.launch=="Pending" && List.isEmpty malformedEffects)
            , ("acceptedClosesAndShowsSuccess",Launch.status accepted.launch=="Submitted" && not accepted.open && status accepted=="Launch submitted." && List.isEmpty acceptedEffects)
            , ("acceptedReceiptNeverReplays",Launch.status acceptedAgain.launch=="Submitted" && not acceptedAgain.open && List.isEmpty acceptedAgainEffects)
            , ("refusedReopensWithContext",Launch.status refused.launch=="Refused" && refused.open && refused.query=="files" && refused.applications==searched.applications && refused.windows.shell.binding==searched.windows.shell.binding && status refused=="Launch refused. Refresh applications and choose again." && List.isEmpty refusedEffects)
            , ("refusedReceiptNeverReplays",Launch.status refusedAgain.launch=="Refused" && refusedAgain.open && refusedAgain.query=="files" && List.isEmpty refusedAgainEffects)
            ]
    in E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed)) checks)),("request",command),("acceptedStatus",E.string (status accepted)),("refusedStatus",E.string (status refused)),("nativeAcceptance",E.bool False)]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
