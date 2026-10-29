port module SearchRemovedReplay exposing (main)

import Binding
import Catalog
import Desktop
import Json.Decode as D
import Json.Encode as E
import Launch
import NativePointerFixture
import Platform
import Shell
import Surface
import UInt64

port outgoing : E.Value -> Cmd msg

one = UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero
bindingWire = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
entry id name = E.object [("id",E.string id),("name",E.string name),("iconHint",E.string ""),("wmclass",E.string ""),("genericName",E.string ""),("keywords",E.list E.string [])]
catalog generation entries = E.object [("catalogProtocol",E.int 2),("lifetime",E.string "1"),("generation",E.string generation),("entries",E.list identity entries)]
oldCatalog = catalog "1" [entry "z-original" "Files",entry "a-replacement" "Editor"]
newCatalog = catalog "2" [entry "a-replacement" "Editor"]
base =
    let initial=Desktop.initial
        windows=initial.windows
        shell=windows.shell
        binding=D.decodeValue Binding.decoder bindingWire |> Result.toMaybe
        host=binding |> Maybe.map (Binding.encode >> E.encode 0) |> Maybe.withDefault ""
    in NativePointerFixture.ready {initial | open=True,applications=Catalog.decode oldCatalog |> Result.toMaybe,windows={windows | shell={shell | binding=binding,phase=Shell.Ready}},launch=Launch.init |> Launch.bind host |> Launch.catalog oldCatalog}

query = E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-query"),("surface",E.string "popup"),("publication",E.string "1"),("lease",E.string "1"),("id",E.string "control:search"),("query",E.string "files")]
action id = E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string "popup"),("publication",E.string "1"),("lease",E.string "1"),("id",E.string id),("trigger",E.string "keyboard")]
applySurface raw model = Surface.resolve one one raw model |> Maybe.map (\msg -> Desktop.update msg model) |> Maybe.withDefault (model,[])
sends effects = List.filterMap (\effect -> case effect of
    Desktop.Send wire -> Just wire
    _ -> Nothing) effects
field name raw = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
replace name value raw = D.decodeValue (D.keyValuePairs D.value) raw |> Result.map (List.map (\(key,old) -> (key,if key==name then value else old)) >> E.object) |> Result.withDefault E.null
outcome intent = E.object [("protocolVersion",E.int 3),("kind",E.string "application-launch-outcome"),("binding",bindingWire),("outcome",E.object [("catalogProtocol",E.int 1),("kind",E.string "launch-outcome"),("intent",intent),("status",E.string "Refused"),("reason",E.string "removed-entry")])]
receipt request snapshot = E.object [("protocolVersion",E.int 3),("kind",E.string "application-catalog"),("binding",bindingWire),("requestId",E.string request),("snapshot",snapshot),("preferences",E.object [("revision",E.string "1"),("identities",E.list E.string [])])]
requestId effects = sends effects |> List.head |> Maybe.map (D.decodeValue (D.field "requestId" D.string) >> Result.withDefault "0") |> Maybe.withDefault "0"
status model = D.decodeValue (D.field "status" D.string) (Surface.packet one one model) |> Result.withDefault ""

result =
    let
        (searched,queryEffects)=applySurface query base
        captured=Surface.resolve one one (action "entry:z-original") searched
        (refreshing,refreshEffects)=applySurface (action "control:refresh") searched
        req=requestId refreshEffects
        (foreignCatalog,foreignEffects)=Desktop.update (Desktop.Incoming (receipt "999" newCatalog)) refreshing
        (current,currentEffects)=Desktop.update (Desktop.Incoming (receipt req newCatalog)) refreshing
        (staleStart,staleEffects)=captured |> Maybe.map (\msg -> Desktop.update msg current) |> Maybe.withDefault (current,[])
        oldControl=Surface.resolve one one (action "entry:z-original") current
        otherControl=Surface.resolve one one (action "entry:a-replacement") current
        (pending,pendingEffects)=captured |> Maybe.map (\msg -> Desktop.update msg searched) |> Maybe.withDefault (searched,[])
        command=sends pendingEffects |> List.head |> Maybe.withDefault E.null
        intent=field "intent" command
        (wrong,wrongEffects)=Desktop.update (Desktop.Incoming (outcome (replace "request" (E.string "2") intent))) pending
        (refused,refusedEffects)=Desktop.update (Desktop.Incoming (outcome intent)) wrong
        (replayed,replayEffects)=Desktop.update (Desktop.Incoming (outcome intent)) refused
        (rereading,rereadEffects)=applySurface (action "control:refresh") replayed
        rereadId=requestId rereadEffects
        (wrongRefresh,wrongRefreshEffects)=Desktop.update (Desktop.Incoming (receipt "999" newCatalog)) rereading
        (reconciled,reconciledEffects)=Desktop.update (Desktop.Incoming (receipt rereadId newCatalog)) wrongRefresh
        (late,lateEffects)=captured |> Maybe.map (\msg -> Desktop.update msg reconciled) |> Maybe.withDefault (reconciled,[])
        checks =
            [ ("searchThroughSurface",searched.query=="files" && List.isEmpty queryEffects && captured/=Nothing)
            , ("refreshIsReadOnly",req/="0" && List.length (sends refreshEffects)==1 && D.decodeValue (D.field "kind" D.string) (List.head (sends refreshEffects) |> Maybe.withDefault E.null)==Ok "catalog-request" && refreshing.query=="files")
            , ("wrongCatalogReceiptRejected",foreignCatalog.expected==refreshing.expected && foreignCatalog.applications==Nothing && List.isEmpty foreignEffects)
            , ("generationTwoReconciles",current.expected==Nothing && current.query=="files" && (current.applications |> Maybe.map (Catalog.scope >> .generation >> UInt64.string))==Just "2" && List.isEmpty (sends currentEffects))
            , ("capturedSelectionCannotLaunchAfterRemoval",captured/=Nothing && Launch.status staleStart.launch=="Idle" && List.isEmpty (sends staleEffects) && staleStart.open)
            , ("removedAndReplacementNotResolvableForQuery",oldControl==Nothing && otherControl==Nothing && status current=="No matching applications. Change your search or Refresh.")
            , ("originalOnlySentBeforeAuthorityRefusal",List.length (sends pendingEffects)==1 && D.decodeValue (D.at ["intent","entry"] D.string) command==Ok "z-original" && D.decodeValue (D.at ["intent","generation"] D.string) command==Ok "1" && Launch.status pending.launch=="Pending")
            , ("wrongIntentReceiptCannotSettle",Launch.status wrong.launch=="Pending" && List.isEmpty wrongEffects)
            , ("correlatedRemovedRefusalPreservesContext",Launch.status refused.launch=="Refused" && refused.open && refused.query=="files" && List.isEmpty refusedEffects && status refused=="Launch refused. Refresh applications and choose again.")
            , ("duplicateRefusalNeverReplays",Launch.status replayed.launch=="Refused" && List.isEmpty replayEffects)
            , ("userRefreshAfterRefusalNoLaunch",rereadId/="0" && List.length (sends rereadEffects)==1 && D.decodeValue (D.field "kind" D.string) (List.head (sends rereadEffects) |> Maybe.withDefault E.null)==Ok "catalog-request" && rereading.query=="files")
            , ("staleRefreshReceiptCannotReconcile",wrongRefresh.expected==rereading.expected && wrongRefresh.applications==Nothing && List.isEmpty wrongRefreshEffects)
            , ("refreshedNoMatchAndQueryPreserved",reconciled.query=="files" && reconciled.open && Launch.status reconciled.launch=="Idle" && status reconciled=="No matching applications. Change your search or Refresh." && Surface.resolve one one (action "entry:z-original") reconciled==Nothing && Surface.resolve one one (action "entry:a-replacement") reconciled==Nothing && List.isEmpty (sends reconciledEffects))
            , ("staleSelectionStillCannotReplay",Launch.status late.launch=="Idle" && List.isEmpty (sends lateEffects) && late.query=="files")
            ]
    in E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed)) checks)),("request",command),("statusAfterRefresh",E.string (status reconciled)),("nativeAcceptance",E.bool False)]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
