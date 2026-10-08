module Desktop exposing (Effect(..), ChoiceToken, choiceToken, Model, Msg(..), initial, update, ViewStamp, capture, key, switcherOpen, canProveCatalogUnsent, pinnedGroup, pinGroups, pinIdentities)

import Menu
import ActionProjection as Scene
import Switcher
import Pins
import Settings
import Notifications
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
import TaskView
import Snap
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
    , pins : Pins.Model
    , notifications : Notifications.Model
    , notificationsOpen : Bool
    , notificationsOpening : Bool
    , notificationsExpected : Maybe Counter
    , settings : Settings.Model
    , settingsOpen : Bool
    , settingsOpening : Bool
    , settingsExpected : Maybe Counter
    , query : String
    , open : Bool
    , overview : Bool
    , overviewWorkspace : Maybe String
    , snap : Maybe Snap.Choice
    , switcher : Switcher.Model
    , nativeSwitcher : Maybe NativeChord
    , switcherOrigin : Maybe Counter
    , switcherExpected : Maybe Counter
    , switcherHistory : Maybe {context : {lifetime : Counter, epoch : Counter, output : Counter, revision : Counter}, roots : List Counter}
    , request : Counter
    , presentation : Maybe Counter
    , expected : Maybe Counter
    , catalogFailure : Maybe { binding : Binding.Binding, request : Counter }
    }

type FocusDestination = TaskbarGroup String | OverviewOpener
type alias FocusTarget = {binding : Binding.Binding, destination : FocusDestination, output : Maybe Counter}

type alias NativeChord = {generation : Counter, roots : List Counter, history : List Counter, origin : Maybe Counter, steps : List Switcher.Direction, released : Bool, cancelled : Bool, consumed : Bool}

type ChoiceToken = ChoiceToken Binding.Binding Counter

type alias Choice = { chord : Maybe Counter, binding : Binding.Binding, output : Counter, root : Counter, application : String, token : ChoiceToken, placement : Maybe Snap.Proposal }

choiceToken : Model -> Maybe ChoiceToken
choiceToken model = model.choice |> Maybe.map .token

type ViewStamp = ViewStamp (Maybe Binding.Binding) Counter

type Msg
    = Window TaskbarShell.Msg
    | OpenWindowMenu Shell.Stamp Counter
    | OpenSnap ViewStamp Counter
    | SelectSnap ViewStamp Snap.Region
    | ApplySnap ViewStamp
    | CloseSnap ViewStamp
    | InvalidateSnap
    | OwnerScope D.Value
    | PresentationOwner (Maybe {outputId : Counter, providerId : Counter})
    | Incoming D.Value
    | OpenApplications ViewStamp
    | OpenNotifications ViewStamp
    | CloseNotifications ViewStamp
    | RefreshNotifications ViewStamp
    | NotificationAction ViewStamp Notifications.Target
    | OpenSettings ViewStamp
    | CloseSettings ViewStamp
    | EditSettings ViewStamp Settings.Values
    | SaveSettings ViewStamp
    | RefreshSettings ViewStamp
    | OpenOverview ViewStamp
    | OpenSwitcher ViewStamp Switcher.Direction
    | SwitcherStep ViewStamp Switcher.Direction
    | SwitcherChoose ViewStamp Counter
    | CommitSwitcher ViewStamp
    | CloseSwitcher ViewStamp
    | CloseOverview ViewStamp
    | OverviewWorkspace ViewStamp (Maybe String)
    | OverviewChoose ViewStamp Counter
    | CloseApplications ViewStamp
    | SearchQuery ViewStamp String
    | TogglePin ViewStamp String
    | MovePin ViewStamp String Int
    | CatalogUnsent Binding.Binding Counter
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
    { windows = TaskbarShell.initial, choice = Nothing, choiceNotice = "", returnFocus = Nothing, menuOrigin = Nothing, ownerScope = Nothing, ownerExhausted = False, launch = Launch.init, applications = Nothing, query = "", pins = Pins.initial, notifications = Notifications.initial, notificationsOpen = False, notificationsOpening = False, notificationsExpected = Nothing, settings = Settings.initial, settingsOpen = False, settingsOpening = False, settingsExpected = Nothing, open = False, overview = False, overviewWorkspace = Nothing, snap = Nothing, switcher=Switcher.initial, nativeSwitcher=Nothing, switcherOrigin=Nothing, switcherExpected=Nothing, switcherHistory=Nothing, request = UInt64.zero, presentation = Just UInt64.zero, expected = Nothing, catalogFailure = Nothing }

switcherOpen : Model -> Bool
switcherOpen model = List.member (Switcher.phase model.switcher) [Switcher.Waiting,Switcher.Browsing]

retireSwitcher : Model -> Model
retireSwitcher model = {model | switcher=Switcher.cancel (Switcher.generation model.switcher) model.switcher,switcherExpected=Nothing,switcherHistory=Nothing,switcherOrigin=Nothing}

switcherFocus : Model -> List Effect
switcherFocus model = Switcher.selected model.switcher |> Maybe.map (\family -> [Focus (key model ("switcher:family:"++UInt64.string family.root))]) |> Maybe.withDefault []

historyRequest : Binding.Binding -> Counter -> Effect
historyRequest binding request = Send (E.object [("protocolVersion",E.int 3),("kind",E.string "activation-history-request"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request))])

readSwitcherHistory : Model -> (Model,List Effect)
readSwitcherHistory model =
    case (model.windows.shell.binding,UInt64.next model.request) of
        (Just binding,Just request) -> ({model | request=request,switcherExpected=Just request,switcherHistory=Nothing},[historyRequest binding request])
        _ -> (retireSwitcher model,[])

chooseFamily : Taskbar.Family -> Model -> (Model,List Effect)
chooseFamily family model =
    case (model.windows.shell.binding,model.windows.shell.effects.observed) of
        (Just binding,Just observed) ->
            if model.choice/=Nothing || MenuBridge.blockedFor family.root model.windows.shell model.windows.menus then (retireSwitcher model,[]) else
            let (next,effects)=windowBase (TaskbarShell.Native Shell.Refresh) (retireSwitcher {model | overview=False,choiceNotice=""})
            in case next.windows.shell.expected of
                Just request ->
                    let token=ChoiceToken binding request
                    in ({next | choice=Just {chord=model.nativeSwitcher |> Maybe.map .generation,binding=binding,output=observed.context.output,root=family.root,application=family.application,token=token,placement=Nothing}},effects++[ArmChoice token])
                Nothing -> (next,effects)
        _ -> (retireSwitcher model,[])

syncSwitcher : Model -> (Model,List Effect)
syncSwitcher model =
    if not (switcherOpen model) then (model,[]) else
    case model.nativeSwitcher of
        Just chord ->
            case TaskView.groups model.windows.shell of
                Just groups ->
                    let candidates=List.concatMap .windows groups |> List.filter (\row -> List.member row.root chord.roots)
                        (switcher,selected)=if Switcher.phase model.switcher==Switcher.Browsing then (Switcher.reconcile candidates model.switcher,Nothing) else Switcher.readyFrozen (Switcher.generation model.switcher) chord.roots chord.history candidates chord.origin model.switcher
                        next=advance {model | switcher=switcher}
                    in case selected of
                        Just family -> chooseFamily family next
                        Nothing -> (next,switcherFocus next)
                Nothing -> (model,[])
        Nothing -> syncLocalSwitcher model

syncLocalSwitcher : Model -> (Model,List Effect)
syncLocalSwitcher model =
    case (model.switcherHistory,model.windows.shell.effects.observed,TaskView.groups model.windows.shell) of
        (Just history,Just observed,Just groups) ->
            if Switcher.phase model.switcher==Switcher.Browsing then
                ( {model | switcher=Switcher.reconcile (List.concatMap .windows groups) model.switcher},[] )
            else if history.context/=observed.context then
                if model.switcherExpected==Nothing then readSwitcherHistory model else (model,[])
            else
                let (switcher,selected)=Switcher.ready (Switcher.generation model.switcher) history.roots (List.concatMap .windows groups) model.switcherOrigin model.switcher
                    next=advance {model | switcher=switcher}
                in case selected of
                    Just family -> chooseFamily family next
                    Nothing -> (next,switcherFocus next)
        _ -> (model,[])

nativeChordDecoder : D.Decoder NativeChord
nativeChordDecoder =
    let positive=UInt64.decoder |> D.andThen (\value -> if value==UInt64.zero then D.fail "Zero chord identity" else D.succeed value)
        identities=D.list positive |> D.andThen (\rows -> if List.length rows<=256 && List.length (List.foldl (\root unique -> if List.member root unique then unique else root::unique) [] rows)==List.length rows then D.succeed rows else D.fail "Chord membership")
        direction=D.int |> D.andThen (\value -> if value==1 then D.succeed Switcher.Forward else if value== -1 then D.succeed Switcher.Reverse else D.fail "Chord direction")
        steps=D.list direction |> D.andThen (\rows -> if List.length rows<=4096 then D.succeed rows else D.fail "Chord ordinals")
    in strict ["generation","roots","history","origin","steps","released","cancelled","consumed"]
        (D.map8 NativeChord (D.field "generation" UInt64.decoder) (D.field "roots" identities) (D.field "history" identities) (D.field "origin" (D.nullable positive)) (D.field "steps" steps) (D.field "released" D.bool) (D.field "cancelled" D.bool) (D.field "consumed" D.bool))
        |> D.andThen (\chord -> if (chord.generation==UInt64.zero)==List.isEmpty chord.steps && List.all (\root -> List.member root chord.roots) chord.history then D.succeed chord else D.fail "Chord entry/history")

receiveChord : NativeChord -> Model -> (Model,List Effect)
receiveChord chord model =
    let old=model.nativeSwitcher
        order=old |> Maybe.map (\previous -> UInt64.compare chord.generation previous.generation) |> Maybe.withDefault GT
        inconsistent=old |> Maybe.map (\previous -> order==EQ && (previous.roots/=chord.roots || previous.history/=chord.history || previous.origin/=chord.origin || List.take (List.length previous.steps) chord.steps/=previous.steps || (previous.released && not chord.released) || (previous.cancelled && not chord.cancelled) || (previous.consumed && not chord.consumed))) |> Maybe.withDefault False
        closed =
            let retired=advance (retireSwitcher {model | notificationsOpen=False,notificationsOpening=False,settingsOpen=False,settingsOpening=False,nativeSwitcher=Just chord})
                choice=retired.choice |> Maybe.andThen (\pending -> if pending.chord==Just chord.generation then Nothing else Just pending)
            in ({retired | choice=choice},[])
    in if chord.generation==UInt64.zero || order==LT then (model,[]) else
       if inconsistent || chord.cancelled || chord.consumed then closed else
       let localGeneration=if order==GT then UInt64.next (Switcher.generation model.switcher) else Just (Switcher.generation model.switcher)
       in case localGeneration of
           Nothing -> (retireSwitcher model,[])
           Just generation ->
               let windows=model.windows
                   base=if order==GT then {model | notificationsOpen=False,notificationsOpening=False,settingsOpen=False,settingsOpening=False,nativeSwitcher=Just chord,choice=Nothing,choiceNotice="",open=False,overview=False,expected=Nothing,returnFocus=Nothing,menuOrigin=Nothing,switcherHistory=Nothing,switcherExpected=Nothing,windows={windows | picker=Nothing,menus=MenuBridge.retireChoices windows.menus}} else {model | notificationsOpen=False,notificationsOpening=False,settingsOpen=False,settingsOpening=False,nativeSwitcher=Just chord}
                   (stepped,_) = List.foldl (\(ordinal,direction) (state,_) -> Switcher.step generation (ordinal+1) direction state) (base.switcher,Nothing) (List.indexedMap Tuple.pair chord.steps)
                   (released,selected)=if chord.released then Switcher.release generation (List.length chord.steps) stepped else (stepped,Nothing)
                   next=advance {base | switcher=released}
               in case selected of
                   Just family -> chooseFamily family next
                   Nothing ->
                       let (synced,effects)=syncSwitcher next
                       in if order==GT && not (Shell.available next.windows.shell) then
                           let (refreshing,reads)=windowBase (TaskbarShell.Native Shell.Refresh) synced
                           in (refreshing,effects++reads)
                       else (synced,effects)

fenceSwitcherSelection : Maybe Counter -> Binding.Binding -> List Effect -> List Effect
fenceSwitcherSelection chord binding effects =
    effects |> List.concatMap (\effect -> case (chord,effect) of
        (Just generation,WindowEffect (Shell.Send raw)) ->
            case D.decodeValue (D.map3 (\kind request root -> (kind,request,root)) (D.field "kind" D.string) (D.at ["intent","request"] UInt64.decoder) (D.at ["intent","incarnation"] UInt64.decoder)) raw of
                Ok ("window-effect",request,root) -> [Send (E.object [("protocolVersion",E.int 3),("kind",E.string "switcher-selection-request"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request)),("chord",E.string (UInt64.string generation)),("root",E.string (UInt64.string root))]),effect]
                _ -> [effect]
        _ -> [effect])

canProveCatalogUnsent : Binding.Binding -> Counter -> Model -> Bool
canProveCatalogUnsent binding request model =
    model.windows.shell.binding==Just binding && model.expected==Just request
        && model.windows.shell.phase/=Shell.Detached && model.windows.shell.phase/=Shell.Exhausted

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
        Nothing -> retireSwitcher { model | presentation = Nothing, open = False, overview = False, applications = Nothing, expected = Nothing }


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
        pins = if disconnected || changed then Pins.initial else model.pins
        read = if changed && not disconnected then windows.shell.binding |> Maybe.andThen (\binding -> UInt64.next model.request |> Maybe.map (\request -> (binding,request))) else Nothing
        settingsRead = read |> Maybe.andThen (\(binding,request) -> UInt64.next request |> Maybe.map (\next -> (binding,next)))
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
        , overview = if disconnected || changed || windows.shell.phase==Shell.Exhausted then False else model.overview
        , overviewWorkspace = if disconnected || changed then Nothing else model.overviewWorkspace
        , snap = if disconnected || changed || windows.shell.phase==Shell.Exhausted then Nothing else
            model.snap |> Maybe.andThen (\choice -> case windows.shell.geometry of
                Nothing -> Just choice
                Just geometry -> if Snap.valid geometry choice then Just {choice|snapshot=geometry} else Nothing)
        , nativeSwitcher = if disconnected || changed || windows.shell.phase==Shell.Exhausted then Nothing else model.nativeSwitcher
        , switcher = if disconnected || changed || windows.shell.phase==Shell.Exhausted then Switcher.cancel (Switcher.generation model.switcher) model.switcher else model.switcher
        , switcherExpected = if disconnected || changed || windows.shell.phase==Shell.Exhausted then Nothing else model.switcherExpected
        , switcherHistory = if disconnected || changed || windows.shell.phase==Shell.Exhausted then Nothing else model.switcherHistory
        , pins = pins
        , notifications = if disconnected || changed then Notifications.initial else model.notifications
        , notificationsOpen = if disconnected || changed || windows.shell.phase==Shell.Exhausted then False else model.notificationsOpen
        , notificationsOpening = if disconnected || changed || windows.shell.phase==Shell.Exhausted then False else model.notificationsOpening
        , notificationsExpected = if disconnected || changed then Nothing else model.notificationsExpected
        , settings = if disconnected || changed then Settings.initial else model.settings
        , settingsOpen = if disconnected || changed || windows.shell.phase==Shell.Exhausted then False else model.settingsOpen
        , settingsOpening = if disconnected || changed || windows.shell.phase==Shell.Exhausted then False else model.settingsOpening
        , settingsExpected = if disconnected || changed then settingsRead |> Maybe.map Tuple.second else model.settingsExpected
        , request = settingsRead |> Maybe.map Tuple.second |> Maybe.withDefault (read |> Maybe.map Tuple.second |> Maybe.withDefault model.request)
        , applications = if disconnected || changed then Nothing else model.applications
        , expected = if disconnected || changed then read |> Maybe.map Tuple.second else model.expected
        , catalogFailure = if disconnected || changed then Nothing else model.catalogFailure
      }, (read |> Maybe.map (\(binding,request) -> [catalogRequest binding request]) |> Maybe.withDefault []) ++ (settingsRead |> Maybe.map (\(binding,request) -> [settingsRequest binding request]) |> Maybe.withDefault []) ++ List.map WindowEffect effects ++
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
        TaskbarShell.MenuEvent (Menu.Activate menuId binding index) ->
            let (next,effects)=windowBase message {model | returnFocus=Nothing}
                inactiveMinimize=case ((MenuBridge.menuSnapshot model.windows.menus).menu,MenuBridge.currentProvider model.windows.menus) of
                    (Just menu,Just provider) ->
                        menu.id==menuId && menu.binding==binding
                            && (menu.items |> List.drop index |> List.head |> Maybe.map .action)==Just Menu.Minimize
                            && (TaskbarShell.groups model.windows |> List.concatMap .families |> List.any (\family -> family.root==Provider.incarnation provider && not family.active))
                    _ -> False
                admitted=MenuBridge.preparedSnapshot model.windows.menus==Nothing && MenuBridge.preparedSnapshot next.windows.menus/=Nothing
            in if inactiveMinimize && admitted then ({next | returnFocus=model.menuOrigin},effects) else (next,effects)
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
                        in ({refreshing | returnFocus=Just {binding=binding,destination=TaskbarGroup picker.key,output=model.windows.shell.effects.observed |> Maybe.map (.context >> .output)}},List.filter (\effect -> case effect of
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
                                    in ({next | choice=Just {chord=Nothing,binding=binding,output=observed.context.output,root=root,application=family.application,token=token,placement=Nothing}},effects++[ArmChoice token])
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
                matchingGeometry = case message of
                    TaskbarShell.Native (Shell.Incoming raw) ->
                        D.decodeValue (D.map2 Tuple.pair (D.field "kind" D.string) (D.field "requestId" UInt64.decoder)) raw |> Result.map (\(kind,request) ->
                            kind=="geometry-facts" && model.windows.shell.geometryExpected==Just request
                                && (updated.windows.shell.geometry |> Maybe.map .request)==Just request
                                && updated.windows.shell.geometry/=model.windows.shell.geometry) |> Result.withDefault False
                    _ -> False
                matchingObservation = matchingProjection || matchingGeometry
                geometryOutput =
                    if updated.windows.shell.geometryCaps |> Maybe.map .effects |> Maybe.withDefault False then
                        updated.windows.shell.geometry |> Maybe.map (.context >> .output)
                    else updated.windows.shell.effects.observed |> Maybe.map (.context >> .output)
                (next,effects)=case updated.returnFocus of
                    Just target ->
                        let blocked=case target.destination of
                                TaskbarGroup groupKey -> TaskbarShell.groups updated.windows |> List.filter (\group -> group.key==groupKey) |> List.concatMap .families |> List.any (\family -> MenuBridge.blockedFor family.root updated.windows.shell updated.windows.menus)
                                OverviewOpener -> False
                        in if not matchingObservation || not (Shell.available updated.windows.shell) || blocked then (updated,ordinaryEffects) else
                            let retired={updated | returnFocus=Nothing}
                                exists=case target.destination of
                                    TaskbarGroup groupKey -> TaskbarShell.groups retired.windows |> List.any (\group -> group.key==groupKey && List.any .available group.families)
                                    OverviewOpener -> retired.choice==Nothing
                                focus=case target.destination of
                                    TaskbarGroup groupKey -> Shell.capture retired.windows.shell |> Maybe.map (\scope -> "group:" ++ Shell.stampKey scope ++ ":" ++ groupKey)
                                    OverviewOpener -> Just (key retired "control:overview-opener")
                            in if retired.open || retired.overview || retired.windows.picker/=Nothing || (MenuBridge.menuSnapshot retired.windows.menus).menu/=Nothing || retired.windows.shell.binding/=Just target.binding || target.output==Nothing || (retired.windows.shell.effects.observed |> Maybe.map (.context >> .output))/=target.output || geometryOutput/=target.output || not exists then (retired,ordinaryEffects) else
                                (retired,ordinaryEffects++(focus |> Maybe.map (Focus >> List.singleton) |> Maybe.withDefault []))
                    Nothing -> (updated,ordinaryEffects)

            in case next.choice of
                Just pending ->
                    if not matchingObservation || not (Shell.available next.windows.shell)
                        || (pending.placement/=Nothing && (next.windows.shell.geometry |> Maybe.map .blocked |> Maybe.withDefault True)) then (next,effects) else
                    let retired={next | choice=Nothing,choiceNotice="The window changed. Choose again."}
                        family=TaskbarShell.groups next.windows |> List.concatMap .families |> List.filter (\item -> item.root==pending.root && item.application==pending.application && item.available) |> List.head
                        output=next.windows.shell.effects.observed |> Maybe.map (.context >> .output)
                    in if next.windows.shell.binding/=Just pending.binding || output/=Just pending.output || geometryOutput/=Just pending.output then (retired,effects) else
                        case (Shell.capture next.windows.shell,family) of
                            (Just scope,Just selected) ->
                                case pending.placement of
                                    Just proposed ->
                                        case (next.windows.shell.geometry,Shell.captureGeometry next.windows.shell) of
                                            (Just geometry,Just stamp) ->
                                                let current={proposed|context=geometry.context}
                                                in if not (Snap.matches geometry pending.root current) then ({retired|choiceNotice="Output or window changed. Open snapping again."},effects) else
                                                    let (applied,commands)=windowBase (TaskbarShell.Native (Shell.Act stamp (Effects.SnapPlacement current) pending.root)) {retired|choiceNotice=""}
                                                    in (applied,effects++commands)
                                            _ -> (retired,effects)
                                    Nothing ->
                                        case Taskbar.selection selected of
                                            Taskbar.Apply operation root ->
                                                let (applied,commands)=windowBase (TaskbarShell.Native (Shell.Act scope operation root)) {retired | choiceNotice=""}
                                                in (applied,effects++fenceSwitcherSelection pending.chord pending.binding commands)
                                            _ -> (retired,effects)
                            _ -> (retired,effects)
                Nothing -> (next,effects)

update : Msg -> Model -> ( Model, List Effect )
update message model =
    case message of
        OpenSnap stamp root ->
            if capture model/=Just stamp || not (Shell.available model.windows.shell)
                || MenuBridge.blockedFor root model.windows.shell model.windows.menus then (model,[]) else
            case model.windows.shell.geometry |> Maybe.andThen (\geometry -> Snap.open geometry root) of
                Nothing -> (model,[])
                Just choice ->
                    let windows=model.windows
                    in (advance (retireSwitcher {model|notificationsOpen=False,notificationsOpening=False,settingsOpen=False,settingsOpening=False,snap=Just choice,open=False,overview=False,choice=Nothing,
                        expected=Nothing,returnFocus=Nothing,menuOrigin=Nothing,
                        windows={windows|picker=Nothing,menus=MenuBridge.retireChoices windows.menus}}),[])
        SelectSnap stamp region ->
            if capture model/=Just stamp then (model,[]) else
            case (model.windows.shell.geometry,model.snap) of
                (Just geometry,Just choice) -> ({model|snap=Snap.select geometry region choice},[])
                _ -> (model,[])
        ApplySnap stamp ->
            if capture model/=Just stamp || model.choice/=Nothing || not (Shell.available model.windows.shell)
                || not (model.windows.shell.geometryCaps |> Maybe.map (\caps -> List.member "snap" caps.operations) |> Maybe.withDefault False) then (model,[]) else
            case (model.snap,model.windows.shell.geometry) of
                (Just choice,Just geometry) ->
                    if not (Snap.valid geometry choice) then (model,[]) else
                    case (Snap.proposal choice,TaskbarShell.groups model.windows |> List.concatMap .families |> List.filter (\family -> family.root==choice.target && family.available) |> List.head) of
                        (Just proposed,Just family) ->
                            let (next,effects)=chooseFamily family {model|snap=Nothing}
                            in ({next|choice=next.choice |> Maybe.map (\pending -> {pending|placement=Just proposed})},effects)
                        _ -> (model,[])
                _ -> (model,[])
        CloseSnap stamp ->
            if capture model/=Just stamp || model.snap==Nothing then (model,[]) else
                (advance {model|snap=Nothing},[])
        InvalidateSnap ->
            if model.snap==Nothing then (model,[]) else
                windowBase (TaskbarShell.Native Shell.Refresh) (advance {model|snap=Nothing,choiceNotice="Output changed. Open snapping again."})
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
            in (retireSwitcher {retired | ownerScope=scope,ownerExhausted=False,snap=Nothing,menuOrigin=Nothing,returnFocus=Nothing},effects)
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
                            in (retireSwitcher {retired | snap=Nothing,ownerScope=Nothing,ownerExhausted=True,menuOrigin=Nothing,returnFocus=Nothing},[])
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
                                        (retireSwitcher {next | snap=Nothing,open=False,overview=False,expected=Nothing,returnFocus=Nothing,menuOrigin=model.windows.shell.binding |> Maybe.andThen (\binding -> TaskbarShell.groups model.windows |> List.filter (\group -> List.any (\family -> family.root==root) group.families) |> List.head |> Maybe.map (\group -> {binding=binding,destination=TaskbarGroup group.key,output=Just observed.context.output}))},effects)
        OpenSwitcher stamp direction ->
            if capture model/=Just stamp || model.choice/=Nothing || not (Shell.available model.windows.shell) || MenuBridge.preparedSnapshot model.windows.menus/=Nothing then (model,[]) else
            case UInt64.next (Switcher.generation model.switcher) of
                Nothing -> (retireSwitcher model,[])
                Just generation ->
                    let base=(MenuBridge.menuSnapshot model.windows.menus).menu |> Maybe.map (\menu -> windowBase (TaskbarShell.MenuEvent (Menu.Dismiss menu.id)) model |> Tuple.first) |> Maybe.withDefault model
                        origin=base.windows.shell.effects.observed |> Maybe.andThen (\observed -> Scene.focused observed.scene |> Maybe.andThen (\root -> Scene.rootOf root observed.scene))
                        (switcher,_)=Switcher.step generation 1 direction base.switcher
                        windows=base.windows
                        opened=advance {base | snap=Nothing,nativeSwitcher=Nothing,notificationsOpen=False,notificationsOpening=False,settingsOpen=False,settingsOpening=False,switcher=switcher,switcherOrigin=origin,switcherHistory=Nothing,open=False,overview=False,expected=Nothing,returnFocus=Nothing,menuOrigin=Nothing,windows={windows | picker=Nothing}}
                        (refreshing,commands)=windowBase (TaskbarShell.Native Shell.Refresh) opened
                        (next,history)=readSwitcherHistory refreshing
                    in (next,commands++history)
        SwitcherStep stamp direction ->
            if capture model/=Just stamp || not (switcherOpen model) then (model,[]) else
            let (switcher,chosen)=if model.nativeSwitcher/=Nothing then (Switcher.navigate direction model.switcher,Nothing) else Switcher.step (Switcher.generation model.switcher) (Switcher.lastStep model.switcher+1) direction model.switcher
                next=advance {model | switcher=switcher}
            in case chosen of
                Just family -> chooseFamily family next
                Nothing -> (next,switcherFocus next)
        SwitcherChoose stamp root ->
            if capture model/=Just stamp || not (switcherOpen model) then (model,[]) else
            if not (List.any (\family -> family.root==root) (Switcher.entries model.switcher)) then (model,[]) else
            let switcher=Switcher.choose (Switcher.generation model.switcher) root model.switcher
                (resolved,selected)=Switcher.commit (Switcher.generation switcher) switcher
            in case selected of
                Just family -> chooseFamily family (advance {model | switcher=resolved})
                Nothing -> (model,[])
        CommitSwitcher stamp ->
            if capture model/=Just stamp || not (switcherOpen model) then (model,[]) else
            let (switcher,selected)=Switcher.commit (Switcher.generation model.switcher) model.switcher
            in case selected of
                Just family -> chooseFamily family (advance {model | switcher=switcher})
                Nothing -> (model,[])
        CloseSwitcher stamp ->
            if capture model/=Just stamp || not (switcherOpen model) then (model,[]) else
            let closed=advance (retireSwitcher model)
            in case (model.nativeSwitcher,model.windows.shell.binding,UInt64.next model.request) of
                (Just chord,Just binding,Just request) ->
                    let (next,reads)=windowBase (TaskbarShell.Native Shell.Refresh) {closed | request=request}
                    in (next,Send (E.object [("protocolVersion",E.int 3),("kind",E.string "switcher-cancel-request"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request)),("chord",E.string (UInt64.string chord.generation))])::reads)
                _ -> windowBase (TaskbarShell.Native Shell.Refresh) closed
        Window value ->
            let (next,effects)=window value model
                (synced,commands)=syncSwitcher next
            in if next.windows.picker/=Nothing && next.windows.picker/=model.windows.picker then (retireSwitcher {next | snap=Nothing,open=False,overview=False,expected=Nothing,menuOrigin=Nothing,returnFocus=Nothing},effects) else (synced,effects++commands)
        Incoming raw ->
            case D.decodeValue (D.field "kind" D.string) raw of
                Ok "switcher-journal" ->
                    let decoder=strict ["protocolVersion","kind","binding","requestId","chord"] (D.map4 (\_ binding request chord -> {binding=binding,request=request,chord=chord}) version (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder) (D.field "chord" nativeChordDecoder))
                    in case D.decodeValue decoder raw of
                        Ok receipt -> if model.windows.shell.binding/=Just receipt.binding || model.windows.shell.phase==Shell.Detached || model.windows.shell.phase==Shell.Exhausted then (model,[]) else receiveChord receipt.chord model
                        Err _ -> (model,[])
                Ok "activation-history" ->
                    let positive=UInt64.decoder |> D.andThen (\value -> if value==UInt64.zero then D.fail "Zero history identity" else D.succeed value)
                        context= strict ["lifetime","epoch","output","revision"] (D.map4 (\lifetime epoch output revision -> {lifetime=lifetime,epoch=epoch,output=output,revision=revision}) (D.field "lifetime" positive) (D.field "epoch" positive) (D.field "output" positive) (D.field "revision" positive))
                        roots=D.list positive |> D.andThen (\rows -> if List.length rows<=256 && List.length (List.foldl (\root unique -> if List.member root unique then unique else root::unique) [] rows)==List.length rows then D.succeed rows else D.fail "History bounds/duplicates")
                        decoder=strict ["protocolVersion","kind","binding","requestId","context","roots"] (D.map5 (\_ binding request scope rows -> {binding=binding,request=request,context=scope,roots=rows}) version (D.field "binding" Binding.decoder) (D.field "requestId" positive) (D.field "context" context) (D.field "roots" roots))
                    in case D.decodeValue decoder raw of
                        Ok receipt ->
                            if not (switcherOpen model) || model.windows.shell.binding/=Just receipt.binding || model.switcherExpected/=Just receipt.request then (model,[]) else
                            syncSwitcher {model | switcherExpected=Nothing,switcherHistory=Just {context=receipt.context,roots=receipt.roots}}
                        Err _ -> (model,[])
                Ok "notification-snapshot" ->
                    let decoder=strict ["protocolVersion","kind","binding","requestId","snapshot"] (D.map4 (\_ binding request snapshot -> {binding=binding,request=request,snapshot=snapshot}) version (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder) (D.field "snapshot" Notifications.decoder))
                    in case D.decodeValue decoder raw of
                        Ok receipt ->
                            if model.windows.shell.binding/=Just receipt.binding || model.notificationsExpected/=Just receipt.request then (model,[]) else
                                let next=advance {model | notifications=Notifications.reconcile receipt.snapshot model.notifications,notificationsExpected=Nothing,notificationsOpening=False}
                                in (next,if model.notificationsOpen && model.notificationsOpening then [Focus (key next "notifications:close")] else [])
                        Err _ -> (model,[])
                Ok "notification-update" ->
                    let decoder=strict ["protocolVersion","kind","binding","snapshot"] (D.map3 (\_ binding snapshot -> {binding=binding,snapshot=snapshot}) version (D.field "binding" Binding.decoder) (D.field "snapshot" Notifications.decoder))
                    in case D.decodeValue decoder raw of
                        Ok receipt ->
                            if model.windows.shell.binding/=Just receipt.binding || model.windows.shell.phase==Shell.Detached then (model,[]) else
                                let notifications=Notifications.observe receipt.snapshot model.notifications
                                in if notifications==model.notifications then (model,[]) else (advance {model | notifications=notifications},[])
                        Err _ -> (model,[])
                Ok "notification-outcome" ->
                    let decoder=strict ["protocolVersion","kind","binding","requestId","status","snapshot"] (D.map5 (\_ binding request status snapshot -> {binding=binding,request=request,status=status,snapshot=snapshot}) version (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder) (D.field "status" D.string) (D.field "snapshot" Notifications.decoder))
                    in case D.decodeValue decoder raw of
                        Ok receipt ->
                            if model.windows.shell.binding/=Just receipt.binding then (model,[]) else
                                let notifications=Notifications.receive receipt.request receipt.status receipt.snapshot model.notifications
                                in if notifications==model.notifications then (model,[]) else (advance {model | notifications=notifications},[])
                        Err _ -> (model,[])
                Ok "shell-settings" ->
                    let decoder=strict ["protocolVersion","kind","binding","requestId","snapshot"] (D.map4 (\_ binding request snapshot -> {binding=binding,request=request,snapshot=snapshot}) version (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder) (D.field "snapshot" (D.nullable Settings.decoder)))
                    in case D.decodeValue decoder raw of
                        Ok receipt ->
                            if model.windows.shell.binding/=Just receipt.binding || model.settingsExpected/=Just receipt.request then (model,[]) else
                                let next=advance {model | settings=Settings.observe receipt.snapshot model.settings,settingsExpected=Nothing,settingsOpening=False}
                                in (next,if model.settingsOpen && model.settingsOpening then [Focus (key next "settings:close")] else [])
                        Err _ -> (model,[])
                Ok "shell-settings-outcome" ->
                    let decoder=strict ["protocolVersion","kind","binding","requestId","status","snapshot"] (D.map5 (\_ binding request status snapshot -> {binding=binding,request=request,status=status,snapshot=snapshot}) version (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder) (D.field "status" D.string) (D.field "snapshot" (D.nullable Settings.decoder)))
                    in case D.decodeValue decoder raw of
                        Ok receipt ->
                            if model.windows.shell.binding/=Just receipt.binding then (model,[]) else
                                let settings=Settings.receive receipt.request receipt.status receipt.snapshot model.settings
                                in if settings==model.settings then (model,[]) else (advance {model | settings=settings},[])
                        Err _ -> (model,[])
                Ok "application-catalog" ->
                    let decoder = D.keyValuePairs D.value |> D.andThen (\pairs ->
                            let fields=List.map Tuple.first pairs
                                legacy=not (List.member "preferences" fields)
                            in strict (["protocolVersion","kind","binding","requestId","snapshot"] ++ (if legacy then [] else ["preferences"])) (D.map5 (\_ binding request snapshot pins -> {binding=binding,request=request,snapshot=snapshot,pins=pins}) version (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder) (D.field "snapshot" D.value) (if legacy then D.succeed Nothing else D.field "preferences" (D.nullable Pins.decoder))))
                    in case D.decodeValue decoder raw of
                        Ok receipt ->
                            if model.windows.shell.phase /= Shell.Detached && model.windows.shell.binding == Just receipt.binding && model.expected == Just receipt.request then
                                let next = advance {model | launch = Launch.catalog receipt.snapshot model.launch, applications = Catalog.decode receipt.snapshot |> Result.toMaybe, pins = Pins.observe receipt.pins model.pins, expected = Nothing, catalogFailure = Nothing}
                                    target = "launcher-search"
                                in (next,if next.open then [Focus target] else [])
                            else (model,[])
                        Err _ -> (model,[])
                Ok "taskbar-pins-outcome" ->
                    let decoder = strict ["protocolVersion","kind","binding","requestId","status","preferences"] (D.map5 (\_ binding request status pins -> {binding=binding,request=request,status=status,pins=pins}) version (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder) (D.field "status" D.string) (D.field "preferences" (D.nullable Pins.decoder)))
                    in case D.decodeValue decoder raw of
                        Ok receipt ->
                            if model.windows.shell.phase==Shell.Detached || model.windows.shell.binding/=Just receipt.binding || not (List.member receipt.status ["Saved","Refused","Unknown"]) then (model,[]) else
                                let pins = Pins.receive receipt.request receipt.status receipt.pins model.pins
                                in ({model | pins=pins},if model.open && pins/=model.pins then [Focus "launcher-search"] else [])
                        Err _ -> (model,[])
                Ok "application-launch-outcome" ->
                    let decoder = strict ["protocolVersion","kind","binding","outcome"] (D.map3 (\_ binding outcome -> (binding,outcome)) version (D.field "binding" Binding.decoder) (D.field "outcome" D.value))
                    in case D.decodeValue decoder raw of
                        Ok (binding,outcome) ->
                            if model.windows.shell.phase /= Shell.Detached && model.windows.shell.binding == Just binding then
                                let launch = Launch.receive (host binding) outcome model.launch
                                    refused = Launch.status model.launch=="Pending" && Launch.status launch=="Refused"
                                    next = {model | launch = launch, open = if refused then True else model.open && Launch.status launch /= "Submitted"}
                                in (next,if refused then [Focus "launcher-search"] else [])
                            else (model,[])
                        Err _ -> (model,[])
                _ ->
                    let (next,effects)=window (TaskbarShell.Native (Shell.Incoming raw)) model
                        (synced,commands)=syncSwitcher next
                    in (synced,effects++commands)
        OpenNotifications stamp ->
            if capture model/=Just stamp || model.choice/=Nothing || model.windows.shell.binding==Nothing then (model,[]) else
            let windows=model.windows
                next=advance (retireSwitcher {model | notificationsOpen=True,notificationsOpening=True,settingsOpen=False,settingsOpening=False,open=False,overview=False,snap=Nothing,returnFocus=Nothing,menuOrigin=Nothing,windows={windows | picker=Nothing,menus=MenuBridge.retireChoices windows.menus}})
                (reading,commands)=readNotifications next
            in (reading,commands++[Focus (key reading "notifications:close")])
        CloseNotifications stamp ->
            if capture model/=Just stamp || not model.notificationsOpen then (model,[]) else
                let next=advance {model | notificationsOpen=False,notificationsOpening=False}
                in (next,[Focus (key next "notifications:opener")])
        RefreshNotifications stamp ->
            if capture model/=Just stamp || not model.notificationsOpen then (model,[]) else readNotifications model
        NotificationAction stamp target ->
            if capture model/=Just stamp || not model.notificationsOpen || model.notificationsExpected/=Nothing then (model,[]) else
            case (model.windows.shell.binding,UInt64.next model.request) of
                (Just binding,Just request) ->
                    let (notifications,proposal)=Notifications.propose request target model.notifications
                    in case proposal of
                        Nothing -> (model,[])
                        Just value -> (advance {model | notifications=notifications,request=request},[Send (E.object [("protocolVersion",E.int 3),("kind",E.string "notification-effect"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request)),("intent",value)])])
                _ -> (model,[])
        OpenSettings stamp ->
            if capture model/=Just stamp || model.choice/=Nothing || model.windows.shell.binding==Nothing then (model,[]) else
            let windows=model.windows
                next=advance (retireSwitcher {model | notificationsOpen=False,notificationsOpening=False,settingsOpen=True,settingsOpening=True,open=False,overview=False,snap=Nothing,returnFocus=Nothing,menuOrigin=Nothing,windows={windows | picker=Nothing,menus=MenuBridge.retireChoices windows.menus}})
                (reading,commands)=readSettings next
            in (reading,commands++[Focus (key reading "settings:close")])
        CloseSettings stamp ->
            if capture model/=Just stamp || not model.settingsOpen then (model,[]) else
                let next=advance {model | notificationsOpen=False,notificationsOpening=False,settingsOpen=False,settingsOpening=False}
                in (next,[Focus (key next "settings:opener")])
        EditSettings stamp values ->
            if capture model/=Just stamp || not model.settingsOpen then (model,[]) else
                (advance {model | settings=Settings.edit values model.settings},[])
        SaveSettings stamp ->
            if capture model/=Just stamp || not model.settingsOpen || model.settingsExpected/=Nothing then (model,[]) else
            case (model.windows.shell.binding,UInt64.next model.request) of
                (Just binding,Just request) ->
                    let (settings,proposal)=Settings.propose request model.settings
                    in case proposal of
                        Nothing -> (model,[])
                        Just value -> (advance {model | settings=settings,request=request},[Send (E.object [("protocolVersion",E.int 3),("kind",E.string "shell-settings-write"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request)),("proposal",value)])])
                _ -> (model,[])
        RefreshSettings stamp ->
            if capture model/=Just stamp || not model.settingsOpen then (model,[]) else readSettings model
        OpenApplications stamp ->
            if capture model /= Just stamp || MenuBridge.preparedSnapshot model.windows.menus/=Nothing then (model,[]) else
            let base =
                    case (MenuBridge.menuSnapshot model.windows.menus).menu of
                        Nothing -> model
                        Just menu -> windowBase (TaskbarShell.MenuEvent (Menu.Dismiss menu.id)) model |> Tuple.first
                windows=base.windows
                retired = advance (retireSwitcher {base | windows={windows | picker=Nothing}, returnFocus=Nothing, menuOrigin=Nothing, snap=Nothing, notificationsOpen=False,notificationsOpening=False,settingsOpen=False,settingsOpening=False,open = True, overview = False, applications = Nothing, launch = Launch.catalog E.null model.launch, expected = Nothing, catalogFailure = Nothing})
            in case (model.windows.shell.binding, UInt64.next model.request) of
                (Just binding,Just request) ->
                    if model.windows.shell.phase == Shell.Detached || retired.presentation == Nothing then (retired,[]) else
                        ({retired | request = request, expected = Just request},[catalogRequest binding request,Focus "launcher-search"])
                _ -> (retired,[])
        CatalogUnsent binding request ->
            if not (canProveCatalogUnsent binding request model) then (model,[]) else
                ({model | expected=Nothing,catalogFailure=Just {binding=binding,request=request}},[])
        CloseApplications stamp ->
            if capture model /= Just stamp || not model.open then (model,[]) else
                let next = advance {model | open = False, expected = Nothing}
                in (next,[Focus (key next "control:opener")])
        OpenOverview stamp ->
            if capture model/=Just stamp || model.choice/=Nothing || not (Shell.available model.windows.shell) || MenuBridge.preparedSnapshot model.windows.menus/=Nothing then (model,[]) else
            let base = (MenuBridge.menuSnapshot model.windows.menus).menu
                    |> Maybe.map (\menu -> windowBase (TaskbarShell.MenuEvent (Menu.Dismiss menu.id)) model |> Tuple.first)
                    |> Maybe.withDefault model
                windows=base.windows
                next=advance (retireSwitcher {base | snap=Nothing,notificationsOpen=False,notificationsOpening=False,settingsOpen=False,settingsOpening=False,overview=True,overviewWorkspace=Nothing,open=False,expected=Nothing,returnFocus=Nothing,menuOrigin=Nothing,windows={windows | picker=Nothing}})
                focus=TaskView.activeWorkspace next.windows.shell |> Maybe.map (\workspace -> key next ("overview:workspace:"++workspace)) |> Maybe.withDefault (key next "overview:all")
            in (next,[Focus focus])
        CloseOverview stamp ->
            if capture model/=Just stamp || not model.overview then (model,[]) else
                let next=advance {model | overview=False,overviewWorkspace=Nothing}
                    (refreshing,commands)=windowBase (TaskbarShell.Native Shell.Refresh) next
                    target=model.windows.shell.binding |> Maybe.map (\binding -> {binding=binding,destination=OverviewOpener,output=model.windows.shell.effects.observed |> Maybe.map (.context >> .output)})
                in ({refreshing | returnFocus=target},commands)
        OverviewWorkspace stamp selected ->
            if capture model/=Just stamp || not model.overview || selected==model.overviewWorkspace then (model,[]) else
            let exists=selected |> Maybe.map (\workspace -> TaskView.groups model.windows.shell |> Maybe.map (List.any (\g -> g.identity==workspace)) |> Maybe.withDefault False) |> Maybe.withDefault True
                next=advance {model | overviewWorkspace=selected}
            in if not exists then (model,[]) else (next,[Focus (key next (selected |> Maybe.map ((++) "overview:workspace:") |> Maybe.withDefault "overview:all"))])
        OverviewChoose stamp root ->
            if capture model/=Just stamp || not model.overview || model.choice/=Nothing || not (Shell.available model.windows.shell) then (model,[]) else
            let selected=TaskView.groups model.windows.shell |> Maybe.withDefault []
                    |> List.filter (\g -> model.overviewWorkspace==Nothing || model.overviewWorkspace==Just g.identity)
                    |> List.concatMap .windows |> List.filter (\family -> family.root==root && family.available && not (MenuBridge.blockedFor root model.windows.shell model.windows.menus)) |> List.head
            in case (selected,model.windows.shell.binding,model.windows.shell.effects.observed) of
                (Just family,Just binding,Just observed) ->
                    let (next,effects)=windowBase (TaskbarShell.Native Shell.Refresh) {model | overview=False,choiceNotice=""}
                    in case next.windows.shell.expected of
                        Just request ->
                            let token=ChoiceToken binding request
                            in ({next | choice=Just {chord=Nothing,binding=binding,output=observed.context.output,root=root,application=family.application,token=token,placement=Nothing}},effects++[ArmChoice token])
                        Nothing -> (next,effects)
                _ -> (model,[])
        SearchQuery stamp query ->
            if capture model /= Just stamp || not model.open || query==model.query || String.length query > 256 || String.any (\c -> Char.toCode c < 32 || Char.toCode c == 127) query then (model,[]) else
                (advance {model | query=query},[])
        TogglePin stamp identity ->
            if capture model/=Just stamp || not model.open || not (Pins.writable model.pins) || (not (List.member identity (pinIdentities model)) && (model.applications |> Maybe.andThen (Catalog.lookup identity))==Nothing) then (model,[]) else
                savePins (Pins.toggle identity (pinIdentities model)) model
        MovePin stamp identity direction ->
            if capture model/=Just stamp || not model.open || not (Pins.writable model.pins) then (model,[]) else
                savePins (Pins.move identity direction (pinIdentities model)) model
        Start selection ->
            if MenuBridge.preparedSnapshot model.windows.menus/=Nothing then (model,[]) else
            let (launch,intent) = Launch.start selection model.launch
            in case (intent,model.windows.shell.binding) of
                (Just wire,Just binding) ->
                    (retireSwitcher {model | launch = launch, open = False, overview = False, expected = Nothing},Send (E.object [("protocolVersion",E.int 3),("kind",E.string "application-launch"),("binding",Binding.encode binding),("intent",wire)]) :: (Launch.pending launch |> Maybe.map (Arm >> List.singleton) |> Maybe.withDefault []))
                _ -> ({model | launch = launch},[])
        Deadline token -> ({model | launch = Launch.timeout token model.launch},[])
        Acknowledge token -> ({model | launch = Launch.acknowledgeUnknown token model.launch},[])


catalogRequest : Binding.Binding -> Counter -> Effect
catalogRequest binding request = Send (E.object [("protocolVersion",E.int 3),("kind",E.string "catalog-request"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request))])

pinIdentities : Model -> List String
pinIdentities model = model.pins.snapshot |> Maybe.map .identities |> Maybe.withDefault []

savePins : List String -> Model -> (Model,List Effect)
savePins values model =
    case (model.windows.shell.binding,UInt64.next model.request) of
        (Just binding,Just request) ->
            let (pins,proposal)=Pins.propose request values model.pins
                wire p=E.object [("protocolVersion",E.int 3),("kind",E.string "taskbar-pins-write"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request)),("proposal",p)]
            in case proposal of
                Just p ->
                    if Pins.bytes (E.encode 0 (wire p))>4095 then ({model|pins={pins|pending=Nothing,notice="Pin order is too large to save."}},[]) else
                        (advance {model|pins=pins,request=request},[Send (wire p)])
                Nothing -> (model,[])
        _ -> (model,[])

pinnedGroup : String -> Model -> Maybe Taskbar.Group
pinnedGroup identity model =
    case pinGroups identity model of
        [group] -> Just group
        _ -> Nothing

pinGroups : String -> Model -> List Taskbar.Group
pinGroups identity model =
    case model.applications |> Maybe.andThen (Catalog.lookup identity) of
        Nothing -> []
        Just entry -> TaskbarShell.groups model.windows |> List.filter (\group -> List.any (\family -> family.application==identity || (not (String.isEmpty entry.wmclass) && family.application==entry.wmclass)) group.families)

settingsRequest : Binding.Binding -> Counter -> Effect
settingsRequest binding request = Send (E.object [("protocolVersion",E.int 3),("kind",E.string "shell-settings-request"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request))])

readSettings : Model -> (Model,List Effect)
readSettings model =
    case (model.windows.shell.binding,UInt64.next model.request) of
        (Just binding,Just request) -> (advance {model | request=request,settingsExpected=Just request},[settingsRequest binding request])
        _ -> (model,[])

readNotifications : Model -> (Model,List Effect)
readNotifications model =
    if model.notificationsExpected/=Nothing then (model,[]) else
    case (model.windows.shell.binding,UInt64.next model.request) of
        (Just binding,Just request) ->
            (advance {model | request=request,notificationsExpected=Just request},[Send (E.object [("protocolVersion",E.int 3),("kind",E.string "notification-request"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request))])])
        _ -> (model,[])
