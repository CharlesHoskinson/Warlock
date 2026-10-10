module CapturedAction exposing (CapturedAction, decode, encode, publication, lease, surface, identity)

import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

-- Opaque transport envelope; not an authenticated input-origin capability.
type CapturedAction = CapturedAction { publication : Counter, lease : Counter, surface : String, identity : String, trigger : Maybe String }

decode : D.Value -> Result D.Error CapturedAction
decode raw =
    let
        hasTrigger=D.decodeValue (D.field "trigger" D.value) raw |> Result.toMaybe |> (/=) Nothing
        origin=if hasTrigger then D.field "trigger" (D.string |> D.andThen (\value -> if List.member value ["pointer","keyboard"] then D.succeed (Just value) else D.fail "Action origin")) else D.succeed Nothing
        fields = ["id","kind","lease","publication","surface","surfaceProtocol"]++(if hasTrigger then ["trigger"] else [])
        decoder = D.keyValuePairs D.value |> D.andThen (\pairs ->
            if List.sort (List.map Tuple.first pairs) /= fields then D.fail "Action fields" else
                D.map7 (\version kind shown scoped role name trigger -> (version,kind,{publication=shown,lease=scoped,surface=role,identity=name,trigger=trigger}))
                    (D.field "surfaceProtocol" D.int) (D.field "kind" D.string)
                    (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder)
                    (D.field "surface" D.string) (D.field "id" D.string) origin
                    |> D.andThen (\(version,kind,value) ->
                        if version==2 && kind=="surface-action" && value.publication/=UInt64.zero && List.member value.surface ["bar","popup"] && not (String.isEmpty value.identity) && String.length value.identity<=512 && not (String.any (\c -> Char.toCode c<32) value.identity) then D.succeed (CapturedAction value) else D.fail "Action scope"))
    in D.decodeValue decoder raw

encode : CapturedAction -> E.Value
encode (CapturedAction value) = E.object ([("surface",E.string value.surface),("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("publication",E.string (UInt64.string value.publication)),("lease",E.string (UInt64.string value.lease)),("id",E.string value.identity)] ++ (value.trigger |> Maybe.map (\trigger -> [("trigger",E.string trigger)]) |> Maybe.withDefault []))

publication : CapturedAction -> Counter
publication (CapturedAction value) = value.publication
lease : CapturedAction -> Counter
lease (CapturedAction value) = value.lease
surface : CapturedAction -> String
surface (CapturedAction value) = value.surface
identity : CapturedAction -> String
identity (CapturedAction value) = value.identity
