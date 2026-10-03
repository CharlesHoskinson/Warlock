# official/packages/elm-explorations/test/1.0.0/docs.json
Source: https://package.elm-lang.org/packages/elm-explorations/test/1.0.0/docs.json

# Expect

 A library to create `Expectation`s, which describe a claim to be tested.


## Quick Reference

  - [`equal`](#equal) `(arg2 == arg1)`
  - [`notEqual`](#notEqual) `(arg2 /= arg1)`
  - [`lessThan`](#lessThan) `(arg2 < arg1)`
  - [`atMost`](#atMost) `(arg2 <= arg1)`
  - [`greaterThan`](#greaterThan) `(arg2 > arg1)`
  - [`atLeast`](#atLeast) `(arg2 >= arg1)`
  - [`true`](#true) `(arg == True)`
  - [`false`](#false) `(arg == False)`
  - [Floating Point Comparisons](#floating-point-comparisons)


## Basic Expectations

@docs Expectation, equal, notEqual, all


## Numeric Comparisons

@docs lessThan, atMost, greaterThan, atLeast


## Floating Point Comparisons

These functions allow you to compare `Float` values up to a specified rounding error, which may be relative, absolute,
or both. For an in-depth look, see our [Guide to Floating Point Comparison](#guide-to-floating-point-comparison).

@docs FloatingPointTolerance, within, notWithin


## Booleans

@docs true, false


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

    test "3.14 approximates pi with absolute precision" <| \_ ->
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
    (Dict.fromList [ ( 1, "one" ), ( 2, "two" ) ])
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
    [1, 2, 3]
        |> Expect.equalLists [1, 2, 3]

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
    (Set.fromList [1, 2])
        |> Expect.equalSets (Set.fromList [1, 2])

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
        |> Expect.err

Test failures will be printed with the unexpected `Ok` value contrasting with
any `Err`.

    -- Fails
    String.toInt "20"
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



## false

```elm
false : String.String -> Basics.Bool -> Expect.Expectation
```

 Passes if the argument is 'False', and otherwise fails with the given message.

    Expect.false "Expected the list not to be empty." (List.isEmpty [ 42 ])

    -- Passes because (List.isEmpty [ 42 ]) is False

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because (List.isEmpty []) is True
    List.isEmpty []
        |> Expect.false "Expected the list not to be empty."

    {-

    Expected the list not to be empty.

    -}



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
    String.toInt "not an int"
        |> Expect.err

Test failures will be printed with the unexpected `Ok` value contrasting with
any `Err`.

    -- Fails
    String.toInt "20"
        |> Expect.err

    {-

    Ok 20
    ╷
    │ Expect.err
    ╵
    Err _

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



## true

```elm
true : String.String -> Basics.Bool -> Expect.Expectation
```

 Passes if the argument is 'True', and otherwise fails with the given message.

    Expect.true "Expected the list to be empty." (List.isEmpty [])

    -- Passes because (List.isEmpty []) is True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because List.isEmpty returns False, but we expect True.
    List.isEmpty [ 42 ]
        |> Expect.true "Expected the list to be empty."

    {-

    Expected the list to be empty.

    -}



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

A `Fuzzer a` knows how to create values of type `a` in two different ways. It
can create them randomly, so that your test's expectations are run against many
values. Fuzzers will often generate edge cases likely to find bugs. If the
fuzzer can make your test fail, it also knows how to "shrink" that failing input
into more minimal examples, some of which might also cause the tests to fail. In
this way, fuzzers can usually find the smallest or simplest input that
reproduces a bug.


## Common Fuzzers

@docs bool, int, intRange, float, floatRange, percentage, string, maybe, result, list, array


## Working with Fuzzers

@docs Fuzzer, oneOf, constant, map, map2, map3, map4, map5, andMap, frequency


## Tuple Fuzzers

Instead of using a tuple, consider using `fuzzN`.

@docs tuple, tuple3


## Uncommon Fuzzers

@docs custom, char, unit, order, invalid



## Fuzzer

```elm
type alias Fuzzer a =
    Fuzz.Internal.Fuzzer a
```

 The representation of fuzzers is opaque. Conceptually, a `Fuzzer a`
consists of a way to randomly generate values of type `a`, and a way to shrink
those values.


## andMap

```elm
andMap : Fuzz.Fuzzer a -> Fuzz.Fuzzer (a -> b) -> Fuzz.Fuzzer b
```

 Map over many fuzzers. This can act as mapN for N > 5.
The argument order is meant to accommodate chaining:
map f aFuzzer
|> andMap anotherFuzzer
|> andMap aThirdFuzzer
Note that shrinking may be better using mapN.


## array

```elm
array : Fuzz.Fuzzer a -> Fuzz.Fuzzer (Array.Array a)
```

 Given a fuzzer of a type, create a fuzzer of an array of that type.
Generates random arrays of varying length, favoring shorter arrays.


## bool

```elm
bool : Fuzz.Fuzzer Basics.Bool
```

 A fuzzer for bool values.


## char

```elm
char : Fuzz.Fuzzer Char.Char
```

 A fuzzer for char values. Generates random ascii chars disregarding the control
characters and the extended character set.


## constant

```elm
constant : a -> Fuzz.Fuzzer a
```

 Create a fuzzer that only and always returns the value provided, and performs no shrinking. This is hardly random,
and so this function is best used as a helper when creating more complicated fuzzers.


## custom

```elm
custom : Random.Generator a -> Shrink.Shrinker a -> Fuzz.Fuzzer a
```

 Build a custom `Fuzzer a` by providing a `Generator a` and a `Shrinker a`.
Generators are defined in [`elm-lang/random`](http://package.elm-lang.org/packages/elm-lang/random/latest),
which is not core's Random module but has a compatible interface. Shrinkers are
defined in [`eeue56/elm-shrink`](http://package.elm-lang.org/packages/eeue56/elm-shrink/latest/).

Here is an example for a record:

    import Random.Pcg as Random
    import Shrink

    type alias Position =
        { x : Int, y : Int }

    position : Fuzzer Position
    position =
        Fuzz.custom
            (Random.map2 Position (Random.int -100 100) (Random.int -100 100))
            (\{ x, y } -> Shrink.map Position (Shrink.int x) |> Shrink.andMap (Shrink.int y))

Here is an example for a custom union type, assuming there is already a `genName : Generator String` defined:

    type Question
        = Name String
        | Age Int

    question =
        let
            generator =
                Random.bool
                    |> Random.andThen
                        (\b ->
                            if b then
                                Random.map Name genName

                            else
                                Random.map Age (Random.int 0 120)
                        )

            shrinker question =
                case question of
                    Name n ->
                        Shrink.string n |> Shrink.map Name

                    Age i ->
                        Shrink.int i |> Shrink.map Age
        in
        Fuzz.custom generator shrinker

It is not possible to extract the generator and shrinker from an existing fuzzer.



## float

```elm
float : Fuzz.Fuzzer Basics.Float
```

 A fuzzer for float values. It will never produce `NaN`, `Infinity`, or `-Infinity`.

It's possible for this fuzzer to generate any other floating-point value, but it
favors numbers between -50 and 50, numbers between -1 and 1, and especially zero.



## floatRange

```elm
floatRange : Basics.Float -> Basics.Float -> Fuzz.Fuzzer Basics.Float
```

 A fuzzer for float values within between a given minimum and maximum
value, inclusive. Shrunken values will also be within the range.


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

There are a few circumstances in which this function will return an invalid
fuzzer, which causes it to fail any test that uses it:

  - If you provide an empty list of frequencies
  - If any of the weights are less than 0
  - If the weights sum to 0

Be careful recursively using this fuzzer in its arguments. Often using `map`
is a better way to do what you want. If you are fuzzing a tree-like data
structure, you should include a depth limit so to avoid infinite recursion, like
so:

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



## int

```elm
int : Fuzz.Fuzzer Basics.Int
```

 A fuzzer for int values. It will never produce `NaN`, `Infinity`, or `-Infinity`.

It's possible for this fuzzer to generate any 32-bit integer, but it favors
numbers between -50 and 50 and especially zero.



## intRange

```elm
intRange : Basics.Int -> Basics.Int -> Fuzz.Fuzzer Basics.Int
```

 A fuzzer for int values within between a given minimum and maximum value,
inclusive. Shrunken values will also be within the range.

Remember that [Random.maxInt](http://package.elm-lang.org/packages/elm-lang/core/latest/Random#maxInt)
is the maximum possible int value, so you can do `intRange x Random.maxInt` to get all
the ints x or bigger.



## invalid

```elm
invalid : String.String -> Fuzz.Fuzzer a
```

 A fuzzer that is invalid for the provided reason. Any fuzzers built with it
are also invalid. Any tests using an invalid fuzzer fail.


## list

```elm
list : Fuzz.Fuzzer a -> Fuzz.Fuzzer (List.List a)
```

 Given a fuzzer of a type, create a fuzzer of a list of that type.
Generates random lists of varying length, favoring shorter lists.


## map

```elm
map : (a -> b) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b
```

 Map a function over a fuzzer. This applies to both the generated and the shrunken values.


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


## maybe

```elm
maybe : Fuzz.Fuzzer a -> Fuzz.Fuzzer (Maybe.Maybe a)
```

 Given a fuzzer of a type, create a fuzzer of a maybe for that type.


## oneOf

```elm
oneOf : List.List (Fuzz.Fuzzer a) -> Fuzz.Fuzzer a
```

 Choose one of the given fuzzers at random. Each fuzzer has an equal chance
of being chosen; to customize the probabilities, use [`frequency`](#frequency).

    Fuzz.oneOf
        [ Fuzz.intRange 0 3
        , Fuzz.intRange 7 9
        ]



## order

```elm
order : Fuzz.Fuzzer Basics.Order
```

 A fuzzer for order values.


## percentage

```elm
percentage : Fuzz.Fuzzer Basics.Float
```

 A fuzzer for percentage values. Generates random floats between `0.0` and
`1.0`. It will test zero and one about 10% of the time each.


## result

```elm
result : Fuzz.Fuzzer error -> Fuzz.Fuzzer value -> Fuzz.Fuzzer (Result.Result error value)
```

 Given fuzzers for an error type and a success type, create a fuzzer for
a result.


## string

```elm
string : Fuzz.Fuzzer String.String
```

 Generates random printable ASCII strings of up to 1000 characters.

Shorter strings are more common, especially the empty string.



## tuple

```elm
tuple : ( Fuzz.Fuzzer a, Fuzz.Fuzzer b ) -> Fuzz.Fuzzer ( a, b )
```

 Turn a tuple of fuzzers into a fuzzer of tuples.


## tuple3

```elm
tuple3 : ( Fuzz.Fuzzer a, Fuzz.Fuzzer b, Fuzz.Fuzzer c ) -> Fuzz.Fuzzer ( a, b, c )
```

 Turn a 3-tuple of fuzzers into a fuzzer of 3-tuples.


## unit

```elm
unit : Fuzz.Fuzzer ()
```

 A fuzzer for the unit value. Unit is a type with only one value, commonly
used as a placeholder.


# Test

 A module containing functions for creating and managing tests.

@docs Test, test


## Organizing Tests

@docs describe, concat, todo, skip, only


## Fuzz Testing

@docs fuzz, fuzz2, fuzz3, fuzzWith, FuzzOptions



## FuzzOptions

```elm
type alias FuzzOptions =
    { runs : Basics.Int }
```

 Options [`fuzzWith`](#fuzzWith) accepts. Currently there is only one but this
API is designed so that it can accept more in the future.


### `runs`

The number of times to run each fuzz test. (Default is 100.)

    import Test exposing (fuzzWith)
    import Fuzz exposing (list, int)
    import Expect


    fuzzWith { runs = 350 } (list int) "List.length should always be positive" <|
        -- This anonymous function will be run 350 times, each time with a
        -- randomly-generated fuzzList value. (It will always be a list of ints
        -- because of (list int) above.)
        \fuzzList ->
            fuzzList
                |> List.length
                |> Expect.atLeast 0



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



## fuzz

```elm
fuzz : Fuzz.Fuzzer a -> String.String -> (a -> Expect.Expectation) -> Test.Test
```

 Take a function that produces a test, and calls it several (usually 100) times, using a randomly-generated input
from a [`Fuzzer`](http://package.elm-lang.org/packages/elm-community/elm-test/latest/Fuzz) each time. This allows you to
test that a property that should always be true is indeed true under a wide variety of conditions. The function also
takes a string describing the test.

These are called "[fuzz tests](https://en.wikipedia.org/wiki/Fuzz_testing)" because of the randomness.
You may find them elsewhere called [property-based tests](http://blog.jessitron.com/2013/04/property-based-testing-what-is-it.html),
[generative tests](http://www.pivotaltracker.com/community/tracker-blog/generative-testing), or
[QuickCheck-style tests](https://en.wikipedia.org/wiki/QuickCheck).

    import Test exposing (fuzz)
    import Fuzz exposing (list, int)
    import Expect


    fuzz (list int) "List.length should always be positive" <|
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

This is a convenience function that lets you skip calling [`Fuzz.tuple`](Fuzz#tuple).

See [`fuzzWith`](#fuzzWith) for an example of writing this in tuple style.

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

This is a convenience function that lets you skip calling [`Fuzz.tuple3`](Fuzz#tuple3).



## fuzzWith

```elm
fuzzWith : Test.FuzzOptions -> Fuzz.Fuzzer a -> String.String -> (a -> Expect.Expectation) -> Test.Test
```

 Run a [`fuzz`](#fuzz) test with the given [`FuzzOptions`](#FuzzOptions).

Note that there is no `fuzzWith2`, but you can always pass more fuzz values in
using [`Fuzz.tuple`](Fuzz#tuple), [`Fuzz.tuple3`](Fuzz#tuple3),
for example like this:

    import Test exposing (fuzzWith)
    import Fuzz exposing (tuple, list, int)
    import Expect


    fuzzWith { runs = 4200 }
        (tuple ( list int, int ))
        "List.reverse never influences List.member" <|
            \(nums, target) ->
                List.member target (List.reverse nums)
                    |> Expect.equal (List.member target nums)



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
        [ only <| describe "reverse"
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
        [ skip <| describe "reverse"
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



# Test.Runner

 This is an "experts only" module that exposes functions needed to run and
display tests. A typical user will use an existing runner library for Node or
the browser, which is implemented using this interface. A list of these runners
can be found in the `README`.


## Runner

@docs Runner, SeededRunners, fromTest


## Expectations

@docs getFailureReason, isTodo


## Formatting

@docs formatLabels


## Fuzzers

These functions give you the ability to run fuzzers separate of running fuzz tests.

@docs Shrinkable, fuzz, shrink



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



## Shrinkable

```elm
-- Opaque type: Shrinkable a (constructors not exposed)
```

 A `Shrinkable a` is an opaque type that allows you to obtain a value of type
`a` that is smaller than the one you've previously obtained.


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
fuzz : Fuzz.Fuzzer a -> Result.Result String.String (Random.Generator ( a, Test.Runner.Shrinkable a ))
```

 Given a fuzzer, return a random generator to produce a value and a
Shrinkable. The value is what a fuzz test would have received as input.


## getFailureReason

```elm
getFailureReason : Expect.Expectation -> Maybe.Maybe { given : Maybe.Maybe String.String, description : String.String, reason : Test.Runner.Failure.Reason }
```

 Return `Nothing` if the given [`Expectation`](#Expectation) is a [`pass`](#pass).

If it is a [`fail`](#fail), return a record containing the expectation
description, the [`Reason`](#Reason) the test failed, and the given inputs if
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


## shrink

```elm
shrink : Basics.Bool -> Test.Runner.Shrinkable a -> Maybe.Maybe ( a, Test.Runner.Shrinkable a )
```

 Given a Shrinkable, attempt to shrink the value further. Pass `False` to
indicate that the last value you've seen (from either `fuzz` or this function)
caused the test to **fail**. This will attempt to find a smaller value. Pass
`True` if the test passed. If you have already seen a failure, this will attempt
to shrink that failure in another way. In both cases, it may be impossible to
shrink the value, represented by `Nothing`.


# Test.Runner.Failure

 The reason a test failed.

@docs Reason, InvalidReason, format



## InvalidReason

```elm
type InvalidReason
    = EmptyList
    | NonpositiveFuzzCount
    | InvalidFuzzer
    | BadDescription
    | DuplicatedName
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



## format

```elm
format : String.String -> Test.Runner.Failure.Reason -> String.String
```

 DEPRECATED. In the future, test runners should implement versions of this
that make sense for their own environments.

Format test run failures in a reasonable way.


