module RetainedPreviewPresenter exposing (Model, initial, present, receive, receiveRealm, image, observe, metadata, enrollment, feedback, enrollRealm, closeRealm, quarantineRealm, realmStatus, issued, retry)

import Html exposing (Html)
import Json.Decode as D
import Json.Encode as E
import NativePreviewRealm as Realm
import NativePreviewProposalIngress as Ingress
import PreviewPresenter as Preview
import SurfaceRenderer

-- One existing policy plus immutable transport intents. A single deferred
-- ordinary transition is bounded to1065 intents and holds back further policy input
-- until its entire original output has entered the bounded queue. Its candidate
-- policy already revokes display/demand on quarantine and retains all known jobs.
-- One urgent quarantine may append its own bounded safety batch even while input
-- is blocked. The existing Presenter closing flag prevents a second such batch.
type Model = Model Preview.Model (Maybe Realm.Grant) (Maybe Ingress.Model) (List Ingress.Intent)

initial : Model
initial = Model Preview.initial Nothing Nothing []

emptyOutput : Maybe Realm.Grant -> E.Value
emptyOutput grant = grant |> Maybe.map (\g -> Realm.commands g.domain (E.list identity [])) |> Maybe.withDefault (E.list identity [])

commit : Model -> (Preview.Model,E.Value) -> (Model,E.Value)
commit ((Model _ grant ingress deferred) as prior) (candidate,output) =
    if not (List.isEmpty deferred) then (prior,emptyOutput grant)
    else case (grant,ingress) of
        (Just g,Just queue) -> case Ingress.decode g output of
            Nothing -> (prior,emptyOutput grant)
            Just intents ->
                let (retained,waiting) = Ingress.split intents queue
                in (Model candidate grant (Just retained) waiting,Ingress.proposals retained)
        _ -> (Model candidate grant ingress deferred,output)

present : Maybe SurfaceRenderer.Snapshot -> Model -> (Model,E.Value)
present snapshot ((Model policy _ _ _) as prior) = commit prior (Preview.present snapshot policy)

receive : Maybe SurfaceRenderer.Snapshot -> D.Value -> Model -> (Model,E.Value)
receive snapshot raw ((Model policy _ _ _) as prior) = commit prior (Preview.receive snapshot raw policy)

receiveRealm : Maybe SurfaceRenderer.Snapshot -> D.Value -> Model -> (Model,E.Value)
receiveRealm snapshot raw ((Model policy _ _ _) as prior) = commit prior (Preview.receiveRealm snapshot raw policy)

quarantineRealm : Realm.Domain -> Model -> (Model,E.Value)
quarantineRealm domain ((Model policy grant ingress deferred) as prior) =
    if List.isEmpty deferred then commit prior (Preview.quarantineRealm domain policy)
    else case (grant,ingress) of
        (Just g,Just queue) ->
            if not (Realm.same g.domain domain) then (prior,emptyOutput grant)
            else
                let (candidate,output) = Preview.quarantineRealm domain policy
                in case Ingress.decode g output of
                    Just (_ :: _) ->
                        let intents = Ingress.decode g output |> Maybe.withDefault []
                            (retained,waiting) = Ingress.split (deferred ++ intents) queue
                        in (Model candidate grant (Just retained) waiting,Ingress.proposals retained)
                    _ -> (prior,emptyOutput grant)
        _ -> (prior,emptyOutput grant)

enrollRealm : Realm.Grant -> Model -> Maybe Model
enrollRealm grant ((Model policy old ingress deferred) as prior) =
    if not (List.isEmpty deferred) || (ingress |> Maybe.map (Ingress.pending >> List.isEmpty >> not) |> Maybe.withDefault False) then
        if old == Just grant then Just prior else Nothing
    else Preview.enrollRealm grant policy |> Maybe.map (\next -> Model next (Just grant) (Just (Ingress.empty grant)) [])

closeRealm : Realm.Domain -> Model -> Maybe Model
closeRealm domain (Model policy grant ingress deferred) =
    if not (List.isEmpty deferred) || (ingress |> Maybe.map (Ingress.pending >> List.isEmpty >> not) |> Maybe.withDefault False) then Nothing
    else Preview.closeRealm domain policy |> Maybe.map (\next -> Model next grant ingress deferred)

issued : D.Value -> Model -> Model
issued raw ((Model policy grant ingress deferred) as prior) =
    ingress |> Maybe.andThen (Ingress.issued raw) |> Maybe.map (\next -> Model policy grant (Just next) deferred) |> Maybe.withDefault prior

retry : Realm.Domain -> Model -> (Model,E.Value)
retry domain ((Model policy grant ingress deferred) as prior) =
    case (grant,ingress) of
        (Just g,Just queue) -> if Realm.same g.domain domain then
            let (next,waiting) = Ingress.split deferred queue
            in (Model policy grant (Just next) waiting,Ingress.proposals next)
          else (prior,emptyOutput grant)
        _ -> (prior,emptyOutput grant)

realmStatus : Model -> E.Value
realmStatus (Model policy _ ingress deferred) =
    let fields = D.decodeValue (D.keyValuePairs D.value) (Preview.realmStatus policy) |> Result.withDefault []
    in E.object (fields ++ [("ingress",ingress |> Maybe.map Ingress.status |> Maybe.withDefault E.null),("deferred",E.int (List.length deferred)),("deferredIntents",E.list (\intent -> E.object [("identity",E.string intent.identity),("commands",E.list identity [intent.command])]) deferred),("inputBlocked",E.bool (not (List.isEmpty deferred)))])

image : SurfaceRenderer.Snapshot -> String -> Model -> Html msg
image snapshot name (Model policy _ _ _) = Preview.image snapshot name policy

observe : Model -> E.Value
observe (Model policy _ _ _) = Preview.observe policy

metadata : Model -> E.Value
metadata (Model policy _ _ _) = Preview.metadata policy

enrollment : Model -> E.Value
enrollment (Model policy _ _ _) = Preview.enrollment policy

feedback : Model -> E.Value
feedback (Model policy _ _ _) = Preview.feedback policy
