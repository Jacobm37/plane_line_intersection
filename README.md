# plane_line_intersection

Computes the intersection point of a parametric line with an implicit plane in 3D space.

## Usage

```python
from plane_line_intersection import intersect, PlaneLineIntersection

# Functional form: plane a*x + b*y + c*z = d, line (x0,y0,z0) + t*(u,v,w)
result = intersect(1, 0, 0, 2, 0, 0, 0, 1, 0, 0)
print(result.kind)   # "point"
print(result.point)  # (2.0, 0.0, 0.0)
print(result.t)      # 2.0

# Persistent form: reuse one plane across many lines
pli = PlaneLineIntersection(1, 0, 0, 2)
r = pli.intersect(0, 0, 0, 1, 0, 0)
```

The exported names are `intersect`, `PlaneLineIntersection`, and `IntersectionResult`.

## Why this exists

A common need in graphics, collision, and geometry code is testing where a ray or line segment meets a plane. The arithmetic is short, but the edge cases (parallel line, line lying in the plane) are easy to get wrong if inlined. This library isolates that logic and returns a structured result so callers can branch on outcome without re-deriving the math.

The trade-off: results are returned as objects rather than raised exceptions. A `no_hit` (parallel, not in plane) is a normal geometric outcome, not a programming error. An in-memory log captures these for diagnostics. If you prefer exceptions, set `Config.configure(raise_on_error=True)`.

## Edge cases

- **Parallel, not in plane**: returns `kind="no_hit"`. No exception by default.
- **Line lies in plane**: returns `kind="coincident"` with no point (the intersection is the entire line).
- **Floating-point near-parallelism**: uses a relative tolerance (`1e-9`) so near-parallel lines are treated as parallel rather than producing wildly unstable points.

No third-party dependencies. Standard library only.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

