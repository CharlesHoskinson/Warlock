module Domain exposing (Effect(..), Model, Msg(..), State(..), initial, update)

import Json.Decode as D
import Protocol exposing (AuthorityId, Event(..), Window)


type State
    = Connecting
    | Inspecting AuthorityId (List Window)


type alias Model =
    { state : State
    , status : String
    }


type Msg
    = Native D.Value
    | Refresh


type Effect
    = RequestSnapshot


initial : Model
initial =
    { state = Connecting, status = "Connecting to the local host" }


update : Msg -> Model -> ( Model, List Effect )
update msg model =
    case msg of
        Refresh ->
            ( { model | status = "Refreshing fixture observations" }, [ RequestSnapshot ] )

        Native value ->
            case Protocol.decode value of
                Ok (FixtureSnapshot epoch windows) ->
                    ( { state = Inspecting epoch windows, status = "Fixture connected. Native window actions are unavailable in this slice." }, [] )

                Err _ ->
                    ( { model | status = "Host message refused; last valid observations retained" }, [] )
