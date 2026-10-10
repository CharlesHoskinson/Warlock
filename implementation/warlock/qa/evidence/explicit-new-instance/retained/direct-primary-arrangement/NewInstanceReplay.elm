port module NewInstanceReplay exposing (main)

import ActionProjection as Scene
import Binding
import Catalog
import Desktop
import Json.Decode as D
import Json.Encode as E
import Launch
import MenuBridge
import NativePointerFixture
import Pins
import Platform
import Shell
import Surface
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

one=UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero
two=UInt64.next one |> Maybe.withDefault one
bound=E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
entry identifier=E.object [("id",E.string identifier),("name",E.string "Editor"),("wmclass",E.string "editor-class"),("iconHint",E.string ""),("genericName",E.string ""),("keywords",E.list E.string [])]
catalog identifiers=E.object [("catalogProtocol",E.int 2),("lifetime",E.string "1"),("generation",E.string "1"),("entries",E.list entry identifiers)]
window identifier app=E.object [("incarnation",E.string identifier),("label",E.string "Editor"),("owner",E.null),("application",E.string app),("minimized",E.bool False),("available",E.bool True)]
base identifiers=
    let initial=Desktop.initial
        windows=initial.windows
        shell=windows.shell
        effects=shell.effects
        scene=Scene.decode (E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity [window "1" "peer-class",window "2" "editor-class"])]) |> Result.toMaybe
        raw=catalog identifiers
    in NativePointerFixture.ready {initial | applications=Catalog.decode raw |> Result.toMaybe,
        launch=Launch.init |> Launch.bind (E.encode 0 bound) |> Launch.catalog raw,
        ownerScope=Just {outputId=one,providerId=one},pins=Pins.observe (Just {revision=one,identities=["editor"]}) Pins.initial,
        windows={windows | shell={shell | binding=D.decodeValue Binding.decoder bound |> Result.toMaybe,phase=Shell.Ready,
            effects={effects | connected=True,observed=scene |> Maybe.map (\value -> {context={lifetime=one,epoch=one,output=one,revision=one},scene=value})}}}}
openMenu current=Shell.capture current.windows.shell |> Maybe.map (\stamp -> Desktop.update (Desktop.OpenWindowMenu stamp two) current |> Tuple.first) |> Maybe.withDefault current
control current=Surface.controls current |> List.filter (\row -> row.id=="control:new-instance:editor") |> List.head
dispatch current=control current |> Maybe.andThen .message |> Maybe.map (\message -> Desktop.update message current) |> Maybe.withDefault (current,[])
launchWires effects=List.filterMap (\effect -> case effect of
    Desktop.Send wire -> if D.decodeValue (D.field "kind" D.string) wire==Ok "application-launch" then Just wire else Nothing
    _ -> Nothing) effects
action shown trigger=E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string "popup"),("publication",E.string shown),("lease",E.string "1"),("id",E.string "control:new-instance:editor"),("trigger",E.string trigger)]
resolve current shown trigger=Surface.resolve one one (action shown trigger) current
checks=
    let current=openMenu (base ["editor"])
        (pending,effects)=dispatch current
        wire=launchWires effects |> List.head
        request=wire |> Maybe.andThen (D.decodeValue (D.field "intent" D.value) >> Result.toMaybe)
        unknownLaunch=Launch.pending pending.launch |> Maybe.map (\token -> Launch.timeout token pending.launch) |> Maybe.withDefault pending.launch
        unknown=openMenu {pending | launch=unknownLaunch}
        pendingMenu=openMenu pending
        (jumpOpening,_)=Desktop.capture (base ["editor"]) |> Maybe.map (\stamp -> Desktop.update (Desktop.OpenJumpList stamp "editor") (base ["editor"])) |> Maybe.withDefault (base ["editor"],[])
        (jumpPending,jumpEffects)=dispatch jumpOpening
        ambiguous=openMenu (base ["editor","alias"])
        old=control current |> Maybe.andThen .message
        changed={current | presentation=current.presentation |> Maybe.andThen UInt64.next}
        staleEffects=old |> Maybe.map (\message -> Desktop.update message changed |> Tuple.second) |> Maybe.withDefault []
        retiredCatalog={current | applications=Catalog.decode (catalog []) |> Result.toMaybe,launch=Launch.catalog (catalog []) current.launch}
        removedEffects=old |> Maybe.map (\message -> Desktop.update message retiredCatalog |> Tuple.second) |> Maybe.withDefault []
        primary=base ["editor"]
        (ordinary,ordinaryEffects)=Shell.capture primary.windows.shell |> Maybe.map (\stamp -> Desktop.update (Desktop.Window (TaskbarShell.Primary stamp "application:editor-class")) primary) |> Maybe.withDefault (primary,[])
        refusedLaunch=request |> Maybe.map (\intent -> Launch.receive (E.encode 0 bound) (E.object [("catalogProtocol",E.int 1),("kind",E.string "launch-outcome"),("intent",intent),("status",E.string "Refused"),("reason",E.string "stale-catalog")]) pending.launch) |> Maybe.withDefault pending.launch
        check name value=(name,E.bool value)
    in [check "UniqueWindowMenuHasLabeledNewInstance" (control current |> Maybe.map (\row -> row.enabled && row.label=="New instance" && row.ariaLabel=="Open new instance of Editor") |> Maybe.withDefault False)
       ,check "PointerAndKeyboardResolveSameTypedAction" (resolve current "1" "pointer"/=Nothing && resolve current "1" "pointer"==resolve current "1" "keyboard")
       ,check "StalePublicationRejected" (resolve current "2" "pointer"==Nothing)
       ,check "OneIdentityBoundLaunch" (List.length (launchWires effects)==1 && (wire |> Maybe.map (D.decodeValue (D.at ["intent","entry"] D.string) >> (==) (Ok "editor")) |> Maybe.withDefault False))
       ,check "CurrentCatalogGeneration" (wire |> Maybe.map (D.decodeValue (D.at ["intent","generation"] D.string) >> (==) (Ok "1")) |> Maybe.withDefault False)
       ,check "WindowPopupClosesBeforeLaunch" (Surface.mode pending=="closed" && (MenuBridge.menuSnapshot pending.windows.menus).menu==Nothing && pending.jumpEntry==Nothing)
       ,check "NewInstanceDoesNotIssueWindowAction" (not (List.any (\effect -> case effect of
            Desktop.WindowEffect _ -> True
            _ -> False) effects))
       ,check "PendingDuplicateCannotLaunch" (List.isEmpty (launchWires (dispatch pendingMenu |> Tuple.second)))
       ,check "UnknownControlDisabled" (control unknown |> Maybe.map (\row -> not row.enabled && row.message==Nothing && String.contains "not confirmed" row.detail) |> Maybe.withDefault False)
       ,check "UnknownCannotLaunch" (Launch.status unknown.launch=="Unknown" && List.isEmpty (launchWires (dispatch unknown |> Tuple.second)))
       ,check "UnknownSurvivesCatalogRefresh" (Launch.status (Launch.catalog (catalog ["editor"]) unknown.launch)=="Unknown")
       ,check "ApplicationActionsHasNewInstance" (control jumpOpening |> Maybe.map .enabled |> Maybe.withDefault False)
       ,check "ApplicationActionsLaunchClosesPopup" (List.length (launchWires jumpEffects)==1 && jumpPending.jumpEntry==Nothing && Surface.mode jumpPending=="closed")
       ,check "NewInstanceIsNotADeclaredJumpAction" (control jumpOpening |> Maybe.map (\row -> not (String.startsWith "jump:action:" row.id)) |> Maybe.withDefault False)
       ,check "AmbiguousWindowCatalogHasNoLaunchControl" (Desktop.menuApplication ambiguous==Nothing && control ambiguous==Nothing)
       ,check "StaleViewDoesNotDispatch" (List.isEmpty staleEffects)
       ,check "RemovedCatalogEntryDoesNotDispatch" (List.isEmpty removedEffects)
       ,check "OrdinaryPrimaryActivationNeverLaunches" (List.isEmpty (launchWires ordinaryEffects) && Launch.status ordinary.launch=="Idle" && ordinary.choice/=Nothing)
       ,check "RefusalNeverAutomaticallyLaunches" (Launch.status refusedLaunch=="Refused" && List.length (launchWires effects)==1)]

main : Program () () Never
main=Platform.worker {init=\_ -> ((),outgoing (E.object [("checks",E.object checks),("scope",E.string "Actual compiled Desktop/Surface launch policy and current event resolution; native GIO/input/paint and AT acceptance separate.")])),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
