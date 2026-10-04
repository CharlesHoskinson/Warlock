module Desktop exposing (Effect(..), ChoiceToken, choiceToken, Model, Msg(..), initial, update, ViewStamp, capture, key)

import Menu
import MenuBridge
import NativeProvider
import Provider
import Binding
import Catalog
import Json.Decode as D
import Json.Encode as E
import Launch
import Shell
import Taskbar
import Effects
import TaskbarShell
import UInt64 exposing (Counter)

type alias Model =
    { windows : TaskbarShell.Model
    , choice : Maybe Choice
    , choiceNotice : String
    , returnFocus : Maybe FocusTarget
    , menuOrigin : Maybe FocusTarget
    , ownerScope : Maybe {outputId : Counter, providerId : Counter}
    , ownerExhausted : Bool
    , launch : Launch.Model
    , applications : Maybe Catalog.Snapshot
    , open : Bool
    , request : Counter
    , presentation : Maybe Counter
    , expected : Maybe Counter
    }

type alias FocusTarget = {binding : Binding.Binding, key : String, output : Maybe Counter}

type ChoiceToken = ChoiceToken Binding.Binding Counter

type alias Choice = { binding : Binding.Binding, output : Counter, root : Counter, application : String, token : ChoiceToken }

choiceToken : Model -> Maybe ChoiceToken
choiceToken model = model.choice |> Maybe.map .token

type ViewStamp = ViewStamp (Maybe Binding.Binding) Counter

type Msg
    = Window TaskbarShell.Msg
    | OpenWindowMenu Shell.Stamp Counter
    | OwnerScope D.Value
    | PresentationOwner (Maybe {outputId : Counter, providerId : Counter})
    | Incoming D.Value
    | OpenApplications ViewStamp
    | CloseApplications ViewStamp
    | Start Launch.Selection
    | Deadline Launch.PendingToken
    | ChoiceDeadline ChoiceToken
    | RetryWindows
    | Acknowledge Launch.Acknowledgement

type Effect
    = WindowEffect Shell.Effect
    | Send E.Value
    | Arm Launch.PendingToken
    | ArmChoice ChoiceToken
    | Focus String

initial : Model
initial =
    { windows = TaskbarShell.initial, choice = Nothing, choiceNotice = "", returnFocus = Nothing, menuOrigin = Nothing, ownerScope = Nothing, ownerExhausted = False, launch = Launch.init, applications = Nothing, open = False, request = UInt64.zero, presentation = Just UInt64.zero, expected = Nothing }

capture : Model -> Maybe ViewStamp
capture model =
    model.presentation |> Maybe.map (ViewStamp model.windows.shell.binding)

key : Model -> String -> String
key model suffix =
    "applications:" ++ (model.windows.shell.binding |> Maybe.map host |> Maybe.withDefault "detached") ++ ":" ++ (model.presentation |> Maybe.map UInt64.string |> Maybe.withDefault "exhausted") ++ ":" ++ suffix

advance : Model -> Model
advance model =
    case model.presentation |> Maybe.andThen UInt64.next of
        Just value -> { model | presentation = Just value }
        Nothing -> { model | presentation = Nothing, open = False, applications = Nothing, expected = Nothing }


host : Binding.Binding -> String
host binding =
    E.encode 0 (Binding.encode binding)

strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder =
    D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Desktop frame fields")

version : D.Decoder ()
version =
    D.field "protocolVersion" D.int |> D.andThen (\value -> if value == 3 then D.succeed () else D.fail "Desktop version")

windowBase : TaskbarShell.Msg -> Model -> ( Model, List Effect )
windowBase message model =
    let
        (windows, effects) = TaskbarShell.update message model.windows
        disconnected = windows.shell.phase == Shell.Detached
        changed = windows.shell.binding /= model.windows.shell.binding
        launch =
            if disconnected then Launch.disconnect model.launch
            else if changed then windows.shell.binding |> Maybe.map (\binding -> Launch.bind (host binding) model.launch) |> Maybe.withDefault (Launch.disconnect model.launch)
            else model.launch
    in
    ( (if disconnected || changed then advance else identity) { model | windows = windows, launch = launch
        , choice = if disconnected || changed || windows.shell.phase==Shell.Exhausted then Nothing else model.choice
        , returnFocus = if disconnected || changed then Nothing else model.returnFocus
        , menuOrigin = if disconnected || changed || (MenuBridge.menuSnapshot windows.menus).menu==Nothing then Nothing else model.menuOrigin
        , choiceNotice = if disconnected || changed then "" else model.choiceNotice
        , applications = if disconnected || changed then Nothing else model.applications
        , expected = if disconnected || changed then Nothing else model.expected
      }, List.map WindowEffect effects ++
        (case (model.windows.picker,windows.picker,message) of
            (prior,Just picker,_) ->
                if (prior |> Maybe.map .generation)==Just picker.generation then [] else
                    TaskbarShell.groups windows |> List.filter (\group -> group.key==picker.key) |> List.concatMap .families |> List.filter .available |> List.head
                        |> Maybe.map (\family -> [Focus ("picker:" ++ Shell.stampKey picker.scope ++ ":" ++ UInt64.string picker.generation ++ ":" ++ UInt64.string family.root)]) |> Maybe.withDefault []
            (Just picker,Nothing,TaskbarShell.Close scope generation) ->
                if picker.scope==scope && picker.generation==generation && Shell.capture windows.shell==Just scope then [Focus ("group:" ++ Shell.stampKey scope ++ ":" ++ picker.key)] else []
            _ -> []
        ) )

window : TaskbarShell.Msg -> Model -> (Model,List Effect)
window message model =
    case message of
        TaskbarShell.MenuEvent (Menu.Dismiss menuId) ->
            case ((MenuBridge.menuSnapshot model.windows.menus).menu,model.menuOrigin) of
                (Just menu,Just origin) ->
                    if menu.id/=menuId then (model,[]) else
                    let (closed,effects)=windowBase message model
                        (refreshing,commands)=windowBase (TaskbarShell.Native Shell.Refresh) closed
                    in ({refreshing | returnFocus=Just origin,menuOrigin=Nothing},effects++commands)
                _ -> windowBase message model
        TaskbarShell.Close scope generation ->
            case (model.windows.picker,model.windows.shell.binding) of
                (Just picker,Just binding) ->
                    let (closed,effects)=windowBase message model
                    in if closed.windows.picker/=Nothing || picker.scope/=scope || picker.generation/=generation then (closed,effects) else
                        let (refreshing,commands)=windowBase (TaskbarShell.Native Shell.Refresh) closed
                        in ({refreshing | returnFocus=Just {binding=binding,key=picker.key,output=model.windows.shell.effects.observed |> Maybe.map (.context >> .output)}},List.filter (\effect -> case effect of
                            Focus _ -> False
                            _ -> True) effects ++ commands)
                _ -> windowBase message model
        TaskbarShell.Choose scope generation root ->
            case (model.windows.picker,model.windows.shell.binding,model.windows.shell.effects.observed) of
                (Just picker,Just binding,Just observed) ->
                    if model.choice/=Nothing || picker.scope/=scope || picker.generation/=generation || Shell.capture model.windows.shell/=Just scope || not (Shell.available model.windows.shell) then (model,[]) else
                    case TaskbarShell.groups model.windows |> List.filter (\group -> group.key==picker.key) |> List.concatMap .families |> List.filter (\family -> family.root==root && family.available) |> List.head of
                        Nothing -> (model,[])
                        Just family ->
                            let windows=model.windows
                                (next,effects)=windowBase (TaskbarShell.Native Shell.Refresh) {model | windows={windows | picker=Nothing},choiceNotice=""}
                            in case next.windows.shell.expected of
                                Just request ->
                                    let token=ChoiceToken binding request
                                    in ({next | choice=Just {binding=binding,output=observed.context.output,root=root,application=family.application,token=token}},effects++[ArmChoice token])
                                Nothing -> (next,effects)
                _ -> (model,[])
        _ ->
            let base=case message of
                    TaskbarShell.Native (Shell.Incoming _) -> model
                    _ -> {model | returnFocus=Nothing}
                (updated,ordinaryEffects)=windowBase message base
                matchingProjection = case message of
                    TaskbarShell.Native (Shell.Incoming raw) ->
                        D.decodeValue (D.map2 Tuple.pair (D.field "kind" D.string) (D.field "requestId" UInt64.decoder)) raw |> Result.map (\(kind,request) -> kind=="action-projection" && model.windows.shell.expected==Just request) |> Result.withDefault False
                    _ -> False
                (next,effects)=case updated.returnFocus of
                    Just target ->
                        if not matchingProjection || not (Shell.available updated.windows.shell) then (updated,ordinaryEffects) else
                            let retired={updated | returnFocus=Nothing}
                                exists=TaskbarShell.groups retired.windows |> List.any (\group -> group.key==target.key && List.any .available group.families)
                            in if retired.open || retired.windows.picker/=Nothing || (MenuBridge.menuSnapshot retired.windows.menus).menu/=Nothing || retired.windows.shell.binding/=Just target.binding || target.output==Nothing || (retired.windows.shell.effects.observed |> Maybe.map (.context >> .output))/=target.output || not exists then (retired,ordinaryEffects) else
                                case Shell.capture retired.windows.shell of
                                    Just scope -> (retired,ordinaryEffects++[Focus ("group:" ++ Shell.stampKey scope ++ ":" ++ target.key)])
                                    Nothing -> (retired,ordinaryEffects)
                    Nothing -> (updated,ordinaryEffects)

            in case next.choice of
                Just pending ->
                    if not matchingProjection || not (Shell.available next.windows.shell) then (next,effects) else
                    let retired={next | choice=Nothing,choiceNotice="The window changed. Choose again."}
                        family=TaskbarShell.groups next.windows |> List.concatMap .families |> List.filter (\item -> item.root==pending.root && item.application==pending.application && item.available) |> List.head
                        output=next.windows.shell.effects.observed |> Maybe.map (.context >> .output)
                    in if next.windows.shell.binding/=Just pending.binding || output/=Just pending.output then (retired,effects) else
                        case (Shell.capture next.windows.shell,family) of
                            (Just scope,Just selected) ->
                                case Taskbar.selection selected of
                                    Taskbar.Apply operation root ->
                                        let (applied,commands)=windowBase (TaskbarShell.Native (Shell.Act scope operation root)) {retired | choiceNotice=""}
                                        in (applied,effects++commands)
                                    _ -> (retired,effects)
                            _ -> (retired,effects)
                Nothing -> (next,effects)

update : Msg -> Model -> ( Model, List Effect )
update message model =
    case message of
        ChoiceDeadline token ->
            if (model.choice |> Maybe.map .token)/=Just token then (model,[]) else
                ({model | choice=Nothing,choiceNotice="Window information took too long. Refresh windows, then choose again."},[])
        RetryWindows ->
            if model.choice/=Nothing || String.isEmpty model.choiceNotice then (model,[]) else
                windowBase (TaskbarShell.Native Shell.Refresh) {model | choiceNotice=""}
        PresentationOwner scope ->
            if scope==model.ownerScope then (model,[]) else
            let (retired,effects) =
                    case MenuBridge.currentProvider model.windows.menus of
                        Nothing -> (model,[])
                        Just provider -> windowBase (TaskbarShell.MenuEvent (Menu.Invalidate (Provider.getBinding provider))) model
            in ({retired | ownerScope=scope,ownerExhausted=False,menuOrigin=Nothing,returnFocus=Nothing},effects)
        OwnerScope raw ->
            let positive = UInt64.decoder |> D.andThen (\counter -> if counter==UInt64.zero then D.fail "Zero owner identity" else D.succeed counter)
                decoder = strict ["surfaceProtocol","kind","outputId","providerId"]
                    (D.map4 (\protocol kind output provider -> (protocol,kind,{outputId=output,providerId=provider})) (D.field "surfaceProtocol" D.int) (D.field "kind" D.string) (D.field "outputId" positive) (D.field "providerId" positive))
            in case D.decodeValue decoder raw of
                Ok (2,"surface-owner",owner) ->
                    if model.ownerExhausted then (model,[]) else
                    case model.ownerScope of
                        Nothing -> ({model | ownerScope=Just owner},[])
                        Just previous ->
                            if previous==owner then (model,[]) else
                            let retired =
                                    case MenuBridge.currentProvider model.windows.menus of
                                        Nothing -> model
                                        Just provider -> windowBase (TaskbarShell.MenuEvent (Menu.Invalidate (Provider.getBinding provider))) model |> Tuple.first
                            in ({retired | ownerScope=Nothing,ownerExhausted=True,menuOrigin=Nothing,returnFocus=Nothing},[])
                _ -> (model,[])
        OpenWindowMenu stamp root ->
            if model.ownerExhausted || model.choice/=Nothing || MenuBridge.preparedSnapshot model.windows.menus/=Nothing || Shell.capture model.windows.shell/=Just stamp || not (Shell.available model.windows.shell) then (model,[]) else
            case model.windows.shell.effects.observed of
                Nothing -> (model,[])
                Just observed ->
                    case model.ownerScope of
                        Nothing -> (model,[])
                        Just owner ->
                            case NativeProvider.fromShell {outputId=owner.outputId,providerId=owner.providerId,capabilityGeneration=observed.context.revision} root model.windows.shell of
                                Err _ -> (model,[])
                                Ok provider ->
                                    let (next,effects)=windowBase (TaskbarShell.OpenMenu provider) model
                                    in if (MenuBridge.menuSnapshot next.windows.menus).menu==(MenuBridge.menuSnapshot model.windows.menus).menu then (model,[]) else
                                        ({next | open=False,expected=Nothing,returnFocus=Nothing,menuOrigin=model.windows.shell.binding |> Maybe.andThen (\binding -> TaskbarShell.groups model.windows |> List.filter (\group -> List.any (\family -> family.root==root) group.families) |> List.head |> Maybe.map (\group -> {binding=binding,key=group.key,output=Just observed.context.output}))},effects)
        Window value ->
            let (next,effects)=window value model
            in if next.windows.picker/=Nothing && next.windows.picker/=model.windows.picker then ({next | open=False,expected=Nothing,menuOrigin=Nothing,returnFocus=Nothing},effects) else (next,effects)
        Incoming raw ->
            case D.decodeValue (D.field "kind" D.string) raw of
                Ok "application-catalog" ->
                    let decoder = strict ["protocolVersion","kind","binding","requestId","snapshot"] (D.map4 (\_ binding request snapshot -> (binding,request,snapshot)) version (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder) (D.field "snapshot" D.value))
                    in case D.decodeValue decoder raw of
                        Ok (binding,request,snapshot) ->
                            if model.windows.shell.phase /= Shell.Detached && model.windows.shell.binding == Just binding && model.expected == Just request then
                                let next = advance {model | launch = Launch.catalog snapshot model.launch, applications = Catalog.decode snapshot |> Result.toMaybe, expected = Nothing}
                                    target = (if List.member (Launch.status next.launch) ["Pending","Unknown"] then Nothing else next.applications) |> Maybe.map Catalog.entries |> Maybe.withDefault [] |> List.head |> Maybe.map (\entry -> key next ("entry:" ++ Catalog.id entry.identity)) |> Maybe.withDefault (key next "control:close")
                                in (next,if next.open then [Focus target] else [])
                            else (model,[])
                        Err _ -> (model,[])
                Ok "application-launch-outcome" ->
                    let decoder = strict ["protocolVersion","kind","binding","outcome"] (D.map3 (\_ binding outcome -> (binding,outcome)) version (D.field "binding" Binding.decoder) (D.field "outcome" D.value))
                    in case D.decodeValue decoder raw of
                        Ok (binding,outcome) ->
                            if model.windows.shell.phase /= Shell.Detached && model.windows.shell.binding == Just binding then
                                ({model | launch = Launch.receive (host binding) outcome model.launch},[])
                            else (model,[])
                        Err _ -> (model,[])
                _ -> window (TaskbarShell.Native (Shell.Incoming raw)) model
        OpenApplications stamp ->
            if capture model /= Just stamp || MenuBridge.preparedSnapshot model.windows.menus/=Nothing then (model,[]) else
            let base =
                    case (MenuBridge.menuSnapshot model.windows.menus).menu of
                        Nothing -> model
                        Just menu -> windowBase (TaskbarShell.MenuEvent (Menu.Dismiss menu.id)) model |> Tuple.first
                windows=base.windows
                retired = advance {base | windows={windows | picker=Nothing}, returnFocus=Nothing, menuOrigin=Nothing, open = True, applications = Nothing, launch = Launch.catalog E.null model.launch, expected = Nothing}
            in case (model.windows.shell.binding, UInt64.next model.request) of
                (Just binding,Just request) ->
                    if model.windows.shell.phase == Shell.Detached || retired.presentation == Nothing then (retired,[]) else
                        ({retired | request = request, expected = Just request},[Send (E.object [("protocolVersion",E.int 3),("kind",E.string "catalog-request"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request))]),Focus (key retired "control:close")])
                _ -> (retired,[])
        CloseApplications stamp ->
            if capture model /= Just stamp || not model.open then (model,[]) else
                let next = advance {model | open = False, expected = Nothing}
                in (next,[Focus (key next "control:opener")])
        Start selection ->
            if MenuBridge.preparedSnapshot model.windows.menus/=Nothing then (model,[]) else
            let (launch,intent) = Launch.start selection model.launch
            in case (intent,model.windows.shell.binding) of
                (Just wire,Just binding) ->
                    ({model | launch = launch, open = False, expected = Nothing},Send (E.object [("protocolVersion",E.int 3),("kind",E.string "application-launch"),("binding",Binding.encode binding),("intent",wire)]) :: (Launch.pending launch |> Maybe.map (Arm >> List.singleton) |> Maybe.withDefault []))
                _ -> ({model | launch = launch},[])
        Deadline token -> ({model | launch = Launch.timeout token model.launch},[])
        Acknowledge token -> ({model | launch = Launch.acknowledgeUnknown token model.launch},[])
