# official/packages/elm/bytes/1.0.2/docs.json
Source: https://package.elm-lang.org/packages/elm/bytes/1.0.2/docs.json

# Bytes



# Bytes
@docs Bytes, width

# Endianness
@docs Endianness, getHostEndianness



## Bytes

```elm
-- Opaque type: Bytes (constructors not exposed)
```

 A sequence of bytes.

A byte is a chunk of eight bits. For example, the letter `j` is usually
represented as the byte `01101010`, and the letter `k` is `01101011`.

Seeing each byte as a stream of zeros and ones can be quite confusing though,
so it is common to use hexidecimal numbers instead:

```
| Binary | Hex |
+--------+-----+
|  0000  |  0  |
|  0001  |  1  |
|  0010  |  2  |
|  0011  |  3  |     j = 01101010
|  0100  |  4  |         \__/\__/
|  0101  |  5  |           |   |
|  0110  |  6  |           6   A
|  0111  |  7  |
|  1000  |  8  |     k = 01101011
|  1001  |  9  |         \__/\__/
|  1010  |  A  |           |   |
|  1011  |  B  |           6   B
|  1100  |  C  |
|  1101  |  D  |
|  1110  |  E  |
|  1111  |  F  |
```

So `j` is `6A` and `k` is `6B` in hexidecimal. This more compact representation
is great when you have a sequence of bytes. You can see this even in a short
string like `"jazz"`:

```
binary                                 hexidecimal
01101010 01100001 01111010 01111010 => 6A 61 7A 7A
```

Anyway, the point is that `Bytes` is a sequence of bytes!


## Endianness

```elm
type Endianness
    = LE
    | BE
```

 Different computers store integers and floats slightly differently in
memory. Say we have the integer `0x1A2B3C4D` in our program. It needs four
bytes (32 bits) in memory. It may seem reasonable to lay them out in order:

```
   Big-Endian (BE)      (Obvious Order)
+----+----+----+----+
| 1A | 2B | 3C | 4D |
+----+----+----+----+
```

But some people thought it would be better to store the bytes in the opposite
order:

```
  Little-Endian (LE)    (Shuffled Order)
+----+----+----+----+
| 4D | 3C | 2B | 1A |
+----+----+----+----+
```

Notice that **the _bytes_ are shuffled, not the bits.** It is like if you cut a
photo into four strips and shuffled the strips. It is not a mirror image.
The theory seems to be that an 8-bit `0x1A` and a 32-bit `0x0000001A` both have
`1A` as the first byte in this scheme. Maybe this was helpful when processors
handled one byte at a time.

**Most processors use little-endian (LE) layout.** This seems to be because
Intel did it this way, and other chip manufactures followed their convention.
**Most network protocols use big-endian (BE) layout.** I suspect this is
because if you are trying to debug a network protocol, it is nice if your
integers are not all shuffled.

**Note:** Endianness is relevant for integers and floats, but not strings.
UTF-8 specifies the order of bytes explicitly.

**Note:** The terms little-endian and big-endian are a reference to an egg joke
in Gulliver's Travels. They first appeared in 1980 in [this essay][essay], and
you can decide for yourself if they stood the test of time. I personally find
these terms quite unhelpful, so I say “Obvious Order” and “Shuffled Order” in
my head. I remember which is more common by asking myself, “if things were
obvious, would I have to ask this question?”

[essay]: http://www.ietf.org/rfc/ien/ien137.txt


## getHostEndianness

```elm
getHostEndianness : Task.Task x Bytes.Endianness
```

 Is this program running on a big-endian or little-endian machine?


## width

```elm
width : Bytes.Bytes -> Basics.Int
```

 Get the width of a sequence of bytes.

So if a sequence has four-hundred bytes, then `width bytes` would give back
`400`. That may be 400 unsigned 8-bit integers, 100 signed 32-bit integers, or
even a UTF-8 string. The content does not matter. This is just figuring out
how many bytes there are!


# Bytes.Decode



# Decoders
@docs Decoder, decode

# Integers
@docs signedInt8, signedInt16, signedInt32,
  unsignedInt8, unsignedInt16, unsignedInt32

# Floats
@docs float32, float64

# Bytes
@docs bytes

# Strings
@docs string

# Map
@docs map, map2, map3, map4, map5

# And Then
@docs andThen, succeed, fail

# Loop
@docs Step, loop


## Decoder

```elm
-- Opaque type: Decoder a (constructors not exposed)
```

 Describes how to turn a sequence of bytes into a nice Elm value.


## Step

```elm
type Step state a
    = Loop (state)
    | Done (a)
```

 Decide what steps to take next in your [`loop`](#loop).

If you are `Done`, you give the result of the whole `loop`. If you decide to
`Loop` around again, you give a new state to work from. Maybe you need to add
an item to a list? Or maybe you need to track some information about what you
just saw?

**Note:** It may be helpful to learn about [finite-state machines][fsm] to get
a broader intuition about using `state`. I.e. You may want to create a `type`
that describes four possible states, and then use `Loop` to transition between
them as you consume characters.

[fsm]: https://en.wikipedia.org/wiki/Finite-state_machine


## andThen

```elm
andThen : (a -> Bytes.Decode.Decoder b) -> Bytes.Decode.Decoder a -> Bytes.Decode.Decoder b
```

 Decode something **and then** use that information to decode something
else. This is most common with strings or sequences where you need to read
how long the value is going to be:

    import Bytes exposing (Endianness(..))
    import Bytes.Decode as Decode

    string : Decoder String
    string =
      Decode.unsignedInt32 BE
        |> Decode.andThen Decode.string

Check out the docs for [`succeed`](#succeed), [`fail`](#fail), and
[`loop`](#loop) to see `andThen` used in more ways!


## bytes

```elm
bytes : Basics.Int -> Bytes.Decode.Decoder Bytes.Bytes
```

 Copy a given number of bytes into a new `Bytes` sequence.


## decode

```elm
decode : Bytes.Decode.Decoder a -> Bytes.Bytes -> Maybe.Maybe a
```

 Turn a sequence of bytes into a nice Elm value.

    -- decode (unsignedInt16 BE) <0007> == Just 7
    -- decode (unsignedInt16 LE) <0700> == Just 7
    -- decode (unsignedInt16 BE) <0700> == Just 1792
    -- decode (unsignedInt32 BE) <0700> == Nothing

The `Decoder` specifies exactly how this should happen. This process may fail
if the sequence of bytes is corrupted or unexpected somehow. The examples above
show a case where there are not enough bytes.


## fail

```elm
fail : Bytes.Decode.Decoder a
```

 A decoder that always fails. This can be useful when using `andThen` to
decode custom types:

    import Bytes exposing (Endianness(..))
    import Bytes.Encode as Encode
    import Bytes.Decode as Decode

    type Distance = Yards Float | Meters Float

    toEncoder : Distance -> Encode.Encoder
    toEncoder distance =
      case distance of
        Yards n -> Encode.sequence [ Encode.unsignedInt8 0, Encode.float32 BE n ]
        Meters n -> Encode.sequence [ Encode.unsignedInt8 1, Encode.float32 BE n ]

    decoder : Decode.Decoder Distance
    decoder =
      Decode.unsignedInt8
        |> Decode.andThen pickDecoder

    pickDecoder : Int -> Decode.Decoder Distance
    pickDecoder tag =
      case tag of
        0 -> Decode.map Yards (Decode.float32 BE)
        1 -> Decode.map Meters (Decode.float32 BE)
        _ -> Decode.fail

The encoding chosen here uses an 8-bit unsigned integer to indicate which
variant we are working with. If we are working with yards do this, if we are
working with meters do that, and otherwise something went wrong!


## float32

```elm
float32 : Bytes.Endianness -> Bytes.Decode.Decoder Basics.Float
```

 Decode four bytes into a floating point number.


## float64

```elm
float64 : Bytes.Endianness -> Bytes.Decode.Decoder Basics.Float
```

 Decode eight bytes into a floating point number.


## loop

```elm
loop : state -> (state -> Bytes.Decode.Decoder (Bytes.Decode.Step state a)) -> Bytes.Decode.Decoder a
```

 A decoder that can loop indefinitely. This can be helpful when parsing
repeated structures, like a list:

    import Bytes exposing (Endianness(..))
    import Bytes.Decode as Decode exposing (..)

    list : Decoder a -> Decoder (List a)
    list decoder =
      unsignedInt32 BE
        |> andThen (\len -> loop (len, []) (listStep decoder))

    listStep : Decoder a -> (Int, List a) -> Decoder (Step (Int, List a) (List a))
    listStep decoder (n, xs) =
      if n <= 0 then
        succeed (Done xs)
      else
        map (\x -> Loop (n - 1, x :: xs)) decoder

The `list` decoder first reads a 32-bit unsigned integer. That determines how
many items will be decoded. From there we use [`loop`](#loop) to track all the
items we have parsed so far and figure out when to stop.


## map

```elm
map : (a -> b) -> Bytes.Decode.Decoder a -> Bytes.Decode.Decoder b
```

 Transform the value produced by a decoder. If you encode negative numbers
in a special way, you can say something like this:

    negativeInt8 : Decoder Int
    negativeInt8 =
      map negate unsignedInt8

In practice you may see something like ProtoBuf’s [ZigZag encoding][zz] which
decreases the size of small negative numbers.

[zz]: https://developers.google.com/protocol-buffers/docs/encoding#types


## map2

```elm
map2 : (a -> b -> result) -> Bytes.Decode.Decoder a -> Bytes.Decode.Decoder b -> Bytes.Decode.Decoder result
```

 Combine two decoders.

    import Bytes exposing (Endiannness(..))
    import Bytes.Decode as Decode

    type alias Point = { x : Float, y : Float }

    decoder : Decode.Decoder Point
    decoder =
      Decode.map2 Point
        (Decode.float32 BE)
        (Decode.float32 BE)


## map3

```elm
map3 : (a -> b -> c -> result) -> Bytes.Decode.Decoder a -> Bytes.Decode.Decoder b -> Bytes.Decode.Decoder c -> Bytes.Decode.Decoder result
```

 Combine three decoders.


## map4

```elm
map4 : (a -> b -> c -> d -> result) -> Bytes.Decode.Decoder a -> Bytes.Decode.Decoder b -> Bytes.Decode.Decoder c -> Bytes.Decode.Decoder d -> Bytes.Decode.Decoder result
```

 Combine four decoders.


## map5

```elm
map5 : (a -> b -> c -> d -> e -> result) -> Bytes.Decode.Decoder a -> Bytes.Decode.Decoder b -> Bytes.Decode.Decoder c -> Bytes.Decode.Decoder d -> Bytes.Decode.Decoder e -> Bytes.Decode.Decoder result
```

 Combine five decoders. If you need to combine more things, it is possible
to define more of these with `map2` or `andThen`.


## signedInt16

```elm
signedInt16 : Bytes.Endianness -> Bytes.Decode.Decoder Basics.Int
```

 Decode two bytes into an integer from `-32768` to `32767`.


## signedInt32

```elm
signedInt32 : Bytes.Endianness -> Bytes.Decode.Decoder Basics.Int
```

 Decode four bytes into an integer from `-2147483648` to `2147483647`.


## signedInt8

```elm
signedInt8 : Bytes.Decode.Decoder Basics.Int
```

 Decode one byte into an integer from `-128` to `127`.


## string

```elm
string : Basics.Int -> Bytes.Decode.Decoder String.String
```

 Decode a given number of UTF-8 bytes into a `String`.

Most protocols store the width of the string right before the content, so you
will probably write things like this:

    import Bytes exposing (Endianness(..))
    import Bytes.Decode as Decode

    sizedString : Decode.Decoder String
    sizedString =
      Decode.unsignedInt32 BE
        |> Decode.andThen Decode.string

In this case we read the width as a 32-bit unsigned integer, but you have the
leeway to read the width as a [Base 128 Varint][pb] for ProtoBuf, a
[Variable-Length Integer][sql] for SQLite, or whatever else they dream up.

[pb]: https://developers.google.com/protocol-buffers/docs/encoding#varints
[sql]: https://www.sqlite.org/src4/doc/trunk/www/varint.wiki


## succeed

```elm
succeed : a -> Bytes.Decode.Decoder a
```

 A decoder that always succeeds with a certain value. Maybe we are making
a `Maybe` decoder:

    import Bytes.Decode as Decode exposing (Decoder)

    maybe : Decoder a -> Decoder (Maybe a)
    maybe decoder =
      let
        helper n =
          if n == 0 then
            Decode.succeed Nothing
          else
            Decode.map Just decoder
      in
      Decode.unsignedInt8
        |> Decode.andThen helper

If the first byte is `00000000` then it is `Nothing`, otherwise we start
decoding the value and put it in a `Just`.


## unsignedInt16

```elm
unsignedInt16 : Bytes.Endianness -> Bytes.Decode.Decoder Basics.Int
```

 Decode two bytes into an integer from `0` to `65535`.


## unsignedInt32

```elm
unsignedInt32 : Bytes.Endianness -> Bytes.Decode.Decoder Basics.Int
```

 Decode four bytes into an integer from `0` to `4294967295`.


## unsignedInt8

```elm
unsignedInt8 : Bytes.Decode.Decoder Basics.Int
```

 Decode one byte into an integer from `0` to `255`.


# Bytes.Encode



# Encoders
@docs encode, Encoder, sequence

# Integers
@docs signedInt8, signedInt16, signedInt32,
  unsignedInt8, unsignedInt16, unsignedInt32

# Floats
@docs float32, float64

# Bytes
@docs bytes

# Strings
@docs string, getStringWidth



## Encoder

```elm
-- Opaque type: Encoder (constructors not exposed)
```

 Describes how to generate a sequence of bytes.

These encoders snap together with [`sequence`](#sequence) so you can start with
small building blocks and put them together into a more complex encoding.


## bytes

```elm
bytes : Bytes.Bytes -> Bytes.Encode.Encoder
```

 Copy bytes directly into the new `Bytes` sequence. This does not record the
width though! You usually want to say something like this:

    import Bytes exposing (Bytes, Endianness(..))
    import Bytes.Encode as Encode

    png : Bytes -> Encode.Encoder
    png imageData =
      Encode.sequence
        [ Encode.unsignedInt32 BE (Bytes.width imageData)
        , Encode.bytes imageData
        ]

This allows you to represent the width however is necessary for your protocol.
For example, you can use [Base 128 Varints][pb] for ProtoBuf,
[Variable-Length Integers][sql] for SQLite, or whatever else they dream up.

[pb]: https://developers.google.com/protocol-buffers/docs/encoding#varints
[sql]: https://www.sqlite.org/src4/doc/trunk/www/varint.wiki


## encode

```elm
encode : Bytes.Encode.Encoder -> Bytes.Bytes
```

 Turn an `Encoder` into `Bytes`.

    encode (unsignedInt8     7) -- <07>
    encode (unsignedInt16 BE 7) -- <0007>
    encode (unsignedInt16 LE 7) -- <0700>

The `encode` function is designed to minimize allocation. It figures out the
exact width necessary to fit everything in `Bytes` and then generate that
value directly. This is valuable when you are encoding more elaborate data:

    import Bytes exposing (Endianness(..))
    import Bytes.Encode as Encode

    type alias Person =
      { age : Int
      , name : String
      }

    toEncoder : Person -> Encode.Encoder
    toEncoder person =
      Encode.sequence
        [ Encode.unsignedInt16 BE person.age
        , Encode.unsignedInt16 BE (Encode.getStringWidth person.name)
        , Encode.string person.name
        ]

    -- encode (toEncoder (Person 33 "Tom")) == <00210003546F6D>

Did you know it was going to be seven bytes? How about when you have a hundred
people to serialize? And when some have Japanese and Norwegian names? Having
this intermediate `Encoder` can help reduce allocation quite a lot!


## float32

```elm
float32 : Bytes.Endianness -> Basics.Float -> Bytes.Encode.Encoder
```

 Encode 32-bit floating point numbers in four bytes.


## float64

```elm
float64 : Bytes.Endianness -> Basics.Float -> Bytes.Encode.Encoder
```

 Encode 64-bit floating point numbers in eight bytes.


## getStringWidth

```elm
getStringWidth : String.String -> Basics.Int
```

 Get the width of a `String` in UTF-8 bytes.

    getStringWidth "$20"   == 3
    getStringWidth "£20"   == 4
    getStringWidth "€20"   == 5
    getStringWidth "bread" == 5
    getStringWidth "brød"  == 5

Most protocols need this number to come directly before a chunk of UTF-8 bytes
as a way to know where the string ends!

Read more about how UTF-8 works [here](https://en.wikipedia.org/wiki/UTF-8).


## sequence

```elm
sequence : List.List Bytes.Encode.Encoder -> Bytes.Encode.Encoder
```

 Put together a bunch of builders. So if you wanted to encode three `Float`
values for the position of a ball in 3D space, you could say:

    import Bytes exposing (Endianness(..))
    import Bytes.Encode as Encode

    type alias Ball = { x : Float, y : Float, z : Float }

    ball : Ball -> Encode.Encoder
    ball {x,y,z} =
      Encode.sequence
        [ Encode.float32 BE x
        , Encode.float32 BE y
        , Encode.float32 BE z
        ]



## signedInt16

```elm
signedInt16 : Bytes.Endianness -> Basics.Int -> Bytes.Encode.Encoder
```

 Encode integers from `-32768` to `32767` in two bytes.


## signedInt32

```elm
signedInt32 : Bytes.Endianness -> Basics.Int -> Bytes.Encode.Encoder
```

 Encode integers from `-2147483648` to `2147483647` in four bytes.


## signedInt8

```elm
signedInt8 : Basics.Int -> Bytes.Encode.Encoder
```

 Encode integers from `-128` to `127` in one byte.


## string

```elm
string : String.String -> Bytes.Encode.Encoder
```

 Encode a `String` as a bunch of UTF-8 bytes.

    encode (string "$20")   -- <24 32 30>
    encode (string "£20")   -- <C2A3 32 30>
    encode (string "€20")   -- <E282AC 32 30>
    encode (string "bread") -- <62 72 65 61 64>
    encode (string "brød")  -- <62 72 C3B8 64>

Some characters take one byte, while others can take up to four. Read more
about [UTF-8](https://en.wikipedia.org/wiki/UTF-8) to learn the details!

But if you just encode UTF-8 directly, how can you know when you get to the end
of the string when you are decoding? So most protocols have an integer saying
how many bytes follow, like this:

    sizedString : String -> Encoder
    sizedString str =
      sequence
        [ unsignedInt32 BE (getStringWidth str)
        , string str
        ]

You can choose whatever representation you want for the width, which is helpful
because many protocols use different integer representations to save space. For
example:

- ProtoBuf uses [Base 128 Varints](https://developers.google.com/protocol-buffers/docs/encoding#varints)
- SQLite uses [Variable-Length Integers](https://www.sqlite.org/src4/doc/trunk/www/varint.wiki)

In both cases, small numbers can fit just one byte, saving some space. (The
SQLite encoding has the benefit that the first byte tells you how long the
number is, making it faster to decode.) In both cases, it is sort of tricky
to make negative numbers small.


## unsignedInt16

```elm
unsignedInt16 : Bytes.Endianness -> Basics.Int -> Bytes.Encode.Encoder
```

 Encode integers from `0` to `65535` in two bytes.


## unsignedInt32

```elm
unsignedInt32 : Bytes.Endianness -> Basics.Int -> Bytes.Encode.Encoder
```

 Encode integers from `0` to `4294967295` in four bytes.


## unsignedInt8

```elm
unsignedInt8 : Basics.Int -> Bytes.Encode.Encoder
```

 Encode integers from `0` to `255` in one byte.

