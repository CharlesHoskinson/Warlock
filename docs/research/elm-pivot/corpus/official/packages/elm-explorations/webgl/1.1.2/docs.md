# official/packages/elm-explorations/webgl/1.1.2/docs.json
Source: https://package.elm-lang.org/packages/elm-explorations/webgl/1.1.2/docs.json

# WebGL

 The WebGL API is for high performance rendering. Definitely read about
[how WebGL works](https://package.elm-lang.org/packages/elm-explorations/webgl/latest)
and look at [some examples](https://github.com/elm-explorations/webgl/tree/master/examples)
before trying to do too much with just the documentation provided here.


# Mesh

@docs Mesh, triangles


# Shaders

@docs Shader


# Entities

@docs Entity, entity


# WebGL Html

@docs toHtml


# Advanced Usage

@docs entityWith, toHtmlWith, Option, alpha, depth, stencil, antialias
@docs clearColor, preserveDrawingBuffer


# Meshes

@docs indexedTriangles, lines, lineStrip, lineLoop, points, triangleFan
@docs triangleStrip



## Option

```elm
type alias Option =
    WebGL.Internal.Option
```

 Provides a way to enable features and change the scene behavior
in [`toHtmlWith`](#toHtmlWith).


## Entity

```elm
-- Opaque type: Entity (constructors not exposed)
```

 Conceptually, an encapsulation of the instructions to render something.


## Mesh

```elm
-- Opaque type: Mesh attributes (constructors not exposed)
```

 Mesh forms geometry from the specified vertices. Each vertex contains a
bunch of attributes, defined as a custom record type, e.g.:

    type alias Attributes =
        { position : Vec3
        , color : Vec3
        }

The supported types in attributes are: `Int`, `Float`, `Texture`
and `Vec2`, `Vec3`, `Vec4`, `Mat4` from the
[linear-algebra](https://package.elm-lang.org/packages/elm-explorations/linear-algebra/latest)
package.

Do not generate meshes in `view`, [read more about this here](https://package.elm-lang.org/packages/elm-explorations/webgl/latest#making-the-most-of-the-gpu).



## Shader

```elm
-- Opaque type: Shader attributes uniforms varyings (constructors not exposed)
```

 Shaders are programs for running many computations on the GPU in parallel.
They are written in a language called
[GLSL](https://en.wikipedia.org/wiki/OpenGL_Shading_Language). Read more about
shaders [here](https://github.com/elm-explorations/webgl/blob/master/README.md).

Normally you specify a shader with a `[glsl| |]` block. Elm compiler will parse
the shader code block and derive the type signature for your shader.

  - `attributes` define vertices in the [mesh](#Mesh);
  - `uniforms` allow you to pass scene parameters like
    transformation matrix, texture, screen size, etc.;
  - `varyings` define the output from the vertex shader.

`attributes`, `uniforms` and `varyings` are records with the fields of the
following types: `Int`, `Float`, [`Texture`](#Texture) and `Vec2`, `Vec3`, `Vec4`,
`Mat4` from the
[linear-algebra](https://package.elm-lang.org/packages/elm-explorations/linear-algebra/latest)
package.



## alpha

```elm
alpha : Basics.Bool -> WebGL.Option
```

 Enable alpha channel in the drawing buffer. If the argument is `True`, then
the page compositor will assume the drawing buffer contains colors with
premultiplied alpha `(r * a, g * a, b * a, a)`.


## antialias

```elm
antialias : WebGL.Option
```

 Enable multisample antialiasing of the drawing buffer, if supported by
the platform. Useful when you need to have smooth lines and smooth edges of
triangles at a lower cost than supersampling (rendering to larger dimensions and
then scaling down with CSS transform).


## clearColor

```elm
clearColor : Basics.Float -> Basics.Float -> Basics.Float -> Basics.Float -> WebGL.Option
```

 Set the red, green, blue and alpha channels, that will be used to
fill the drawing buffer every time before drawing the scene. The values are
clamped between 0 and 1. The default is all 0's.


## depth

```elm
depth : Basics.Float -> WebGL.Option
```

 Enable the depth buffer, and prefill it with given value each time before
the scene is rendered. The value is clamped between 0 and 1.


## entity

```elm
entity : WebGL.Shader attributes uniforms varyings -> WebGL.Shader {} uniforms varyings -> WebGL.Mesh attributes -> uniforms -> WebGL.Entity
```

 Packages a vertex shader, a fragment shader, a mesh, and uniforms
as an `Entity`. This specifies a full rendering pipeline to be run
on the GPU. You can read more about the pipeline
[here](https://github.com/elm-explorations/webgl/blob/master/README.md).

The vertex shader receives `attributes` and `uniforms` and returns `varyings`
and `gl_Position`—the position of the vertex on the screen, defined as
`vec4(x, y, z, w)`, that means `(x/w, y/w, z/w)` in the clip space coordinates:

    --   (-1,1,1) +================+ (1,1,1)
    --           /|               /|
    --          / |     |        / |
    --(-1,1,-1)+================+ (1,1,-1)
    --         |  |     | /     |  |
    --         |  |     |/      |  |
    --         |  |     +-------|->|
    -- (-1,-1,1|) +--(0,0,0)----|--+ (1,-1,1)
    --         | /              | /
    --         |/               |/
    --         +================+
    --   (-1,-1,-1)         (1,-1,-1)



The fragment shader is called for each pixel inside the clip space with
`varyings` and `uniforms` and returns `gl_FragColor`—the color of
the pixel, defined as `vec4(r, g, b, a)` where each color component is a float
from 0 to 1.

Shaders and a mesh are cached so that they do not get resent to the GPU.
It should be relatively cheap to create new entities out of existing
values.

By default, [depth test](WebGL-Settings-DepthTest#default) is enabled for you.
If you need more [settings](WebGL-Settings), like
[blending](WebGL-Settings-Blend) or [stencil test](WebG-Settings-StencilTest),
then use [`entityWith`](#entityWith).

    entity =
        entityWith [ DepthTest.default ]



## entityWith

```elm
entityWith : List.List WebGL.Settings.Setting -> WebGL.Shader attributes uniforms varyings -> WebGL.Shader {} uniforms varyings -> WebGL.Mesh attributes -> uniforms -> WebGL.Entity
```

 The same as [`entity`](#entity), but allows to configure an entity with
[settings](WebGL-Settings).


## indexedTriangles

```elm
indexedTriangles : List.List attributes -> List.List ( Basics.Int, Basics.Int, Basics.Int ) -> WebGL.Mesh attributes
```

 Create triangles from vertices and indices, grouped in sets of three to
define each triangle by refering the vertices. This helps to avoid duplicated vertices whenever two triangles share an
edge.

    -- v2 +---+ v1
    --    |\  |
    --    | \ |
    --    |  \|
    -- v3 +---+ v0



For example, if you want to define a rectangle using
[`triangles`](#triangles), `v0` and `v2` will have to be duplicated:

    rectangle =
        triangles [ ( v0, v1, v2 ), ( v2, v3, v0 ) ]

This will use two vertices less:

    rectangle =
        indexedTriangles [ v0, v1, v2, v3 ] [ ( 0, 1, 2 ), ( 2, 3, 0 ) ]



## lineLoop

```elm
lineLoop : List.List attributes -> WebGL.Mesh attributes
```

 Similar to [`lineStrip`](#lineStrip), but connects the last vertex back to
the first.


## lineStrip

```elm
lineStrip : List.List attributes -> WebGL.Mesh attributes
```

 Connects each two subsequent vertices with a line.


## lines

```elm
lines : List.List ( attributes, attributes ) -> WebGL.Mesh attributes
```

 Connects each pair of vertices with a line.


## points

```elm
points : List.List attributes -> WebGL.Mesh attributes
```

 Draws a single dot per vertex.


## preserveDrawingBuffer

```elm
preserveDrawingBuffer : WebGL.Option
```

 By default, WebGL canvas swaps the drawing and display buffers.
This option forces it to copy the drawing buffer into the display buffer.

Even though this slows down the rendering, it allows you to extract an image
from the canvas element using `canvas.toBlob()` in JavaScript without having
to worry about synchronization between frames.



## stencil

```elm
stencil : Basics.Int -> WebGL.Option
```

 Enable the stencil buffer, specifying the index used to fill the
stencil buffer before we render the scene. The index is masked with 2^m - 1,
where m >= 8 is the number of bits in the stencil buffer. The default is 0.


## toHtml

```elm
toHtml : List.List (Html.Attribute msg) -> List.List WebGL.Entity -> Html.Html msg
```

 Render a WebGL scene with the given html attributes, and entities.

`width` and `height` html attributes resize the drawing buffer, while
the corresponding css properties scale the canvas element.

To prevent blurriness on retina screens, you may want the drawing buffer
to be twice the size of the canvas element.

To remove an extra whitespace around the canvas, set `display: block`.

By default, alpha channel with premultiplied alpha, antialias and depth buffer
are enabled. Use [`toHtmlWith`](#toHtmlWith) for custom options.

    toHtml =
        toHtmlWith [ alpha True, antialias, depth 1 ]



## toHtmlWith

```elm
toHtmlWith : List.List WebGL.Option -> List.List (Html.Attribute msg) -> List.List WebGL.Entity -> Html.Html msg
```

 Render a WebGL scene with the given options, html attributes, and entities.

Due to browser limitations, options will be applied only once,
when the canvas is created for the first time.



## triangleFan

```elm
triangleFan : List.List attributes -> WebGL.Mesh attributes
```

 Similar to [`triangleStrip`](#triangleStrip), but creates a fan shaped
output.


## triangleStrip

```elm
triangleStrip : List.List attributes -> WebGL.Mesh attributes
```

 Creates a strip of triangles where each additional vertex creates an
additional triangle once the first three vertices have been drawn.


## triangles

```elm
triangles : List.List ( attributes, attributes, attributes ) -> WebGL.Mesh attributes
```

 Triangles are the basic building blocks of a mesh. You can put them together
to form any shape.

So when you create `triangles` you are really providing three sets of attributes
that describe the corners of each triangle.



# WebGL.Settings




# Settings

@docs Setting, scissor, colorMask, polygonOffset, sampleAlphaToCoverage
@docs sampleCoverage, cullFace


## Face Modes

@docs FaceMode, front, back, frontAndBack



## Setting

```elm
type alias Setting =
    WebGL.Internal.Setting
```

 Lets you customize how an [`Entity`](WebGL#Entity) is rendered. So if you
only want to see the red part of your entity, you would use
[`entityWith`](WebGL#entityWith) and [`colorMask`](#colorMask) to say:

    entityWith [colorMask True False False False]
        vertShader fragShader mesh uniforms

    -- vertShader : Shader attributes uniforms varyings
    -- fragShader : Shader {} uniforms varyings
    -- mesh : Mesh attributes
    -- uniforms : uniforms



## FaceMode

```elm
-- Opaque type: FaceMode (constructors not exposed)
```

 Targets the polygons based on their facing.


## back

```elm
back : WebGL.Settings.FaceMode
```

 

## colorMask

```elm
colorMask : Basics.Bool -> Basics.Bool -> Basics.Bool -> Basics.Bool -> WebGL.Settings.Setting
```

 Specify whether or not each channel (red, green, blue, alpha) should be
output on the screen.


## cullFace

```elm
cullFace : WebGL.Settings.FaceMode -> WebGL.Settings.Setting
```

 Excludes polygons based on winding (the order of the vertices) in window
coordinates. Polygons with counter-clock-wise winding are front-facing.


## front

```elm
front : WebGL.Settings.FaceMode
```

 

## frontAndBack

```elm
frontAndBack : WebGL.Settings.FaceMode
```

 

## polygonOffset

```elm
polygonOffset : Basics.Float -> Basics.Float -> WebGL.Settings.Setting
```

 When you want to draw the highlighting wireframe on top of the solid
object, the lines may fade in and out of the coincident polygons,
which is sometimes called "stitching" and is visually unpleasant.

[Polygon Offset](https://www.glprogramming.com/red/chapter06.html#name4)
helps to avoid "stitching" by adding an offset to pixel’s depth
values before the depth test is performed and before the value is written
into the depth buffer.

    polygonOffset factor units

This adds an `offset = m * factor + r * units`, where

  - `m = max (dz / dx) (dz / dy)` is the maximum depth slope of the polygon.
    The depth slope is the change in `z` (depth) values divided by the change in
    either `x` or `y` coordinates, as you traverse a polygon;
  - `r` is the smallest value guaranteed to produce a resolvable difference in
    window coordinate depth values. The value `r` is an implementation-specific
    constant.

The question is: "How much offset is enough?". It really depends on the slope.
For polygons that are parallel to the near and far clipping planes,
the depth slope is zero, so the minimum offset is needed:

    polygonOffset 0 1

For polygons that are at a great angle to the clipping planes, the depth slope
can be significantly greater than zero. Use small non-zero values for factor,
such as `0.75` or `1.0` should be enough to generate distinct depth values:

    polygonOffset 0.75 1



## sampleAlphaToCoverage

```elm
sampleAlphaToCoverage : WebGL.Settings.Setting
```

 When you render overlapping transparent entities, like grass or hair, you
may notice that alpha blending doesn’t really work with depth testing, because
depth test ignores transparency.
[Alpha To Coverage](https://wiki.polycount.com/wiki/Transparency_map#Alpha_To_Coverage)
is a way to address this issue without sorting transparent entities.

It works by computing a temporary coverage value, where each bit is determined
by the alpha value at the corresponding sample location. The temporary coverage
value is then ANDed with the fragment coverage value.

Requires [`WebGL.antialias`](WebGL#antialias) option.



## sampleCoverage

```elm
sampleCoverage : Basics.Float -> Basics.Bool -> WebGL.Settings.Setting
```

 Specifies multisample coverage parameters. The fragment's coverage is ANDed
with the temporary coverage value.

  - the first argument specifies sample coverage value, that is clamped to the
    range from 0 to 1;
  - the second argument represents if the coverage masks should be inverted.

Requires [`WebGL.antialias`](WebGL#antialias) option.



## scissor

```elm
scissor : Basics.Int -> Basics.Int -> Basics.Int -> Basics.Int -> WebGL.Settings.Setting
```

 Set the scissor box, which limits the drawing of fragments to the
screen to a specified rectangle.

The arguments are the coordinates of the lower left corner, width and height.



# WebGL.Settings.Blend




# Blenders

@docs add, subtract, reverseSubtract


# Blend Factors

@docs Factor, zero, one, srcColor, oneMinusSrcColor, dstColor
@docs oneMinusDstColor, srcAlpha, oneMinusSrcAlpha, dstAlpha
@docs oneMinusDstAlpha, srcAlphaSaturate


# Custom Blenders

@docs custom, Blender, customAdd, customSubtract, customReverseSubtract
@docs constantColor, oneMinusConstantColor, constantAlpha
@docs oneMinusConstantAlpha



## Blender

```elm
-- Opaque type: Blender (constructors not exposed)
```

 A `Blender` mixes the color of the current `Entity` (the source color)
with whatever is behind it (the destination color).
You can get a feel for all the options [here](https://threejs.org/examples/webgl_materials_blending_custom.html).


## Factor

```elm
-- Opaque type: Factor (constructors not exposed)
```

 

## add

```elm
add : WebGL.Settings.Blend.Factor -> WebGL.Settings.Blend.Factor -> WebGL.Settings.Setting
```

 Add the color of the current `Renderable` (the source color)
with whatever is behind it (the destination color). For example,
here is the “default” blender:

    add one zero

The resulting color will be `(src * 1) + (dest * 0)`, which means
we do not use the destination color at all!
You can get a feel for all the different blending factors
[here](https://threejs.org/examples/webgl_materials_blending_custom.html).



## constantAlpha

```elm
constantAlpha : WebGL.Settings.Blend.Factor
```

 

## constantColor

```elm
constantColor : WebGL.Settings.Blend.Factor
```

 This uses the constant `r`, `g`, `b`, and `a` values
given to [`custom`](#custom). If you use this `Factor` with
[`add`](#add), the constant color will default to black.

Because of
[restriction in WebGL](https://www.khronos.org/registry/webgl/specs/latest/1.0/#6.13),
you cannot create a `Blender`, that has one factor set to
`constantColor` or `oneMinusConstantColor` and another set to
`constantAlpha` or `oneMinusConstantAlpha`.



## custom

```elm
custom : { r : Basics.Float, g : Basics.Float, b : Basics.Float, a : Basics.Float, color : WebGL.Settings.Blend.Blender, alpha : WebGL.Settings.Blend.Blender } -> WebGL.Settings.Setting
```

 It is possible to do some very fancy blending with
`custom`. For example, you can blend the color value and
the alpha values separately:

    myBlender : Float -> Setting
    myBlender alpha =
        custom
            { r = 0
            , g = 0
            , b = 0
            , a = alpha
            , color = customAdd one zero
            , alpha = customAdd one constantAlpha
            }



## customAdd

```elm
customAdd : WebGL.Settings.Blend.Factor -> WebGL.Settings.Blend.Factor -> WebGL.Settings.Blend.Blender
```

 

## customReverseSubtract

```elm
customReverseSubtract : WebGL.Settings.Blend.Factor -> WebGL.Settings.Blend.Factor -> WebGL.Settings.Blend.Blender
```

 

## customSubtract

```elm
customSubtract : WebGL.Settings.Blend.Factor -> WebGL.Settings.Blend.Factor -> WebGL.Settings.Blend.Blender
```

 

## dstAlpha

```elm
dstAlpha : WebGL.Settings.Blend.Factor
```

 

## dstColor

```elm
dstColor : WebGL.Settings.Blend.Factor
```

 

## one

```elm
one : WebGL.Settings.Blend.Factor
```

 

## oneMinusConstantAlpha

```elm
oneMinusConstantAlpha : WebGL.Settings.Blend.Factor
```

 

## oneMinusConstantColor

```elm
oneMinusConstantColor : WebGL.Settings.Blend.Factor
```

 

## oneMinusDstAlpha

```elm
oneMinusDstAlpha : WebGL.Settings.Blend.Factor
```

 

## oneMinusDstColor

```elm
oneMinusDstColor : WebGL.Settings.Blend.Factor
```

 

## oneMinusSrcAlpha

```elm
oneMinusSrcAlpha : WebGL.Settings.Blend.Factor
```

 

## oneMinusSrcColor

```elm
oneMinusSrcColor : WebGL.Settings.Blend.Factor
```

 

## reverseSubtract

```elm
reverseSubtract : WebGL.Settings.Blend.Factor -> WebGL.Settings.Blend.Factor -> WebGL.Settings.Setting
```

 Similar to [`add`](#add), but it does `(dest * factor2) - (src * factor1)`.
This one is weird.


## srcAlpha

```elm
srcAlpha : WebGL.Settings.Blend.Factor
```

 

## srcAlphaSaturate

```elm
srcAlphaSaturate : WebGL.Settings.Blend.Factor
```

 

## srcColor

```elm
srcColor : WebGL.Settings.Blend.Factor
```

 

## subtract

```elm
subtract : WebGL.Settings.Blend.Factor -> WebGL.Settings.Blend.Factor -> WebGL.Settings.Setting
```

 Similar to [`add`](#add), but it does `(src * factor1) - (dest * factor2)`.
For example:

    subtract one one

This would do `(src * 1) - (dest * 1)` so you would take away colors
based on the background.



## zero

```elm
zero : WebGL.Settings.Blend.Factor
```

 

# WebGL.Settings.DepthTest

 You can read more about depth-testing in the
[OpenGL wiki](https://www.khronos.org/opengl/wiki/Depth_Test)
or [OpenGL docs](https://www.opengl.org/sdk/docs/man2/xhtml/glDepthFunc.xml).


# Depth Test

@docs default


# Custom Tests

@docs Options, less, never, always, equal, greater, notEqual
@docs lessOrEqual, greaterOrEqual



## Options

```elm
type alias Options =
    { write : Basics.Bool, near : Basics.Float, far : Basics.Float }
```

 When rendering, you have a buffer of pixels. Depth-testing works by
creating a second buffer with exactly the same number of entries, but
instead of holding colors, each entry holds the distance from the camera.
You go through all your entities, writing into the depth buffer, and then
you draw the color of the “winner”.

Which color wins? This is based on a bunch of comparison functions:

    less options           -- value < depth
    never options          -- Never pass
    always options         -- Always pass
    equal options          -- value == depth
    greater options        -- value > depth
    notEqual options       -- value != depth
    lessOrEqual options    -- value <= depth
    greaterOrEqual options -- value >= depth

If the test passes, the current value will be written into the depth buffer, so
the next pixels will be tested against it. Sometimes you may want to disable
writing. For example, when using depth test together with stencil test to create
[reflection effect](https://open.gl/depthstencils) you want to draw the
reflection *underneath* the floor, in this case you set `write = False`
when drawing the floor. The
[crate example](https://github.com/elm-explorations/webgl/blob/master/examples/crate.elm)
shows how to do it in Elm.

`near` and `far` allow to allocate a portion of the depth range from 0 to 1.
For example, if you want to render GUI on top of the scene, you can
set `near = 0.1, far = 1` for the scene and then render the GUI with
`near = 0, far = 0.1`.



## always

```elm
always : WebGL.Settings.DepthTest.Options -> WebGL.Settings.Setting
```

 

## default

```elm
default : WebGL.Settings.Setting
```

 With every pixel, we have to figure out which color to show.

Imagine you have many entities in the same line of sight. The floor,
then a table, then a plate. When depth-testing is off, you go through
the entities in the order they appear in your *code*! That means if
you describe the floor last, it will be “on top” of the table and plate.

Depth-testing means the color is chosen based on the distance from the
camera. So `default` uses the color closest to the camera. This means
the plate will be on top of the table, and both are on top of the floor.
Seems more reasonable!

There are a bunch of ways you can customize the depth test, shown later,
and you can use them to define `default` like this:

    default =
        less { write = True, near = 0, far = 1 }

Requires [`WebGL.depth`](WebGL#depth) option in
[`toHtmlWith`](WebGL#toHtmlWith).



## equal

```elm
equal : WebGL.Settings.DepthTest.Options -> WebGL.Settings.Setting
```

 

## greater

```elm
greater : WebGL.Settings.DepthTest.Options -> WebGL.Settings.Setting
```

 

## greaterOrEqual

```elm
greaterOrEqual : WebGL.Settings.DepthTest.Options -> WebGL.Settings.Setting
```

 

## less

```elm
less : WebGL.Settings.DepthTest.Options -> WebGL.Settings.Setting
```

 

## lessOrEqual

```elm
lessOrEqual : WebGL.Settings.DepthTest.Options -> WebGL.Settings.Setting
```

 

## never

```elm
never : WebGL.Settings.DepthTest.Options -> WebGL.Settings.Setting
```

 

## notEqual

```elm
notEqual : WebGL.Settings.DepthTest.Options -> WebGL.Settings.Setting
```

 

# WebGL.Settings.StencilTest

 You can read more about stencil-testing in the
[OpenGL wiki](https://www.khronos.org/opengl/wiki/Stencil_Test)
or [OpenGL docs](https://www.opengl.org/sdk/docs/man2/xhtml/glStencilFunc.xml).


# Stencil Test

@docs test


## Tests

@docs Test, always, equal, never, less, greater, notEqual
@docs lessOrEqual, greaterOrEqual


## Operations

@docs Operation, replace, keep, zero, increment, decrement, invert
@docs incrementWrap, decrementWrap


# Separate Test

@docs testSeparate



## Operation

```elm
-- Opaque type: Operation (constructors not exposed)
```

 Defines how to update the value in the stencil buffer.


## Test

```elm
-- Opaque type: Test (constructors not exposed)
```

 The `Test` allows you to define how to compare the reference value
with the stencil buffer value, in order to set the conditions under which
the pixel will be drawn.

    always         -- Always pass
    equal          -- ref & mask == stencil & mask
    never          -- Never pass
    less           -- ref & mask < stencil & mask
    greater        -- ref & mask > stencil & mask
    notEqual       -- ref & mask != stencil & mask
    lessOrEqual    -- ref & mask <= stencil & mask
    greaterOrEqual -- ref & mask >= stencil & mask



## always

```elm
always : WebGL.Settings.StencilTest.Test
```

 

## decrement

```elm
decrement : WebGL.Settings.StencilTest.Operation
```

 Decrements the current stencil buffer value. Clamps to 0.


## decrementWrap

```elm
decrementWrap : WebGL.Settings.StencilTest.Operation
```

 Decrements the current stencil buffer value.
Wraps stencil buffer value to the maximum representable unsigned
value when decrementing a stencil buffer value of zero.


## equal

```elm
equal : WebGL.Settings.StencilTest.Test
```

 

## greater

```elm
greater : WebGL.Settings.StencilTest.Test
```

 

## greaterOrEqual

```elm
greaterOrEqual : WebGL.Settings.StencilTest.Test
```

 

## increment

```elm
increment : WebGL.Settings.StencilTest.Operation
```

 Increments the current stencil buffer value. Clamps to the maximum
representable unsigned value.


## incrementWrap

```elm
incrementWrap : WebGL.Settings.StencilTest.Operation
```

 Increments the current stencil buffer value. Wraps stencil buffer value to
zero when incrementing the maximum representable unsigned value.


## invert

```elm
invert : WebGL.Settings.StencilTest.Operation
```

 Bitwise inverts the current stencil buffer value.


## keep

```elm
keep : WebGL.Settings.StencilTest.Operation
```

 Keeps the current stencil buffer value. Use this as a noop.


## less

```elm
less : WebGL.Settings.StencilTest.Test
```

 

## lessOrEqual

```elm
lessOrEqual : WebGL.Settings.StencilTest.Test
```

 

## never

```elm
never : WebGL.Settings.StencilTest.Test
```

 

## notEqual

```elm
notEqual : WebGL.Settings.StencilTest.Test
```

 

## replace

```elm
replace : WebGL.Settings.StencilTest.Operation
```

 Sets the stencil buffer value to `ref` from the stencil test.


## test

```elm
test : { ref : Basics.Int, mask : Basics.Int, test : WebGL.Settings.StencilTest.Test, fail : WebGL.Settings.StencilTest.Operation, zfail : WebGL.Settings.StencilTest.Operation, zpass : WebGL.Settings.StencilTest.Operation, writeMask : Basics.Int } -> WebGL.Settings.Setting
```

 When you need to draw an intercection of two entities, e.g. a reflection in
the mirror, you can test against the stencil buffer, that has to be enabled
with [`stencil`](WebGL#stencil) option in [`toHtmlWith`](WebGL#toHtmlWith).

Stencil test decides if the pixel should be drawn on the screen.
Depending on the results, it performs one of the following
[operations](#Operation) on the stencil buffer:

  - `fail`—the operation to use when the stencil test fails;
  - `zfail`—the operation to use when the stencil test passes, but the depth
    test fails;
  - `zpass`—the operation to use when both the stencil test and the depth test
    pass, or when the stencil test passes and there is no depth buffer or depth
    testing is disabled.

For example, draw the mirror `Entity` on the screen and fill the stencil buffer
with all 1's:

    test
        { ref = 1
        , mask = 0xFF
        , test = always    -- pass for each pixel
        , fail = keep      -- noop
        , zfail = keep     -- noop
        , zpass = replace  -- write ref to the stencil buffer
        , writeMask = 0xFF -- enable all stencil bits for writing
        }

Crop the reflection `Entity` using the values from the stencil buffer:

    test
        { ref = 1
        , mask = 0xFF
        , test = equal  -- pass when the stencil value is equal to ref = 1
        , fail = keep   -- noop
        , zfail = keep  -- noop
        , zpass = keep  -- noop
        , writeMask = 0 -- disable writing to the stencil buffer
        }

You can see the complete example
[here](https://github.com/elm-explorations/webgl/blob/master/examples/crate.elm).



## testSeparate

```elm
testSeparate : { ref : Basics.Int, mask : Basics.Int, writeMask : Basics.Int } -> { test : WebGL.Settings.StencilTest.Test, fail : WebGL.Settings.StencilTest.Operation, zfail : WebGL.Settings.StencilTest.Operation, zpass : WebGL.Settings.StencilTest.Operation } -> { test : WebGL.Settings.StencilTest.Test, fail : WebGL.Settings.StencilTest.Operation, zfail : WebGL.Settings.StencilTest.Operation, zpass : WebGL.Settings.StencilTest.Operation } -> WebGL.Settings.Setting
```

 Different options for front and back facing polygons.


## zero

```elm
zero : WebGL.Settings.StencilTest.Operation
```

 Sets the stencil buffer value to 0.


# WebGL.Texture




# Texture

@docs Texture, load, Error, size


# Custom Loading

@docs loadWith, Options, defaultOptions


## Resizing

@docs Resize, linear, nearest
@docs nearestMipmapLinear, nearestMipmapNearest
@docs linearMipmapNearest, linearMipmapLinear
@docs Bigger, Smaller


## Wrapping

@docs Wrap, repeat, clampToEdge, mirroredRepeat


# Things You Shouldn’t Do

@docs nonPowerOfTwoOptions



## Options

```elm
type alias Options =
    { magnify : WebGL.Texture.Resize WebGL.Texture.Bigger, minify : WebGL.Texture.Resize WebGL.Texture.Smaller, horizontalWrap : WebGL.Texture.Wrap, verticalWrap : WebGL.Texture.Wrap, flipY : Basics.Bool }
```

 `Options` describe how to:

  - `magnify` - how to [`Resize`](#Resize) into a bigger texture
  - `minify` - how to [`Resize`](#Resize) into a smaller texture
  - `horizontalWrap` - how to [`Wrap`](#Wrap) the texture horizontally if the width is not a power of two
  - `verticalWrap` - how to [`Wrap`](#Wrap) the texture vertically if the height is not a power of two
  - `flipY` - flip the Y axis of the texture so it has the same direction
    as the clip-space, i.e. pointing up.

You can read more about these parameters in the
[specification](https://www.khronos.org/opengles/sdk/docs/man/xhtml/glTexParameter.xml).



## Bigger

```elm
-- Opaque type: Bigger (constructors not exposed)
```

 Helps restrict `options.magnify` to only allow
[`linear`](#linear) and [`nearest`](#nearest).


## Error

```elm
type Error
    = LoadError
    | SizeError (Basics.Int) (Basics.Int)
```

 Loading a texture can result in two kinds of errors:

  - `LoadError` means the image did not load for some reason. Maybe
    it was a network problem, or maybe it was a bad file format.

  - `SizeError` means you are trying to load a weird shaped image.
    For most operations you want a rectangle where the width is a power
    of two and the height is a power of two. This is more efficient on
    the GPU and it makes mipmapping possible. You can use
    [`nonPowerOfTwoOptions`](#nonPowerOfTwoOptions) to get things working
    now, but it is way better to create power-of-two assets!



## Resize

```elm
-- Opaque type: Resize a (constructors not exposed)
```

 How to resize a texture.


## Smaller

```elm
-- Opaque type: Smaller (constructors not exposed)
```

 Helps restrict `options.magnify`, while also allowing
`options.minify` to use mipmapping resizes, like
[`nearestMipmapNearest`](#nearestMipmapNearest).


## Texture

```elm
-- Opaque type: Texture (constructors not exposed)
```

 Use `Texture` to pass the `sampler2D` uniform value to the shader.
You can create a texture with [`load`](#load) or [`loadWith`](#loadWith)
and measure its dimensions with [`size`](#size).


## Wrap

```elm
-- Opaque type: Wrap (constructors not exposed)
```

 Sets the wrap parameter for texture coordinate.


## clampToEdge

```elm
clampToEdge : WebGL.Texture.Wrap
```

 Causes coordinates to be clamped to the range 1 2N 1 - 1 2N, where N is
the size of the texture in the direction of clamping.


## defaultOptions

```elm
defaultOptions : WebGL.Texture.Options
```

 Default options for the loaded texture.

    { magnify = linear
    , minify = nearestMipmapLinear
    , horizontalWrap = repeat
    , verticalWrap = repeat
    , flipY = True
    }



## linear

```elm
linear : WebGL.Texture.Resize a
```

 Returns the weighted average of the four texture elements that are closest
to the center of the pixel being textured.


## linearMipmapLinear

```elm
linearMipmapLinear : WebGL.Texture.Resize WebGL.Texture.Smaller
```

 Chooses the two mipmaps that most closely match the size of the pixel being
textured and uses the `linear` criterion (a weighted average of the four
texture elements that are closest to the center of the pixel) to produce a
texture value from each mipmap. The final texture value is a weighted average
of those two values.


## linearMipmapNearest

```elm
linearMipmapNearest : WebGL.Texture.Resize WebGL.Texture.Smaller
```

 Chooses the mipmap that most closely matches the size of the pixel being
textured and uses the `linear` criterion (a weighted average of the four
texture elements that are closest to the center of the pixel) to produce a
texture value.


## load

```elm
load : String.String -> Task.Task WebGL.Texture.Error WebGL.Texture.Texture
```

 Loads a texture from the given url with default options.
PNG and JPEG are known to work, but other formats have not been as
well-tested yet.

The Y axis of the texture is flipped automatically for you, so it has
the same direction as in the clip-space, i.e. pointing up.

If you need to change flipping, filtering or wrapping, you can use
[`loadWith`](#loadWith).

    load url =
        loadWith defaultOptions url



## loadWith

```elm
loadWith : WebGL.Texture.Options -> String.String -> Task.Task WebGL.Texture.Error WebGL.Texture.Texture
```

 Same as load, but allows to set options.


## mirroredRepeat

```elm
mirroredRepeat : WebGL.Texture.Wrap
```

 Causes the coordinate c to be set to the fractional part of the texture
coordinate if the integer part is even; if the integer part is odd, then
the coordinate is set to 1 - frac, where frac represents the fractional part
of the coordinate.


## nearest

```elm
nearest : WebGL.Texture.Resize a
```

 Returns the value of the texture element that is nearest
(in Manhattan distance) to the center of the pixel being textured.


## nearestMipmapLinear

```elm
nearestMipmapLinear : WebGL.Texture.Resize WebGL.Texture.Smaller
```

 Chooses the two mipmaps that most closely match the size of the pixel being
textured and uses the `nearest` criterion (the texture element nearest to the
center of the pixel) to produce a texture value from each mipmap. The final
texture value is a weighted average of those two values.


## nearestMipmapNearest

```elm
nearestMipmapNearest : WebGL.Texture.Resize WebGL.Texture.Smaller
```

 Chooses the mipmap that most closely matches the size of the pixel being
textured and uses the `nearest` criterion (the texture element nearest to
the center of the pixel) to produce a texture value.

A mipmap is an ordered set of arrays representing the same image at
progressively lower resolutions.

This is the default value of the minify filter.



## nonPowerOfTwoOptions

```elm
nonPowerOfTwoOptions : WebGL.Texture.Options
```

 The exact options needed to load textures with weird shapes.
If your image width or height is not a power of two, you need these
options:

    { magnify = linear
    , minify = nearest
    , horizontalWrap = clampToEdge
    , verticalWrap = clampToEdge
    , flipY = True
    }



## repeat

```elm
repeat : WebGL.Texture.Wrap
```

 Causes the integer part of the coordinate to be ignored. This is the
default value for both texture axis.


## size

```elm
size : WebGL.Texture.Texture -> ( Basics.Int, Basics.Int )
```

 Return the (width, height) size of a texture. Useful for sprite sheets
or other times you may want to use only a potion of a texture image.

