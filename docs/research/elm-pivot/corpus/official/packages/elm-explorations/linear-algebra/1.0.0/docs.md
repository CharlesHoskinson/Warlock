# official/packages/elm-explorations/linear-algebra/1.0.0/docs.json
Source: https://package.elm-lang.org/packages/elm-explorations/linear-algebra/1.0.0/docs.json

# Math.Matrix4

 A high performance linear algebra library using native JS arrays. Geared
towards 3D graphics and use with `Graphics.WebGL`. All matrices are immutable.

This library uses the convention that the prefix `make` is creating a new
array,as without the prefix, you are applying some transform to an
existing matrix.


# Create

@docs Mat4, identity


# Operations

@docs inverse, inverseOrthonormal, mul, mulAffine, transpose, makeBasis, transform


# Projections

@docs makeFrustum, makePerspective, makeOrtho, makeOrtho2D, makeLookAt


# Apply Transformations

@docs rotate, scale, scale3, translate, translate3


# Create Transformations

@docs makeRotate, makeScale, makeScale3, makeTranslate, makeTranslate3


# Conversions

@docs toRecord, fromRecord



## Mat4

```elm
-- Opaque type: Mat4 (constructors not exposed)
```

 4x4 matrix type


## fromRecord

```elm
fromRecord : { m11 : Basics.Float, m21 : Basics.Float, m31 : Basics.Float, m41 : Basics.Float, m12 : Basics.Float, m22 : Basics.Float, m32 : Basics.Float, m42 : Basics.Float, m13 : Basics.Float, m23 : Basics.Float, m33 : Basics.Float, m43 : Basics.Float, m14 : Basics.Float, m24 : Basics.Float, m34 : Basics.Float, m44 : Basics.Float } -> Math.Matrix4.Mat4
```

 Convert a record to a matrix.


## identity

```elm
identity : Math.Matrix4.Mat4
```

 A matrix with all 0s, except 1s on the diagonal.


## inverse

```elm
inverse : Math.Matrix4.Mat4 -> Maybe.Maybe Math.Matrix4.Mat4
```

 Computes the inverse of any matrix. This is somewhat computationally
intensive. If the matrix is not invertible, `Nothing` is returned.


## inverseOrthonormal

```elm
inverseOrthonormal : Math.Matrix4.Mat4 -> Math.Matrix4.Mat4
```

 Computes the inverse of the given matrix, assuming that the matrix is
orthonormal. This algorithm is more efficient than general matrix inversion, and
has no possibility of failing.


## makeBasis

```elm
makeBasis : Math.Vector3.Vec3 -> Math.Vector3.Vec3 -> Math.Vector3.Vec3 -> Math.Matrix4.Mat4
```

 Creates a transform from a basis consisting of 3 linearly independent vectors.


## makeFrustum

```elm
makeFrustum : Basics.Float -> Basics.Float -> Basics.Float -> Basics.Float -> Basics.Float -> Basics.Float -> Math.Matrix4.Mat4
```

 Creates a matrix for a projection frustum with the given parameters.

Parameters:

  - left - the left coordinate of the frustum
  - right- the right coordinate of the frustum
  - bottom - the bottom coordinate of the frustum
  - top - the top coordinate of the frustum
  - znear - the near z distance of the frustum
  - zfar - the far z distance of the frustum



## makeLookAt

```elm
makeLookAt : Math.Vector3.Vec3 -> Math.Vector3.Vec3 -> Math.Vector3.Vec3 -> Math.Matrix4.Mat4
```

 Creates a transformation matrix for a camera.

Parameters:

  - eye - The location of the camera
  - center - The location of the focused object
  - up - The "up" direction according to the camera



## makeOrtho

```elm
makeOrtho : Basics.Float -> Basics.Float -> Basics.Float -> Basics.Float -> Basics.Float -> Basics.Float -> Math.Matrix4.Mat4
```

 Creates a matrix for an orthogonal frustum projection with the given parameters.

Parameters:

  - left - the left coordinate of the frustum
  - right- the right coordinate of the frustum
  - bottom - the bottom coordinate of the frustum
  - top - the top coordinate of the frustum
  - znear - the near z distance of the frustum
  - zfar - the far z distance of the frustum



## makeOrtho2D

```elm
makeOrtho2D : Basics.Float -> Basics.Float -> Basics.Float -> Basics.Float -> Math.Matrix4.Mat4
```

 Creates a matrix for a 2D orthogonal frustum projection with the given
parameters. `znear` and `zfar` are assumed to be -1 and 1, respectively.

Parameters:

  - left - the left coordinate of the frustum
  - right- the right coordinate of the frustum
  - bottom - the bottom coordinate of the frustum
  - top - the top coordinate of the frustum



## makePerspective

```elm
makePerspective : Basics.Float -> Basics.Float -> Basics.Float -> Basics.Float -> Math.Matrix4.Mat4
```

 Creates a matrix for a perspective projection with the given parameters.

Parameters:

  - fovy - field of view in the y axis, in degrees
  - aspect - aspect ratio
  - znear - the near z distance of the projection
  - zfar - the far z distance of the projection



## makeRotate

```elm
makeRotate : Basics.Float -> Math.Vector3.Vec3 -> Math.Matrix4.Mat4
```

 Creates a transformation matrix for rotation in radians about the
3-element vector axis.


## makeScale

```elm
makeScale : Math.Vector3.Vec3 -> Math.Matrix4.Mat4
```

 Creates a transformation matrix for scaling each of the x, y, and z axes by
the amount given in the corresponding element of the 3-element vector.


## makeScale3

```elm
makeScale3 : Basics.Float -> Basics.Float -> Basics.Float -> Math.Matrix4.Mat4
```

 Creates a transformation matrix for scaling by 3 scalar values, one for
each of the x, y, and z directions.


## makeTranslate

```elm
makeTranslate : Math.Vector3.Vec3 -> Math.Matrix4.Mat4
```

 Creates a transformation matrix for translating each of the x, y, and z
axes by the amount given in the corresponding element of the 3-element vector.


## makeTranslate3

```elm
makeTranslate3 : Basics.Float -> Basics.Float -> Basics.Float -> Math.Matrix4.Mat4
```

 Creates a transformation matrix for translating by 3 scalar values, one for
each of the x, y, and z directions.


## mul

```elm
mul : Math.Matrix4.Mat4 -> Math.Matrix4.Mat4 -> Math.Matrix4.Mat4
```

 Matrix multiplcation: a * b


## mulAffine

```elm
mulAffine : Math.Matrix4.Mat4 -> Math.Matrix4.Mat4 -> Math.Matrix4.Mat4
```

 Matrix multiplication, assuming a and b are affine: a * b


## rotate

```elm
rotate : Basics.Float -> Math.Vector3.Vec3 -> Math.Matrix4.Mat4 -> Math.Matrix4.Mat4
```

 Concatenates a rotation in radians about an axis to the given matrix.


## scale

```elm
scale : Math.Vector3.Vec3 -> Math.Matrix4.Mat4 -> Math.Matrix4.Mat4
```

 Concatenates a scaling to the given matrix.


## scale3

```elm
scale3 : Basics.Float -> Basics.Float -> Basics.Float -> Math.Matrix4.Mat4 -> Math.Matrix4.Mat4
```

 Concatenates a scaling to the given matrix.


## toRecord

```elm
toRecord : Math.Matrix4.Mat4 -> { m11 : Basics.Float, m21 : Basics.Float, m31 : Basics.Float, m41 : Basics.Float, m12 : Basics.Float, m22 : Basics.Float, m32 : Basics.Float, m42 : Basics.Float, m13 : Basics.Float, m23 : Basics.Float, m33 : Basics.Float, m43 : Basics.Float, m14 : Basics.Float, m24 : Basics.Float, m34 : Basics.Float, m44 : Basics.Float }
```

 Convert a matrix to a record.


## transform

```elm
transform : Math.Matrix4.Mat4 -> Math.Vector3.Vec3 -> Math.Vector3.Vec3
```

 Multiply a vector by a 4x4 matrix: m * v


## translate

```elm
translate : Math.Vector3.Vec3 -> Math.Matrix4.Mat4 -> Math.Matrix4.Mat4
```

 Concatenates a translation to the given matrix.


## translate3

```elm
translate3 : Basics.Float -> Basics.Float -> Basics.Float -> Math.Matrix4.Mat4 -> Math.Matrix4.Mat4
```

 Concatenates a translation to the given matrix.


## transpose

```elm
transpose : Math.Matrix4.Mat4 -> Math.Matrix4.Mat4
```

 "Flip" the matrix across the diagonal by swapping row index and column
index.


# Math.Vector2

 A high performance linear algebra library using native JS arrays. Geared
towards 3D graphics and use with `Graphics.WebGL`. All vectors are immutable.


# Create

@docs Vec2, vec2


# Get and Set

The set functions create a new copy of the vector, updating a single field.

@docs getX, getY, setX, setY


# Operations

@docs add, sub, negate, scale, dot, normalize, direction
@docs length, lengthSquared, distance, distanceSquared


# Conversions

@docs toRecord, fromRecord



## Vec2

```elm
-- Opaque type: Vec2 (constructors not exposed)
```

 Two dimensional vector type


## add

```elm
add : Math.Vector2.Vec2 -> Math.Vector2.Vec2 -> Math.Vector2.Vec2
```

 Vector addition: a + b


## direction

```elm
direction : Math.Vector2.Vec2 -> Math.Vector2.Vec2 -> Math.Vector2.Vec2
```

 The normalized direction from b to a: (a - b) / |a - b|


## distance

```elm
distance : Math.Vector2.Vec2 -> Math.Vector2.Vec2 -> Basics.Float
```

 The distance between two vectors.


## distanceSquared

```elm
distanceSquared : Math.Vector2.Vec2 -> Math.Vector2.Vec2 -> Basics.Float
```

 The square of the distance between two vectors.


## dot

```elm
dot : Math.Vector2.Vec2 -> Math.Vector2.Vec2 -> Basics.Float
```

 The dot product of a and b


## fromRecord

```elm
fromRecord : { x : Basics.Float, y : Basics.Float } -> Math.Vector2.Vec2
```

 Convert a record to a vector.


## getX

```elm
getX : Math.Vector2.Vec2 -> Basics.Float
```

 Extract the x component of a vector.


## getY

```elm
getY : Math.Vector2.Vec2 -> Basics.Float
```

 Extract the y component of a vector.


## length

```elm
length : Math.Vector2.Vec2 -> Basics.Float
```

 The length of the given vector: |a|


## lengthSquared

```elm
lengthSquared : Math.Vector2.Vec2 -> Basics.Float
```

 The square of the length of the given vector: |a| * |a|


## negate

```elm
negate : Math.Vector2.Vec2 -> Math.Vector2.Vec2
```

 Vector negation: -a


## normalize

```elm
normalize : Math.Vector2.Vec2 -> Math.Vector2.Vec2
```

 A unit vector with the same direction as the given vector: a / |a|


## scale

```elm
scale : Basics.Float -> Math.Vector2.Vec2 -> Math.Vector2.Vec2
```

 Multiply the vector by a scalar: s * v


## setX

```elm
setX : Basics.Float -> Math.Vector2.Vec2 -> Math.Vector2.Vec2
```

 Update the x component of a vector, returning a new vector.


## setY

```elm
setY : Basics.Float -> Math.Vector2.Vec2 -> Math.Vector2.Vec2
```

 Update the y component of a vector, returning a new vector.


## sub

```elm
sub : Math.Vector2.Vec2 -> Math.Vector2.Vec2 -> Math.Vector2.Vec2
```

 Vector subtraction: a - b


## toRecord

```elm
toRecord : Math.Vector2.Vec2 -> { x : Basics.Float, y : Basics.Float }
```

 Convert a vector to a record.


## vec2

```elm
vec2 : Basics.Float -> Basics.Float -> Math.Vector2.Vec2
```

 Creates a new 2-element vector with the given values.


# Math.Vector3

 A high performance linear algebra library using native JS arrays. Geared
towards 3D graphics and use with `Graphics.WebGL`. All vectors are immutable.


# Create

@docs Vec3, vec3, i, j, k


# Get and Set

The set functions create a new copy of the vector, updating a single field.

@docs getX, getY, getZ, setX, setY, setZ


# Operations

@docs add, sub, negate, scale, dot, cross, normalize, direction
@docs length, lengthSquared, distance, distanceSquared


# Conversions

@docs toRecord, fromRecord



## Vec3

```elm
-- Opaque type: Vec3 (constructors not exposed)
```

 Three dimensional vector type


## add

```elm
add : Math.Vector3.Vec3 -> Math.Vector3.Vec3 -> Math.Vector3.Vec3
```

 Vector addition: a + b


## cross

```elm
cross : Math.Vector3.Vec3 -> Math.Vector3.Vec3 -> Math.Vector3.Vec3
```

 The cross product of a and b


## direction

```elm
direction : Math.Vector3.Vec3 -> Math.Vector3.Vec3 -> Math.Vector3.Vec3
```

 The normalized direction from b to a: (a - b) / |a - b|


## distance

```elm
distance : Math.Vector3.Vec3 -> Math.Vector3.Vec3 -> Basics.Float
```

 The distance between two vectors.


## distanceSquared

```elm
distanceSquared : Math.Vector3.Vec3 -> Math.Vector3.Vec3 -> Basics.Float
```

 The square of the distance between two vectors.


## dot

```elm
dot : Math.Vector3.Vec3 -> Math.Vector3.Vec3 -> Basics.Float
```

 The dot product of a and b


## fromRecord

```elm
fromRecord : { x : Basics.Float, y : Basics.Float, z : Basics.Float } -> Math.Vector3.Vec3
```

 Convert a record to a vector.


## getX

```elm
getX : Math.Vector3.Vec3 -> Basics.Float
```

 Extract the x component of a vector.


## getY

```elm
getY : Math.Vector3.Vec3 -> Basics.Float
```

 Extract the y component of a vector.


## getZ

```elm
getZ : Math.Vector3.Vec3 -> Basics.Float
```

 Extract the z component of a vector.


## i

```elm
i : Math.Vector3.Vec3
```

 The unit vector &icirc; which points in the x direction: `vec3 1 0 0`


## j

```elm
j : Math.Vector3.Vec3
```

 The unit vector &jcirc; which points in the y direction: `vec3 0 1 0`


## k

```elm
k : Math.Vector3.Vec3
```

 The unit vector k&#0770; which points in the z direction: `vec3 0 0 1`


## length

```elm
length : Math.Vector3.Vec3 -> Basics.Float
```

 The length of the given vector: |a|


## lengthSquared

```elm
lengthSquared : Math.Vector3.Vec3 -> Basics.Float
```

 The square of the length of the given vector: |a| * |a|


## negate

```elm
negate : Math.Vector3.Vec3 -> Math.Vector3.Vec3
```

 Vector negation: -a


## normalize

```elm
normalize : Math.Vector3.Vec3 -> Math.Vector3.Vec3
```

 A unit vector with the same direction as the given vector: a / |a|


## scale

```elm
scale : Basics.Float -> Math.Vector3.Vec3 -> Math.Vector3.Vec3
```

 Multiply the vector by a scalar: s * v


## setX

```elm
setX : Basics.Float -> Math.Vector3.Vec3 -> Math.Vector3.Vec3
```

 Update the x component of a vector, returning a new vector.


## setY

```elm
setY : Basics.Float -> Math.Vector3.Vec3 -> Math.Vector3.Vec3
```

 Update the y component of a vector, returning a new vector.


## setZ

```elm
setZ : Basics.Float -> Math.Vector3.Vec3 -> Math.Vector3.Vec3
```

 Update the z component of a vector, returning a new vector.


## sub

```elm
sub : Math.Vector3.Vec3 -> Math.Vector3.Vec3 -> Math.Vector3.Vec3
```

 Vector subtraction: a - b


## toRecord

```elm
toRecord : Math.Vector3.Vec3 -> { x : Basics.Float, y : Basics.Float, z : Basics.Float }
```

 Convert a vector to a record.


## vec3

```elm
vec3 : Basics.Float -> Basics.Float -> Basics.Float -> Math.Vector3.Vec3
```

 Creates a new 3-element vector with the given values.


# Math.Vector4

 A high performance linear algebra library using native JS arrays. Geared
towards 3D graphics and use with `Graphics.WebGL`. All vectors are immutable.


# Create

@docs Vec4, vec4


# Get and Set

The set functions create a new copy of the vector, updating a single field.

@docs getX, getY, getZ, getW, setX, setY, setZ, setW


# Operations

@docs add, sub, negate, scale, dot, normalize, direction
@docs length, lengthSquared, distance, distanceSquared


# Conversions

@docs toRecord, fromRecord



## Vec4

```elm
-- Opaque type: Vec4 (constructors not exposed)
```

 Four dimensional vector type


## add

```elm
add : Math.Vector4.Vec4 -> Math.Vector4.Vec4 -> Math.Vector4.Vec4
```

 Vector addition: a + b


## direction

```elm
direction : Math.Vector4.Vec4 -> Math.Vector4.Vec4 -> Math.Vector4.Vec4
```

 The normalized direction from b to a: (a - b) / |a - b|


## distance

```elm
distance : Math.Vector4.Vec4 -> Math.Vector4.Vec4 -> Basics.Float
```

 The distance between two vectors.


## distanceSquared

```elm
distanceSquared : Math.Vector4.Vec4 -> Math.Vector4.Vec4 -> Basics.Float
```

 The square of the distance between two vectors.


## dot

```elm
dot : Math.Vector4.Vec4 -> Math.Vector4.Vec4 -> Basics.Float
```

 The dot product of a and b


## fromRecord

```elm
fromRecord : { x : Basics.Float, y : Basics.Float, z : Basics.Float, w : Basics.Float } -> Math.Vector4.Vec4
```

 Convert a record to a vector.


## getW

```elm
getW : Math.Vector4.Vec4 -> Basics.Float
```

 Extract the w component of a vector.


## getX

```elm
getX : Math.Vector4.Vec4 -> Basics.Float
```

 Extract the x component of a vector.


## getY

```elm
getY : Math.Vector4.Vec4 -> Basics.Float
```

 Extract the y component of a vector.


## getZ

```elm
getZ : Math.Vector4.Vec4 -> Basics.Float
```

 Extract the z component of a vector.


## length

```elm
length : Math.Vector4.Vec4 -> Basics.Float
```

 The length of the given vector: |a|


## lengthSquared

```elm
lengthSquared : Math.Vector4.Vec4 -> Basics.Float
```

 The square of the length of the given vector: |a| * |a|


## negate

```elm
negate : Math.Vector4.Vec4 -> Math.Vector4.Vec4
```

 Vector negation: -a


## normalize

```elm
normalize : Math.Vector4.Vec4 -> Math.Vector4.Vec4
```

 A unit vector with the same direction as the given vector: a / |a|


## scale

```elm
scale : Basics.Float -> Math.Vector4.Vec4 -> Math.Vector4.Vec4
```

 Multiply the vector by a scalar: s * v


## setW

```elm
setW : Basics.Float -> Math.Vector4.Vec4 -> Math.Vector4.Vec4
```

 Update the w component of a vector, returning a new vector.


## setX

```elm
setX : Basics.Float -> Math.Vector4.Vec4 -> Math.Vector4.Vec4
```

 Update the x component of a vector, returning a new vector.


## setY

```elm
setY : Basics.Float -> Math.Vector4.Vec4 -> Math.Vector4.Vec4
```

 Update the y component of a vector, returning a new vector.


## setZ

```elm
setZ : Basics.Float -> Math.Vector4.Vec4 -> Math.Vector4.Vec4
```

 Update the z component of a vector, returning a new vector.


## sub

```elm
sub : Math.Vector4.Vec4 -> Math.Vector4.Vec4 -> Math.Vector4.Vec4
```

 Vector subtraction: a - b


## toRecord

```elm
toRecord : Math.Vector4.Vec4 -> { x : Basics.Float, y : Basics.Float, z : Basics.Float, w : Basics.Float }
```

 Convert a vector to a record.


## vec4

```elm
vec4 : Basics.Float -> Basics.Float -> Basics.Float -> Basics.Float -> Math.Vector4.Vec4
```

 Creates a new 4-element vector with the given x, y, z, and w values.

