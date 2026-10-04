module TaskbarShell exposing (Model, Msg(..), Picker, initial, update, groups)
import Shell
import Taskbar
import UInt64 exposing (Counter)
type alias Picker = { scope : Shell.Stamp, key : String, generation : Counter }
type alias Model = { shell : Shell.Model, picker : Maybe Picker, generation : Counter }
type Msg = Native Shell.Msg | Primary Shell.Stamp String | Choose Shell.Stamp Counter Counter | Close Shell.Stamp Counter
initial : Model
initial = { shell = Shell.initial, picker = Nothing, generation = UInt64.zero }
groups model = model.shell.effects.observed |> Maybe.map (.scene >> Taskbar.groups) |> Maybe.withDefault []
valid scope model = Shell.capture model.shell == Just scope && Shell.available model.shell
native message model =
    let
        (shell,effects) = Shell.update message model.shell
        picker = model.picker |> Maybe.andThen (\current -> if Shell.capture shell == Just current.scope && Shell.available shell then Just current else Nothing)
    in ({model | shell = shell, picker = picker},effects)
apply scope decision model =
    case decision of
        Taskbar.Apply operation root -> native (Shell.Act scope operation root) {model | picker = Nothing}
        _ -> (model,[])
update : Msg -> Model -> (Model,List Shell.Effect)
update message model =
    case message of
        Native value -> native value model
        Primary scope key ->
            if not (valid scope model) then (model,[]) else
                case groups model |> List.filter (\group -> group.key == key) |> List.head of
                    Nothing -> (model,[])
                    Just group ->
                        case Taskbar.primary False group.families of
                            Taskbar.Picker ->
                                case UInt64.next model.generation of
                                    Just generation -> ({model | generation = generation, picker = Just {scope = scope,key = key,generation = generation}},[])
                                    Nothing -> ({model | picker = Nothing},[])
                            decision -> apply scope decision model
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
