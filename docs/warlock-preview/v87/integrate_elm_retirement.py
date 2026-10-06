"""Integrate typed retirement into the existing immutable Elm presenter."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v87')
p=r/'src/PreviewPresenter.elm';s=p.read_text()
assert 'NativeActorRetirement' not in s
s=s.replace('import NativePreviewSource','import NativePreviewSource\nimport NativeActorRetirement as Retirement')
s=s.replace('feedbackFloor : Maybe Counter }','feedbackFloor : Maybe Counter, retirement : Maybe Retirement.Observation, readySent : Bool }')
s=s.replace('type Model = Model (Dict String Entry) (Maybe CatalogStamp)','type Model = Model (Dict String Entry) (Maybe CatalogStamp) Retirement.Ledger')
s=s.replace('| Feedback String LocalFeedback','| Feedback String LocalFeedback | Retirement Retirement.Observation | Retired Retirement.Fact')
s=s.replace('Model Dict.empty Nothing','Model Dict.empty Nothing Retirement.empty')
s=s.replace('Model entries catalog','Model entries catalog ledger')
s=s.replace('Model entries previousCatalog','Model entries previousCatalog ledger')
s=s.replace('Model entries _)','Model entries _ _)')
s=s.replace('Model collected catalog,','Model collected catalog ledger,')
s=s.replace('Model enrolled (Just current),','Model enrolled (Just current) ledger,')
s=s.replace(' previousCatalog,encode',' previousCatalog ledger,encode')
s=s.replace('feedbackFloor=Nothing} next','feedbackFloor=Nothing,retirement=Nothing,readySent=False} next')
s=s.replace('feedbackFloor=if unissued then floor else advanceFloor floor sequence}', 'feedbackFloor=if unissued then floor else advanceFloor floor sequence,retirement=Nothing,readySent=False}')
s=s.replace('closed.model == Nothing','(closed.model == Nothing && closed.retirement == Nothing)')
s=s.replace('if entry.model /= Nothing then next','if entry.model /= Nothing || entry.retirement /= Nothing then next')
s=s.replace('entry.binding /= owner || (icon', 'entry.binding /= owner || entry.retirement /= Nothing || (icon')
s=s.replace('not scoped || not newer || entry.binding', 'not scoped || not newer || entry.retirement /= Nothing || entry.binding')
s=s.replace('entry.binding == owner && (entry.model', 'entry.binding == owner && entry.retirement == Nothing && (entry.model')
s=s.replace('if not allowed || not matching || (old == Nothing && Dict.size entries >= 2051)', 'if not allowed || not matching || (old == Nothing && not (Retirement.admittedAfter ledger owner native)) || (old == Nothing && Dict.size entries >= 2051)')
s=s.replace('not allowed || not monotonic || not ownersMatch', 'not allowed || not monotonic || not ownersMatch || (ledger.settled |> Maybe.map (\\final -> UInt64.compare current.request final.native.request /= GT) |> Maybe.withDefault False)')
s=s.replace('if not (eventOwns identity wire && familyFrameOwns entry.source wire)', 'if not (eventOwns identity wire && familyFrameOwns entry.source wire) || (entry.retirement /= Nothing && (D.decodeValue (D.field "kind" D.string) wire |> Result.map (\\kind -> List.member kind ["open","request","attach","observe"]) |> Result.withDefault True))')
a='    "demand-feedback" -> strict';b='''    "native-incarnation-retirement" -> D.map Retirement Retirement.observationDecoder
    "native-actor-retired" -> D.map Retired Retirement.actorDecoder
    "demand-feedback" -> strict'''
assert s.count(a)==1;s=s.replace(a,b)
a='receive snapshot raw ((Model entries previousCatalog ledger) as prior) =';b='receiveInput snapshot raw ((Model entries previousCatalog ledger) as prior) =';assert s.count(a)==1;s=s.replace(a,b)
a='receive : Maybe SurfaceRenderer.Snapshot -> D.Value -> Model -> (Model,E.Value)';assert s.count(a)==1
s=s.replace(a,'''-- Readiness shares the same output port as cleanup and exact terminal ACK.
-- It is appended after those controls, with no Cmd.batch ordering assumption.
receive : Maybe SurfaceRenderer.Snapshot -> D.Value -> Model -> (Model,E.Value)
receive snapshot raw prior =
    let
        (Model entries catalog ledger,emitted) = receiveInput snapshot raw prior
        settled entry = entry.model |> Maybe.map Preview.settled |> Maybe.withDefault True
        advance identity entry (next,ready) =
            case entry.retirement of
                Just observation ->
                    if not entry.readySent && settled entry then
                        (Dict.insert identity {entry | readySent=True} next,
                            ready ++ [E.object [("identity",E.string identity),("commands",E.list identity [Retirement.readyCommand observation])]])
                    else (Dict.insert identity entry next,ready)
                Nothing -> (Dict.insert identity entry next,ready)
        (retained,barriers) = Dict.foldl advance (Dict.empty,[]) entries
        cleanup = D.decodeValue (D.list D.value) emitted |> Result.withDefault []
    in (Model retained catalog ledger,E.list identity (cleanup ++ barriers))

receiveInput : Maybe SurfaceRenderer.Snapshot -> D.Value -> Model -> (Model,E.Value)''')
a='        Ok (Catalog stamp current rows) ->';assert s.count(a)==1
s=s.replace(a,'''        Ok (Retirement observation) ->
            let identity = "family:" ++ UInt64.string observation.subject
            in case Dict.get identity entries of
                Nothing -> (prior,encode [])
                Just entry ->
                    if entry.binding /= Retirement.owner observation || entry.retirement /= Nothing || not (Retirement.fresh ledger.observed observation) then (prior,encode [])
                    else
                        let (closed,commands) = closeEntry entry
                            pending = {closed | retirement=Just observation,readySent=False}
                        in (Model (Dict.insert identity pending entries) previousCatalog {ledger | observed=Just observation},
                            encode [{identity=identity,commands=commands}])
        Ok (Retired fact) ->
            let identity = "family:" ++ UInt64.string fact.native.subject
            in case Dict.get identity entries of
                Nothing -> (prior,encode [])
                Just entry ->
                    let settled = entry.model |> Maybe.map Preview.settled |> Maybe.withDefault True
                        exact = entry.retirement |> Maybe.map (\\pending -> Retirement.settles pending fact) |> Maybe.withDefault False
                        frontier = ledger.settled |> Maybe.map (\\previous -> UInt64.compare fact.entryIssuedThrough previous.entryIssuedThrough /= LT) |> Maybe.withDefault True
                    in if not entry.readySent || not settled || not exact || not frontier || not (Retirement.fresh ledger.observed fact.native) then (prior,encode [])
                       else (Model (Dict.remove identity entries) previousCatalog {ledger | observed=Just fact.native,settled=Just fact},encode [])
        Ok (Catalog stamp current rows) ->''')
p.write_text(s)
print(p)
