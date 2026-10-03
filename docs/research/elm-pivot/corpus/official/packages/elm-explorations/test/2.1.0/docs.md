# official/packages/elm-explorations/test/2.1.0/docs.json
Source: https://package.elm-lang.org/packages/elm-explorations/test/2.1.0/docs.json

# Expect

 A library to create `Expectation`s, which describe a claim to be tested.


## Quick Reference

  - [`equal`](#equal) `(arg2 == arg1)`
  - [`notEqual`](#notEqual) `(arg2 /= arg1)`
  - [`lessThan`](#lessThan) `(arg2 < arg1)`
  - [`atMost`](#atMost) `(arg2 <= arg1)`
  - [`greaterThan`](#greaterThan) `(arg2 > arg1)`
  - [`atLeast`](#atLeast) `(arg2 >= arg1)`
  - [Floating Point Comparisons](#floating-point-comparisons)


## Basic Expectations

@docs Expectation, equal, notEqual, all


## Numeric Comparisons

@docs lessThan, atMost, greaterThan, atLeast


## Floating Point Comparisons

These functions allow you to compare `Float` values up to a specified rounding error, which may be relative, absolute,
or both. For an in-depth look, see our [Guide to Floating Point Comparison](#guide-to-floating-point-comparison).

@docs FloatingPointTolerance, within, notWithin


## Collections

@docs ok, err, equalLists, equalDicts, equalSets


## Customizing

These functions will let you build your own expectations.

@docs pass, fail, onFail


## Guide to Floating Point Comparison

In general, if you are multiplying, you want relative tolerance, and if you're adding,
you want absolute tolerance. If you are doing both, you want both kinds of tolerance,
or to split the calculation into smaller parts for testing.


### Absolute Tolerance

Let's say we want to figure out if our estimation of pi is precise enough.

Is `3.14` within `0.01` of `pi`? Yes, because `3.13 < pi < 3.15`.

    test "3.14 approximates pi with absolute precision" <|
        \_ ->
            3.14 |> Expect.within (Absolute 0.01) pi


### Relative Tolerance

What if we also want to know if our circle circumference estimation is close enough?

Let's say our circle has a radius of `r` meters. The formula for circle circumference is `C=2*r*pi`.
To make the calculations a bit easier ([ahem](https://tauday.com/tau-manifesto)), we'll look at half the circumference; `C/2=r*pi`.
Is `r * 3.14` within `0.01` of `r * pi`?
That depends, what does `r` equal? If `r` is `0.01`mm, or `0.00001` meters, we're comparing
`0.00001 * 3.14 - 0.01 < r * pi < 0.00001 * 3.14 + 0.01` or `-0.0099686 < 0.0000314159 < 0.0100314`.
That's a huge tolerance! A circumference that is _a thousand times longer_ than we expected would pass that test!

On the other hand, if `r` is very large, we're going to need many more digits of pi.
For an absolute tolerance of `0.01` and a pi estimation of `3.14`, this expectation only passes if `r < 2*pi`.

If we use a relative tolerance of `0.01` instead, the circle area comparison becomes much better. Is `r * 3.14` within
`1%` of `r * pi`? Yes! In fact, three digits of pi approximation is always good enough for a 0.1% relative tolerance,
as long as `r` isn't [too close to zero](https://en.wikipedia.org/wiki/Denormal_number).

    fuzz
        (floatRange 0.000001 100000)
        "Circle half-circumference with relative tolerance"
        (\r -> r * 3.14 |> Expect.within (Relative 0.001) (r * pi))


### Trouble with Numbers Near Zero

If you are adding things near zero, you probably want absolute tolerance. If you're comparing values between `-1` and `1`, you should consider using absolute tolerance.

For example: Is `1 + 2 - 3` within `1%` of `0`? Well, if `1`, `2` and `3` have any amount of rounding error, you might not get exactly zero. What is `1%` above and below `0`? Zero. We just lost all tolerance. Even if we hard-code the numbers, we might not get exactly zero; `0.1 + 0.2` rounds to a value just above `0.3`, since computers, counting in binary, cannot write down any of those three numbers using a finite number of digits, just like we cannot write `0.333...` exactly in base 10.

Another example is comparing values that are on either side of zero. `0.0001` is more than `100%` away from `-0.0001`. In fact, `infinity` is closer to `0.0001` than `0.0001` is to `-0.0001`, if you are using a relative tolerance. Twice as close, actually. So even though both `0.0001` and `-0.0001` could be considered very close to zero, they are very far apart relative to each other. The same argument applies for any number of zeroes.



## Expectation

```elm
type alias Expectation =
    Test.Expectation.Expectation
```

 The result of a single test run: either a [`pass`](#pass) or a
[`fail`](#fail).


## FloatingPointTolerance

```elm
type FloatingPointTolerance
    = Absolute (Basics.Float)
    | Relative (Basics.Float)
    | AbsoluteOrRelative (Basics.Float) (Basics.Float)
```

 A type to describe how close a floating point number must be to the expected value for the test to pass. This may be
specified as absolute or relative.

`AbsoluteOrRelative` tolerance uses a logical OR between the absolute (specified first) and relative tolerance. If you
want a logical AND, use [`Expect.all`](#all).



## all

```elm
all : List.List (subject -> Expect.Expectation) -> subject -> Expect.Expectation
```

 Passes if each of the given functions passes when applied to the subject.

Passing an empty list is assumed to be a mistake, so `Expect.all []`
will always return a failed expectation no matter what else it is passed.

    Expect.all
        [ Expect.greaterThan -2
        , Expect.lessThan 5
        ]
        (List.length [])
    -- Passes because (0 > -2) is True and (0 < 5) is also True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because (0 < -10) is False
    List.length []
        |> Expect.all
            [ Expect.greaterThan -2
            , Expect.lessThan -10
            , Expect.equal 0
            ]
    {-
    0
    ╷
    │ Expect.lessThan
    ╵
    -10
    -}



## atLeast

```elm
atLeast : comparable -> comparable -> Expect.Expectation
```

 Passes if the second argument is greater than or equal to the first.

    Expect.atLeast -2 (List.length [])

    -- Passes because (0 >= -2) is True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because (0 >= 3) is False
    List.length []
        |> Expect.atLeast 3

    {-

    0
    ╷
    │ Expect.atLeast
    ╵
    3

    -}



## atMost

```elm
atMost : comparable -> comparable -> Expect.Expectation
```

 Passes if the second argument is less than or equal to the first.

    Expect.atMost 1 (List.length [])

    -- Passes because (0 <= 1) is True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because (0 <= -3) is False
    List.length []
        |> Expect.atMost -3

    {-

    0
    ╷
    │ Expect.atMost
    ╵
    -3

    -}



## equal

```elm
equal : a -> a -> Expect.Expectation
```

 Passes if the arguments are equal.

    Expect.equal 0 (List.length [])

    -- Passes because (0 == 0) is True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because the expected value didn't split the space in "Betty Botter"
    String.split " " "Betty Botter bought some butter"
        |> Expect.equal [ "Betty Botter", "bought", "some", "butter" ]

    {-

    [ "Betty", "Botter", "bought", "some", "butter" ]
    ╷
    │ Expect.equal
    ╵
    [ "Betty Botter", "bought", "some", "butter" ]

    -}

Do not equate `Float` values; use [`within`](#within) instead.



## equalDicts

```elm
equalDicts : Dict.Dict comparable a -> Dict.Dict comparable a -> Expect.Expectation
```

 Passes if the arguments are equal dicts.

    -- Passes
    Dict.fromList [ ( 1, "one" ), ( 2, "two" ) ]
        |> Expect.equalDicts (Dict.fromList [ ( 1, "one" ), ( 2, "two" ) ])

Failures resemble code written in pipeline style, so you can tell
which argument is which, and reports which keys were missing from
or added to each dict:

    -- Fails
    (Dict.fromList [ ( 1, "one" ), ( 2, "too" ) ])
        |> Expect.equalDicts (Dict.fromList [ ( 1, "one" ), ( 2, "two" ), ( 3, "three" ) ])

    {-

    Dict.fromList [(1,"one"),(2,"too")]
    diff: -[ (2,"two"), (3,"three") ] +[ (2,"too") ]
    ╷
    │ Expect.equalDicts
    ╵
    diff: +[ (2,"two"), (3,"three") ] -[ (2,"too") ]
    Dict.fromList [(1,"one"),(2,"two"),(3,"three")]

    -}



## equalLists

```elm
equalLists : List.List a -> List.List a -> Expect.Expectation
```

 Passes if the arguments are equal lists.

    -- Passes
    [ 1, 2, 3 ]
        |> Expect.equalLists [ 1, 2, 3 ]

Failures resemble code written in pipeline style, so you can tell
which argument is which, and reports which index the lists first
differed at or which list was longer:

    -- Fails
    [ 1, 2, 4, 6 ]
        |> Expect.equalLists [ 1, 2, 5 ]

    {-

    [1,2,4,6]
    first diff at index index 2: +`4`, -`5`
    ╷
    │ Expect.equalLists
    ╵
    first diff at index index 2: +`5`, -`4`
    [1,2,5]

    -}



## equalSets

```elm
equalSets : Set.Set comparable -> Set.Set comparable -> Expect.Expectation
```

 Passes if the arguments are equal sets.

    -- Passes
    Set.fromList [ 1, 2 ]
        |> Expect.equalSets (Set.fromList [ 1, 2 ])

Failures resemble code written in pipeline style, so you can tell
which argument is which, and reports which keys were missing from
or added to each set:

    -- Fails
    (Set.fromList [ 1, 2, 4, 6 ])
        |> Expect.equalSets (Set.fromList [ 1, 2, 5 ])

    {-

    Set.fromList [1,2,4,6]
    diff: -[ 5 ] +[ 4, 6 ]
    ╷
    │ Expect.equalSets
    ╵
    diff: +[ 5 ] -[ 4, 6 ]
    Set.fromList [1,2,5]

    -}



## err

```elm
err : Result.Result a b -> Expect.Expectation
```

 Passes if the
[`Result`](http://package.elm-lang.org/packages/elm-lang/core/latest/Result) is
an `Err` rather than `Ok`. This is useful for tests where you expect to get an
error but you don't care what the actual error is.

_(Tip: If your function returns a `Maybe` instead, consider `Expect.equal Nothing`.)_

    -- Passes
    String.toInt "not an int"
        |> Result.fromMaybe "not an int"
        |> Expect.err

Test failures will be printed with the unexpected `Ok` value contrasting with
any `Err`.

    -- Fails
    String.toInt "20"
        |> Result.fromMaybe "not an int"
        |> Expect.err

    {-

    Ok 20
    ╷
    │ Expect.err
    ╵
    Err _

    -}



## fail

```elm
fail : String.String -> Expect.Expectation
```

 Fails with the given message.

    import Json.Decode exposing (decodeString, int)
    import Test exposing (test)
    import Expect


    test "Json.Decode.int can decode the number 42." <|
        \_ ->
            case decodeString int "42" of
                Ok _ ->
                    Expect.pass

                Err err ->
                    Expect.fail err



## greaterThan

```elm
greaterThan : comparable -> comparable -> Expect.Expectation
```

 Passes if the second argument is greater than the first.

    Expect.greaterThan -2 List.length []

    -- Passes because (0 > -2) is True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because (0 > 1) is False
    List.length []
        |> Expect.greaterThan 1

    {-

    0
    ╷
    │ Expect.greaterThan
    ╵
    1

    -}



## lessThan

```elm
lessThan : comparable -> comparable -> Expect.Expectation
```

 Passes if the second argument is less than the first.

    Expect.lessThan 1 (List.length [])

    -- Passes because (0 < 1) is True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because (0 < -1) is False
    List.length []
        |> Expect.lessThan -1


    {-

    0
    ╷
    │ Expect.lessThan
    ╵
    -1

    -}

Do not equate `Float` values; use [`notWithin`](#notWithin) instead.



## notEqual

```elm
notEqual : a -> a -> Expect.Expectation
```

 Passes if the arguments are not equal.

    -- Passes because (11 /= 100) is True
    90 + 10
        |> Expect.notEqual 11


    -- Fails because (100 /= 100) is False
    90 + 10
        |> Expect.notEqual 100

    {-

    100
    ╷
    │ Expect.notEqual
    ╵
    100

    -}



## notWithin

```elm
notWithin : Expect.FloatingPointTolerance -> Basics.Float -> Basics.Float -> Expect.Expectation
```

 Passes if (and only if) a call to `within` with the same arguments would have failed.


## ok

```elm
ok : Result.Result a b -> Expect.Expectation
```

 Passes if the
[`Result`](https://package.elm-lang.org/packages/lang/core/latest/Result) is
an `Ok` rather than `Err`. This is useful for tests where you expect not to see
an error, but you don't care what the actual result is.

_(Tip: If your function returns a `Maybe` instead, consider `Expect.notEqual Nothing`.)_

    -- Passes
    String.toInt "20"
        |> Result.fromMaybe "not an int"
        |> Expect.ok

Test failures will be printed with the unexpected `Err` value contrasting with
any `Ok`.

    -- Fails
    String.toInt "not an int"
        |> Result.fromMaybe "not an int"
        |> Expect.ok

    {-

    Err "not an int"
    ╷
    │ Expect.ok
    ╵
    Ok _

    -}



## onFail

```elm
onFail : String.String -> Expect.Expectation -> Expect.Expectation
```

 If the given expectation fails, replace its failure message with a custom one.

    "something"
        |> Expect.equal "something else"
        |> Expect.onFail "thought those two strings would be the same"



## pass

```elm
pass : Expect.Expectation
```

 Always passes.

    import Json.Decode exposing (decodeString, int)
    import Test exposing (test)
    import Expect


    test "Json.Decode.int can decode the number 42." <|
        \_ ->
            case decodeString int "42" of
                Ok _ ->
                    Expect.pass

                Err err ->
                    Expect.fail err



## within

```elm
within : Expect.FloatingPointTolerance -> Basics.Float -> Basics.Float -> Expect.Expectation
```

 Passes if the second and third arguments are equal within a tolerance
specified by the first argument. This is intended to avoid failing because of
minor inaccuracies introduced by floating point arithmetic.

    -- Fails because 0.1 + 0.2 == 0.30000000000000004 (0.1 is non-terminating in base 2)
    0.1 + 0.2 |> Expect.equal 0.3

    -- So instead write this test, which passes
    0.1 + 0.2 |> Expect.within (Absolute 0.000000001) 0.3

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because 3.14 is not close enough to pi
    3.14 |> Expect.within (Absolute 0.0001) pi

    {-

    3.14
    ╷
    │ Expect.within Absolute 0.0001
    ╵
    3.141592653589793

    -}



# Fuzz

 This is a library of _fuzzers_ you can use to supply values to your fuzz
tests. You can typically pick out which ones you need according to their types.

A `Fuzzer a` knows how to create values of type `a`. It can create them randomly,
so that your test's expectations are run against many values. Fuzzers will often
generate edge cases likely to find bugs. If the fuzzer can make your test fail,
the test runner also knows how to "simplify" that failing input into more minimal
examples, some of which might also cause the tests to fail. In this way, fuzzers
can usually find the simplest input that reproduces a bug.


## Fuzzers

@docs Fuzzer, examples, labelExamples


## Number fuzzers

@docs int, intRange, uniformInt, intAtLeast, intAtMost
@docs float, niceFloat, percentage, floatRange, floatAtLeast, floatAtMost


## String-related fuzzers

@docs char, asciiChar
@docs string, stringOfLength, stringOfLengthBetween, asciiString, asciiStringOfLength, asciiStringOfLengthBetween


## Collection fuzzers

@docs pair, triple
@docs list, listOfLength, listOfLengthBetween, shuffledList
@docs array, maybe, result


## Other fuzzers

@docs bool, unit, order, weightedBool


## Choosing fuzzers

@docs oneOf, oneOfValues, frequency, frequencyValues


## Working with Fuzzers

@docs constant, invalid, filter
@docs map, map2, map3, map4, map5, map6, map7, map8, andMap
@docs andThen, lazy, sequence, traverse


## Misc helpers

@docs fromGenerator



## Fuzzer

```elm
type alias Fuzzer a =
    Fuzz.Internal.Fuzzer a
```

 The representation of fuzzers is opaque. Conceptually, a `Fuzzer a` consists
of a way to randomly generate values of type `a` in a way allowing the test runner
to simplify those values.


## andMap

```elm
andMap : Fuzz.Fuzzer a -> Fuzz.Fuzzer (a -> b) -> Fuzz.Fuzzer b
```

 Map over many fuzzers. This can act as `mapN` for `N > 8`.
The argument order is meant to accommodate chaining:

    Fuzz.constant fn
        |> Fuzz.andMap fuzzerA
        |> Fuzz.andMap fuzzerB
        |> Fuzz.andMap fuzzerC



## andThen

```elm
andThen : (a -> Fuzz.Fuzzer b) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b
```

 Use a generated value to decide what fuzzer to use next.

For example, let's say you want to generate a list of given length.
One (not ideal) possible way to do that is first choosing how many elements
will there be (generating a number), `andThen` generating a list with that many
items:

    Fuzz.intRange 1 10
        |> Fuzz.andThen
            (\length ->
                let
                    go : Int -> List a -> Fuzzer (List a)
                    go left acc =
                        if left <= 0 then
                            Fuzz.constant (List.reverse acc)

                        else
                            itemFuzzer
                                |> Fuzz.andThen (\item -> go (length - 1) (item :: acc))
                in
                go length []
            )

This will work! Different fuzzers will have different PRNG usage patterns
though and will shrink with varying success. The currently best known way to
fuzz a list of items is based on a "flip a coin, `andThen` generate a value and
repeat or end" approach, and is implemented in the [`Fuzz.list`](#list) helpers
in this module. Use them instead of rolling your own list generator!

Think of `andThen` as a generalization of [`Fuzz.map`](#map). Inside
[`Fuzz.map`](#map) you don't have the option to fuzz another value based on
what you already have; inside `andThen` you do.



## array

```elm
array : Fuzz.Fuzzer a -> Fuzz.Fuzzer (Array.Array a)
```

 Given a fuzzer of a type, create a fuzzer of an array of that type.
Generates random arrays of varying length, favoring shorter arrays.


## asciiChar

```elm
asciiChar : Fuzz.Fuzzer Char.Char
```

 A fuzzer for simple ASCII char values (range 32..126).
Skips control characters and the extended character set.

For more serious char fuzzing look at [`Fuzz.char`](#char) which generates the
whole Unicode range.



## asciiString

```elm
asciiString : Fuzz.Fuzzer String.String
```

 Generates random ASCII strings of up to 10 characters.


## asciiStringOfLength

```elm
asciiStringOfLength : Basics.Int -> Fuzz.Fuzzer String.String
```

 Generates random ASCII strings of a given length.


## asciiStringOfLengthBetween

```elm
asciiStringOfLengthBetween : Basics.Int -> Basics.Int -> Fuzz.Fuzzer String.String
```

 Generates random ASCII strings of length between the given limits.


## bool

```elm
bool : Fuzz.Fuzzer Basics.Bool
```

 A fuzzer for boolean values. It's useful when building up fuzzers of complex
types that contain a boolean somewhere.

We recommend against writing tests fuzzing over booleans. Write a unit test for
the true and false cases explicitly.

Simplifies in order `False < True`.



## char

```elm
char : Fuzz.Fuzzer Char.Char
```

 A fuzzer for arbitrary Unicode char values.

Avoids surrogate pairs or their components (`0xD800..0xDFFF`).

Will prefer ASCII characters, whitespace, and some examples known to cause
trouble, like combining diacritics marks and emojis.



## constant

```elm
constant : a -> Fuzz.Fuzzer a
```

 Create a fuzzer that only and always returns the value provided, and performs
no simplifying. This is hardly random, and so this function is best used as a
helper when creating more complicated fuzzers.


## examples

```elm
examples : Basics.Int -> Fuzz.Fuzzer a -> List.List a
```

 Generate a few example values from the fuzzer.

Useful in REPL:

    > import Fuzz
    > Fuzz.examples 20 (Fuzz.intRange 20 50)
    [42,45,32,26,33,29,41,45,23,45,34,23,22,42,29,27,41,43,30,50]
        : List Int

Uses the first argument as the seed as well as the count of examples to generate.

Will return an empty list in case of rejection.



## filter

```elm
filter : (a -> Basics.Bool) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer a
```

 A fuzzer that only lets through values satisfying the given predicate
function.

Warning: By using `Fuzz.filter` you can get exceptionally unlucky and get 15
rejections in a row, in which case the test will fluke out and fail!

It's always preferable to get to your wanted values using [`Fuzz.map`](#map),
as you don't run the risk of rejecting too may values and slowing down your
tests, for example using `Fuzz.intRange 0 5 |> Fuzz.map (\x -> x * 2)` instead
of `Fuzz.intRange 0 9 |> Fuzz.filter (\x -> modBy 2 x == 0)`.

If you want to generate indefinitely until you find a satisfactory value (with
a risk of infinite loop depending on the predicate), you can use this pattern:

    goodItemFuzzer =
        itemFuzzer
            |> Fuzz.andThen
                (\item ->
                    if isGood item then
                        Fuzz.constant item

                    else
                        goodItemFuzzer
                )



## float

```elm
float : Fuzz.Fuzzer Basics.Float
```

 A fuzzer for float values.

Will prefer integer values, nice fractions and positive numbers over the rest.

Will occasionally try infinities and NaN. If you don't want to generate these,
use [`Fuzz.niceFloat`](#niceFloat).



## floatAtLeast

```elm
floatAtLeast : Basics.Float -> Fuzz.Fuzzer Basics.Float
```

 Fuzzer generating floats in range `n..Infinity`.

The positive part of the range will shrink nicely, the negative part will shrink uniformly.

The fuzzer will occasionally try the minimum, 0 (if in range) and Infinity.



## floatAtMost

```elm
floatAtMost : Basics.Float -> Fuzz.Fuzzer Basics.Float
```

 Fuzzer generating floats in range `-Infinity..n`.

The negative part of the range will shrink nicely, the positive part will shrink uniformly.

The fuzzer will occasionally try the maximum, 0 (if in range) and -Infinity.



## floatRange

```elm
floatRange : Basics.Float -> Basics.Float -> Fuzz.Fuzzer Basics.Float
```

 A fuzzer for float values within between a given minimum and maximum (inclusive).

Shrunken values will also be within the range.



## frequency

```elm
frequency : List.List ( Basics.Float, Fuzz.Fuzzer a ) -> Fuzz.Fuzzer a
```

 Create a new `Fuzzer` by providing a list of probabilistic weights to use
with other fuzzers.
For example, to create a `Fuzzer` that has a 1/4 chance of generating an int
between -1 and -100, and a 3/4 chance of generating one between 1 and 100,
you could do this:

    Fuzz.frequency
        [ ( 1, Fuzz.intRange -100 -1 )
        , ( 3, Fuzz.intRange 1 100 )
        ]

This fuzzer will simplify towards the fuzzers earlier in the list (each of which
will also apply its own way to simplify the values).

There are a few circumstances in which this function will return an invalid
fuzzer, which causes it to fail any test that uses it:

  - If you provide an empty list of frequencies
  - If any of the weights are less than 0
  - If the weights sum to 0

Be careful recursively using this fuzzer in its arguments. Often using
[`Fuzz.map`](#map) is a better way to do what you want. If you are fuzzing a
tree-like data structure, you should include a depth limit so to avoid infinite
recursion, like so:

    type Tree
        = Leaf
        | Branch Tree Tree

    tree : Int -> Fuzzer Tree
    tree i =
        if i <= 0 then
            Fuzz.constant Leaf

        else
            Fuzz.frequency
                [ ( 1, Fuzz.constant Leaf )
                , ( 2, Fuzz.map2 Branch (tree (i - 1)) (tree (i - 1)) )
                ]



## frequencyValues

```elm
frequencyValues : List.List ( Basics.Float, a ) -> Fuzz.Fuzzer a
```

 Create a `Fuzzer` by providing a list of probabilistic weights to use with
values.
For example, to create a `Fuzzer` that has a 1/4 chance of generating a string
"foo", and a 3/4 chance of generating a string "bar", you could do this:

    Fuzz.frequencyValues
        [ ( 1, "foo" )
        , ( 3, "bar" )
        ]

This fuzzer will simplify towards the values earlier in the list.

There are a few circumstances in which this function will return an invalid
fuzzer, which causes it to fail any test that uses it:

  - If you provide an empty list of frequencies
  - If any of the weights are less than 0
  - If the weights sum to 0



## fromGenerator

```elm
fromGenerator : Random.Generator a -> Fuzz.Fuzzer a
```

 (Avoid this function if you can! It is only provided as an escape hatch.)

Convert a Random.Generator into a Fuzzer.

Works internally by generating a random seed and running `Random.step`.

Note this will not shrink well (in fact it will shrink randomly, to smaller
_seeds_), as Generators are black boxes from the perspective of Fuzzers. If you
want meaningful shrinking, define fuzzers using the other functions in this
module!



## int

```elm
int : Fuzz.Fuzzer Basics.Int
```

 A fuzzer for int values. It will never produce `NaN`, `Infinity`, or
`-Infinity`.

This fuzzer will generate values in the range `Random.minInt .. Random.maxInt`.

  - Simplifies towards 0
  - Prefers positive values over negative ones
  - Prefers smaller values over larger ones



## intAtLeast

```elm
intAtLeast : Basics.Int -> Fuzz.Fuzzer Basics.Int
```

 A fuzzer that will generate values in range n..2^32-1.


## intAtMost

```elm
intAtMost : Basics.Int -> Fuzz.Fuzzer Basics.Int
```

 A fuzzer that will generate values in range -(2^32-1)..n.


## intRange

```elm
intRange : Basics.Int -> Basics.Int -> Fuzz.Fuzzer Basics.Int
```

 A fuzzer for int values between a given minimum and maximum value,
inclusive. Shrunk values will also be within the range.


## invalid

```elm
invalid : String.String -> Fuzz.Fuzzer a
```

 A fuzzer that is invalid for the provided reason. Any fuzzers built with it
are also invalid. Any tests using an invalid fuzzer fail.


## labelExamples

```elm
labelExamples : Basics.Int -> List.List ( String.String, a -> Basics.Bool ) -> Fuzz.Fuzzer a -> List.List ( List.List String.String, Maybe.Maybe a )
```

 Show examples of values satisfying given classification predicates (see
also [`Test.reportDistribution`](Test#reportDistribution) and
[`Test.expectDistribution`](Test#expectDistribution)).

Generates a given number of values and classifies them based on the predicates.

Uses the first argument as the seed as well as the count of examples to
generate.

This function will always return all the given "base" labels, even if no
examples of them could be found:

    Fuzz.labelExamples 100
        [ ( "Lower boundary (1)", \n -> n == 1 )
        , ( "Upper boundary (20)", \n -> n == 20 )
        , ( "In the middle (2..19)", \n -> n > 1 && n < 20 )
        , ( "Outside boundaries??", \n -> n < 1 || n > 20 )
        ]
        (Fuzz.intRange 1 20)

    -->
    [ ( [ "Lower boundary (1)" ], Just 1 )
    , ( [ "Upper boundary (20)" ], Just 20 )
    , ( [ "In the middle (2..19)" ], Just 5 )
    , ( [ "Outside boundaries??" ], Nothing )
    ]

In case of predicate overlap (eg. something is both green and big) this
function will also return all the found combinations:

    Fuzz.labelExamples 100
        [ ( "fizz", \n -> (n |> modBy 3) == 0 )
        , ( "buzz", \n -> (n |> modBy 5) == 0 )
        ]
        (Fuzz.intRange 1 20)

    -->
    [ ( [ "fizz" ], Just 3 )
    , ( [ "buzz" ], Just 10 )
    , ( [ "fizz, buzz" ], Just 15 )
    ]



## lazy

```elm
lazy : (() -> Fuzz.Fuzzer a) -> Fuzz.Fuzzer a
```

 A fuzzer that delays its execution. Handy for recursive types and preventing
infinite recursion.


## list

```elm
list : Fuzz.Fuzzer a -> Fuzz.Fuzzer (List.List a)
```

 Given a fuzzer of a type, create a fuzzer of a list of that type.
Generates random lists of varying length, up to 32 elements.


## listOfLength

```elm
listOfLength : Basics.Int -> Fuzz.Fuzzer a -> Fuzz.Fuzzer (List.List a)
```

 Given a fuzzer of a type, create a fuzzer of a list of that type.
Generates random lists of exactly the specified length.


## listOfLengthBetween

```elm
listOfLengthBetween : Basics.Int -> Basics.Int -> Fuzz.Fuzzer a -> Fuzz.Fuzzer (List.List a)
```

 Given a fuzzer of a type, create a fuzzer of a list of that type.
Generates random lists of length between the two given integers.


## map

```elm
map : (a -> b) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b
```

 Map a function over a fuzzer.


## map2

```elm
map2 : (a -> b -> c) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c
```

 Map over two fuzzers.


## map3

```elm
map3 : (a -> b -> c -> d) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c -> Fuzz.Fuzzer d
```

 Map over three fuzzers.


## map4

```elm
map4 : (a -> b -> c -> d -> e) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c -> Fuzz.Fuzzer d -> Fuzz.Fuzzer e
```

 Map over four fuzzers.


## map5

```elm
map5 : (a -> b -> c -> d -> e -> f) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c -> Fuzz.Fuzzer d -> Fuzz.Fuzzer e -> Fuzz.Fuzzer f
```

 Map over five fuzzers.


## map6

```elm
map6 : (a -> b -> c -> d -> e -> f -> g) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c -> Fuzz.Fuzzer d -> Fuzz.Fuzzer e -> Fuzz.Fuzzer f -> Fuzz.Fuzzer g
```

 Map over six fuzzers.


## map7

```elm
map7 : (a -> b -> c -> d -> e -> f -> g -> h) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c -> Fuzz.Fuzzer d -> Fuzz.Fuzzer e -> Fuzz.Fuzzer f -> Fuzz.Fuzzer g -> Fuzz.Fuzzer h
```

 Map over seven fuzzers.


## map8

```elm
map8 : (a -> b -> c -> d -> e -> f -> g -> h -> i) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c -> Fuzz.Fuzzer d -> Fuzz.Fuzzer e -> Fuzz.Fuzzer f -> Fuzz.Fuzzer g -> Fuzz.Fuzzer h -> Fuzz.Fuzzer i
```

 Map over eight fuzzers.


## maybe

```elm
maybe : Fuzz.Fuzzer a -> Fuzz.Fuzzer (Maybe.Maybe a)
```

 Given a fuzzer of a type, create a fuzzer of a maybe for that type.


## niceFloat

```elm
niceFloat : Fuzz.Fuzzer Basics.Float
```

 A fuzzer for float values.

Will prefer integer values, nice fractions and positive numbers over the rest.

Will never try infinities or NaN.



## oneOf

```elm
oneOf : List.List (Fuzz.Fuzzer a) -> Fuzz.Fuzzer a
```

 Choose one of the given fuzzers at random. Each fuzzer has an equal chance
of being chosen; to customize the probabilities, use [`Fuzz.frequency`](#frequency).

This fuzzer will simplify towards the fuzzers earlier in the list (each of which
will also apply its own way to simplify the values).

    Fuzz.oneOf
        [ Fuzz.intRange 0 3
        , Fuzz.intRange 7 9
        ]



## oneOfValues

```elm
oneOfValues : List.List a -> Fuzz.Fuzzer a
```

 Choose one of the given values at random. Each value has an equal chance
of being chosen; to customize the probabilities, use
[`Fuzz.frequencyValues`](#frequencyValues).

This fuzzer will simplify towards the values earlier in the list.

    Fuzz.oneOfValues
        [ 999
        , -42
        ]



## order

```elm
order : Fuzz.Fuzzer Basics.Order
```

 A fuzzer for order values.

Simplifies in order `LT < EQ < GT`.



## pair

```elm
pair : Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer ( a, b )
```

 Create a fuzzer of pairs from two fuzzers.


## percentage

```elm
percentage : Fuzz.Fuzzer Basics.Float
```

 A fuzzer for percentage values. Generates random floats between `0.0`
inclusive and `1.0` exclusive, in an uniform fashion.

Will occasionally try the boundaries.

Doesn't shrink to nice values like [`Fuzz.float`](#float) does; shrinks towards
zero.



## result

```elm
result : Fuzz.Fuzzer error -> Fuzz.Fuzzer value -> Fuzz.Fuzzer (Result.Result error value)
```

 Given fuzzers for an error type and a success type, create a fuzzer for
a result.


## sequence

```elm
sequence : List.List (Fuzz.Fuzzer a) -> Fuzz.Fuzzer (List.List a)
```

 Executes every fuzzer in the list and collects their values into the returned
list.

Rejections (eg. from [`Fuzz.filter`](#filter) or [`Fuzz.invalid`](#invalid))
bubble up instead of being discarded.



## shuffledList

```elm
shuffledList : List.List a -> Fuzz.Fuzzer (List.List a)
```

 A fuzzer that shuffles the given list.


## string

```elm
string : Fuzz.Fuzzer String.String
```

 Generates random unicode strings of up to 10 characters.


## stringOfLength

```elm
stringOfLength : Basics.Int -> Fuzz.Fuzzer String.String
```

 Generates random unicode strings of a given length.

Note that some unicode characters have `String.length` of 2. This fuzzer will
make sure the `String.length` of the returned string is equal to the wanted
length, even if it will mean there are less characters. If you instead want it
to give N characters even if their `String.length` will be above N, you can use

    Fuzz.listOfLength n Fuzz.char
        |> Fuzz.map String.fromList



## stringOfLengthBetween

```elm
stringOfLengthBetween : Basics.Int -> Basics.Int -> Fuzz.Fuzzer String.String
```

 Generates random unicode strings of length between the given limits.

Note that some unicode characters have `String.length` of 2. This fuzzer will
make sure the `String.length` of the returned string is equal to the wanted
length, even if it will mean there are less characters. If you instead want it
to give between MIN and MAX characters even if their `String.length` will be
above MAX, you can use

    Fuzz.listOfLengthBetween min max Fuzz.char
        |> Fuzz.map String.fromList



## traverse

```elm
traverse : (a -> Fuzz.Fuzzer b) -> List.List a -> Fuzz.Fuzzer (List.List b)
```

 Runs the Fuzzer-returning function on every item in the list, executes them=
and collects their values into the returned list.

Rejections (eg. from [`Fuzz.filter`](#filter) or [`Fuzz.invalid`](#invalid))
bubble up instead of being discarded.



## triple

```elm
triple : Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c -> Fuzz.Fuzzer ( a, b, c )
```

 Create a fuzzer of triples from three fuzzers.


## uniformInt

```elm
uniformInt : Basics.Int -> Fuzz.Fuzzer Basics.Int
```

 Draw an integer between 0 and n inclusive.

Will simplify towards 0, but draws uniformly over the whole range.

Max supported value is 2^32 - 1.



## unit

```elm
unit : Fuzz.Fuzzer ()
```

 A fuzzer for the unit value. Unit is a type with only one value, commonly
used as a placeholder.


## weightedBool

```elm
weightedBool : Basics.Float -> Fuzz.Fuzzer Basics.Bool
```

 A fuzzer for boolean values, generating True with the given probability
(0.0 = always False, 1.0 = always True).

Probabilities outside the `0..1` range will be clamped to `0..1`.

Simplifies towards False (if not prevented to do that by using probability >= 1).



# Test

 A module containing functions for creating and managing tests.

@docs Test, test


## Organizing Tests

@docs describe, concat, todo, skip, only


## Fuzz Testing

@docs fuzz, fuzz2, fuzz3, fuzzWith, FuzzOptions
@docs Distribution, noDistribution, reportDistribution, expectDistribution



## Distribution

```elm
type alias Distribution a =
    Test.Distribution.Internal.Distribution a
```

 With `Distribution` you can observe statistics about your fuzz test inputs and
assert that a given proportion of test cases belong to a given class.

  - `noDistribution` opts out of these checks.

  - `reportDistribution` will collect statistics and report them after the test
    runs (both when it passes and fails) and so is mostly useful as a temporary
    setting when creating your fuzzers and tests.

  - `expectDistribution` will collect statistics, but only report them (and fail
    the test) if the `ExpectedDistribution` is not met. Handy for checking your
    fuzzers are giving interesting and relevant inputs to your tests.

```elm
fuzzWith { runs = 10000, distribution = noDistribution }

fuzzWith
    { runs = 10000
    , distribution =
        reportDistribution
            [ ( "fizz", \n -> (n |> modBy 3) == 0 )
            , ( "buzz", \n -> (n |> modBy 5) == 0 )
            , ( "even", \n -> (n |> modBy 2) == 0 )
            , ( "odd", \n -> (n |> modBy 2) == 1 )
            ]
    }

fuzzWith
    { runs = 10000
    , distribution =
        expectDistribution
            [ ( Test.Distribution.atLeast 30, "fizz", \n -> (n |> modBy 3) == 0 )
            , ( Test.Distribution.atLeast 15, "buzz", \n -> (n |> modBy 5) == 0 )
            , ( Test.Distribution.moreThanZero, "fizz buzz", \n -> (n |> modBy 15) == 0 )
            , ( Test.Distribution.zero, "outside range", \n -> n < 1 || n > 20 )
            ]
    }
```

The `a` type variable in `Distribution a` is the same type as your fuzzed type.

For example, if you're fuzzing a String with `Fuzzer String` and want to see
distribution information for values produced by this fuzzer, you need to provide
`String -> Bool` functions to your `reportDistribution` or `expectDistribution` calls,
which will in turn produce a `Distribution String`.



## FuzzOptions

```elm
type alias FuzzOptions a =
    { runs : Basics.Int, distribution : Test.Distribution a }
```

 Options [`fuzzWith`](#fuzzWith) accepts.


### `runs`

The number of times to run each fuzz test. (Default is 100.)

    import Test exposing (fuzzWith)
    import Fuzz exposing (list, int)
    import Expect

    fuzzWith { runs = 350, distribution = noDistribution }
        (list int)
        "List.length should never be negative" <|
        -- This anonymous function will be run 350 times, each time with a
        -- randomly-generated fuzzList value. (It will always be a list of ints
        -- because of (list int) above.)
        \fuzzList ->
            fuzzList
                |> List.length
                |> Expect.atLeast 0


### `distribution`

A way to report/enforce a statistical distribution of your input values.
(Default is `noDistribution`.)

    import Test exposing (fuzzWith)
    import Test.Distribution
    import Fuzz exposing (list, int)
    import Expect

    fuzzWith
        { runs = 350
        , distribution =
            expectDistribution
                [ ( Test.Distribution.zero, "empty", \xs -> List.length xs == 0 )
                , ( Test.Distribution.atLeast 10, "3+ items", \xs -> List.length xs >= 3 )
                ]
        }
        (list int)
        "Sum > Average"
    <|
        \xs ->
            List.sum xs
                |> Expect.greaterThan (average xs)



## Test

```elm
type alias Test =
    Test.Internal.Test
```

 A test which has yet to be evaluated. When evaluated, it produces one
or more [`Expectation`](../Expect#Expectation)s.

See [`test`](#test) and [`fuzz`](#fuzz) for some ways to create a `Test`.



## concat

```elm
concat : List.List Test.Test -> Test.Test
```

 Run each of the given tests.

    concat [ testDecoder, testSorting ]



## describe

```elm
describe : String.String -> List.List Test.Test -> Test.Test
```

 Apply a description to a list of tests.

    import Test exposing (describe, test, fuzz)
    import Fuzz exposing (int)
    import Expect


    describe "List"
        [ describe "reverse"
            [ test "has no effect on an empty list" <|
                \_ ->
                    List.reverse []
                        |> Expect.equal []
            , fuzz int "has no effect on a one-item list" <|
                \num ->
                     List.reverse [ num ]
                        |> Expect.equal [ num ]
            ]
        ]

Passing an empty list will result in a failing test, because you either made a
mistake or are creating a placeholder.



## expectDistribution

```elm
expectDistribution : List.List ( Test.Distribution.ExpectedDistribution, String.String, a -> Basics.Bool ) -> Test.Distribution a
```

 Collects statistics and makes sure the expected distribution is met.

Fails the test and reports the distribution if the expected distribution is not met.

Uses a statistical test to make sure the distribution doesn't pass or fail the
distribution by accident (a flaky test). Will run more tests than specified with the
`runs` config option if needed.

This has the consequence of running more tests the closer your expected distribution
is to the true distribution. You can thus minimize and speed up this
"making sure" process by requesting slightly less % of your distribution than
needed.

Currently the statistical test is tuned to allow a false positive/negative in
1 in every 10^9 tests.



## fuzz

```elm
fuzz : Fuzz.Fuzzer a -> String.String -> (a -> Expect.Expectation) -> Test.Test
```

 Take a function that produces a test, and calls it several (usually 100) times, using a randomly-generated input
from a [`Fuzzer`](http://package.elm-lang.org/packages/elm-explorations/test/latest/Fuzz) each time. This allows you to
test that a property that should always be true is indeed true under a wide variety of conditions. The function also
takes a string describing the test.

These are called "[fuzz tests](https://en.wikipedia.org/wiki/Fuzz_testing)" because of the randomness.
You may find them elsewhere called [property-based tests](http://blog.jessitron.com/2013/04/property-based-testing-what-is-it.html),
[generative tests](http://www.pivotaltracker.com/community/tracker-blog/generative-testing), or
[QuickCheck-style tests](https://en.wikipedia.org/wiki/QuickCheck).

    import Test exposing (fuzz)
    import Fuzz exposing (list, int)
    import Expect


    fuzz (list int) "List.length should never be negative" <|
        -- This anonymous function will be run 100 times, each time with a
        -- randomly-generated fuzzList value.
        \fuzzList ->
            fuzzList
                |> List.length
                |> Expect.atLeast 0



## fuzz2

```elm
fuzz2 : Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> String.String -> (a -> b -> Expect.Expectation) -> Test.Test
```

 Run a [fuzz test](#fuzz) using two random inputs.

This is a convenience function that lets you skip calling [`Fuzz.pair`](Fuzz#pair).

See [`fuzzWith`](#fuzzWith) for an example of writing this using tuples.

    import Test exposing (fuzz2)
    import Fuzz exposing (list, int)


    fuzz2 (list int) int "List.reverse never influences List.member" <|
        \nums target ->
            List.member target (List.reverse nums)
                |> Expect.equal (List.member target nums)



## fuzz3

```elm
fuzz3 : Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c -> String.String -> (a -> b -> c -> Expect.Expectation) -> Test.Test
```

 Run a [fuzz test](#fuzz) using three random inputs.

This is a convenience function that lets you skip calling [`Fuzz.triple`](Fuzz#triple).



## fuzzWith

```elm
fuzzWith : Test.FuzzOptions a -> Fuzz.Fuzzer a -> String.String -> (a -> Expect.Expectation) -> Test.Test
```

 Run a [`fuzz`](#fuzz) test with the given [`FuzzOptions`](#FuzzOptions).

Note that there is no `fuzzWith2`, but you can always pass more fuzz values in
using [`Fuzz.pair`](Fuzz#pair), [`Fuzz.triple`](Fuzz#triple),
for example like this:

    import Test exposing (fuzzWith)
    import Fuzz exposing (pair, list, int)
    import Expect


    fuzzWith { runs = 4200, distribution = noDistribution }
        (pair (list int) int)
        "List.reverse never influences List.member" <|
            \(nums, target) ->
                List.member target (List.reverse nums)
                    |> Expect.equal (List.member target nums)



## noDistribution

```elm
noDistribution : Test.Distribution a
```

 Opts out of the test input distribution checking.


## only

```elm
only : Test.Test -> Test.Test
```

 Returns a [`Test`](#Test) that causes other tests to be skipped, and
only runs the given one.

Calls to `only` aren't meant to be committed to version control. Instead, use
them when you want to focus on getting a particular subset of your tests to pass.
If you use `only`, your entire test suite will fail, even if
each of the individual tests pass. This is to help avoid accidentally
committing a `only` to version control.

If you you use `only` on multiple tests, only those tests will run. If you
put a `only` inside another `only`, only the outermost `only`
will affect which tests gets run.

See also [`skip`](#skip). Note that `skip` takes precedence over `only`;
if you use a `skip` inside an `only`, it will still get skipped, and if you use
an `only` inside a `skip`, it will also get skipped.

    describe "List"
        [ only <|
            describe "reverse"
                [ test "has no effect on an empty list" <|
                    \_ ->
                        List.reverse []
                            |> Expect.equal []
                , fuzz int "has no effect on a one-item list" <|
                    \num ->
                        List.reverse [ num ]
                            |> Expect.equal [ num ]
                ]
        , test "This will not get run, because of the `only` above!" <|
            \_ ->
                List.length []
                    |> Expect.equal 0
        ]



## reportDistribution

```elm
reportDistribution : List.List ( String.String, a -> Basics.Bool ) -> Test.Distribution a
```

 Collects statistics and reports them after the test runs (both when it passes
and fails).


## skip

```elm
skip : Test.Test -> Test.Test
```

 Returns a [`Test`](#Test) that gets skipped.

Calls to `skip` aren't meant to be committed to version control. Instead, use
it when you want to focus on getting a particular subset of your tests to
pass. If you use `skip`, your entire test suite will fail, even if
each of the individual tests pass. This is to help avoid accidentally
committing a `skip` to version control.

See also [`only`](#only). Note that `skip` takes precedence over `only`;
if you use a `skip` inside an `only`, it will still get skipped, and if you use
an `only` inside a `skip`, it will also get skipped.

    describe "List"
        [ skip <|
            describe "reverse"
                [ test "has no effect on an empty list" <|
                    \_ ->
                        List.reverse []
                            |> Expect.equal []
                , fuzz int "has no effect on a one-item list" <|
                    \num ->
                        List.reverse [ num ]
                            |> Expect.equal [ num ]
                ]
        , test "This is the only test that will get run; the other was skipped!" <|
            \_ ->
                List.length []
                    |> Expect.equal 0
        ]



## test

```elm
test : String.String -> (() -> Expect.Expectation) -> Test.Test
```

 Return a [`Test`](#Test) that evaluates a single
[`Expectation`](../Expect#Expectation).

    import Test exposing (fuzz)
    import Expect


    test "the empty list has 0 length" <|
        \_ ->
            List.length []
                |> Expect.equal 0



## todo

```elm
todo : String.String -> Test.Test
```

 Returns a [`Test`](#Test) that is "TODO" (not yet implemented). These tests
always fail, but test runners will only include them in their output if there
are no other failures.

These tests aren't meant to be committed to version control. Instead, use them
when you're brainstorming lots of tests you'd like to write, but you can't
implement them all at once. When you replace `todo` with a real test, you'll be
able to see if it fails without clutter from tests still not implemented. But,
unlike leaving yourself comments, you'll be prompted to implement these tests
because your suite will fail.

    describe "a new thing"
        [ todo "does what is expected in the common case"
        , todo "correctly handles an edge case I just thought of"
        ]

This functionality is similar to "pending" tests in other frameworks, except
that a TODO test is considered failing but a pending test often is not.



# Test.Distribution




## Distribution

@docs ExpectedDistribution, atLeast, zero, moreThanZero
@docs DistributionReport, distributionReportTable



## ExpectedDistribution

```elm
type alias ExpectedDistribution =
    Test.Distribution.Internal.ExpectedDistribution
```

 Your input distribution requirement for the fuzzer used in a test.

For example, "this test shouldn't ever receive strings of length < 3 as an input"
or "at least 30% of the test input trees should be balanced".



## DistributionReport

```elm
type DistributionReport
    = NoDistribution
    | DistributionToReport ({ distributionCount : Dict.Dict (List.List String.String) Basics.Int, runsElapsed : Basics.Int })
    | DistributionCheckSucceeded ({ distributionCount : Dict.Dict (List.List String.String) Basics.Int, runsElapsed : Basics.Int })
    | DistributionCheckFailed ({ distributionCount : Dict.Dict (List.List String.String) Basics.Int, runsElapsed : Basics.Int, badLabel : String.String, badLabelPercentage : Basics.Float, expectedDistribution : String.String })
```

 A result of a distribution check.

Get it from your `Expectation` with `Test.Runner.getDistributionReport`.



## atLeast

```elm
atLeast : Basics.Float -> Test.Distribution.ExpectedDistribution
```

 A requirement that a given value class should happen at least N% of the time
in a given test.

The example below says that at least 30% of the fuzz test inputs should be
multiples of 3.

    fuzzWith
        { runs = 10000
        , distribution =
            expectDistribution
                [ ( atLeast 30, "multiple of 3", \n -> (n |> modBy 3) == 0 )
                ]
        }



## distributionReportTable

```elm
distributionReportTable : { a | runsElapsed : Basics.Int, distributionCount : Dict.Dict (List.List String.String) Basics.Int } -> String.String
```

 Prettyprints the record inside `DistributionReport` into a table with histograms.


## moreThanZero

```elm
moreThanZero : Test.Distribution.ExpectedDistribution
```

 A requirement that a given value class should happen at least once in a given
test.


## zero

```elm
zero : Test.Distribution.ExpectedDistribution
```

 A requirement that a given value class should never happen in a given test.


# Test.Html.Event

 This module lets you simulate events on `Html` values and expect that
they result in certain `Msg` values being sent to `update`.


## Simulating Events

@docs Event, simulate, expect, toResult


## Testing Event Effects

These functions allow you to test that your event handlers are (or are not) calling
[`stopPropagation()`](https://developer.mozilla.org/en-US/docs/Web/API/Event/stopPropagation)
and
[`preventDefault()`](https://developer.mozilla.org/en-US/docs/Web/API/Event/preventDefault).
In Elm, you do this by calling
[special functions](https://package.elm-lang.org/packages/elm/html/latest/Html-Events#stopPropagationOn)
in `Html.Events`.

@docs expectStopPropagation, expectNotStopPropagation, expectPreventDefault, expectNotPreventDefault


## Event Builders

@docs custom, click, doubleClick, mouseDown, mouseUp, mouseEnter, mouseLeave, mouseOver, mouseOut, input, check, submit, blur, focus



## Event

```elm
-- Opaque type: Event msg (constructors not exposed)
```

 A simulated event.

See [`simulate`](#simulate).



## blur

```elm
blur : ( String.String, Json.Encode.Value )
```

 A [`blur`](https://developer.mozilla.org/en-US/docs/Web/Events/blur) event.


## check

```elm
check : Basics.Bool -> ( String.String, Json.Encode.Value )
```

 A [`change`](https://developer.mozilla.org/en-US/docs/Web/Events/change) event
where `event.target.checked` is set to the given `Bool` value.


## click

```elm
click : ( String.String, Json.Encode.Value )
```

 A [`click`](https://developer.mozilla.org/en-US/docs/Web/Events/click) event.


## custom

```elm
custom : String.String -> Json.Encode.Value -> ( String.String, Json.Encode.Value )
```

 Simulate a custom event. The `String` is the event name, and the `Value` is the event object
the browser would send to the event listener callback.

    import Test.Html.Event as Event
    import Json.Encode as Encode exposing (Value)


    type Msg
        = Change String


    test "Input produces expected Msg" <|
        \() ->
            let
                simulatedEventObject : Value
                simulatedEventObject =
                    Encode.object
                        [ ( "target"
                          , Encode.object [ ( "value", Encode.string "cats" ) ]
                          )
                        ]
            in
                Html.input [ onInput Change ] [ ]
                    |> Query.fromHtml
                    |> Event.simulate (Event.custom "input" simulatedEventObject)
                    |> Event.expect (Change "cats")



## doubleClick

```elm
doubleClick : ( String.String, Json.Encode.Value )
```

 A [`dblclick`](https://developer.mozilla.org/en-US/docs/Web/Events/dblclick) event.


## expect

```elm
expect : msg -> Test.Html.Event.Event msg -> Expect.Expectation
```

 Passes if the given message is triggered by the simulated event.

    import Test.Html.Event as Event

    type Msg
        = Change String


    test "Input produces expected Msg" <|
        \() ->
            Html.input [ onInput Change ] [ ]
                |> Query.fromHtml
                |> Event.simulate (Event.input "cats")
                |> Event.expect (Change "cats")



## expectNotPreventDefault

```elm
expectNotPreventDefault : Test.Html.Event.Event msg -> Expect.Expectation
```

 Passes if the event handler doesn't prevent default action of the event.


## expectNotStopPropagation

```elm
expectNotStopPropagation : Test.Html.Event.Event msg -> Expect.Expectation
```

 Passes if the event handler doesn't stop propagation of the event.


## expectPreventDefault

```elm
expectPreventDefault : Test.Html.Event.Event msg -> Expect.Expectation
```

 Passes if the event handler prevents default action of the event.


## expectStopPropagation

```elm
expectStopPropagation : Test.Html.Event.Event msg -> Expect.Expectation
```

 Passes if the event handler stops propagation of the event.


## focus

```elm
focus : ( String.String, Json.Encode.Value )
```

 A [`focus`](https://developer.mozilla.org/en-US/docs/Web/Events/focus) event.


## input

```elm
input : String.String -> ( String.String, Json.Encode.Value )
```

 An [`input`](https://developer.mozilla.org/en-US/docs/Web/Events/input) event.


## mouseDown

```elm
mouseDown : ( String.String, Json.Encode.Value )
```

 A [`mousedown`](https://developer.mozilla.org/en-US/docs/Web/Events/mousedown) event.


## mouseEnter

```elm
mouseEnter : ( String.String, Json.Encode.Value )
```

 A [`mouseenter`](https://developer.mozilla.org/en-US/docs/Web/Events/mouseenter) event.


## mouseLeave

```elm
mouseLeave : ( String.String, Json.Encode.Value )
```

 A [`mouseleave`](https://developer.mozilla.org/en-US/docs/Web/Events/mouseleave) event.


## mouseOut

```elm
mouseOut : ( String.String, Json.Encode.Value )
```

 A [`mouseout`](https://developer.mozilla.org/en-US/docs/Web/Events/mouseout) event.


## mouseOver

```elm
mouseOver : ( String.String, Json.Encode.Value )
```

 A [`mouseover`](https://developer.mozilla.org/en-US/docs/Web/Events/mouseover) event.


## mouseUp

```elm
mouseUp : ( String.String, Json.Encode.Value )
```

 A [`mouseup`](https://developer.mozilla.org/en-US/docs/Web/Events/mouseup) event.


## simulate

```elm
simulate : ( String.String, Json.Encode.Value ) -> Test.Html.Query.Single msg -> Test.Html.Event.Event msg
```

 Simulate an event on a node.

    import Test.Html.Event as Event

    type Msg
        = Change String


    test "Input produces expected Msg" <|
        \() ->
            Html.input [ onInput Change ] [ ]
                |> Query.fromHtml
                |> Event.simulate (Event.input "cats")
                |> Event.expect (Change "cats")



## submit

```elm
submit : ( String.String, Json.Encode.Value )
```

 A [`submit`](https://developer.mozilla.org/en-US/docs/Web/Events/submit) event.


## toResult

```elm
toResult : Test.Html.Event.Event msg -> Result.Result String.String msg
```

 Returns a Result with the Msg produced by the event simulated on a node.
Note that Event.expect gives nicer messages; this is generally more useful
when testing that an event handler is _not_ present.

    import Test.Html.Event as Event


    test "Input produces expected Msg" <|
        \() ->
            Html.input [ onInput Change ] [ ]
                |> Query.fromHtml
                |> Event.simulate (Event.input "cats")
                |> Event.toResult
                |> Expect.equal (Ok (Change "cats"))



# Test.Html.Query

 Querying HTML structure.

@docs Single, Multiple, fromHtml


## Querying

@docs find, findAll, children, first, index, keep


## Expecting

@docs count, contains, has, hasNot, each



## Multiple

```elm
type alias Multiple msg =
    Test.Html.Query.Internal.Multiple msg
```

 A query that may find any number of elements, including zero.

Contrast with [`Single`](#Single).



## Single

```elm
type alias Single msg =
    Test.Html.Query.Internal.Single msg
```

 A query that expects to find exactly one element.

Contrast with [`Multiple`](#Multiple).



## children

```elm
children : List.List Test.Html.Selector.Selector -> Test.Html.Query.Single msg -> Test.Html.Query.Multiple msg
```

 Return the matched element's immediate child elements.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The <ul> only has <li> children" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [ class "item"] [ text "first item" ]
                    , li [ class "item selected"] [ text "second item" ]
                    , li [ class "item"] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.find [ class "items" ]
                |> Query.children [ class "selected" ]
                |> Query.count (Expect.equal 1)



## contains

```elm
contains : List.List (Html.Html msg) -> Test.Html.Query.Single msg -> Expect.Expectation
```

 Expect the element to have at least one descendant matching each node in the list.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The list has two li: one with the text \"third item\" and \
        another one with \"first item\"" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.contains
                    [ li [] [ text "third item" ]
                    , li [] [ text "first item" ]
                    ]



## count

```elm
count : (Basics.Int -> Expect.Expectation) -> Test.Html.Query.Multiple msg -> Expect.Expectation
```

 Expect the number of elements matching the query fits the given expectation.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag)
    import Expect


    test "The list has three items" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.findAll [ tag "li" ]
                |> Query.count (Expect.equal 3)



## each

```elm
each : (Test.Html.Query.Single msg -> Expect.Expectation) -> Test.Html.Query.Multiple msg -> Expect.Expectation
```

 Expect that a [`Single`](#Single) expectation will hold true for each of the
[`Multiple`](#Multiple) matched elements.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The list has both the classes 'items' and 'active'" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.findAll [ tag "ul" ]
                |> Query.each
                    (Expect.all
                        [ Query.has [ tag "ul" ]
                        , Query.has [ classes [ "items", "active" ] ]
                        ]
                    )



## find

```elm
find : List.List Test.Html.Selector.Selector -> Test.Html.Query.Single msg -> Test.Html.Query.Single msg
```

 Find exactly one descendant element which matches all the given selectors.
If no descendants match, or if more than one matches, the test will fail.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The list has both the classes 'items' and 'active'" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.find [ tag "ul" ]
                |> Query.has [ classes [ "items", "active" ] ]



## findAll

```elm
findAll : List.List Test.Html.Selector.Selector -> Test.Html.Query.Single msg -> Test.Html.Query.Multiple msg
```

 Find the descendant elements which match all the given selectors.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag)
    import Expect


    test "The list has three items" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.findAll [ tag "li" ]
                |> Query.count (Expect.equal 3)



## first

```elm
first : Test.Html.Query.Multiple msg -> Test.Html.Query.Single msg
```

 Return the first element in a match. If there were no matches, the test
will fail.

`Query.first` is a shorthand for `Query.index 0` - they do the same thing.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The first <li> is called 'first item'" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.findAll [ tag "li" ]
                |> Query.first
                |> Query.has [ text "first item" ]



## fromHtml

```elm
fromHtml : Html.Html msg -> Test.Html.Query.Single msg
```

 Translate a `Html` value into a `Single` query. This is how queries
typically begin.

    import Html
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (text)


    test "Button has the expected text" <|
        \() ->
            Html.button [] [ Html.text "I'm a button!" ]
                |> Query.fromHtml
                |> Query.has [ text "I'm a button!" ]



## has

```elm
has : List.List Test.Html.Selector.Selector -> Test.Html.Query.Single msg -> Expect.Expectation
```

 Expect the element to match all of the given selectors.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The list has both the classes 'items' and 'active'" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.find [ tag "ul" ]
                |> Query.has [ tag "ul", classes [ "items", "active" ] ]



## hasNot

```elm
hasNot : List.List Test.Html.Selector.Selector -> Test.Html.Query.Single msg -> Expect.Expectation
```

 Expect the element to **not** match all of the given selectors.

    import Html exposing (div)
    import Html.Attributes as Attributes
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, class)


    test "The div element has no progress-bar class" <|
        \() ->
            div [ Attributes.class "button" ] []
                |> Query.fromHtml
                |> Query.find [ tag "div" ]
                |> Query.hasNot [ tag "div", class "progress-bar" ]



## index

```elm
index : Basics.Int -> Test.Html.Query.Multiple msg -> Test.Html.Query.Single msg
```

 Return the element in a match at the given index. For example,
`Query.index 0` would match the first element, and `Query.index 1` would match
the second element.

You can pass negative numbers to get elements from the end - for example, `Query.index -1`
will match the last element, and `Query.index -2` will match the second-to-last.

If the index falls outside the bounds of the match, the test will fail.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The second <li> is called 'second item'" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.findAll [ tag "li" ]
                |> Query.index 1
                |> Query.has [ text "second item" ]



## keep

```elm
keep : Test.Html.Selector.Selector -> Test.Html.Query.Multiple msg -> Test.Html.Query.Multiple msg
```

 Find the descendant elements of the result of `findAll` which match all the given selectors.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag)
    import Expect


    test "The list has three items" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ a [] [ text "first item" ]]
                    , li [] [ a [] [ text "second item" ]]
                    , li [] [ a [] [ text "third item" ]]
                    , li [] [ button [] [ text "button" ]]
                    ]
                ]
                |> Query.fromHtml
                |> Query.findAll [ tag "li" ]
                |> Query.keep ( tag "a" )
                |> Expect.all
                    [ Query.each (Query.has [ tag "a" ])
                    , Query.first >> Query.has [ text "first item" ]
                    ]



# Test.Html.Selector

 Selecting HTML elements.

@docs Selector


## General Selectors

@docs tag, text, exactText, containing, attribute, all


## Attributes

@docs id, class, classes, exactClassName, style, checked, selected, disabled



## Selector

```elm
type alias Selector =
    Test.Html.Selector.Internal.Selector
```

 A selector used to filter sets of elements.


## all

```elm
all : List.List Test.Html.Selector.Selector -> Test.Html.Selector.Selector
```

 Combine the given selectors into one which requires all of them to match.

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (class, text, all, Selector)


    replyBtnSelector : Selector
    replyBtnSelector =
        all [ class "btn", text "Reply" ]


    test "Button has the class 'btn' and the text 'Reply'" <|
        \() ->
            Html.button [ Attr.class "btn btn-large" ] [ Html.text "Reply" ]
                |> Query.fromHtml
                |> Query.has [ replyBtnSelector ]



## attribute

```elm
attribute : Html.Attribute Basics.Never -> Test.Html.Selector.Selector
```

 Matches elements that have the given attribute in a way that makes sense
given their semantics in `Html`.


## checked

```elm
checked : Basics.Bool -> Test.Html.Selector.Selector
```

 Matches elements that have a
[`checked`](http://package.elm-lang.org/packages/elm-lang/html/latest/Html-Attributes#checked)
attribute with the given value.


## class

```elm
class : String.String -> Test.Html.Selector.Selector
```

 Matches elements that have the given class (and possibly others as well).

To match multiple classes at once, use [`classes`](#classes) instead.

To match the element's exact class attribute string, use [`exactClassName`](#exactClassName).

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (class)


    test "Button has the class btn-large" <|
        \() ->
            Html.button [ Attr.class "btn btn-large" ] [ Html.text "Reply" ]
                |> Query.fromHtml
                |> Query.has [ class "btn-large" ]



## classes

```elm
classes : List.List String.String -> Test.Html.Selector.Selector
```

 Matches elements that have all the given classes (and possibly others as well).

When you only care about one class instead of several, you can use
[`class`](#class) instead of passing this function a list with one value in it.

To match the element's exact class attribute string, use [`exactClassName`](#exactClassName).

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (classes)


    test "Button has the classes btn and btn-large" <|
        \() ->
            Html.button [ Attr.class "btn btn-large" ] [ Html.text "Reply" ]
                |> Query.fromHtml
                |> Query.has [ classes [ "btn", "btn-large" ] ]



## containing

```elm
containing : List.List Test.Html.Selector.Selector -> Test.Html.Selector.Selector
```

 Matches elements whose descendants match the given selectors.

(You will get the element and **not** the descendant.)

This is especially useful to find elements which contain specific
text somewhere in their descendants.

    import Html
    import Html.Events exposing (onClick)
    import Test exposing (test)
    import Test.Html.Event as Event
    import Test.Html.Query as Query
    import Test.Html.Selector exposing (containing, tag)

    test : Test
    test =
        test "..." <|
            Html.div []
                [ Html.button [ onClick NopeMsg ] [ Html.text "not me" ]
                , Html.button [ onClick ClickedMsg ] [ Html.text "click me" ]
                ]
                |> Query.fromHtml
                |> Query.find
                    [ tag "button"
                    , containing [ text "click me" ]
                    ]
                |> Event.simulate Event.click
                |> Event.expect ClickedMsg



## disabled

```elm
disabled : Basics.Bool -> Test.Html.Selector.Selector
```

 Matches elements that have a
[`disabled`](http://package.elm-lang.org/packages/elm-lang/html/latest/Html-Attributes#disabled)
attribute with the given value.


## exactClassName

```elm
exactClassName : String.String -> Test.Html.Selector.Selector
```

 Matches the element's exact class attribute string.

This is used less often than [`class`](#class), [`classes`](#classes) or
[`attribute`](#attribute), which check for the _presence_ of a class as opposed
to matching the entire class attribute exactly.

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (exactClassName)


    test "Button has the exact class 'btn btn-large'" <|
        \() ->
            Html.button [ Attr.class "btn btn-large" ] [ Html.text "Reply" ]
                |> Query.fromHtml
                |> Query.has [ exactClassName "btn btn-large" ]



## exactText

```elm
exactText : String.String -> Test.Html.Selector.Selector
```

 Matches elements that have a
[`text`](http://package.elm-lang.org/packages/elm-lang/html/latest/Html-Attributes#text)
attribute with _exactly_ the given value (sans leading/trailing whitespace).

`Selector.exactText "11,22"` will _not_ match `Html.text "11,222"`.

Note this selector is whitespace sensitive (it _doesn't_ trim strings prior to
checking them):

`Selector.exactText "11,22"` will _not_ match `Html.text "\n    11,22   \n"`.

If you need a partial match, take a look at [`text`](#text).



## id

```elm
id : String.String -> Test.Html.Selector.Selector
```

 Matches elements that have the given `id` attribute.

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (id, text)


    test "the welcome <h1> says hello!" <|
        \() ->
            Html.div []
                [ Html.h1 [ Attr.id "welcome" ] [ Html.text "Hello!" ] ]
                |> Query.fromHtml
                |> Query.find [ id "welcome" ]
                |> Query.has [ text "Hello!" ]



## selected

```elm
selected : Basics.Bool -> Test.Html.Selector.Selector
```

 Matches elements that have a
[`selected`](http://package.elm-lang.org/packages/elm-lang/html/latest/Html-Attributes#selected)
attribute with the given value.


## style

```elm
style : String.String -> String.String -> Test.Html.Selector.Selector
```

 Matches elements that have the given style properties (and possibly others as well).

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (classes)


    test "the Reply button has red text" <|
        \() ->
            Html.div []
                [ Html.button
                    [ Attr.style "color" "red" ]
                    [ Html.text "Reply" ]
                ]
                |> Query.has [ style "color" "red" ]



## tag

```elm
tag : String.String -> Test.Html.Selector.Selector
```

 Matches elements that have the given tag.

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, text)


    test "the welcome <h1> says hello!" <|
        \() ->
            Html.div []
                [ Html.h1 [ Attr.id "welcome" ] [ Html.text "Hello!" ] ]
                |> Query.fromHtml
                |> Query.find [ tag "h1" ]
                |> Query.has [ text "Hello!" ]



## text

```elm
text : String.String -> Test.Html.Selector.Selector
```

 Matches elements that have a
[`text`](http://package.elm-lang.org/packages/elm-lang/html/latest/Html-Attributes#text)
attribute _containing_ the given value.

`Selector.text "11,22"` will match `Html.text "11,222"`.

If you need an exact match, take a look at [`exactText`](#exactText).



# Test.Runner

 This is an "experts only" module that exposes functions needed to run and
display tests. A typical user will use an existing runner library for Node or
the browser, which is implemented using this interface. A list of these runners
can be found in the `README`.


## Runner

@docs Runner, SeededRunners, fromTest


## Expectations

@docs getFailureReason, isTodo


## Distribution

@docs getDistributionReport


## Formatting

@docs formatLabels


## Fuzzers

These functions give you the ability to run fuzzers separate of running fuzz tests.

@docs Simplifiable, fuzz, simplify



## Runner

```elm
type alias Runner =
    { run : () -> List.List Expect.Expectation, labels : List.List String.String }
```

 A function which, when evaluated, produces a list of expectations. Also a
list of labels which apply to this outcome.


## SeededRunners

```elm
type SeededRunners
    = Plain (List.List Test.Runner.Runner)
    | Only (List.List Test.Runner.Runner)
    | Skipping (List.List Test.Runner.Runner)
    | Invalid (String.String)
```

 Test Runners which have had seeds distributed to them, and which are now
either invalid or are ready to run. Seeded runners include some metadata:

  - `Invalid` runners had a problem (e.g. two sibling tests had the same description) making them un-runnable.
  - `Only` runners can be run, but `Test.only` was used somewhere, so ultimately they will lead to a failed test run even if each test that gets run passes.
  - `Skipping` runners can be run, but `Test.skip` was used somewhere, so ultimately they will lead to a failed test run even if each test that gets run passes.
  - `Plain` runners are ready to run, and have none of these issues.



## Simplifiable

```elm
-- Opaque type: Simplifiable a (constructors not exposed)
```

 A `Simplifiable a` is an opaque type that allows you to obtain a value of type
`a` that is simpler than the one you've previously obtained.


## formatLabels

```elm
formatLabels : (String.String -> format) -> (String.String -> format) -> List.List String.String -> List.List format
```

 A standard way to format descriptions and test labels, to keep things
consistent across test runner implementations.

The HTML, Node, String, and Log runners all use this.

What it does:

  - drop any labels that are empty strings
  - format the first label differently from the others
  - reverse the resulting list

Example:

    [ "the actual test that failed"
    , "nested description failure"
    , "top-level description failure"
    ]
    |> formatLabels ((++) "↓ ") ((++) "✗ ")

    {-
    [ "↓ top-level description failure"
    , "↓ nested description failure"
    , "✗ the actual test that failed"
    ]
    -}



## fromTest

```elm
fromTest : Basics.Int -> Random.Seed -> Test.Test -> Test.Runner.SeededRunners
```

 Convert a `Test` into `SeededRunners`.

In order to run any fuzz tests that the `Test` may have, it requires a default run count as well
as an initial `Random.Seed`. `100` is a good run count. To obtain a good random seed, pass a
random 32-bit integer to `Random.initialSeed`. You can obtain such an integer by running
`Math.floor(Math.random()*0xFFFFFFFF)` in Node. It's typically fine to hard-code this value into
your Elm code; it's easy and makes your tests reproducible.



## fuzz

```elm
fuzz : Fuzz.Fuzzer a -> Random.Generator (Result.Result String.String ( a, Test.Runner.Simplifiable a ))
```

 Given a fuzzer, return a random generator to produce a value and a
Simplifiable. The value is what a fuzz test would have received as input.

Note that fuzzers aren't generated to succeed, which is why this function returns
a Result. The String inside the Err case will contain a failure reason.



## getDistributionReport

```elm
getDistributionReport : Expect.Expectation -> Test.Distribution.DistributionReport
```

 Returns a `DistributionReport` computed for a given test.


## getFailureReason

```elm
getFailureReason : Expect.Expectation -> Maybe.Maybe { given : Maybe.Maybe String.String, description : String.String, reason : Test.Runner.Failure.Reason }
```

 Return `Nothing` if the given [`Expectation`](Expect#Expectation) is a [`pass`](Expect#pass).

If it is a [`fail`](Expect#fail), return a record containing the expectation
description, the [`Reason`](Test-Runner-Failure#Reason) the test failed, and the given inputs if
it was a fuzz test. (If it was not a fuzz test, the record's `given` field
will be `Nothing`).

For example:

    getFailureReason (Expect.equal 1 2)
    -- Just { reason = Equal 1 2, description = "Expect.equal", given = Nothing }

    getFailureReason (Expect.equal 1 1)
    -- Nothing



## isTodo

```elm
isTodo : Expect.Expectation -> Basics.Bool
```

 Determine if an expectation was created by a call to `Test.todo`. Runners
may treat these tests differently in their output.


## simplify

```elm
simplify : (a -> Expect.Expectation) -> ( a, Test.Runner.Simplifiable a ) -> Maybe.Maybe ( a, Test.Runner.Simplifiable a )
```

 Given a Simplifiable, simplify the value further. Pass your test function to
drive the simplification process: if a simplified value passes the test, it will
be discarded. In this sense, you will get the simplest value that still fails
your test.


# Test.Runner.Failure

 The reason a test failed.

@docs Reason, InvalidReason



## InvalidReason

```elm
type InvalidReason
    = EmptyList
    | NonpositiveFuzzCount
    | InvalidFuzzer
    | BadDescription
    | DuplicatedName
    | DistributionInsufficient
    | DistributionBug
```

 The reason a test run was invalid.

Test runners should report these to the user in whatever format is appropriate.



## Reason

```elm
type Reason
    = Custom
    | Equality (String.String) (String.String)
    | Comparison (String.String) (String.String)
    | ListDiff (List.List String.String) (List.List String.String)
    | CollectionDiff ({ expected : String.String, actual : String.String, extra : List.List String.String, missing : List.List String.String })
    | TODO
    | Invalid (Test.Runner.Failure.InvalidReason)
```

 The reason a test failed.

Test runners can use this to provide nice output, e.g. by doing diffs on the
two parts of an `Expect.equal` failure.


