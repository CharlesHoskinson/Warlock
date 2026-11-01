module SurfaceSnapshot exposing (Snapshot, Control, Details, enabled, decode, encode, controlIdentities, publication, lease, mode, action, queryValue, pendingQuery, pendingQueryBlocked, honestPendingQuery, composingPopup, fieldIdentity, details)

import Json.Decode as D
import Json.Encode as E
import Set
import Settings
import UInt64 exposing (Counter)

type alias Control = { identity : String, domId : String, label : String, ariaLabel : String, detail : String, enabled : Bool, focusOnly : Bool, checked : Maybe Bool }
type alias Details = { publication : Counter, lease : Counter, keyboardParent : Maybe Bool, mode : String, status : String, appearance : Settings.Values, motion : String, bar : List Control, popup : List Control }
type Snapshot = Snapshot Details

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

pendingQueryBlocked : String -> Bool
pendingQueryBlocked identity =
    String.startsWith "entry:" identity
        || String.startsWith "pin:" identity
        || String.startsWith "unpin:" identity
        || String.startsWith "pin-left:" identity
        || String.startsWith "pin-right:" identity
        || String.startsWith "jump:open:" identity
        || identity == "control:page-previous"
        || identity == "control:page-next"
        || identity == "files:open-path"
        || String.startsWith "files:collection:" identity
        || identity == "files:home"

honestPendingQuery : String -> Snapshot -> Snapshot
honestPendingQuery query ((Snapshot snapshot) as current) =
    Snapshot {snapshot | popup=List.map (\item -> if List.member snapshot.mode ["applications","files"] && item.identity==fieldIdentity current then {item | label=query} else if pendingQueryBlocked item.identity then {item | enabled=False} else item) snapshot.popup}

composingPopup : Snapshot -> Snapshot
composingPopup ((Snapshot snapshot) as current) =
    Snapshot {snapshot | popup=List.map (\item -> if List.member snapshot.mode ["applications","files"] && item.identity==fieldIdentity current then item else {item | enabled=False}) snapshot.popup}

enabled : Bool -> String -> Snapshot -> Bool
enabled popup identity (Snapshot snapshot) = List.any (\control -> control.identity==identity && control.enabled) (if popup then snapshot.popup else snapshot.bar)

action : Bool -> String -> Snapshot -> Maybe E.Value
action popup identity (Snapshot snapshot) =
    if List.any (\control -> control.identity==identity && control.enabled) (if popup then snapshot.popup else snapshot.bar) then
        Just (E.object [("surface",E.string (if popup then "popup" else "bar")),("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("publication",E.string (UInt64.string snapshot.publication)),("lease",E.string (UInt64.string snapshot.lease)),("id",E.string identity)])
    else Nothing

details : Snapshot -> Details
details (Snapshot snapshot) = snapshot
