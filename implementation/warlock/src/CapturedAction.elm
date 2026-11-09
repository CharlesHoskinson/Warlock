module CapturedAction exposing (CapturedAction, decode, encode, publication, lease, surface, identity, Context, decodeContext, encodeContext, contextPublication, contextLease, contextIdentity)

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


-- Keyboard context is a distinct envelope, never an action-kind alias.
-- Its publication/lease are revalidated against the current Bar presentation.
type Context = Context { publication : Counter, lease : Counter, identity : String }

decodeContext : D.Value -> Result D.Error Context
decodeContext raw =
    let
        contextDecoder =
            D.keyValuePairs D.value |> D.andThen (\pairs ->
                if List.sort (List.map Tuple.first pairs) /= ["id","kind","lease","publication","surface","surfaceProtocol","trigger","x","y"] then
                    D.fail "Context fields"
                else
                    D.map8 (\version contextKind shown scoped role targetId origin coordinates ->
                        {version=version,kind=contextKind,publication=shown,lease=scoped,role=role,targetId=targetId,origin=origin,coordinates=coordinates})
                        (D.field "surfaceProtocol" D.int) (D.field "kind" D.string)
                        (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder)
                        (D.field "surface" D.string) (D.field "id" D.string)
                        (D.field "trigger" D.string)
                        (D.map2 Tuple.pair (D.field "x" D.int) (D.field "y" D.int))
                        |> D.andThen (\captured ->
                            let taskbarTarget =
                                    List.any (\prefix -> String.startsWith prefix captured.targetId && String.length captured.targetId > String.length prefix) ["bar:group:","bar:pin:"]
                            in if captured.version==2 && captured.kind=="surface-context" && captured.role=="bar"
                                && captured.origin=="keyboard" && captured.coordinates==(0,0)
                                && captured.publication/=UInt64.zero && taskbarTarget
                                && String.length captured.targetId<=512 && not (String.any (\c -> Char.toCode c<32) captured.targetId) then
                                D.succeed (Context {publication=captured.publication,lease=captured.lease,identity=captured.targetId})
                            else
                                D.fail "Context scope"))
    in
    D.decodeValue contextDecoder raw

encodeContext : Context -> E.Value
encodeContext (Context captured) =
    E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-context"),("surface",E.string "bar")
        ,("publication",E.string (UInt64.string captured.publication)),("lease",E.string (UInt64.string captured.lease))
        ,("id",E.string captured.identity),("trigger",E.string "keyboard"),("x",E.int 0),("y",E.int 0)]

contextPublication : Context -> Counter
contextPublication (Context captured) = captured.publication

contextLease : Context -> Counter
contextLease (Context captured) = captured.lease

contextIdentity : Context -> String
contextIdentity (Context captured) = captured.identity
