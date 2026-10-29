port module SurfaceSnapshotContracts exposing (main)
import BaselineSurfaceRenderer as Old
import SurfaceSnapshot as New
import Presentation
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64
port outgoing : E.Value -> Cmd msg
same a b = E.encode 0 a == E.encode 0 b
actionsEqual old new =
    List.all (\popup ->
        let ids = Old.controlIdentities popup old ++ New.controlIdentities popup new ++ [ "missing:identity" ]
        in List.all (\identity -> (Old.action popup identity old |> Maybe.map (E.encode 0)) == (New.action popup identity new |> Maybe.map (E.encode 0))) ids
    ) [ False, True ]
caseResult raw =
    case (Old.decode raw,New.decode raw) of
        (Err _,Err _) -> E.object [("accepted",E.bool False),("equivalent",E.bool True),("idempotent",E.bool True),("pendingEquivalent",E.bool True),("pendingSuppressesEntry",E.bool True),("actionsEquivalent",E.bool True)]
        (Ok a,Ok b) ->
            let ea=Old.encode a
                eb=New.encode b
                roundtrip=New.decode eb |> Result.map (New.encode >> same eb) |> Result.withDefault False
                pending=same (Old.encode (Old.pendingQuery "typed" a)) (New.encode (New.pendingQuery "typed" b))
                suppressed=not (New.enabled True "entry:1" (New.pendingQuery "typed" b))
            in E.object [("accepted",E.bool True),("equivalent",E.bool (same ea eb)),("idempotent",E.bool roundtrip),("pendingEquivalent",E.bool pending),("pendingSuppressesEntry",E.bool suppressed),("actionsEquivalent",E.bool (actionsEqual a b))]
        _ -> E.object [("accepted",E.bool False),("equivalent",E.bool False),("idempotent",E.bool False),("pendingEquivalent",E.bool False),("pendingSuppressesEntry",E.bool False),("actionsEquivalent",E.bool False)]
value field raw = D.decodeValue (D.field field D.value) raw |> Result.withDefault E.null
pub model = Presentation.current model |> Maybe.map (New.publication >> UInt64.string) |> Maybe.withDefault "none"
some x = case x of
    Just _ -> True
    Nothing -> False
sequence flags =
    let first=value "first" flags
        next=value "next" flags
        stale=value "stale" flags
        duplicate=value "duplicate" flags
        edit=value "edit" flags
        future=value "future" flags
        wrongLease=value "wrongLease" flags
        wrongId=value "wrongId" flags
        invalid=value "invalid" flags
        third=value "third" flags
        currentAction=value "currentAction" flags
        retiredFrame=value "retiredFrame" flags
        retiredLeaseAction=value "retiredLeaseAction" flags
        firstState=Presentation.accept first Presentation.initial
        nextState=Presentation.accept next firstState
        retiredState=Presentation.accept retiredFrame nextState
        staleState=Presentation.accept stale nextState
        dupState=Presentation.accept duplicate nextState
        cleared=Presentation.accept invalid nextState
        recovered=Presentation.accept third cleared
        local=Presentation.localEdit edit nextState
        localKind=local |> Maybe.andThen (D.decodeValue (D.field "kind" D.string) >> Result.toMaybe)
        localPublication=local |> Maybe.andThen (D.decodeValue (D.field "publication" D.string) >> Result.toMaybe)
        checks=[("firstAccepted",pub firstState=="1"),("nextAccepted",pub nextState=="2"),
          ("staleIgnored",pub staleState=="2"),("duplicateIgnored",pub dupState=="2"),
          ("oldExternalEditRejected",not (some (Presentation.editQuery edit nextState))),
          ("sameLeaseLocalEditRebased",some local && localKind==Just "surface-query" && localPublication==Just "2"),
          ("futureEditRejected",not (some (Presentation.localEdit future nextState))),
          ("wrongLeaseRejected",not (some (Presentation.localEdit wrongLease nextState))),
          ("wrongIdentityRejected",not (some (Presentation.localEdit wrongId nextState))),
          ("localQueryIsNotAction",local |> Maybe.map (\wire -> not (some (Presentation.dispatch True wire nextState))) |> Maybe.withDefault False),
          ("invalidClearsSnapshot",pub cleared=="none"),("freshFrameRecovers",pub recovered=="3"),
          ("currentCapturedButtonAccepted",some (Presentation.dispatch True currentAction nextState)),
          ("oldCapturedButtonRejectedAfterNewPublication",not (some (Presentation.dispatch True currentAction recovered))),
          ("oldCapturedButtonRejectedAfterLeaseRetirement",not (some (Presentation.dispatch True retiredLeaseAction retiredState)))]
    in E.object (List.map (Tuple.mapSecond E.bool) checks)
result flags =
    let frames=D.decodeValue (D.field "frames" (D.list D.value)) flags |> Result.withDefault []
    in E.object [("cases",E.list caseResult frames),("sequence",sequence flags)]
main : Program D.Value () Never
main = Platform.worker {init=\flags -> ((),outgoing (result flags)),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
