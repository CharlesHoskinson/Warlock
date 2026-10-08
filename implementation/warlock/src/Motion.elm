module Motion exposing (Model, Profile(..), Observation, Receipt, initial, name, desired, observe, rebind, propose, receive, ready, decoder, receiptDecoder, request, notice)

import Binding
import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type Profile = Reduced | Full
type alias Observation = { serial : Counter, profile : Profile, source : String }
type alias Pending = { binding : Binding.Binding, request : Counter, profile : Profile }
type alias Receipt = Pending
type alias Model = { observation : Maybe Observation, pending : Maybe Pending, applied : Maybe { binding : Binding.Binding, profile : Profile } }

initial : Model
initial = { observation = Nothing, pending = Nothing, applied = Nothing }

name : Profile -> String
name profile = case profile of
    Reduced -> "reduced"
    Full -> "full"

desired : Model -> Profile
desired model = model.observation |> Maybe.map .profile |> Maybe.withDefault Reduced

strict fields decoder_ =
    D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then decoder_ else D.fail "Motion fields")

version = D.field "protocolVersion" D.int |> D.andThen (\v -> if v==3 then D.succeed () else D.fail "Motion version")
kind expected = D.field "kind" D.string |> D.andThen (\v -> if v==expected then D.succeed () else D.fail "Motion kind")
positive = UInt64.decoder |> D.andThen (\v -> if v/=UInt64.zero then D.succeed v else D.fail "Motion counter")
profileDecoder = D.string |> D.andThen (\v -> case v of
    "reduced" -> D.succeed Reduced
    "full" -> D.succeed Full
    _ -> D.fail "Motion profile")

decoder : D.Decoder Observation
decoder = strict ["protocolVersion","kind","serial","profile","source"]
    (D.map5 (\_ _ serial profile source -> {serial=serial,profile=profile,source=source}) version (kind "host-motion-preference") (D.field "serial" positive) (D.field "profile" profileDecoder) (D.field "source" D.string |> D.andThen (\v -> if List.member v ["portal","gtk"] then D.succeed v else D.fail "Motion source")))

receiptDecoder : D.Decoder Receipt
receiptDecoder = strict ["protocolVersion","kind","binding","requestId","profile"]
    (D.map5 (\_ _ binding request_ profile -> {binding=binding,request=request_,profile=profile}) version (kind "motion-profile") (D.field "binding" Binding.decoder) (D.field "requestId" positive) (D.field "profile" profileDecoder))

observe : Observation -> Model -> Model
observe observation model =
    if model.observation |> Maybe.map (\old -> UInt64.compare observation.serial old.serial /= GT) |> Maybe.withDefault False then model
    else {model | observation=Just observation}

rebind : Model -> Model
rebind model = {model | pending=Nothing,applied=Nothing}

propose : Binding.Binding -> Counter -> Model -> (Model, Maybe E.Value)
propose binding request_ model =
    if model.pending/=Nothing || request_==UInt64.zero || model.observation==Nothing || (model.applied |> Maybe.map (\a -> a.binding==binding && a.profile==desired model) |> Maybe.withDefault False) then (model,Nothing)
    else
        let pending={binding=binding,request=request_,profile=desired model}
        in ({model | pending=Just pending},Just (request pending))

request pending = E.object [("protocolVersion",E.int 3),("kind",E.string "motion-profile-set"),("binding",Binding.encode pending.binding),("requestId",E.string (UInt64.string pending.request)),("profile",E.string (name pending.profile))]

receive : Maybe Binding.Binding -> Receipt -> Model -> Model
receive binding receipt model =
    if binding/=Just receipt.binding || model.pending/=Just receipt then model
    else {model | pending=Nothing,applied=Just {binding=receipt.binding,profile=receipt.profile}}

ready : Maybe Binding.Binding -> Model -> Bool
ready binding model =
    -- The native session defaults to the instant profile before observation.
    model.observation==Nothing || (model.pending==Nothing && (model.applied |> Maybe.map (\a -> binding==Just a.binding && a.profile==desired model) |> Maybe.withDefault False))

notice : Model -> String
notice model =
    case model.observation of
        Nothing -> "Motion preference is being read; transitions are instant."
        Just observation ->
            if model.pending/=Nothing then "Applying motion preference…"
            else if observation.profile==Reduced then "Reduced motion: instant transitions"
            else "System motion preference: full motion"
