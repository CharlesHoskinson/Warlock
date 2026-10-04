module SurfaceRenderer exposing (Snapshot, decode, publication, lease, mode, view, action)

import Html exposing (Html, button, div, h1, p, text)
import Html.Attributes exposing (attribute, class, disabled, id)
import Html.Events exposing (onClick)
import Json.Decode as D
import Json.Encode as E
import Set
import UInt64 exposing (Counter)

type alias Control = { identity : String, domId : String, label : String, detail : String, enabled : Bool }
type Snapshot = Snapshot { publication : Counter, lease : Counter, mode : String, status : String, bar : List Control, popup : List Control }

strict : List String -> D.Decoder a -> D.Decoder a
strict names decoder = D.keyValuePairs D.value |> D.andThen (\fields -> if List.sort (List.map Tuple.first fields)==List.sort names then decoder else D.fail "Presentation fields")

bounded : Int -> D.Decoder String
bounded limit = D.string |> D.andThen (\value -> if String.length value<=limit && not (String.any (\c -> Char.toCode c<32) value) then D.succeed value else D.fail "Presentation text")

controls : Int -> D.Decoder (List Control)
controls maximum =
    D.list D.value |> D.andThen (\values -> if List.length values>maximum then D.fail "Presentation capacity" else
        D.list (strict ["id","domId","label","detail","enabled"] (D.map5 Control (D.field "id" (bounded 512)) (D.field "domId" (bounded 1024)) (D.field "label" (bounded 1024)) (D.field "detail" (bounded 128)) (D.field "enabled" D.bool))))

decode : D.Value -> Result String Snapshot
decode raw =
    let decoder = strict ["surfaceProtocol","publication","lease","mode","status","bar","popup"]
            (D.map7 (\version shown scoped current notice bar popup -> {version=version,shown=shown,scoped=scoped,current=current,notice=notice,bar=bar,popup=popup})
                (D.field "surfaceProtocol" D.int) (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder) (D.field "mode" (bounded 16)) (D.field "status" (bounded 1024)) (D.field "bar" (controls 257)) (D.field "popup" (controls 2051)))
    in D.decodeValue decoder raw |> Result.mapError D.errorToString |> Result.andThen (\record ->
        let all = record.bar ++ record.popup
            identities = List.map .identity all
            unique names = List.length names == Set.size (Set.fromList names)
        in if record.version/=1 || record.shown==UInt64.zero || not (List.member record.current ["closed","picker","applications"]) || (record.current/="closed" && record.scoped==UInt64.zero) || (record.current=="closed" && not (List.isEmpty record.popup)) || not (unique identities) || not (unique (List.map .domId all)) || List.any (\control -> String.isEmpty control.identity || String.isEmpty control.domId) all then Err "Invalid presentation scope/identities"
        else Ok (Snapshot {publication=record.shown,lease=record.scoped,mode=record.current,status=record.notice,bar=record.bar,popup=record.popup}))

publication : Snapshot -> Counter
publication (Snapshot snapshot) = snapshot.publication

lease : Snapshot -> Counter
lease (Snapshot snapshot) = snapshot.lease

mode : Snapshot -> String
mode (Snapshot snapshot) = snapshot.mode

action : String -> Snapshot -> Maybe E.Value
action identity (Snapshot snapshot) =
    if List.any (\control -> control.identity==identity && control.enabled) (snapshot.bar ++ snapshot.popup) then
        Just (E.object [("surfaceProtocol",E.int 1),("kind",E.string "surface-action"),("publication",E.string (UInt64.string snapshot.publication)),("lease",E.string (UInt64.string snapshot.lease)),("id",E.string identity)])
    else Nothing

view : Bool -> (E.Value -> msg) -> Snapshot -> Html msg
view popup send ((Snapshot snapshot) as current) =
    let control item = button [id item.domId,disabled (not item.enabled),attribute "data-surface-control" item.identity,onClick (action item.identity current |> Maybe.withDefault E.null |> send)] [text item.label]
    in if popup then div [class "surface-popup",attribute "data-publication" (UInt64.string snapshot.publication)] [h1 [] [text (if snapshot.mode=="applications" then "Applications" else "Choose a window")],p [attribute "role" "status"] [text snapshot.status],div [class "surface-controls"] (List.map control snapshot.popup)]
       else div [class "surface-bar"] (List.map control snapshot.bar)
