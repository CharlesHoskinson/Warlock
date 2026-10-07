port module SearchReplay exposing (main)
import Binding
import Catalog
import Desktop
import Json.Encode as E
import Json.Decode as D
import Launch
import Platform
import Shell
import Surface
import UInt64
port outgoing : E.Value -> Cmd msg
one = UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero
snapshot = E.object [("catalogProtocol",E.int 2),("lifetime",E.string "1"),("generation",E.string "1"),("entries",E.list identity [entry "z-exact" "Files" "File manager" ["folders"],entry "a-prefix" "Files Plus" "" [],entry "b-token" "Explorer" "File manager" ["files"],entry "c-unicode" "Straße" "" []])]
entry identity name generic words = E.object [("id",E.string identity),("name",E.string name),("iconHint",E.string ""),("wmclass",E.string ""),("genericName",E.string generic),("keywords",E.list E.string words)]
base =
    let initial=Desktop.initial
        windows=initial.windows
        shell=windows.shell
        binding= D.decodeValue Binding.decoder (E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]) |> Result.toMaybe
    in {initial | open=True,applications=Catalog.decode snapshot |> Result.toMaybe,windows={windows | shell={shell | binding=binding,phase=Shell.Ready}},launch=Launch.init |> Launch.bind "fixture-host" |> Launch.catalog snapshot}
main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
result =
    let ids query = base.applications |> Maybe.map (Catalog.search query >> List.map (.identity >> Catalog.id)) |> Maybe.withDefault []
        stamp=Desktop.capture base
        searched=stamp |> Maybe.map (\s -> Desktop.update (Desktop.SearchQuery s "files") base) |> Maybe.withDefault (base,[])
        stale=stamp |> Maybe.map (\s -> Desktop.update (Desktop.SearchQuery s "old") (Tuple.first searched)) |> Maybe.withDefault searched
        started=Launch.select "z-exact" base.launch |> Maybe.map (\selection -> Launch.start selection base.launch) |> Maybe.withDefault (base.launch,Nothing)
        refused=Tuple.second started |> Maybe.map (\intent -> Launch.receive "fixture-host" (E.object [("catalogProtocol",E.int 1),("kind",E.string "launch-outcome"),("intent",intent),("status",E.string "Refused"),("reason",E.string "stale-catalog")]) (Tuple.first started)) |> Maybe.withDefault base.launch
        unknown=Launch.pending (Tuple.first started) |> Maybe.map (\token -> Launch.timeout token (Tuple.first started)) |> Maybe.withDefault base.launch
        noMatch=Desktop.capture (Tuple.first searched) |> Maybe.map (\s -> Desktop.update (Desktop.SearchQuery s "nonexistent") (Tuple.first searched) |> Tuple.first) |> Maybe.withDefault base
    in E.object [("refreshClearsSettledRefusal",E.bool (Launch.status refused=="Refused" && Launch.status (Launch.catalog snapshot refused)=="Idle")),("refreshPreservesUnknown",E.bool (Launch.status (Launch.catalog snapshot unknown)=="Unknown")),("rank",E.list E.string (ids "FILES")),("keyword",E.list E.string (ids "folders")),("generic",E.list E.string (ids "manager")),("unicode",E.list E.string (ids "STRASSE")),("queryEditHasNoEffects",E.bool (List.isEmpty (Tuple.second searched))),("staleQueryRejected",E.bool (Tuple.first stale==Tuple.first searched && List.isEmpty (Tuple.second stale))),("noMatchStatus",E.string (D.decodeValue (D.field "status" D.string) (Surface.packet one one noMatch) |> Result.withDefault "")),("queryRetained",E.string noMatch.query),("frame",Surface.packet one one (Tuple.first searched))]
