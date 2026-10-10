module Surface exposing (Control, controls, mode, packet, resolve)

import Menu
import Switcher
import Pins
import Settings
import Motion
import MotionPreferences
import Notifications
import JumpList
import Files
import SystemMenu
import MenuBridge
import Provider
import Catalog
import Desktop
import Effects
import Json.Decode as D
import Json.Encode as E
import Launch
import Shell
import Taskbar
import TaskbarShell
import TaskView
import Transfer
import Snap
import GeometryProjection
import UInt64 exposing (Counter)

type alias Control =
    { id : String, domId : String, label : String, ariaLabel : String, detail : String, enabled : Bool, message : Maybe Desktop.Msg }

confirmedWindowState : Desktop.Model -> Counter -> String
confirmedWindowState model root =
    let shell=model.windows.shell
    in if shell.geometryExpected/=Nothing then "" else
        shell.geometry |> Maybe.andThen (\observed -> if shell.binding/=Just observed.binding then Nothing else GeometryProjection.window root observed)
            |> Maybe.map (\window -> String.join " • " ((if window.nativeMode==GeometryProjection.Maximized then ["Maximized"] else []) ++ (window.pin |> Maybe.map (\pin -> if pin.pinned then ["Always on top"] else []) |> Maybe.withDefault [])))
            |> Maybe.withDefault ""

reservationReason : String
reservationReason = "Window action awaits native confirmation. Refresh status only reads observations; it does not retry the action."

familyBlocked : Desktop.Model -> Counter -> Bool
familyBlocked model incarnation = MenuBridge.blockedFor incarnation model.windows.shell model.windows.menus

menuBlocked : Desktop.Model -> Bool
menuBlocked model = MenuBridge.currentProvider model.windows.menus |> Maybe.map (Provider.incarnation >> familyBlocked model) |> Maybe.withDefault False

recoveryNeeded : Desktop.Model -> Bool
recoveryNeeded model = List.any (\transaction -> List.member transaction.status [Effects.Pending,Effects.Unknown]) model.windows.shell.effects.unresolved || (model.windows.shell.effects.transaction |> Maybe.map (\transaction -> List.member transaction.status [Effects.Refused,Effects.Unknown]) |> Maybe.withDefault False) || (MenuBridge.menuSnapshot model.windows.menus).outstanding > 0

recoveryControl : String -> Desktop.Model -> Control
recoveryControl identity model =
    {id=identity,domId=Desktop.key model identity,label="Refresh window status",ariaLabel="Refresh window status; read observations without retrying actions",detail="Observation only",enabled=model.windows.shell.phase/=Shell.Detached && model.windows.shell.phase/=Shell.Exhausted && not (Effects.pending model.windows.shell.effects),message=Just (Desktop.Window (TaskbarShell.Native Shell.Refresh))}

recoveryPopup : Desktop.Model -> List Control
recoveryPopup model = if recoveryNeeded model then [recoveryControl "control:recovery-refresh" model] else []

mode : Desktop.Model -> String
mode model =
    if model.jumpEntry/=Nothing then "jump"
    else if model.filesOpen then "files"
    else if model.systemMenuOpen then "system"
    else if model.notificationsOpen then "notifications"
    else if model.settingsOpen then "settings"
    else if model.snap/=Nothing then "snap"
    else if Desktop.switcherOpen model then "switcher"
    else if model.overview then "overview"
    else if model.open then "applications"
    else if (MenuBridge.menuSnapshot model.windows.menus).menu/=Nothing then "menu"
    else if model.windows.picker /= Nothing then "picker"
    else "closed"

controls : Desktop.Model -> List Control
controls model =
    if model.jumpEntry/=Nothing then
        let scoped message=Desktop.capture model |> Maybe.map message
            control identity label detail enabled message={id=identity,domId=Desktop.key model (if identity=="control:close" then "jump:close" else identity),label=label,ariaLabel=label,detail=detail,enabled=enabled,message=if enabled then scoped message else Nothing}
            current=model.jumpList.snapshot |> Maybe.andThen (\snapshot -> if Just snapshot.entry==model.jumpEntry then Just snapshot else Nothing)
            row snapshot action=
                let intent=JumpList.intent snapshot action.id
                in control ("jump:action:"++action.id) action.label (if action.kind=="recent" then "Recent file" else "Application action") (model.jumpExpected==Nothing && JumpList.supported intent model.jumpList) (\stamp -> Desktop.JumpAction stamp intent)
            title=current |> Maybe.map (\snapshot -> "Actions for "++snapshot.name) |> Maybe.withDefault "Application actions"
            entries=current |> Maybe.map (\snapshot -> List.map (row snapshot) snapshot.actions) |> Maybe.withDefault []
        in [control "control:close" "Close application actions" "" True Desktop.CloseJumpList
           ,control "jump:refresh" "Refresh application actions" "Read actions; never repeat a request" (model.jumpExpected==Nothing) Desktop.RefreshJumpList
           ,control "jump:title:state" title "" False Desktop.CloseJumpList]
           ++entries++(if List.isEmpty entries && model.jumpExpected==Nothing then [control "jump:empty:state" "No supported actions or recent files." "" False Desktop.CloseJumpList] else [])
    else if model.filesOpen then
        let scoped message=Desktop.capture model |> Maybe.map message
            control identity label detail enabled message={id=identity,domId=Desktop.key model (if identity=="control:close" then "files:close" else identity),label=label,ariaLabel=label,detail=detail,enabled=enabled,message=if enabled then scoped message else Nothing}
            ready target=model.filesExpected==Nothing && (model.files.snapshot |> Maybe.map (\snapshot -> Files.supported (Files.intent snapshot target) model.files) |> Maybe.withDefault False)
            openTarget target stamp=model.files.snapshot |> Maybe.map (\snapshot -> Desktop.OpenFilesTarget stamp (Files.intent snapshot target)) |> Maybe.withDefault (Desktop.CloseFiles stamp)
            collection (identifier,label)=control ("files:collection:"++identifier) label "" (ready ("coll:"++identifier)) (openTarget ("coll:"++identifier))
            location=model.files.snapshot |> Maybe.andThen .peer |> Maybe.map (\peer -> "Current location: "++peer.target) |> Maybe.withDefault "No Files window observed."
        in [control "control:close" "Close Files menu" "" True Desktop.CloseFiles
           ,control "files:refresh" "Refresh Files state" "Read location; never repeat an opening" (model.filesExpected==Nothing) Desktop.RefreshFiles
           ,control "files:location:state" location "" False Desktop.CloseFiles
           ,control "files:home" "Home" "" (ready "home") (openTarget "home")]
           ++List.map collection Files.collections
           ++[{id="control:files-path",domId=Desktop.key model "files:path",label=model.files.draft,ariaLabel="Folder path",detail="",enabled=True,message=scoped (\stamp -> Desktop.EditFilesPath stamp model.files.draft)}
             ,control "files:open-path" "Open folder" "Open this path in Files" (ready model.files.draft) Desktop.OpenFilesPath]
    else if model.systemMenuOpen then
        let scoped action=Desktop.capture model |> Maybe.map action
            control identity label detail enabled message={id=identity,domId=Desktop.key model (if identity=="control:close" then "system:close" else identity),label=label,ariaLabel=label,detail=detail,enabled=enabled,message=if enabled then scoped message else Nothing}
            state section value=control ("system:"++section++":state") value "" False Desktop.CloseSystemMenu
            rows snapshot =
                let change operation value label=
                        let intent=SystemMenu.intent snapshot operation value
                            ready=model.systemMenu.pending==Nothing && model.systemMenuExpected==Nothing && model.systemMenuConfirmation==Nothing && SystemMenu.supported intent model.systemMenu
                        in control ("system:"++SystemMenu.code operation++":"++String.fromInt value) label "" ready (\stamp -> Desktop.SystemChange stamp intent)
                    volume=case snapshot.volume of
                        Nothing -> [state "volume" "Volume unavailable"]
                        Just current -> state "volume" ("Volume "++String.fromInt current.percent++"%"++(if current.muted then "; muted" else "; unmuted")++" · "++current.label) :: (List.map (\percent -> change SystemMenu.Volume percent ("Set volume "++String.fromInt percent++"%")) [0,25,50,75,100]) ++ [change SystemMenu.Mute (if current.muted then 0 else 1) (if current.muted then "Unmute" else "Mute")]
                    network=case snapshot.network of
                        Nothing -> [state "network" "Network unavailable"]
                        Just current -> [state "network" ("Network "++(if current.enabled then "enabled" else "disabled")++" · "++current.state++(if current.permission=="no" then "; changes unavailable" else "")),change SystemMenu.Network (if current.enabled then 0 else 1) (if current.enabled then "Disable networking" else "Enable networking")]
                    capability value=if value=="yes" then "available" else if value=="challenge" then "authorization required" else "unavailable"
                    power=case snapshot.power of
                        Nothing -> [state "power" "Power controls unavailable"]
                        Just current -> [state "power" ("Power · suspend "++capability current.suspend++", restart "++capability current.reboot++", shutdown "++capability current.poweroff),change SystemMenu.Suspend 0 "Suspend",change SystemMenu.Reboot 0 "Restart",change SystemMenu.PowerOff 0 "Shut down"]
                    session=case snapshot.session of
                        Nothing -> [state "session" "Session controls unavailable"]
                        Just current -> [state "session" ("Session "++current.name++" · "++current.state++(if current.locked then "; locked" else "; unlocked")),change SystemMenu.Lock 0 "Lock session",change SystemMenu.Logout 0 "Log out"]
                in volume++network++power++session
            confirmation=case model.systemMenuConfirmation of
                Nothing -> []
                Just intent -> [state "confirmation" ("Confirm "++SystemMenu.name intent.operation++"? Unsaved work or active connections may be affected."),control "system:cancel" "Cancel system change" "" True Desktop.CancelSystemChange,control "system:confirm" ("Confirm "++SystemMenu.name intent.operation) "" (SystemMenu.supported intent model.systemMenu && model.systemMenu.pending==Nothing && model.systemMenuExpected==Nothing) (\stamp -> Desktop.ConfirmSystemChange stamp intent)]
        in [control "control:close" "Close system menu" "" True Desktop.CloseSystemMenu,control "system:refresh" "Refresh system state" "Read current state; never repeat a change" (model.systemMenuExpected==Nothing) Desktop.RefreshSystemMenu]
           ++ (model.systemMenu.snapshot |> Maybe.map rows |> Maybe.withDefault []) ++ confirmation
    else if model.notificationsOpen then
        let scoped message=Desktop.capture model |> Maybe.map message
            control identity label detail enabled message={id=identity,domId=Desktop.key model (if identity=="control:close" then "notifications:close" else identity),label=label,ariaLabel=label,detail=detail,enabled=enabled,message=if enabled then scoped message else Nothing}
            clean value=String.join " " (String.words value)
            entryRows snapshot entry=
                let prefix="notification:"++UInt64.string snapshot.service++":"++UInt64.string entry.incarnation
                    textRow identity label detail={id=identity,domId=Desktop.key model identity,label=clean label,ariaLabel=clean label,detail=detail,enabled=False,message=Nothing}
                    action verb key label=
                        let target=Notifications.target snapshot entry verb key
                            ready=Notifications.live target model.notifications && model.notifications.pending==Nothing && model.notificationsExpected==Nothing
                        in control (Notifications.identity target) (clean label) "" ready (\stamp -> Desktop.NotificationAction stamp target)
                in [textRow (prefix++":summary") (entry.app++": "++entry.summary) (if entry.state=="live" then "Live" else "History · "++entry.state)]
                   ++ (if String.isEmpty entry.body then [] else [textRow (prefix++":body") entry.body ""])
                   ++ (if entry.state=="live" then List.map (\item -> action "invoke" item.key item.label) entry.actions ++ [action "dismiss" "" "Dismiss notification"] else [])
        in [control "control:close" "Close notifications" "" True Desktop.CloseNotifications
           ,control "notifications:refresh" "Refresh notifications" "Read current targets; no action is repeated" (model.notificationsExpected==Nothing) Desktop.RefreshNotifications]
           ++ (model.notifications.snapshot |> Maybe.map (\snapshot -> List.concatMap (entryRows snapshot) snapshot.entries) |> Maybe.withDefault [])
    else if model.settingsOpen then
        let scoped message=Desktop.capture model |> Maybe.map message
            ready=Settings.writable model.settings && model.settingsExpected==Nothing
            control identity label detail enabled message={id=identity,domId=Desktop.key model (if identity=="control:close" then "settings:close" else identity),label=label,ariaLabel=label,detail=detail,enabled=enabled,message=if enabled then scoped message else Nothing}
            theme selected label=control ("settings:theme:"++Settings.themeName selected) label (if model.settings.draft.theme==selected then "Selected" else "") ready (\stamp -> Desktop.EditSettings stamp {theme=selected,textScale=model.settings.draft.textScale})
            scale percent=control ("settings:scale:"++String.fromInt percent) ("Text size "++String.fromInt percent++"%") (if model.settings.draft.textScale==percent then "Selected" else "") ready (\stamp -> Desktop.EditSettings stamp {theme=model.settings.draft.theme,textScale=percent})
            motionReady=MotionPreferences.writable model.motion.preferences && model.motionExpected==Nothing
            motionOption selected=control ("settings:motion:"++(case selected of
                MotionPreferences.System -> "system"
                MotionPreferences.Reduce -> "reduced"
                MotionPreferences.Full -> "full")) (MotionPreferences.label selected) (if model.motion.preferences.draft==selected then "Selected" else "") motionReady (\stamp -> Desktop.EditMotionPreference stamp selected)
            changed=model.settings.snapshot |> Maybe.map (\current -> current.values/=model.settings.draft) |> Maybe.withDefault False
            guidance =
                if not model.settingsHelp then [] else
                    [control "settings:help:text:keyboard" "Keyboard navigation" "Tab and Shift+Tab move focus. Arrows move through lists; Home/End reach endpoints. Enter chooses; Escape closes." False Desktop.ToggleSettingsHelp
                    ,control "settings:help:text:preferences" "Keeping your preferences" "Save settings applies theme and text size. Motion has a separate Save control. Dismissing help keeps unsaved edits." False Desktop.ToggleSettingsHelp
                    ,control "settings:help:text:recovery" "When an action is not confirmed" "Pending is waiting; Refused did not proceed; Unknown is unconfirmed. Refresh reads state without repeating an action." False Desktop.ToggleSettingsHelp]
        in [control "control:close" "Close settings" "" True Desktop.CloseSettings
           ,control "settings:help" (if model.settingsHelp then "Dismiss help" else "Show help") (if model.settingsHelp then "Expanded" else "Collapsed") True Desktop.ToggleSettingsHelp]
           ++guidance
           ++[control "settings:motion" (Motion.notice model.motion) model.motion.preferences.notice False Desktop.RefreshMotionPreference
           ,motionOption MotionPreferences.System,motionOption MotionPreferences.Reduce,motionOption MotionPreferences.Full
           ,control "settings:motion:save" "Save motion preference" "Apply and keep across restart" (motionReady && model.motion.preferences.draft/=MotionPreferences.selected model.motion.preferences) Desktop.SaveMotionPreference
           ,control "settings:motion:refresh" "Refresh motion preference" "Read stored preference; no write is repeated" (model.motionExpected==Nothing) Desktop.RefreshMotionPreference
           ,theme Settings.Night "Night theme",theme Settings.Dawn "Dawn theme",theme Settings.HighContrast "High contrast theme"]++List.map scale [100,125,150,200]
           ++[control "settings:save" "Save settings" "Apply and keep across restart" (ready && changed) Desktop.SaveSettings
             ,control "settings:refresh" "Refresh settings" "Read stored values; discard unsaved changes" (model.settingsExpected==Nothing) Desktop.RefreshSettings]
    else if model.snap/=Nothing then
        case model.snap of
            Nothing -> []
            Just choice ->
                let scoped message=Desktop.capture model |> Maybe.map message
                    ready=Shell.available model.windows.shell
                    placement=Snap.proposal choice
                    applyReady=ready && model.choice==Nothing && (model.windows.shell.geometryCaps |> Maybe.map (\caps -> List.member "snap" caps.operations) |> Maybe.withDefault False) && placement/=Nothing
                    applyLabel=if applyReady then "Snap to "++String.toLower (Snap.name choice.selected) else "Snapping unavailable"
                    regionControl region=
                        let identity="snap:region:"++Snap.identity region
                            selected=region==choice.selected
                        in {id=identity,domId=Desktop.key model identity,label=Snap.name region,
                            ariaLabel=Snap.name region++(if selected then "; selected preview" else ""),
                            detail=if selected then "Selected" else "",enabled=ready,
                            message=if ready then scoped (\stamp -> Desktop.SelectSnap stamp region) else Nothing}
                in {id="control:close",domId=Desktop.key model "snap:close",label="Close",ariaLabel="Close snapping",detail="",enabled=True,message=scoped Desktop.CloseSnap}
                    :: List.map regionControl Snap.regions
                    ++ [{id="snap:apply",domId=Desktop.key model "snap:apply",label=applyLabel,ariaLabel=applyLabel,detail="",enabled=applyReady,message=if applyReady then scoped Desktop.ApplySnap else Nothing}]
    else if Desktop.switcherOpen model then
        let scoped message=Desktop.capture model |> Maybe.map message
            selected=Switcher.selected model.switcher |> Maybe.map .root
            browsing=Switcher.phase model.switcher==Switcher.Browsing
            row family=
                let ready=browsing && family.available && not (familyBlocked model family.root)
                    identity="switcher:family:"++UInt64.string family.root
                    detail=if selected==Just family.root then "Selected" else if family.minimized then "Minimized" else "Open"
                in {id=identity,domId=Desktop.key model identity,label=family.label,ariaLabel=(if family.minimized then "Restore " else "Activate ")++family.label++(if selected==Just family.root then "; selected" else ""),detail=detail,enabled=ready,message=if ready then scoped (\stamp -> Desktop.SwitcherChoose stamp family.root) else Nothing}
            control identity label enabled message={id=identity,domId=Desktop.key model identity,label=label,ariaLabel=label,detail="",enabled=enabled,message=if enabled then scoped message else Nothing}
        in [control "control:close" "Cancel window switcher" True Desktop.CloseSwitcher
           ,control "control:reverse" "Previous window" True (\stamp -> Desktop.SwitcherStep stamp Switcher.Reverse)
           ,control "control:forward" "Next window" True (\stamp -> Desktop.SwitcherStep stamp Switcher.Forward)
           ,control "control:commit" "Activate selected window" (browsing && (selected |> Maybe.map (familyBlocked model >> not) |> Maybe.withDefault False)) Desktop.CommitSwitcher]
           ++ List.map row (Switcher.entries model.switcher)
    else if model.overview then
        let
            transferReady=Shell.available model.windows.shell && model.choice==Nothing
            scoped message = Desktop.capture model |> Maybe.map message
            groups = TaskView.groups model.windows.shell |> Maybe.withDefault []
            workspaceControl group =
                {id="overview:workspace:"++group.identity,domId=Desktop.key model ("overview:workspace:"++group.identity),label="Workspace "++group.identity,ariaLabel="Browse workspace "++group.identity++(if group.active then "; active workspace" else ""),detail=(if group.active then "Active workspace" else "")++(if model.overviewWorkspace==Just group.identity then " • Selected" else ""),enabled=True,message=scoped (\stamp -> Desktop.OverviewWorkspace stamp (Just group.identity))}
            familyControl group family =
                let ready=Shell.available model.windows.shell && family.available && not (familyBlocked model family.root)
                    identity="overview:family:"++UInt64.string family.root
                    detail="Workspace "++group.identity++" • "++(if familyBlocked model family.root then "Awaiting native confirmation" else if not family.available then "Unavailable for activation" else if family.minimized then "Minimized" else "Open")
                in {id=identity,domId=Desktop.key model identity,label=family.label,ariaLabel=(if family.minimized then "Restore " else "Activate ")++family.label++" on workspace "++group.identity,detail=detail,enabled=ready,message=if ready then scoped (\stamp -> Desktop.OverviewChoose stamp family.root) else Nothing}
            transferControl family =
                let identity="overview:transfer:"++UInt64.string family.root
                    enabled=transferReady && family.available && not (familyBlocked model family.root) && (model.windows.shell.geometryCaps |> Maybe.map (\caps -> List.member "transfer-workspace" caps.operations) |> Maybe.withDefault False)
                in {id=identity,domId=Desktop.key model identity,label="Move "++family.label++"…",ariaLabel="Move "++family.label++" to another workspace",detail="",enabled=enabled,message=if enabled then scoped (\stamp -> Desktop.OpenOverviewTransfer stamp family.root) else Nothing}
            destinationRows root = model.windows.shell.geometry |> Maybe.map (\geometry ->
                Transfer.destinations geometry |> List.filterMap (\destination -> Transfer.propose geometry root destination |> Maybe.map (\_ ->
                    let identity="overview:destination:"++destination
                    in {id=identity,domId=Desktop.key model identity,label="Move to workspace "++destination,ariaLabel="Move selected window to workspace "++destination,detail="",enabled=transferReady,message=if transferReady then scoped (\stamp -> Desktop.OverviewTransfer stamp root destination) else Nothing}))) |> Maybe.withDefault []
            workspaceRows group = workspaceControl group ::
                (if model.overviewWorkspace==Nothing || model.overviewWorkspace==Just group.identity then List.concatMap (\family -> [familyControl group family,transferControl family]) group.windows else [])
        in if model.overviewTransfer/=Nothing then
            [{id="control:close",domId=Desktop.key model "overview:transfer-cancel",label="Cancel transfer",ariaLabel="Cancel window transfer",detail="",enabled=True,message=scoped Desktop.CancelOverviewTransfer}]
                ++ (model.overviewTransfer |> Maybe.map destinationRows |> Maybe.withDefault [])
        else [{id="control:close",domId=Desktop.key model "overview:close",label="Close Task View",ariaLabel="Close Task View and return to windows",detail="",enabled=True,message=scoped Desktop.CloseOverview}
           ,{id="overview:all",domId=Desktop.key model "overview:all",label="All windows",ariaLabel="Browse all workspaces",detail=if model.overviewWorkspace==Nothing then "Selected" else "",enabled=True,message=scoped (\stamp -> Desktop.OverviewWorkspace stamp Nothing)}]
            ++ List.concatMap workspaceRows groups ++ [recoveryControl "overview:refresh" model]
    else if model.open then
        let
            scoped build = Desktop.capture model |> Maybe.map build
            entries = model.applications |> Maybe.map (Catalog.search model.query) |> Maybe.withDefault []
            ready = not (List.member (Launch.status model.launch) ["Pending","Unknown"])
            entryControl entry =
                let choice = if ready then Launch.select (Catalog.id entry.identity) model.launch |> Maybe.map Desktop.Start else Nothing
                in {id="entry:" ++ Catalog.id entry.identity,domId=Desktop.key model ("entry:" ++ Catalog.id entry.identity),label="Open " ++ entry.name,ariaLabel="Open " ++ entry.name,detail="",enabled=choice/=Nothing,message=choice}
            pinIds = Desktop.pinIdentities model
            pinAction suffix label detail allowed message = {id=suffix,domId=Desktop.key model suffix,label=label,ariaLabel=label,detail=detail,enabled=Pins.writable model.pins && allowed,message=if Pins.writable model.pins && allowed then scoped message else Nothing}
            pinFirst = entries |> List.head |> Maybe.andThen (\entry -> if List.member (Catalog.id entry.identity) pinIds then Nothing else Just (pinAction ("pin:" ++ Catalog.id entry.identity) ("Pin " ++ entry.name) "Add to taskbar" True (\stamp -> Desktop.TogglePin stamp (Catalog.id entry.identity)))) |> Maybe.map List.singleton |> Maybe.withDefault []
            pinRows index identity =
                let label=model.applications |> Maybe.andThen (Catalog.lookup identity) |> Maybe.map .name |> Maybe.withDefault identity
                in [pinAction ("unpin:" ++ identity) ("Unpin " ++ label) "Pinned application" True (\stamp -> Desktop.TogglePin stamp identity)
                   ,pinAction ("pin-left:" ++ identity) ("Move " ++ label ++ " left") "Pin order" (index>0) (\stamp -> Desktop.MovePin stamp identity -1)
                   ,pinAction ("pin-right:" ++ identity) ("Move " ++ label ++ " right") "Pin order" (index<List.length pinIds-1) (\stamp -> Desktop.MovePin stamp identity 1)]
            acknowledge = Launch.uncertain model.launch |> Maybe.map (\token -> {id="control:acknowledge",domId=Desktop.key model "control:acknowledge",label="I checked; allow another launch",ariaLabel="I checked; allow another launch",detail="",enabled=True,message=Just (Desktop.Acknowledge token)}) |> Maybe.map List.singleton |> Maybe.withDefault []
            jump=entries |> List.head |> Maybe.map (\entry -> {id="jump:open:"++Catalog.id entry.identity,domId=Desktop.key model ("jump:open:"++Catalog.id entry.identity),label="Actions for "++entry.name,ariaLabel="Actions for "++entry.name,detail="Application actions and recent files",enabled=True,message=scoped (\stamp -> Desktop.OpenJumpList stamp (Catalog.id entry.identity))}) |> Maybe.map List.singleton |> Maybe.withDefault []
        in [ {id="control:search",domId="launcher-search",label=model.query,ariaLabel="Search applications",detail="",enabled=True,message=scoped (\stamp -> Desktop.SearchQuery stamp model.query)}
           , {id="control:close",domId=Desktop.key model "control:close",label="Windows",ariaLabel="Close applications and return to windows",detail="",enabled=True,message=scoped Desktop.CloseApplications}
           , {id="control:refresh",domId=Desktop.key model "control:refresh",label="Refresh",ariaLabel="Refresh applications",detail="",enabled=True,message=scoped Desktop.OpenApplications}
           ] ++ acknowledge ++ jump ++ pinFirst ++ List.concat (List.indexedMap pinRows pinIds) ++ List.map entryControl entries
    else if (MenuBridge.menuSnapshot model.windows.menus).menu/=Nothing then
        case (MenuBridge.menuSnapshot model.windows.menus).menu of
            Nothing -> []
            Just menu ->
                let prefix="menu:" ++ String.fromInt (Menu.menuNumber menu.id) ++ ":"
                    ready=Shell.available model.windows.shell && menu.status==Menu.Ready && not (menuBlocked model)
                    row index item =
                        let committed=MenuBridge.currentProvider model.windows.menus |> Maybe.map (Provider.incarnation >> confirmedWindowState model) |> Maybe.withDefault ""
                            detail = String.join " • " (List.filter (not << String.isEmpty) [committed,if menuBlocked model then "Awaiting native confirmation" else if menu.selected==Just index then "Selected" else ""])
                        in {id=prefix ++ String.fromInt index,domId=prefix ++ String.fromInt index,label=item.label,ariaLabel=item.label ++ (if menuBlocked model then "; " ++ detail else ""),detail=detail,enabled=ready && item.enabled,message=if ready && item.enabled then Just (Desktop.Window (TaskbarShell.MenuEvent (Menu.Activate menu.id menu.binding index))) else Nothing}
                    snap = MenuBridge.currentProvider model.windows.menus |> Maybe.andThen (\provider ->
                        model.windows.shell.geometry |> Maybe.andThen (\geometry -> Snap.open geometry (Provider.incarnation provider))
                            |> Maybe.map (\_ -> {id="control:snap-open",domId=prefix++"snap",label="Snap window",ariaLabel="Open snapping",detail="",enabled=ready,
                                message=if ready then Desktop.capture model |> Maybe.map (\stamp -> Desktop.OpenSnap stamp (Provider.incarnation provider)) else Nothing}))
                    applicationActions = MenuBridge.currentProvider model.windows.menus |> Maybe.andThen (\provider ->
                        model.applications |> Maybe.map Catalog.entries |> Maybe.withDefault []
                            |> List.filter (\entry -> Desktop.pinGroups (Catalog.id entry.identity) model |> List.any (\group -> List.any (\family -> family.root==Provider.incarnation provider) group.families))
                            |> (\matches -> case matches of
                                [entry] -> Just {id="jump:open:"++Catalog.id entry.identity,domId=prefix++"application-actions",label="Application actions",ariaLabel="Actions for "++entry.name,detail="Declared actions and recent files",enabled=ready,message=if ready then Desktop.capture model |> Maybe.map (\stamp -> Desktop.OpenJumpList stamp (Catalog.id entry.identity)) else Nothing}
                                _ -> Nothing))
                in {id="control:menu-close",domId=prefix ++ "close",label="Close",ariaLabel="Close window actions",detail="",enabled=True,message=Just (Desktop.Window (TaskbarShell.MenuEvent (Menu.Dismiss menu.id)))} :: List.indexedMap row menu.items ++ (snap |> Maybe.map List.singleton |> Maybe.withDefault []) ++ (applicationActions |> Maybe.map List.singleton |> Maybe.withDefault []) ++ recoveryPopup model
    else
        case model.windows.picker of
            Just picker ->
                let families = TaskbarShell.groups model.windows |> List.filter (\group -> group.key==picker.key) |> List.concatMap .families
                    familyControl family =
                        let ready = Shell.available model.windows.shell && family.available && not (familyBlocked model family.root) && Shell.capture model.windows.shell==Just picker.scope
                            detail = String.join " • " (List.filter (not << String.isEmpty) [confirmedWindowState model family.root,if familyBlocked model family.root then "Awaiting native confirmation" else if family.minimized then "Minimized" else "Open"])
                        in {id="family:" ++ UInt64.string family.root,domId="picker:" ++ Shell.stampKey picker.scope ++ ":" ++ UInt64.string picker.generation ++ ":" ++ UInt64.string family.root,label=(if family.minimized then "Restore " else "Activate ") ++ family.label,ariaLabel=(if family.minimized then "Restore " else "Activate ") ++ family.label ++ (if familyBlocked model family.root then "; " ++ detail else ""),detail=detail,enabled=ready,message=if ready then Just (Desktop.Window (TaskbarShell.Choose picker.scope picker.generation family.root)) else Nothing}
                in {id="control:close",domId="picker-close:" ++ Shell.stampKey picker.scope ++ ":" ++ UInt64.string picker.generation,label="Close",ariaLabel="Close window picker",detail="",enabled=True,message=Just (Desktop.Window (TaskbarShell.Close picker.scope picker.generation))} :: List.map familyControl families ++ recoveryPopup model
            Nothing -> []

barControls : Desktop.Model -> List Control
barControls model =
    let
        application = {id="bar:applications",domId=Desktop.key model "control:opener",label="Applications",ariaLabel="Open applications",detail="",enabled=model.windows.shell.phase/=Shell.Detached,message=Desktop.capture model |> Maybe.map Desktop.OpenApplications}
        overview = {id="bar:overview",domId=Desktop.key model "control:overview-opener",label="Task View",ariaLabel="Open Task View",detail="",enabled=Shell.available model.windows.shell && model.choice==Nothing,message=Desktop.capture model |> Maybe.map Desktop.OpenOverview}
        switcher = {id="bar:switcher",domId=Desktop.key model "control:switcher-opener",label="Switch windows",ariaLabel="Open window switcher",detail="",enabled=Shell.available model.windows.shell && model.choice==Nothing,message=Desktop.capture model |> Maybe.map (\stamp -> Desktop.OpenSwitcher stamp Switcher.Forward)}
        groupControl group =
            let scoped = Shell.capture model.windows.shell
                blocked = case Taskbar.primary False group.families of
                    Taskbar.Apply _ incarnation -> familyBlocked model incarnation
                    _ -> False
                ready = Shell.available model.windows.shell && Taskbar.primary False group.families/=Taskbar.Unavailable && not blocked
                operation = case Taskbar.primary False group.families of
                    Taskbar.Apply Effects.Minimize _ -> "Minimize "
                    Taskbar.Apply Effects.Restore _ -> "Restore "
                    Taskbar.Apply Effects.Activate _ -> "Activate "
                    Taskbar.Picker -> "Choose a window from "
                    _ -> "Unavailable "
                label = group.families |> List.head |> Maybe.map .label |> Maybe.withDefault "Windows"
                attention = List.any .attention group.families && not (List.any .active group.families)
                state = case group.families of
                    [family] ->
                        if family.minimized then "Minimized"
                        else if family.active then "Active"
                        else "Open"
                    _ -> String.fromInt (List.length group.families) ++ " windows"
                observedState = if attention then "Attention; "++state else state
            in {id="bar:group:" ++ group.key,domId=scoped |> Maybe.map (\stamp -> "group:" ++ Shell.stampKey stamp ++ ":" ++ group.key) |> Maybe.withDefault "detached-group",label=label,ariaLabel=operation ++ label ++ "; " ++ observedState ++ (if blocked then "; awaiting native confirmation" else ""),detail=if blocked then "Awaiting native confirmation; " ++ observedState else observedState,enabled=ready,message=if ready then scoped |> Maybe.map (\stamp -> Desktop.Window (TaskbarShell.Primary stamp group.key)) else Nothing}
        pinIds = Desktop.pinIdentities model
        owners group = pinIds |> List.filter (\identity -> Desktop.pinnedGroup identity model |> Maybe.map (\matched -> matched.key==group.key) |> Maybe.withDefault False)
        pinControl identity =
            let entry=model.applications |> Maybe.andThen (Catalog.lookup identity)
                label=entry |> Maybe.map .name |> Maybe.withDefault identity
                choice=if Shell.available model.windows.shell then Launch.select identity model.launch |> Maybe.map Desktop.Start else Nothing
                disabled reason={id="bar:pin:" ++ identity,domId=Desktop.key model ("pin:" ++ identity),label=label,ariaLabel=reason ++ label,detail=reason,enabled=False,message=Nothing}
            in case Desktop.pinnedGroup identity model of
                Just group ->
                    if List.length (owners group)==1 then
                        let control=groupControl group
                        in {control|id="bar:pin:" ++ identity,label=label,detail="Pinned; " ++ control.detail}
                    else disabled "Ambiguous application identity: "
                Nothing ->
                    if entry==Nothing then disabled "Unavailable application: " else if not (List.isEmpty (Desktop.pinGroups identity model)) then disabled "Ambiguous application identity: " else
                        {id="bar:pin:" ++ identity,domId=Desktop.key model ("pin:" ++ identity),label=label,ariaLabel="Open " ++ label,detail="Pinned launcher",enabled=choice/=Nothing,message=choice}
        ordinaryGroups=TaskbarShell.groups model.windows |> List.filter (\group -> List.length (owners group)/=1)
        reconnect = {id="bar:reconnect",domId="reconnect",label="Reconnect",ariaLabel="Reconnect to the window system",detail="",enabled=not model.windows.shell.reconnecting,message=Just (Desktop.Window (TaskbarShell.Native Shell.Reconnect))}
        retry = {id="bar:refresh-windows",domId=Desktop.key model "refresh-windows",label="Refresh windows",ariaLabel="Refresh windows",detail="",enabled=model.choice==Nothing,message=Just Desktop.RetryWindows}
        utilities = (if model.windows.shell.phase==Shell.Detached then reconnect else application) :: overview :: switcher :: {id="bar:notifications",domId=Desktop.key model "notifications:opener",label="Notifications"++(model.notifications.snapshot |> Maybe.map (\snapshot -> let count=List.length (List.filter (\entry -> entry.state=="live") snapshot.entries) in if count==0 then "" else " · "++String.fromInt count) |> Maybe.withDefault ""),ariaLabel="Open notifications",detail="",enabled=model.windows.shell.binding/=Nothing,message=Desktop.capture model |> Maybe.map Desktop.OpenNotifications} :: {id="bar:files",domId=Desktop.key model "files:opener",label="Files",ariaLabel="Open Files menu",detail="",enabled=model.windows.shell.binding/=Nothing,message=Desktop.capture model |> Maybe.map Desktop.OpenFiles} :: {id="bar:system",domId=Desktop.key model "system:opener",label="System",ariaLabel="Open system menu",detail="",enabled=model.windows.shell.binding/=Nothing,message=Desktop.capture model |> Maybe.map Desktop.OpenSystemMenu} :: {id="bar:settings",domId=Desktop.key model "settings:opener",label="Settings",ariaLabel="Open settings",detail="",enabled=model.windows.shell.binding/=Nothing,message=Desktop.capture model |> Maybe.map Desktop.OpenSettings} :: []
        applications = List.map pinControl pinIds ++ List.map groupControl ordinaryGroups
    in (if model.windows.shell.phase==Shell.Detached then utilities++applications else applications++utilities) ++ (if not (String.isEmpty model.choiceNotice) && model.windows.shell.phase/=Shell.Detached then [retry] else []) ++ (if recoveryNeeded model && model.windows.shell.phase/=Shell.Detached then [recoveryControl "bar:recovery-refresh" model] else [])

notice : Desktop.Model -> String
notice model =
    if model.jumpEntry/=Nothing then (if model.jumpExpected/=Nothing then "Reading application actions…" else model.jumpList.notice)
    else if model.filesOpen then (if model.filesExpected/=Nothing then "Reading Files state…" else model.files.notice)
    else if model.systemMenuOpen then (if model.systemMenuExpected/=Nothing then "Reading native system state…" else if model.systemMenuConfirmation/=Nothing then "Confirm or cancel the requested system change." else model.systemMenu.notice)
    else if model.notificationsOpen then (if model.notificationsExpected/=Nothing then "Loading notifications…" else model.notifications.notice)
    else if model.settingsOpen then (if model.settingsExpected/=Nothing then "Loading settings…" else model.settings.notice)
    else if Desktop.switcherOpen model then
        if Switcher.phase model.switcher==Switcher.Waiting then "Loading window activation history…"
        else if model.nativeSwitcher/=Nothing then "Alt+Tab: next window. Alt+Shift+Tab: previous. Release Alt: activate. Escape: cancel."
        else "Tab or Right: next window. Shift+Tab or Left: previous. Enter: activate. Escape: cancel."
    else if model.overview then
        if recoveryNeeded model then windowNotice model else
        case TaskView.groups model.windows.shell of
            Nothing -> "Waiting for current workspace information. Refresh window status."
            Just [] -> "No windows to show. Close Task View to return."
            Just _ -> "Choose a window to reveal its workspace, or browse another workspace."
    else if mode model=="menu" then
        case (MenuBridge.menuSnapshot model.windows.menus).menu |> Maybe.map .status of
            Just (Menu.Refused reason) -> reason
            Just (Menu.Unknown _) -> "The operation could not be confirmed."
            Just (Menu.Pending _) -> "Working…"
            _ -> if menuBlocked model then reservationReason else "Window actions"
    else if model.choice/=Nothing then "Updating your window choice…" else if not (String.isEmpty model.choiceNotice) then model.choiceNotice else
    if not model.open && (model.windows.shell.effects.transaction |> Maybe.map (\transaction -> List.member transaction.status [Effects.Pending,Effects.Unknown,Effects.Refused,Effects.Cancelled]) |> Maybe.withDefault False) then windowNotice model else
    if not (String.isEmpty model.pins.notice) && model.pins.notice/="Pin order saved." then model.pins.notice else
    case Launch.status model.launch of
        "Pending" -> "Opening application…"
        "Unknown" -> "The launch could not be confirmed. Check your windows before opening it again."
        "Submitted" -> "Launch submitted."
        "Refused" -> "Launch refused. Refresh applications and choose again."
        _ -> if model.catalogFailure/=Nothing then
                if recoveryNeeded model && model.windows.shell.phase/=Shell.Detached then reservationReason else "Applications were not opened. Choose Applications again."
            else if model.open then (if model.expected/=Nothing then "Loading applications…" else if model.applications==Nothing then "Application list unavailable. Refresh to try again." else if model.applications |> Maybe.map (Catalog.search model.query >> List.isEmpty) |> Maybe.withDefault False then "No matching applications. Change your search or Refresh." else if String.isEmpty (String.trim model.query) then "Type to search applications." else "Choose a matching application.") else windowNotice model

windowNotice : Desktop.Model -> String
windowNotice model =
    let
        subject transaction =
            let
                operation = case transaction.intent.operation of
                    Effects.Minimize -> "Minimize"
                    Effects.Restore -> "Restore"
                    Effects.Activate -> "Activate"
                    Effects.Maximize -> "Maximize"
                    Effects.RestoreGeometry -> "Restore size"
                    Effects.Pin -> "Always on top"
                    Effects.Unpin -> "Unpin window"
                    Effects.SnapPlacement _ -> "Snap"
                    Effects.TransferWorkspace p -> "Move to workspace "++p.destination
                label = TaskbarShell.groups model.windows |> List.concatMap .families
                    |> List.filter (\family -> family.root==transaction.intent.incarnation)
                    |> List.head |> Maybe.map (.label >> String.left 512) |> Maybe.withDefault "selected window"
            in (operation,label)
    in
    case model.windows.shell.effects.transaction of
        Just transaction ->
            let (operation,label)=subject transaction
            in case transaction.status of
                Effects.Pending -> operation ++ ": applying to " ++ label ++ "…"
                Effects.Unknown -> operation ++ ": not confirmed for " ++ label ++ (if model.windows.shell.phase==Shell.Detached then ". Reconnect to read window status; the action will not be repeated." else ". Check your windows; Refresh only reads status.")
                Effects.Refused -> operation ++ ": refused for " ++ label ++ ". Refresh window status, then choose again."
                Effects.Cancelled -> operation ++ ": cancelled for " ++ label ++ "."
                Effects.Committed -> if recoveryNeeded model then reservationReason else Shell.status model.windows.shell
        Nothing -> if recoveryNeeded model && model.windows.shell.phase/=Shell.Detached then reservationReason else Shell.status model.windows.shell

packet : Counter -> Counter -> Desktop.Model -> E.Value
packet publication lease model =
    let
        encode control = E.object [("id",E.string control.id),("domId",E.string control.domId),("label",E.string control.label),("ariaLabel",E.string control.ariaLabel),("detail",E.string control.detail),("enabled",E.bool (control.enabled && control.message/=Nothing))]
    in E.object [("surfaceProtocol",E.int 2),("motion",E.string (Motion.name (Motion.desired model.motion))),("appearance",Settings.encodeValues (model.settings.snapshot |> Maybe.map .values |> Maybe.withDefault Settings.defaults)),("publication",E.string (UInt64.string publication)),("lease",E.string (UInt64.string lease)),("mode",E.string (mode model)),("status",E.string ((notice model)++(if not model.filesOpen && (model.files.pending/=Nothing || String.startsWith "Files:" model.files.notice) then " · "++model.files.notice else "")++(if model.jumpEntry==Nothing && (model.jumpList.pending/=Nothing || String.startsWith "Application action:" model.jumpList.notice) then " · "++model.jumpList.notice else ""))),("bar",E.list encode (barControls model)),("popup",E.list encode (controls model))]

resolveAction : Counter -> Counter -> D.Value -> Desktop.Model -> Maybe Desktop.Msg
resolveAction publication lease raw model =
    let
        strict child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==["id","kind","lease","publication","surface","surfaceProtocol"] then child else D.fail "Surface action fields")
        decoder = strict (D.map6 (\version kind shown scoped identity role -> {version=version,kind=kind,shown=shown,scoped=scoped,identity=identity,role=role}) (D.field "surfaceProtocol" D.int) (D.field "kind" D.string) (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder) (D.field "id" D.string) (D.field "surface" D.string))
    in case D.decodeValue decoder raw of
        Ok event ->
            if event.version/=2 || event.kind/="surface-action" || event.shown/=publication || event.scoped/=lease then Nothing else
                (if event.role=="bar" then barControls model else if event.role=="popup" then controls model else []) |> List.filter (\control -> control.id==event.identity && control.enabled) |> List.head |> Maybe.andThen .message
        Err _ -> Nothing

resolve : Counter -> Counter -> D.Value -> Desktop.Model -> Maybe Desktop.Msg
resolve publication lease raw model =
    let strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "Surface event fields")
        scopes child = D.map4 (\version shown scoped role -> (version==2 && shown==publication && scoped==lease,role)) (D.field "surfaceProtocol" D.int) (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder) (D.field "surface" D.string) |> D.andThen (\(valid,role) -> if valid then child role else D.fail "Stale surface event")
        context = strict ["surfaceProtocol","kind","surface","publication","lease","id","trigger","x","y"] (scopes (\role -> D.map4 (\identity trigger x y -> (role,identity,trigger)) (D.field "id" D.string) (D.field "trigger" D.string) (D.field "x" D.int) (D.field "y" D.int)))
        navigation = strict ["surfaceProtocol","kind","surface","publication","lease","key"] (scopes (\role -> if role=="popup" && mode model=="menu" then D.field "key" D.string else D.fail "No menu"))
        query = strict ["surfaceProtocol","kind","surface","publication","lease","id","query"] (scopes (\role -> if role=="popup" && (model.open || model.filesOpen) then D.map2 Tuple.pair (D.field "id" D.string) (D.field "query" D.string) else D.fail "No applications"))
        menuMessage key =
            (MenuBridge.menuSnapshot model.windows.menus).menu |> Maybe.andThen (\menu ->
                let send = Just << Desktop.Window << TaskbarShell.MenuEvent
                in case key of
                    "Escape" -> send (Menu.Dismiss menu.id)
                    "Close" -> send (Menu.Dismiss menu.id)
                    "ArrowUp" -> send (Menu.Navigate menu.id Menu.Up)
                    "ArrowDown" -> send (Menu.Navigate menu.id Menu.Down)
                    "Home" -> send (Menu.Navigate menu.id Menu.Home)
                    "End" -> send (Menu.Navigate menu.id Menu.End)
                    "Enter" -> if Shell.available model.windows.shell && menu.status==Menu.Ready && not (menuBlocked model) then menu.selected |> Maybe.map (\index -> Desktop.Window (TaskbarShell.MenuEvent (Menu.Activate menu.id menu.binding index))) else Nothing
                    _ -> Nothing)
    in case D.decodeValue (D.field "kind" D.string) raw of
        Ok "surface-action" -> resolveAction publication lease raw model
        Ok "surface-query" -> D.decodeValue query raw |> Result.toMaybe |> Maybe.andThen (\(identity,value) -> if identity=="control:search" && model.open then Desktop.capture model |> Maybe.map (\stamp -> Desktop.SearchQuery stamp value) else if identity=="control:files-path" && model.filesOpen then Desktop.capture model |> Maybe.map (\stamp -> Desktop.EditFilesPath stamp value) else Nothing)
        Ok "surface-menu-navigation" -> D.decodeValue navigation raw |> Result.toMaybe |> Maybe.andThen menuMessage
        Ok "surface-context" ->
            D.decodeValue context raw |> Result.toMaybe |> Maybe.andThen (\(role,identity,trigger) ->
                if not (List.member trigger ["pointer","keyboard"]) || model.choice/=Nothing then Nothing else
                Shell.capture model.windows.shell |> Maybe.andThen (\stamp ->
                    if role=="bar" then
                        let enabled=barControls model |> List.any (\control -> control.id==identity && control.enabled)
                            group=if String.startsWith "bar:pin:" identity then
                                let pin=String.dropLeft 8 identity
                                in if List.member pin (Desktop.pinIdentities model) then Desktop.pinnedGroup pin model else Nothing
                                else TaskbarShell.groups model.windows |> List.filter (\candidate -> "bar:group:" ++ candidate.key==identity) |> List.head
                            emptyPin=if enabled && String.startsWith "bar:pin:" identity then
                                let entryId=String.dropLeft 8 identity
                                in if List.member entryId (Desktop.pinIdentities model) && List.isEmpty (Desktop.pinGroups entryId model) then model.applications |> Maybe.andThen (Catalog.lookup entryId) |> Maybe.andThen (\_ -> Desktop.capture model |> Maybe.map (\current -> Desktop.OpenJumpList current entryId)) else Nothing
                                else Nothing
                        in if group==Nothing then emptyPin else (if enabled then group else Nothing) |> Maybe.andThen (\current ->
                            case current.families of
                                [family] -> if family.available then Just (Desktop.OpenWindowMenu stamp family.root) else Nothing
                                _ -> if Taskbar.primary False current.families==Taskbar.Picker then Just (Desktop.Window (TaskbarShell.Primary stamp current.key)) else Nothing)
                    else if role=="popup" && model.open && String.startsWith "entry:" identity then
                        let entry=String.dropLeft 6 identity
                        in model.applications |> Maybe.andThen (Catalog.lookup entry) |> Maybe.andThen (\_ -> Desktop.capture model |> Maybe.map (\current -> Desktop.OpenJumpList current entry))
                    else if role=="popup" && mode model=="picker" then
                        model.windows.picker |> Maybe.andThen (\picker ->
                            if picker.scope/=stamp then Nothing else
                            TaskbarShell.groups model.windows |> List.filter (\group -> group.key==picker.key) |> List.concatMap .families |> List.filter (\family -> "family:" ++ UInt64.string family.root==identity && family.available) |> List.head |> Maybe.map (\family -> Desktop.OpenWindowMenu stamp family.root))
                    else Nothing))
        _ -> Nothing
