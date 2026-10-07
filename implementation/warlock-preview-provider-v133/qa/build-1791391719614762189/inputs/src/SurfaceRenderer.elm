module SurfaceRenderer exposing (enabled, Snapshot, decode, encode, controlIdentities, publication, lease, mode, view, viewWithPreview, action)

import Html exposing (Html, button, div, h1, p, span, text)
import Html.Attributes exposing (attribute, class, disabled, id)
import Html.Keyed as Keyed
import Json.Decode as D
import Json.Encode as E
import Set
import UInt64 exposing (Counter)

type alias Control = { identity : String, domId : String, label : String, ariaLabel : String, detail : String, enabled : Bool }
type Snapshot = Snapshot { publication : Counter, lease : Counter, mode : String, status : String, bar : List Control, popup : List Control }

strict : List String -> D.Decoder a -> D.Decoder a
strict names decoder = D.keyValuePairs D.value |> D.andThen (\fields -> if List.sort (List.map Tuple.first fields)==List.sort names then decoder else D.fail "Presentation fields")

bounded : Int -> D.Decoder String
bounded limit = D.string |> D.andThen (\value -> if String.length value<=limit && not (String.any (\c -> Char.toCode c<32) value) then D.succeed value else D.fail "Presentation text")

controls : Int -> D.Decoder (List Control)
controls maximum =
    D.list D.value |> D.andThen (\values -> if List.length values>maximum then D.fail "Presentation capacity" else
        D.list (strict ["id","domId","label","ariaLabel","detail","enabled"] (D.map6 Control (D.field "id" (bounded 512)) (D.field "domId" (bounded 1024)) (D.field "label" (bounded 1024)) (D.field "ariaLabel" (bounded 1024)) (D.field "detail" (bounded 128)) (D.field "enabled" D.bool))))

decode : D.Value -> Result String Snapshot
decode raw =
    let decoder = strict ["surfaceProtocol","publication","lease","mode","status","bar","popup"]
            (D.map7 (\version shown scoped current notice bar popup -> {version=version,shown=shown,scoped=scoped,current=current,notice=notice,bar=bar,popup=popup})
                (D.field "surfaceProtocol" D.int) (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder) (D.field "mode" (bounded 16)) (D.field "status" (bounded 1024)) (D.field "bar" (controls 259)) (D.field "popup" (controls 2051)))
    in D.decodeValue decoder raw |> Result.mapError D.errorToString |> Result.andThen (\record ->
        let all = record.bar ++ record.popup
            identities = List.map .identity all
            unique names = List.length names == Set.size (Set.fromList names)
        in if record.version/=2 || record.shown==UInt64.zero || not (List.member record.current ["closed","picker","applications","menu"]) || (record.current/="closed" && record.scoped==UInt64.zero) || (record.current=="closed" && not (List.isEmpty record.popup)) || not (unique identities) || not (unique (List.map .domId all)) || List.any (\control -> String.isEmpty control.identity || String.isEmpty control.domId) all then Err "Invalid presentation scope/identities"
        else Ok (Snapshot {publication=record.shown,lease=record.scoped,mode=record.current,status=record.notice,bar=record.bar,popup=record.popup}))

publication : Snapshot -> Counter
publication (Snapshot snapshot) = snapshot.publication

encode : Snapshot -> E.Value
encode (Snapshot snapshot) =
    let control row = E.object [("id",E.string row.identity),("domId",E.string row.domId),("label",E.string row.label),("ariaLabel",E.string row.ariaLabel),("detail",E.string row.detail),("enabled",E.bool row.enabled)]
    in E.object [("surfaceProtocol",E.int 2),("publication",E.string (UInt64.string snapshot.publication)),("lease",E.string (UInt64.string snapshot.lease)),("mode",E.string snapshot.mode),("status",E.string snapshot.status),("bar",E.list control snapshot.bar),("popup",E.list control snapshot.popup)]

controlIdentities : Bool -> Snapshot -> List String
controlIdentities popup (Snapshot snapshot) = List.map .identity (if popup then snapshot.popup else snapshot.bar)

lease : Snapshot -> Counter
lease (Snapshot snapshot) = snapshot.lease

mode : Snapshot -> String
mode (Snapshot snapshot) = snapshot.mode

enabled : Bool -> String -> Snapshot -> Bool
enabled popup identity (Snapshot snapshot) = List.any (\control -> control.identity==identity && control.enabled) (if popup then snapshot.popup else snapshot.bar)

action : Bool -> String -> Snapshot -> Maybe E.Value
action popup identity (Snapshot snapshot) =
    if List.any (\control -> control.identity==identity && control.enabled) (if popup then snapshot.popup else snapshot.bar) then
        Just (E.object [("surface",E.string (if popup then "popup" else "bar")),("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("publication",E.string (UInt64.string snapshot.publication)),("lease",E.string (UInt64.string snapshot.lease)),("id",E.string identity)])
    else Nothing

view : Bool -> (E.Value -> msg) -> Snapshot -> Html msg
view popup send current = viewWithPreview (\_ -> text "") popup send current

viewWithPreview : (String -> Html msg) -> Bool -> (E.Value -> msg) -> Snapshot -> Html msg
viewWithPreview preview popup send ((Snapshot snapshot) as current) =
    let control item =
            let kind = if String.startsWith "bar:group:" item.identity then "control-group" else if item.identity=="bar:recovery-refresh" then "control-recovery" else "control-utility"
            in button [class kind,id item.domId,attribute "aria-label" item.ariaLabel,disabled (not item.enabled),attribute "data-surface-control" item.identity,attribute "role" (if popup && snapshot.mode=="menu" then "menuitem" else "button"),attribute "aria-current" (if popup && snapshot.mode=="menu" && item.detail=="Selected" then "true" else "false")] [preview item.identity,span [class "control-label"] [text item.label],span [class "control-detail"] [text item.detail]]
    in if popup then div [class "surface-popup",attribute "data-mode" snapshot.mode,attribute "data-publication" (UInt64.string snapshot.publication),attribute "data-lease" (UInt64.string snapshot.lease)] [h1 [] [text (if snapshot.mode=="applications" then "Applications" else if snapshot.mode=="menu" then "Window actions" else "Choose a window")],p [attribute "role" "status",attribute "aria-live" "polite"] [text snapshot.status],div [class "surface-controls",attribute "role" (if snapshot.mode=="menu" then "menu" else "group")] (List.map control snapshot.popup)]
       else Keyed.node "div" [class "surface-bar",attribute "data-publication" (UInt64.string snapshot.publication),attribute "data-lease" (UInt64.string snapshot.lease)] (List.map (\item -> ("control:" ++ item.identity,control item)) snapshot.bar ++ [("status",span [class "surface-status",attribute "role" "status",attribute "aria-live" "polite"] [text snapshot.status])])
