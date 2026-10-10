port module SwitcherFocusReplay exposing (main)

import ActionProjection as Scene
import Desktop
import Json.Decode as D
import Json.Encode as E
import Surface
import Platform
import Shell
import Switcher
import SwitcherReplay as Fixture
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

refresh model=Desktop.update (Desktop.Window (TaskbarShell.Native (Shell.Incoming E.null))) model
selected model=Switcher.selected model.switcher |> Maybe.map (.root >> UInt64.string)
focuses effects=List.filterMap (\effect -> case effect of
    Desktop.Focus target -> Just target
    _ -> Nothing) effects
ownFocus identity effects=case focuses effects of
    [target] -> String.endsWith (":switcher:family:"++identity) target
    _ -> False

fixture ids label model=
    let windows=model.windows
        shell=windows.shell
        effects=shell.effects
        focus=if List.member "3" ids then Just (Fixture.counter "3") else List.head ids |> Maybe.map Fixture.counter
        scene=Scene.decode (E.object [("revision",E.string "1"),("focused",focus |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null),("windows",E.list Fixture.window ids)]) |> Result.toMaybe
        observed=Maybe.map2 (\old current -> {old | scene=current}) effects.observed scene
        relabelled=observed |> Maybe.map (\old -> {old | scene=Scene.decode (E.object [("revision",E.string "1"),("focused",focus |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null),("windows",E.list (\id -> if id=="2" then E.object [("incarnation",E.string id),("label",E.string label),("owner",E.null),("application",E.string id),("minimized",E.bool False),("available",E.bool True)] else Fixture.window id) ids)]) |> Result.withDefault old.scene})
        geometry= shell.geometry |> Maybe.map (\old -> {old | focused=focus,windows=List.map (Fixture.counter >> Fixture.geometryWindow) ids})
    in {model | windows={windows | shell={shell | phase=Shell.Ready,effects={effects | observed=relabelled},geometry=geometry}}}

main : Program () () Never
main=Platform.worker {init=\_ -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
result=
    let opened=Fixture.scoped (\stamp -> Desktop.OpenSwitcher stamp Switcher.Forward) Fixture.base |> Tuple.first
        windows=opened.windows
        ready={opened | windows={windows | shell=Fixture.base.windows.shell}}
        local=Desktop.update (Desktop.Incoming (Fixture.historyFrame ready)) ready |> Tuple.first
        native=Fixture.journal "90" ["1","2","3"] [1] False False Fixture.base |> Tuple.first
        localQuiet=refresh local
        nativeQuiet=refresh native
        nativeCancelled=Fixture.journal "90" ["1","2","3"] [1] False True native
        nativeStep=Fixture.journal "90" ["1","2","3"] [1,1] False False native
        nativeRepeated=Fixture.journal "90" ["1","2","3"] [1,1] False False (Tuple.first nativeStep)
        localRetired=refresh (fixture ["1","3","4"] "2" local)
        nativeRetired=refresh (fixture ["1","3","4"] "2" native)
        localAfter=refresh (Tuple.first localRetired)
        nativeAfter=refresh (Tuple.first nativeRetired)
        renamed=refresh (fixture ["1","2","3"] "Renamed window" native)
        empty=refresh (fixture ["4"] "2" native)
        checks=[("fixtureStartsAtSelectedIncarnation",selected local==Just "2" && selected native==Just "2")
            ,("localUnchangedDoesNotRefocus",List.isEmpty (focuses (Tuple.second localQuiet)))
            ,("nativeChordKeepsApplicationKeyboardParent",D.decodeValue (D.field "keyboardParent" D.bool) (Surface.packet (Fixture.counter "1") (Fixture.counter "1") native)==Ok False && D.decodeValue (D.field "keyboardParent" D.bool) (Surface.packet (Fixture.counter "2") (Fixture.counter "1") (Tuple.first nativeCancelled))==Ok False && List.isEmpty (Tuple.second nativeCancelled))
            ,("nativeUnchangedDoesNotRefocus",List.isEmpty (focuses (Tuple.second nativeQuiet)))
            ,("nativePhysicalStepFocusesNewSelection",selected (Tuple.first nativeStep)==Just "1" && ownFocus "1" (Tuple.second nativeStep))
            ,("duplicateNativeStepDoesNotRefocus",List.isEmpty (focuses (Tuple.second nativeRepeated)))
            ,("localRetirementFocusesSurvivor",selected (Tuple.first localRetired)==Just "1" && ownFocus "1" (Tuple.second localRetired))
            ,("nativeRetirementFocusesSurvivor",selected (Tuple.first nativeRetired)==Just "1" && ownFocus "1" (Tuple.second nativeRetired))
            ,("survivingSelectionIsFocusedOnce",List.isEmpty (focuses (Tuple.second localAfter)) && List.isEmpty (focuses (Tuple.second nativeAfter)))
            ,("labelUpdatesWithoutRefocus",selected (Tuple.first renamed)==Just "2" && (Switcher.selected (Tuple.first renamed).switcher |> Maybe.map .label)==Just "Renamed window" && List.isEmpty (focuses (Tuple.second renamed)))
            ,("arrivalNeverEntersFrozenSelection",List.all (\row -> UInt64.string row.root/="4") (Switcher.entries (Tuple.first nativeRetired).switcher))
            ,("emptyChordDismissesWithoutFocusOrChoice",Switcher.phase (Tuple.first empty).switcher==Switcher.Cancelled && List.isEmpty (focuses (Tuple.second empty)) && (Tuple.first empty).choice==Nothing)]
    in E.object [("checks",E.object (List.map (\(name,value) -> (name,E.bool value)) checks)),("scope",E.string "Real Desktop update reconciliation with existing admitted component fixtures; no physical/native focus or speech/braille claim.")]
