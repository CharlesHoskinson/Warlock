# official/packages/elm-explorations/benchmark/1.0.1/docs.json
Source: https://package.elm-lang.org/packages/elm-explorations/benchmark/1.0.1/docs.json

# Benchmark

 Benchmark Elm Programs

@docs Benchmark


# Creating and Organizing Benchmarks

@docs benchmark, compare, scale, describe


# Writing Runners

@docs step, done



## Benchmark

```elm
type alias Benchmark =
    Benchmark.Benchmark.Benchmark
```

 Benchmarks that contain potential, in-progress, and completed runs.

To make these, try [`benchmark`](#benchmark), [`compare`](#compare),
or [`scale`](#scale), and organize them with [`describe`](#describe).



## benchmark

```elm
benchmark : String.String -> (() -> a) -> Benchmark.Benchmark
```

 Benchmark a single function.

    benchmark "head" (\_ -> List.head [ 1 ])

The name here should be short and descriptive. Ideally, it should also
uniquely identify a single benchmark among your whole suite.

Your code is wrapped in an anonymous function, which we will call
repeatedly to measure speed. Note that this is slightly slower than
calling functions directly. This is OK! The point of this library is
to _reliably_ measure execution speed. In this case, we get more
consistent results by calling them inside thunks like this.

Now, a note about benchmark design: when you first write benchmarks,
you usually think something along the lines of "I need to test the
worst possible complexity!" You should test this _eventually_, but
it's a bad _first_ step.

Instead, benchmark the smallest _real_ sample. If your typical use of
a data structure has 20 items, measure with 20 items. You'll get edge
cases eventually, but it's better to get the basics right
first. **Solve the problems you know are real** instead of inventing
situations you may never encounter.

When you get the point where you _know_ you need to measure a bunch of
different sizes, we've got your back: that's what [`scale`](#scale) is
for.



## compare

```elm
compare : String.String -> String.String -> (() -> a) -> String.String -> (() -> b) -> Benchmark.Benchmark
```

 Run two benchmarks head-to-head. This is useful when optimizing
data structures or other situations where you can make
apples-to-apples comparisons between different approaches.

As with [`benchmark`](#benchmark), the first argument is the name for
the comparison. The other string arguments are the names of the
functions that follow them directly.

    compare "initialize"
        "Hamt"
        (\_ -> Array.HAMT.initialize 100 identity)
        "Core"
        (\_ -> Array.initialize 100 identity)

In addition to the general advice in [`benchmark`](#benchmark), try as
hard as possible to make the arguments the same. It wouldn't be a
valid comparison if, in the example above, we told `Array.HAMT` to use
1,000 items instead of 100. In the cases where you can't get _exactly_
the same arguments, at least try to match output.



## describe

```elm
describe : String.String -> List.List Benchmark.Benchmark -> Benchmark.Benchmark
```

 Group a number of benchmarks together. Grouping benchmarks using
`describe` will never effect measurement, only organization.

You'll typically have at least one call to this in your benchmark
program, at the top level:

    describe "your program"
        [{- your benchmarks here -}]



## done

```elm
done : Benchmark.Benchmark -> Basics.Bool
```

 find out if a Benchmark is finished. For progress information for
reporting purposes, see `Benchmark.Status.progress`.

The default runner uses this function to find out if it should call
`step` any more.



## scale

```elm
scale : String.String -> List.List ( String.String, () -> a ) -> Benchmark.Benchmark
```

 Specify scale benchmarks for a function. This is especially good
for measuring the performance of your data structures under
differently sized workloads.

Beware that large series can make very heavy benchmarks. Adjust your
expectations and measurements accordingly!

For example, this benchmark will see how long it takes to get a
dictionary size, where the size is powers of 10 between 1 and 100,000:

    dictOfSize : Int -> Dict Int ()
    dictOfSize size =
        List.range 0 size
            |> List.map (\a -> (\a b -> ( a, b )) a ())
            |> Dict.fromList

    dictSize : Benchmark
    dictSize =
        List.range 0 5
            -- tip: prepare your data structures _outside_ the
            -- benchmark function. Here, we're measuring `Dict.size`
            -- without interference from `dictOfSize` and the
            -- functions that it uses.
            |> List.map ((^) 10)
            |> List.map (\size -> ( size, dictOfSize size ))
            -- now we have a list of structures, make benchmarks pass
            -- them to `scale`!
            |> List.map (\( size, target ) -> ( toString size, \_ -> Dict.size target ))
            |> scale "Dict.size"

**Note:** The API for this function is newer, and may change in the future than
other functions. If you use it, please [open an
issue](https://github.com/brianhicks/elm-benchmark/issues) with your
use case so we can know the right situations to optimize for in future
releases.



## step

```elm
step : Benchmark.Benchmark -> Task.Task Basics.Never Benchmark.Benchmark
```

 Step a benchmark forward to completion.

**Warning:** `step` is only useful for writing runners. As a consumer
of the `elm-benchmark` library, you'll probably never need it!

...

Still with me? OK, let's go.

This function "advances" a benchmark through a series of states
(described below.) If the benchmark has no more work to do, this is a
no-op. But you probably want to know about that so you can present
results to the user, so use [`done`](#done) to figure it out before
you call this.

At a high level, a runner just needs to receive benchmarks from the
user, iterate over them using this function, and convert them to
`Report`s whenever it makes sense to you to do so. You shouldn't need
to care _too much_ about the nuances of the internal benchmark state,
but a little knowledge is useful for making a really great user
experience, so read on.


## The Life of a Benchmark

         ┌─────────────┐
         │    cold     │
         │  benchmark  │
         └─────────────┘
                │
                │  warm up JIT
                ▼
         ┌─────────────┐
         │   unsized   │
         │  benchmark  │
         └─────────────┘
                │
                │  determine
                │  sample size
                ▼
        ┌──────────────┐
        │              │ ───┐
        │    sized     │    │ collect
        │  benchmark   │    │ another
        │  (running)   │    │ sample
        │              │ ◀──┘
        └──────────────┘
            │      │
         ┌──┘      └──┐
         │            │
         ▼            ▼
    ┌─────────┐  ┌─────────┐
    │         │  │         │
    │ success │  │ failure │
    │         │  │         │
    └─────────┘  └─────────┘

When you get a [`Benchmark`](#Benchmark) from the user it won't have
any idea how big the sample size should be. In fact, we can't know
this in advance because different functions will have different
performance characteristics on different machines and browsers and
phases of the moon and so on and so forth.

This is difficult, but not hopeless! We can determine sample size
automatically by running the benchmark a few times to get a feel for
how it behaves in this particular environment. This becomes our first
step. (If you're curious about how exactly we do this, check the
`Benchmark.LowLevel` documentation.)

Once we have the base sample size, we start collecting samples. We
multiply the base sample size to spread runs into a series of buckets.
We do this because running a benchmark twice _ought to_ take about
twice as long as running it once. Since this relationship is perfectly
linear, we can get a number of sample sizes, then create a trend from
them which will be resilient to outliers.

The final result takes the form of an error or a set of samples, their
sizes, and a trend created from that data.

At this point, we're done! The results are presented to the user, and
they make optimizations and try again for ever higher runs per second.



# Benchmark.LowLevel

 Low Level Elm Benchmarking API

This API exposes the raw tasks necessary to create higher-level
benchmarking abstractions.

As a user, you're probably not going to need to use this library. Take
a look at `Benchmark` instead, it has the user-friendly primitives. If
you _do_ find yourself using this library often, please [open an issue
on
`elm-benchmark`](https://github.com/BrianHicks/elm-benchmark/issues/new)
and we'll find a way to make your use case friendlier.


# Operations

@docs Operation, operation


## Measuring Operations

@docs warmup, findSampleSize, sample, Error



## Error

```elm
type Error
    = StackOverflow
    | UnknownError (String.String)
```

 Error states that can terminate a sampling run.


## Operation

```elm
-- Opaque type: Operation (constructors not exposed)
```

 An operation to benchmark. Use [`operation`](#operation) to
construct these.


## findSampleSize

```elm
findSampleSize : Benchmark.LowLevel.Operation -> Task.Task Benchmark.LowLevel.Error Basics.Int
```

 Find an appropriate sample size for benchmarking. This should be
much greater than the clock resolution (5µs in the browser) to make
sure we get good data.

We do this by starting at sample size 1. If that doesn't pass our
threshold, we multiply by [the golden
ratio](https://en.wikipedia.org/wiki/Golden_ratio) and try again until
we get a large enough sample.

In addition, we want the sample size to be more-or-less the same
across runs, despite small differences in measured fit. We do this by
rounding to the nearest order of magnitude. So, for example, if the
sample size is 1,234 we round to 1,000. If it's 8,800, we round to
9,000.



## operation

```elm
operation : (() -> a) -> Benchmark.LowLevel.Operation
```

 Make an `Operation`, given a function that runs the code you want
to benchmark when given a unit (`()`.)


## sample

```elm
sample : Basics.Int -> Benchmark.LowLevel.Operation -> Task.Task Benchmark.LowLevel.Error Basics.Float
```

 Run a benchmark a number of times. The returned value is the total
time it took for the given number of runs.

In the browser, high-resolution timing data from these functions comes
from the [Performance
API](https://developer.mozilla.org/en-US/docs/Web/API/Performance) and
is accurate to 5µs. If `performance.now` is unavailable, it will fall
back to
[Date](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date),
accurate to 1ms.



## warmup

```elm
warmup : Benchmark.LowLevel.Operation -> Task.Task Benchmark.LowLevel.Error ()
```

 Warm up the JIT for a benchmarking run. You should call this
before calling [`findSampleSize`](#findSampleSize) or trusting the
times coming out of [`measure`](#measure).

If we don't warm up the JIT beforehand, it will slow down your
benchmark and result in inaccurate data. (By the way, [Mozilla has an
excellent
explanation](https://hacks.mozilla.org/2017/02/a-crash-course-in-just-in-time-jit-compilers/)
of how this all works.)



# Benchmark.Reporting

 Reporting for Benchmarks

@docs Report, fromBenchmark



## Report

```elm
type Report
    = Single (String.String) (Benchmark.Status.Status)
    | Series (String.String) (List.List ( String.String, Benchmark.Status.Status ))
    | Group (String.String) (List.List Benchmark.Reporting.Report)
```

 Reports are the public version of Benchmarks.

Each tag of Report has a name and some other information about the
structure of a benchmarking run.



## fromBenchmark

```elm
fromBenchmark : Benchmark.Benchmark.Benchmark -> Benchmark.Reporting.Report
```

 Get a report from a Benchmark.


# Benchmark.Runner

 Browser Benchmark Runner

@docs program, BenchmarkProgram



## BenchmarkProgram

```elm
type alias BenchmarkProgram =
    Platform.Program () Benchmark.Runner.App.Model Benchmark.Runner.App.Msg
```

 A handy type alias for values produced by [`program`](#program)


## program

```elm
program : Benchmark.Benchmark -> Benchmark.Runner.BenchmarkProgram
```

 Create a runner program from a benchmark. For example:

    main : BenchmarkProgram
    main =
        Runner.program <|
            Benchmark.describe "your benchmarks"
                [{- your benchmarks here -}]

Compile this and visit the result in your browser to run the
benchmarks.



# Benchmark.Status

 Report the status of a Benchmark.


# Reporting

@docs Status, progress

@docs Error


## Runtime Configuration

@docs numBuckets, samplesPerBucket, bucketSpacingRatio



## Error

```elm
type Error
    = MeasurementError (Benchmark.LowLevel.Error)
    | AnalysisError (Trend.Math.Error)
```

 Ways a benchmark can fail, expressed as either at runtime (in
which case we have a `LowLevel.Error`) or while analyzing data (in
which case we have a `Trend.Math.Error`.)


## Status

```elm
type Status
    = Cold
    | Unsized
    | Pending (Basics.Int) (Benchmark.Samples.Samples)
    | Failure (Benchmark.Status.Error)
    | Success (Benchmark.Samples.Samples) (Trend.Linear.Trend Trend.Linear.Quick)
```

 Indicate the status of a benchmark.

  - `Cold`: We have not warmed up the JIT yet.

  - `Unsized`: We have not yet determined the best sample size for
    this benchmark.

  - `Pending`: We are in the process of collecting sample data. We
    will keep collecting sample data using the base sample size (first
    argument) until we have enough samples (`numBuckets *
    samplesPerBucket`.) We also store samples while in progress
    (second argument.)

  - `Failure`: We ran into an exception while collecting sample
    data. The attached `Error` tells us what went wrong.

  - `Success`: We finished collecting all our sample data (first
    argument.) We've calculated a trend using this data (second
    argument.)

See "The Life of a Benchmark" in the docs for `Benchmark` for an
explanation of how these fit together.



## bucketSpacingRatio

```elm
bucketSpacingRatio : Basics.Int
```

 How far apart should the sample size for each bucket be?


## numBuckets

```elm
numBuckets : Basics.Int
```

 How many buckets are samples spread out into?


## progress

```elm
progress : Benchmark.Status.Status -> Basics.Float
```

 How far along is this benchmark? This is a percentage, represented
as a `Float` between `0` and `1`.


## samplesPerBucket

```elm
samplesPerBucket : Basics.Int
```

 How many samples will we take per bucket?

