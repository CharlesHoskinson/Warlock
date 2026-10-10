module SurfaceRenderer exposing (enabled, Snapshot, decode, encode, controlIdentities, publication, lease, mode, view, viewWithPreview, action, queryValue, pendingQuery, fieldIdentity)

import Html exposing (Html, button, div, h1, input, p, span, text)
import Html.Attributes exposing (attribute, class, disabled, hidden, id, title, type_, value, placeholder)
import Html.Events exposing (on)
import Html.Keyed as Keyed
import Json.Decode as D
import Json.Encode as E
import Set
import Settings
import PreviewVisual as Preview
import UInt64 exposing (Counter)

type alias Control = { identity : String, domId : String, label : String, ariaLabel : String, detail : String, enabled : Bool, focusOnly : Bool, checked : Maybe Bool }
type Snapshot = Snapshot { publication : Counter, lease : Counter, keyboardParent : Maybe Bool, mode : String, status : String, appearance : Settings.Values, motion : String, bar : List Control, popup : List Control }

strict : List String -> D.Decoder a -> D.Decoder a
strict names decoder = D.keyValuePairs D.value |> D.andThen (\fields -> if List.sort (List.map Tuple.first fields)==List.sort names then decoder else D.fail "Presentation fields")

bounded : Int -> D.Decoder String
bounded limit = D.string |> D.andThen (\value -> if String.length value<=limit && not (String.any (\c -> Char.toCode c<32) value) then D.succeed value else D.fail "Presentation text")

controls : Int -> D.Decoder (List Control)
controls maximum =
    D.list D.value |> D.andThen (\values -> if List.length values>maximum then D.fail "Presentation capacity" else
        D.list (D.keyValuePairs D.value |> D.andThen (\pairs ->
            let extended=List.member "focusOnly" (List.map Tuple.first pairs)
                hasChecked=List.member "checked" (List.map Tuple.first pairs)
                base=D.map6 (\identity domId label ariaLabel detail available -> {identity=identity,domId=domId,label=label,ariaLabel=ariaLabel,detail=detail,enabled=available,focusOnly=False,checked=Nothing}) (D.field "id" (bounded 512)) (D.field "domId" (bounded 1024)) (D.field "label" (bounded 1024)) (D.field "ariaLabel" (bounded 1024)) (D.field "detail" (bounded 128)) (D.field "enabled" D.bool)
            in if hasChecked && not extended then D.fail "Checked presentation requires current control shape" else strict (["id","domId","label","ariaLabel","detail","enabled"]++(if extended then ["focusOnly"] else [])++(if hasChecked then ["checked"] else [])) (D.map3 (\row focusOnly checked -> {row|focusOnly=focusOnly,checked=checked}) base (if extended then D.field "focusOnly" D.bool else D.succeed False) (if hasChecked then D.field "checked" (D.map Just D.bool) else D.succeed Nothing)))))


decode : D.Value -> Result String Snapshot
decode raw =
    let legacy = D.decodeValue (D.field "appearance" D.value) raw |> Result.toMaybe |> (==) Nothing
        hasMotion = D.decodeValue (D.field "motion" D.value) raw |> Result.toMaybe |> (/=) Nothing
        hasParent = D.decodeValue (D.field "keyboardParent" D.value) raw |> Result.toMaybe |> (/=) Nothing
        parentDecoder = if hasParent then D.field "keyboardParent" (D.map Just D.bool) else D.succeed Nothing
        motionDecoder = if hasMotion then D.field "motion" (D.string |> D.andThen (\v -> if List.member v ["reduced","full"] then D.succeed v else D.fail "Motion profile")) else D.succeed "reduced"
        decoder = strict (["surfaceProtocol","publication","lease","mode","status","bar","popup"] ++ (if legacy then [] else ["appearance"]) ++ (if hasMotion then ["motion"] else []) ++ (if hasParent then ["keyboardParent"] else []))
            (D.map3 (\motion parent record -> (motion,parent,record)) motionDecoder parentDecoder (D.map8 (\version shown scoped current notice bar popup appearance -> {version=version,shown=shown,scoped=scoped,current=current,notice=notice,bar=bar,popup=popup,appearance=appearance})
                (D.field "surfaceProtocol" D.int) (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder) (D.field "mode" (bounded 16)) (D.field "status" (bounded 1024)) (D.field "bar" (controls 300)) (D.field "popup" (controls 2150)) (if legacy then D.succeed Settings.defaults else D.field "appearance" Settings.valuesDecoder)))
    in D.decodeValue decoder raw |> Result.mapError D.errorToString |> Result.andThen (\(motion,parent,record) ->
        let all = record.bar ++ record.popup
            identities = List.map .identity all
            unique names = List.length names == Set.size (Set.fromList names)
            overviewFilter control = control.identity=="overview:all" || (String.startsWith "overview:workspace:" control.identity && String.length control.identity>String.length "overview:workspace:")
            checkedRows = List.filter (\control -> control.checked/=Nothing) record.popup
            overviewFilters = List.filter overviewFilter record.popup
            checkedScopeInvalid = List.any (\control -> control.checked/=Nothing) record.bar || List.any (\control -> if record.current=="menu" then not (String.startsWith "menu:" control.identity) else if record.current=="overview" then not (overviewFilter control) else True) checkedRows
            checkedSelectionInvalid = if record.current=="overview" && not (List.isEmpty checkedRows) then List.any (\control -> control.checked==Nothing) overviewFilters || List.length (List.filter (\control -> control.checked==Just True) overviewFilters)/=1 else List.length checkedRows>1
        in if record.version/=2 || record.shown==UInt64.zero || not (List.member record.current ["closed","picker","applications","menu","overview","switcher","snap","settings","notifications","system","files","jump"]) || (record.current/="closed" && record.scoped==UInt64.zero) || (record.current=="closed" && not (List.isEmpty record.popup)) || not (unique identities) || not (unique (List.map .domId all)) || List.any (\control -> String.isEmpty control.identity || String.isEmpty control.domId || (control.focusOnly && control.enabled)) all || List.any .focusOnly record.bar || (List.any .focusOnly record.popup && record.current/="notifications") || List.length (List.filter .focusOnly record.popup)>1 || checkedScopeInvalid || checkedSelectionInvalid then Err "Invalid presentation scope/identities"
        else Ok (Snapshot {publication=record.shown,lease=record.scoped,keyboardParent=parent,mode=record.current,status=record.notice,appearance=record.appearance,motion=motion,bar=record.bar,popup=record.popup}))

publication : Snapshot -> Counter
publication (Snapshot snapshot) = snapshot.publication

encode : Snapshot -> E.Value
encode (Snapshot snapshot) =
    let control row = E.object ([("id",E.string row.identity),("domId",E.string row.domId),("label",E.string row.label),("ariaLabel",E.string row.ariaLabel),("detail",E.string row.detail),("enabled",E.bool row.enabled),("focusOnly",E.bool row.focusOnly)] ++ (row.checked |> Maybe.map (\value -> [("checked",E.bool value)]) |> Maybe.withDefault []))
    in E.object ([("surfaceProtocol",E.int 2),("motion",E.string snapshot.motion),("appearance",Settings.encodeValues snapshot.appearance),("publication",E.string (UInt64.string snapshot.publication)),("lease",E.string (UInt64.string snapshot.lease)),("mode",E.string snapshot.mode),("status",E.string snapshot.status),("bar",E.list control snapshot.bar),("popup",E.list control snapshot.popup)] ++ (snapshot.keyboardParent |> Maybe.map (\parent -> [("keyboardParent",E.bool parent)]) |> Maybe.withDefault []))

controlIdentities : Bool -> Snapshot -> List String
controlIdentities popup (Snapshot snapshot) = List.map .identity (if popup then snapshot.popup else snapshot.bar)

lease : Snapshot -> Counter
lease (Snapshot snapshot) = snapshot.lease

mode : Snapshot -> String
mode (Snapshot snapshot) = snapshot.mode

queryValue : Snapshot -> Maybe String
queryValue ((Snapshot snapshot) as current) = snapshot.popup |> List.filter (\item -> item.identity==fieldIdentity current) |> List.head |> Maybe.map .label

fieldIdentity : Snapshot -> String
fieldIdentity (Snapshot snapshot) = if snapshot.mode=="files" then "control:files-path" else "control:search"

pendingQuery : String -> Snapshot -> Snapshot
pendingQuery query ((Snapshot snapshot) as current) = Snapshot {snapshot | popup=List.map (\item -> if item.identity==fieldIdentity current then {item | label=query} else if String.startsWith "entry:" item.identity || item.identity=="files:open-path" || String.startsWith "files:collection:" item.identity || item.identity=="files:home" then {item | enabled=False} else item) snapshot.popup}

enabled : Bool -> String -> Snapshot -> Bool
enabled popup identity (Snapshot snapshot) = List.any (\control -> control.identity==identity && control.enabled) (if popup then snapshot.popup else snapshot.bar)

action : Bool -> String -> Snapshot -> Maybe E.Value
action popup identity (Snapshot snapshot) =
    if List.any (\control -> control.identity==identity && control.enabled) (if popup then snapshot.popup else snapshot.bar) then
        Just (E.object [("surface",E.string (if popup then "popup" else "bar")),("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("publication",E.string (UInt64.string snapshot.publication)),("lease",E.string (UInt64.string snapshot.lease)),("id",E.string identity)])
    else Nothing

view : Bool -> (E.Value -> msg) -> Snapshot -> Html msg
view popup send current = viewWithPreview (\_ -> Preview.Hidden) popup send current

viewWithPreview : (String -> Preview.Visual) -> Bool -> (E.Value -> msg) -> Snapshot -> Html msg
viewWithPreview preview popup send ((Snapshot snapshot) as current) =
    let -- A description ID is stable across state changes and cannot collide
        -- with any control ID supplied by the current closed projection.
        domIds = Set.fromList (List.map .domId (snapshot.bar ++ snapshot.popup))
        prefix candidate = if List.any (\item -> Set.member (candidate ++ item.domId) domIds) (snapshot.bar ++ snapshot.popup) then prefix (candidate ++ "-") else candidate
        descriptionPrefix = prefix "preview-description-"
        control item =
            let visual = preview item.identity
                description = Preview.description visual
                descriptionId = descriptionPrefix ++ item.domId
                settingsToggle = popup && ((snapshot.mode=="settings" && List.member item.identity ["settings:effects-off","settings:reduced-transparency"]) || (snapshot.mode=="notifications" && List.member item.identity ["notifications:dnd","notifications:critical-interrupt"]))
                switcherOption = popup && snapshot.mode=="switcher" && String.startsWith "switcher:family:" item.identity
                overviewFilter = popup && snapshot.mode=="overview" && (item.identity=="overview:all" || String.startsWith "overview:workspace:" item.identity)
                active = not popup && (String.startsWith "bar:group:" item.identity || String.startsWith "bar:pin:" item.identity) && String.contains "Active" item.detail && not (String.contains "Attention; " item.detail)
                kind = if String.startsWith "bar:group:" item.identity || String.startsWith "bar:pin:" item.identity then "control-group" else if item.identity=="bar:recovery-refresh" then "control-recovery" else "control-utility"
            in if popup && snapshot.mode=="settings" && (String.startsWith "settings:help:text:" item.identity || (String.startsWith "settings:shortcuts:" item.identity && String.endsWith ":state" item.identity)) then
                p [class "notification-text",id item.domId,attribute (if String.startsWith "settings:help:text:" item.identity then "data-settings-help" else "data-shortcut-state") item.identity] [span [class "control-label"] [text item.label],span [class "control-detail"] [text item.detail]]
            else if popup && snapshot.mode=="notifications" && (String.endsWith ":summary" item.identity || String.endsWith ":body" item.identity) then
                p [class "notification-text",id item.domId,attribute "data-notification-content" item.identity] [span [class "control-label"] [text item.label],span [class "control-detail"] [text item.detail]]
            else if popup && List.member snapshot.mode ["system","files","jump"] && String.endsWith ":state" item.identity then
                p [class "notification-text",id item.domId,attribute (if snapshot.mode=="jump" then "data-jump-content" else if snapshot.mode=="files" then "data-files-content" else "data-system-content") item.identity] [span [class "control-label"] [text item.label]]
            else if popup && List.member snapshot.mode ["applications","files"] && item.identity==fieldIdentity current then
                let packet inputKind query = send (E.object [("surfaceProtocol",E.int 2),("kind",E.string inputKind),("surface",E.string "popup"),("publication",E.string (UInt64.string snapshot.publication)),("lease",E.string (UInt64.string snapshot.lease)),("id",E.string item.identity),("query",E.string query)])
                    edit = D.map2 (\query composing -> packet (if composing then "surface-preedit" else "surface-query") query) (D.at ["target","value"] D.string) (D.oneOf [D.field "isComposing" D.bool,D.succeed False])
                    composition inputKind = D.map (packet inputKind) (D.at ["target","value"] D.string)
                in input [class "launcher-search",id item.domId,type_ (if snapshot.mode=="files" then "text" else "search"),placeholder (if snapshot.mode=="files" then "/path/to/folder or ~/Documents" else "Search applications"),value item.label,attribute "aria-label" item.ariaLabel,attribute "data-surface-field" item.identity,attribute "autocomplete" "off",disabled (not item.enabled),on "input" edit,on "compositionstart" (composition "surface-composition-start"),on "compositionend" (composition "surface-composition-end")] []
            else button ([class kind,id item.domId,attribute "data-window-state" (if kind/="control-group" then "none" else if String.contains "Attention; " item.detail then "attention" else if String.contains "Active" item.detail then "active" else if String.contains "Minimized" item.detail then "minimized" else "open"),attribute "aria-label" item.ariaLabel,disabled (not item.enabled && not item.focusOnly),attribute "aria-disabled" (if not item.enabled then "true" else "false"),attribute "data-focus-only" (if item.focusOnly then "true" else "false"),attribute "data-surface-control" item.identity,attribute "role" (if switcherOption then "option" else if popup && snapshot.mode=="menu" then (if item.checked/=Nothing then "menuitemcheckbox" else "menuitem") else "button"),attribute "aria-current" (if (not popup && kind=="control-group" && String.contains "Active" item.detail && not (String.contains "Attention; " item.detail)) || (popup && List.member snapshot.mode ["menu","switcher","snap","settings","notifications","system","files","jump"] && (item.detail=="Selected" || (snapshot.mode=="menu" && String.endsWith " • Selected" item.detail) || (settingsToggle && String.startsWith "On" item.detail))) then "true" else "false")] ++ (if overviewFilter then [attribute "aria-pressed" (if item.checked==Just True then "true" else "false")] else (item.checked |> Maybe.map (\checked -> [attribute "aria-checked" (if checked then "true" else "false")]) |> Maybe.withDefault [])) ++ (if String.isEmpty description then [] else [attribute "aria-describedby" descriptionId]) ++ (if popup && snapshot.mode=="settings" && item.identity=="settings:help" then [attribute "aria-expanded" (if item.detail=="Expanded" then "true" else "false")] else []) ++ (if settingsToggle then [attribute "aria-pressed" (if String.startsWith "On" item.detail then "true" else "false")] else []) ++ (if switcherOption then [attribute "aria-selected" (if item.detail=="Selected" then "true" else "false")] else if not popup && kind=="control-group" then [attribute "aria-pressed" (if active then "true" else "false")] else [])) [Preview.decorativeInlineView visual,span [class "control-label"] [text item.label],span [class "control-detail"] [text item.detail],if String.isEmpty description then text "" else span [class "preview-description",id descriptionId,hidden True] [text description]]
        familyPrefix rows = case rows of
            first :: rest -> if String.startsWith "overview:family:" first.identity then first :: familyPrefix rest else []
            [] -> []
        overviewRows rows =
            case rows of
                [] -> []
                first :: rest ->
                    if String.startsWith "overview:workspace:" first.identity then
                        let members = familyPrefix rest
                        in div [class "overview-workspace",attribute "role" "group",attribute "aria-labelledby" first.domId] (List.map control (first::members)) :: overviewRows (List.drop (List.length members) rest)
                    else control first :: overviewRows rest
    in if popup then div [attribute "data-motion" snapshot.motion,attribute "data-theme" (Settings.themeName snapshot.appearance.theme),attribute "data-text-scale" (String.fromInt snapshot.appearance.textScale),attribute "data-effects" (if snapshot.appearance.effectsOff then "off" else "on"),attribute "data-reduced-transparency" (if snapshot.appearance.reducedTransparency then "true" else "false"),class "surface-popup",attribute "data-mode" snapshot.mode,attribute "data-publication" (UInt64.string snapshot.publication),attribute "data-lease" (UInt64.string snapshot.lease)] [h1 [] [text (if snapshot.mode=="applications" then "Applications" else if snapshot.mode=="overview" then "Task View" else if snapshot.mode=="switcher" then "Switch windows" else if snapshot.mode=="snap" then "Snap window" else if snapshot.mode=="jump" then "Application actions" else if snapshot.mode=="files" then "Files" else if snapshot.mode=="system" then "System" else if snapshot.mode=="notifications" then "Notifications" else if snapshot.mode=="settings" then "Settings" else if snapshot.mode=="menu" then "Window actions" else "Choose a window")],p [attribute "role" "status",attribute "aria-live" "off"] [text snapshot.status],(if snapshot.mode=="overview" then div [class "surface-controls",attribute "role" "group"] (overviewRows snapshot.popup) else if snapshot.mode=="switcher" then div [class "surface-controls",attribute "role" "group",attribute "aria-label" "Window switcher controls"] [Keyed.node "div" [attribute "role" "listbox",attribute "aria-label" "Switch windows",attribute "aria-multiselectable" "false"] (snapshot.popup |> List.filter (\item -> String.startsWith "switcher:family:" item.identity) |> List.map (\item -> ("control:" ++ item.identity,control item))),Keyed.node "div" [attribute "role" "group",attribute "aria-label" "Window switcher actions"] (snapshot.popup |> List.filter (\item -> not (String.startsWith "switcher:family:" item.identity)) |> List.map (\item -> ("control:" ++ item.identity,control item)))] else Keyed.node "div" [class "surface-controls",attribute "role" (if snapshot.mode=="menu" then "menu" else "group")] (List.map (\item -> ("control:" ++ item.identity,control item)) snapshot.popup))]
       else Keyed.node "div" [attribute "data-motion" snapshot.motion,attribute "data-theme" (Settings.themeName snapshot.appearance.theme),attribute "data-text-scale" (String.fromInt snapshot.appearance.textScale),attribute "data-effects" (if snapshot.appearance.effectsOff then "off" else "on"),attribute "data-reduced-transparency" (if snapshot.appearance.reducedTransparency then "true" else "false"),class "surface-bar",attribute "data-publication" (UInt64.string snapshot.publication),attribute "data-lease" (UInt64.string snapshot.lease)]
            [("actions",Keyed.node "div" [class "surface-actions",attribute "role" "toolbar",attribute "aria-label" "Warlock taskbar"] (List.map (\item -> ("control:" ++ item.identity,control item)) snapshot.bar))
            ,("status",span [class (if String.isEmpty snapshot.status || snapshot.status=="Ready" then "surface-status surface-status-idle" else "surface-status"),attribute "role" "status",attribute "aria-live" "off",attribute "aria-atomic" "true",attribute "aria-label" snapshot.status,title snapshot.status] [text snapshot.status])]
