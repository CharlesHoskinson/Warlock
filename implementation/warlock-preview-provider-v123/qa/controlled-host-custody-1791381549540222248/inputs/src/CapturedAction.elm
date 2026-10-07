module CapturedAction exposing (CapturedAction, decode, encode, publication, lease, surface, identity)

import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

-- Opaque transport envelope; not an authenticated input-origin capability.
type CapturedAction = CapturedAction { publication : Counter, lease : Counter, surface : String, identity : String }

decode : D.Value -> Result D.Error CapturedAction
decode raw =
    let
        fields = ["id","kind","lease","publication","surface","surfaceProtocol"]
        decoder = D.keyValuePairs D.value |> D.andThen (\pairs ->
            if List.sort (List.map Tuple.first pairs) /= fields then D.fail "Action fields" else
                D.map6 (\version kind shown scoped role name -> (version,kind,{publication=shown,lease=scoped,surface=role,identity=name}))
                    (D.field "surfaceProtocol" D.int) (D.field "kind" D.string)
                    (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder)
                    (D.field "surface" D.string) (D.field "id" D.string)
                    |> D.andThen (\(version,kind,value) ->
                        if version==2 && kind=="surface-action" && value.publication/=UInt64.zero && List.member value.surface ["bar","popup"] && not (String.isEmpty value.identity) && String.length value.identity<=512 && not (String.any (\c -> Char.toCode c<32) value.identity) then D.succeed (CapturedAction value) else D.fail "Action scope"))
    in D.decodeValue decoder raw

encode : CapturedAction -> E.Value
encode (CapturedAction value) = E.object [("surface",E.string value.surface),("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("publication",E.string (UInt64.string value.publication)),("lease",E.string (UInt64.string value.lease)),("id",E.string value.identity)]

publication : CapturedAction -> Counter
publication (CapturedAction value) = value.publication
lease : CapturedAction -> Counter
lease (CapturedAction value) = value.lease
surface : CapturedAction -> String
surface (CapturedAction value) = value.surface
identity : CapturedAction -> String
identity (CapturedAction value) = value.identity
