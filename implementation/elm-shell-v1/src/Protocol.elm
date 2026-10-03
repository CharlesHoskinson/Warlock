module Protocol exposing (AuthorityId, Event(..), Window, decode, encodeRequest, idString)

import Json.Decode as D
import Json.Encode as E


type AuthorityId
    = AuthorityId String


idString : AuthorityId -> String
idString (AuthorityId value) =
    value


identityDecoder : D.Decoder AuthorityId
identityDecoder =
    D.string
        |> D.andThen
            (\value ->
                if not (String.isEmpty value) && String.all (\c -> c >= '0' && c <= '9') value && (value == "0" || not (String.startsWith "0" value)) && String.length value <= 20 && (String.length value < 20 || value <= "18446744073709551615") then
                    D.succeed (AuthorityId value)

                else
                    D.fail "Expected canonical unsigned 64-bit decimal string"
            )


type alias Window =
    { incarnation : AuthorityId
    , label : String
    , minimized : Bool
    }


type Event
    = FixtureSnapshot AuthorityId (List Window)


windowDecoder : D.Decoder Window
windowDecoder =
    D.map3 Window (D.field "incarnation" identityDecoder) (D.field "label" D.string) (D.field "minimized" D.bool)


uniqueWindows : List Window -> D.Decoder (List Window)
uniqueWindows windows =
    let
        ids = List.map (.incarnation >> idString) windows
        unique = List.foldl (\item acc -> if List.member item acc then acc else item :: acc) [] ids
    in
    if List.length ids == List.length unique && List.length ids <= 64 then
        D.succeed windows
    else
        D.fail "Duplicate identity or fixture item bound exceeded"


decoder : D.Decoder Event
decoder =
    D.field "protocolVersion" D.int
        |> D.andThen
            (\version ->
                if version /= 1 then
                    D.fail "Unsupported protocol version"
                else
                    D.field "kind" D.string
                        |> D.andThen
                            (\kind ->
                                if kind == "fixture-snapshot" then
                                    D.field "source" D.string
                                        |> D.andThen (\source -> if source == "fixture" then D.map2 FixtureSnapshot (D.field "epoch" identityDecoder) (D.field "windows" (D.list windowDecoder |> D.andThen uniqueWindows)) else D.fail "This slice admits fixture observations only")
                                else
                                    D.fail "Unsupported event kind"
                            )
            )


decode : D.Value -> Result D.Error Event
decode =
    D.decodeValue decoder


encodeRequest : String -> E.Value
encodeRequest kind =
    E.object [ ( "protocolVersion", E.int 1 ), ( "kind", E.string kind ) ]
