module TaskbarShell exposing (Model, Msg(..), Picker, initial, update, groups)
import Shell
import Json.Encode as E
import Json.Decode as D
import Menu
import MenuBridge
import Provider
import NativeOutcome
import Taskbar
import UInt64 exposing (Counter)
type alias Picker = { scope : Shell.Stamp, key : String, generation : Counter }
type alias Model = { shell : Shell.Model, picker : Maybe Picker, generation : Counter, menus : MenuBridge.Model }
type Msg = Native Shell.Msg | Primary Shell.Stamp String | Choose Shell.Stamp Counter Counter | Close Shell.Stamp Counter | OpenMenu Provider.Snapshot | MenuEvent Menu.Msg | ExpirePrepared Counter | CancelPrepared Counter
initial : Model
initial = { shell = Shell.initial, picker = Nothing, generation = UInt64.zero, menus = MenuBridge.initial }
groups model = model.shell.effects.observed |> Maybe.map (.scene >> Taskbar.groups) |> Maybe.withDefault []
valid scope model = MenuBridge.preparedSnapshot model.menus==Nothing && Shell.capture model.shell == Just scope && Shell.available model.shell
native message model =
    let
        menus = case message of
            Shell.Incoming raw ->
                case D.decodeValue (D.field "kind" D.string) raw of
                    Ok "effect-outcome" ->
                        if NativeOutcome.valid raw then MenuBridge.nativeFrame (E.encode 0 raw) model.menus |> Tuple.first
                        else model.menus
                    Ok "host-disconnected" -> MenuBridge.connectionLost model.menus
                    _ -> model.menus
            _ -> model.menus
        (shell,effects) = case message of
            Shell.Act scope operation target ->
                let (next,emitted,error) = MenuBridge.guardedAct scope operation target model.shell menus
                in ({next | notice = Maybe.withDefault next.notice error},emitted)
            Shell.Incoming raw ->
                if D.decodeValue (D.field "kind" D.string) raw == Ok "effect-outcome" && not (NativeOutcome.valid raw) then
                    (model.shell,[])
                else Shell.update message model.shell
            _ -> Shell.update message model.shell
        picker = model.picker |> Maybe.andThen (\current -> if Shell.capture shell == Just current.scope && Shell.available shell then Just current else Nothing)
        advanced = MenuBridge.advancePrepared message model.shell shell menus
        settledMenus = MenuBridge.reconcileWithShell advanced.shell advanced.bridge
        finalShell = advanced.shell
    in ({model | shell = {finalShell | notice = Maybe.withDefault finalShell.notice advanced.error}, picker = picker, menus = settledMenus},effects++advanced.effects)
apply scope decision model =
    case decision of
        Taskbar.Apply operation root -> native (Shell.Act scope operation root) {model | picker = Nothing}
        _ -> (model,[])
dismissMenus model =
    case (MenuBridge.menuSnapshot model.menus).menu of
        Nothing -> model
        Just view ->
            let result = MenuBridge.menuEvent (Menu.Dismiss view.id) model.shell model.menus
            in {model | menus = result.bridge}
update : Msg -> Model -> (Model,List Shell.Effect)
update message model =
    case message of
        OpenMenu provider ->
            let menus = MenuBridge.open provider model.menus
            in ({model | menus = menus, picker = if menus == model.menus then model.picker else Nothing},[])
        MenuEvent event ->
            let result = MenuBridge.menuEvent event model.shell model.menus
                shell = result.shell
            in ({model | menus = result.bridge, shell = {shell | notice = Maybe.withDefault shell.notice result.error}, picker = if List.isEmpty result.effects then model.picker else Nothing},result.effects)
        CancelPrepared token ->
            let result=MenuBridge.cancelSelection token model.shell model.menus
                shell=result.shell
            in ({model|menus=result.bridge,shell={shell|notice=Maybe.withDefault shell.notice result.error}},result.effects)
        ExpirePrepared token ->
            let result=MenuBridge.expirePrepared token model.shell model.menus
                shell=result.shell
            in ({model|menus=result.bridge,shell={shell|notice=Maybe.withDefault shell.notice result.error}},result.effects)
        Native value -> native value model
        Primary scope key ->
            if not (valid scope model) then (model,[]) else
                case groups model |> List.filter (\group -> group.key == key) |> List.head of
                    Nothing -> (model,[])
                    Just group ->
                        let base = dismissMenus model
                        in
                        case Taskbar.primary False group.families of
                            Taskbar.Picker ->
                                case UInt64.next model.generation of
                                    Just generation -> ({base | generation = generation, picker = Just {scope = scope,key = key,generation = generation}},[])
                                    Nothing -> ({base | picker = Nothing},[])
                            decision -> apply scope decision base
        Choose scope generation root ->
            case model.picker of
                Just picker ->
                    if not (valid scope model) || picker.scope /= scope || picker.generation /= generation then (model,[]) else
                        groups model |> List.filter (\group -> group.key == picker.key) |> List.concatMap .families |> List.filter (\family -> family.root == root) |> List.head
                            |> Maybe.map (\family -> apply scope (Taskbar.selection family) model) |> Maybe.withDefault (model,[])
                Nothing -> (model,[])
        Close scope generation ->
            case model.picker of
                Just picker -> if picker.scope == scope && picker.generation == generation then ({model | picker = Nothing},[]) else (model,[])
                Nothing -> (model,[])
