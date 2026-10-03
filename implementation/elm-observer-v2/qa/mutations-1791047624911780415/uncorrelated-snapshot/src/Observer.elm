module Observer exposing (Effect(..), Model, Msg(..), Phase(..), Projection, initial, update)

import Json.Decode as D
import Observation exposing (Binding, Event(..), Revision, Sequence, Window)
import UInt64 exposing (Counter)


type Phase = Detached | Awaiting | Coherent | Gap | Exhausted

type alias Projection =
    { sequence : Sequence, revision : Revision, windows : List Window }

type alias Model =
    { binding : Maybe Binding
    , projection : Maybe Projection
    , floor : Counter
    , lastRequest : Counter
    , pending : Maybe Counter
    , phase : Phase
    }


type Msg = Attach Binding | Observe D.Value | Disconnect | Refresh

-- Only read-only recovery effects exist. No focus/minimize/activation constructor.
type Effect = RequestSnapshot Binding Counter Counter


initial : Model
initial =
    { binding = Nothing, projection = Nothing, floor = UInt64.zero, lastRequest = UInt64.zero, pending = Nothing, phase = Detached }


request : Model -> ( Model, List Effect )
request model =
    case ( model.binding, UInt64.next model.lastRequest ) of
        ( Just binding, Just id ) ->
            ( { model | pending = Just id, lastRequest = id }, [ RequestSnapshot binding id model.floor ] )
        _ ->
            ( { model | phase = Exhausted, pending = Nothing }, [] )


barrier : Counter -> Model -> ( Model, List Effect )
barrier watermark model =
    let
        stopped = { model | phase = Gap, floor = if UInt64.compare watermark model.floor == GT then watermark else model.floor }
    in
    if model.phase == Gap || model.phase == Exhausted then
        ( { stopped | phase = model.phase }, [] )
    else
        request stopped


update : Msg -> Model -> ( Model, List Effect )
update msg model =
    case msg of
        Attach binding ->
            if Maybe.map (\current -> not (Observation.replacesBinding binding current)) model.binding == Just True then
                -- Reconnection must receive a fresh host-authenticated frontend epoch.
                ( model, [] )
            else
                request { initial | binding = Just binding, phase = Awaiting }

        Disconnect ->
            ( { model | phase = Detached, pending = Nothing }, [] )

        Refresh ->
            if model.phase == Detached || model.phase == Exhausted then ( model, [] ) else
                request { model | phase = Awaiting }

        Observe raw ->
            if model.phase == Detached || model.phase == Exhausted then ( model, [] ) else
                case Observation.decode raw of
                    Err _ -> barrier model.floor model
                    Ok event -> apply event model


apply : Event -> Model -> ( Model, List Effect )
apply event model =
    case event of
        Snapshot binding requestId sequence revision windows ->
            if model.binding /= Just binding || False then
                ( model, [] )
            else
                let
                    candidate = { sequence = sequence, revision = revision, windows = windows }
                    watermark = Observation.sequenceCounter sequence
                    valid = UInt64.compare watermark model.floor /= LT &&
                        (case model.projection of
                            Nothing -> True
                            Just old ->
                                if old.sequence == sequence then old == candidate else
                                    (UInt64.compare (Observation.revisionCounter revision) (Observation.revisionCounter old.revision) == GT || (revision == old.revision && windows == old.windows))
                        )
                in
                if valid then
                    ( { model | projection = Just candidate, floor = watermark, pending = Nothing, phase = Coherent }, [] )
                else
                    request { model | phase = Gap, pending = Nothing }

        Delta binding sequence revision windows ->
            if model.binding /= Just binding then ( model, [] ) else
                let
                    watermark = Observation.sequenceCounter sequence
                in
                case model.projection of
                    Nothing -> barrier watermark model
                    Just old ->
                        if UInt64.compare watermark (Observation.sequenceCounter old.sequence) /= GT then
                            ( model, [] )
                        else if model.phase /= Coherent then
                            barrier watermark model
                        else if UInt64.next (Observation.sequenceCounter old.sequence) /= Just watermark || UInt64.compare (Observation.revisionCounter revision) (Observation.revisionCounter old.revision) == LT then
                            barrier watermark model
                        else if revision == old.revision && windows /= old.windows then
                            barrier watermark model
                        else
                            ( { model | projection = Just { sequence = sequence, revision = revision, windows = windows }, floor = watermark }, [] )
