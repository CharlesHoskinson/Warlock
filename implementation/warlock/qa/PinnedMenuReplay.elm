port module PinnedMenuReplay exposing (main)

import ActionProjection as Scene
import Binding
import Catalog
import Desktop
import Json.Decode as D
import Json.Encode as E
import Menu
import MenuBridge
import Pins
import Platform
import Shell
import Surface
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

one=UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero
binding=D.decodeValue Binding.decoder (E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]) |> Result.toMaybe
entry id wmclass=E.object [("id",E.string id),("name",E.string id),("wmclass",E.string wmclass),("iconHint",E.string ""),("genericName",E.string ""),("keywords",E.list E.string [])]
catalog entries=Catalog.decode (E.object [("catalogProtocol",E.int 2),("lifetime",E.string "1"),("generation",E.string "1"),("entries",E.list identity entries)]) |> Result.toMaybe
window id app=E.object [("incarnation",E.string id),("label",E.string app),("owner",E.null),("application",E.string app),("minimized",E.bool False),("available",E.bool True)]
model apps pins windows =
    let initial=Desktop.initial
        native=initial.windows
        shell=native.shell
        effects=shell.effects
        scene=Scene.decode (E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity windows)]) |> Result.toMaybe
    in {initial | applications=catalog apps,pins=Pins.observe (Just {revision=one,identities=pins}) Pins.initial,windows={native | shell={shell | binding=binding,phase=Shell.Ready,effects={effects | connected=True,observed=scene |> Maybe.map (\value -> {context={lifetime=one,epoch=one,output=one,revision=one},scene=value})}}}}
event id trigger publication=E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-context"),("surface",E.string "bar"),("publication",E.string publication),("lease",E.string "1"),("id",E.string id),("trigger",E.string trigger),("x",E.int 0),("y",E.int 0)]
resolve id trigger publication current=Surface.resolve one one (event id trigger publication) current
menuRoot message=case message of
    Just (Desktop.OpenWindowMenu _ root) -> Just root
    _ -> Nothing
picker message=case message of
    Just (Desktop.Window (TaskbarShell.Primary _ _)) -> True
    _ -> False
base=model [entry "owned-pin" "owned-app",entry "empty-pin" "empty-app"] ["owned-pin","empty-pin"] [window "1" "owned-app"]
menuModel active =
    let current=if active then base else model [entry "owned-pin" "owned-app"] ["owned-pin"] [window "1" "other-app",window "2" "owned-app"]
        owned={current | ownerScope=Just {outputId=one,providerId=one}}
        root=if active then one else UInt64.next one |> Maybe.withDefault one
    in Shell.capture owned.windows.shell |> Maybe.map (\stamp -> Desktop.update (Desktop.OpenWindowMenu stamp root) owned |> Tuple.first) |> Maybe.withDefault owned
selectMinimize active invalid =
    let current=menuModel active
    in case (MenuBridge.menuSnapshot current.windows.menus).menu of
        Just menu ->
            let index=menu.items |> List.indexedMap Tuple.pair |> List.filter (\(_,item) -> item.action==Menu.Minimize) |> List.head |> Maybe.map Tuple.first |> Maybe.withDefault -1
            in Desktop.update (Desktop.Window (TaskbarShell.MenuEvent (Menu.Activate menu.id menu.binding (if invalid then 999 else index)))) current |> Tuple.first
        Nothing -> current
checks=
    [("pinnedPointerUsesExistingRoot",menuRoot (resolve "bar:pin:owned-pin" "pointer" "1" base)==Just one)
    ,("pinnedKeyboardUsesExistingRoot",menuRoot (resolve "bar:pin:owned-pin" "keyboard" "1" base)==Just one)
    ,("stalePublicationRefused",resolve "bar:pin:owned-pin" "keyboard" "2" base==Nothing)
    ,("zeroWindowPinHasNoWindowMenu",resolve "bar:pin:empty-pin" "keyboard" "1" base==Nothing)
    ,("missingCatalogRefused",resolve "bar:pin:owned-pin" "keyboard" "1" {base | applications=Nothing}==Nothing)
    ,("unconfiguredPinRefused",resolve "bar:pin:owned-pin" "keyboard" "1" {base | pins=Pins.initial}==Nothing)
    ,("unpinnedGroupStillWorks",menuRoot (resolve "bar:group:application:owned-app" "keyboard" "1" {base | pins=Pins.initial})==Just one)
    ,("hiddenUnpinnedAliasRefused",resolve "bar:group:application:owned-app" "keyboard" "1" base==Nothing)
    ,("multiplePinOwnersRefused",let ambiguous=model [entry "a" "owned-app",entry "b" "owned-app"] ["a","b"] [window "1" "owned-app"] in resolve "bar:pin:a" "keyboard" "1" ambiguous==Nothing)
    ,("multipleApplicationGroupsRefused",let ambiguous=model [entry "owned-pin" "owned-app"] ["owned-pin"] [window "1" "owned-app",window "2" "owned-pin"] in resolve "bar:pin:owned-pin" "keyboard" "1" ambiguous==Nothing)
    ,("multipleFamiliesKeepPickerRoute",let multiple=model [entry "owned-pin" "owned-app"] ["owned-pin"] [window "1" "owned-app",window "2" "owned-app"] in picker (resolve "bar:pin:owned-pin" "keyboard" "1" multiple))
    ,("inactiveMinimizeRetainsOriginUntilCurrentObservation",let selected=selectMinimize False False in MenuBridge.preparedSnapshot selected.windows.menus/=Nothing && selected.returnFocus/=Nothing)
    ,("activeMinimizeLeavesNativeSuccessorAuthority",let selected=selectMinimize True False in MenuBridge.preparedSnapshot selected.windows.menus/=Nothing && selected.returnFocus==Nothing)
    ,("invalidMenuSelectionCannotCreateFocusIntent",let selected=selectMinimize False True in MenuBridge.preparedSnapshot selected.windows.menus==Nothing && selected.returnFocus==Nothing)]

main : Program () () Never
main=Platform.worker {init=\_ -> ((),outgoing (E.object [("checks",E.object (List.map (\(name,value) -> (name,E.bool value)) checks)),("scope",E.string "Compiled existing context-event resolution only; native pointer/keyboard proof and menu outcome are separate.")])),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
