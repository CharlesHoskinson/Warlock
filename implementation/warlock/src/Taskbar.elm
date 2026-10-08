module Taskbar exposing (Family, Group, Decision(..), groups, primary, selection, encode)

import ActionProjection as Projection
import Effects
import Json.Encode as E
import UInt64 exposing (Counter)

type alias Family = { root : Counter, label : String, application : String, minimized : Bool, available : Bool, active : Bool, attention : Bool }
type alias Group = { key : String, families : List Family }
type Decision = Launch | Picker | Apply Effects.Operation Counter | Unavailable

-- Application hints group roots; transient children never add family entries.
-- Catalog identity matching and persisted pins remain a separate native contract.
groups projection =
    let rows = Projection.windows projection
        activeRoot = Projection.focused projection |> Maybe.andThen (\id -> Projection.rootOf id projection)
        family root =
            let members = List.filter (\w -> Projection.rootOf w.incarnation projection == Just root.incarnation) rows
                key = if String.isEmpty root.application then "window:" ++ UInt64.string root.incarnation else "application:" ++ root.application
            in (key,{root=root.incarnation,label=root.label,application=root.application,minimized=root.minimized,available=List.all .available members,active=activeRoot==Just root.incarnation,attention=List.any .attention members})
        add (key,entry) accumulated =
            if List.any (\g -> g.key == key) accumulated then List.map (\g -> if g.key == key then {g | families=g.families ++ [entry]} else g) accumulated
            else accumulated ++ [{key=key,families=[entry]}]
    in rows |> List.filter (\w -> w.owner == Nothing) |> List.sortWith (\a b -> UInt64.compare a.incarnation b.incarnation) |> List.map family |> List.foldl add []
primary pinned families =
    case families of
        [] -> if pinned then Launch else Unavailable
        [entry] ->
            if not entry.available then Unavailable
            else if entry.minimized then Apply Effects.Restore entry.root
            else if entry.active then Apply Effects.Minimize entry.root
            else Apply Effects.Activate entry.root
        _ -> Picker
selection entry =
    if not entry.available then Unavailable
    else Apply (if entry.minimized then Effects.Restore else Effects.Activate) entry.root
encode projection =
    E.list (\group -> E.object [("key",E.string group.key),("families",E.list (\f -> E.object [("root",E.string (UInt64.string f.root)),("label",E.string f.label),("minimized",E.bool f.minimized),("active",E.bool f.active),("attention",E.bool f.attention),("available",E.bool f.available)]) group.families)]) (groups projection)
