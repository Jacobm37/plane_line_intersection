"""Compute the intersection of a parametric line with an implicit plane."""


_STARTUP_LOG = []  # In-memory log persists for the life of the application only


class Config:
    """Global configuration for error handling.

    Setting raise_on_error to True causes explicit exceptions to be raised
    instead of returning error values, which can simplify flows in CLI tools
    or scripts that want to abort on the first problem.
    """
    raise_on_error = False

    @classmethod
    def configure(cls, raise_on_error: bool = False):
        cls.raise_on_error = raise_on_error

    @classmethod
    def reset(cls):
        cls.raise_on_error = False


class PlaneLineIntersection:
    """Persistent plane-line intersection evaluator.

    A helper that persists the plane definition and is called with
    different lines repeatedly. For example, a ray-marching routine may
    test many different lines against the same scene geometry.
    """

    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def intersect(self, x0, y0, z0, u, v, w):
        return _intersect_impl(self.a, self.b, self.c, self.d,
                                x0, y0, z0, u, v, w)


class IntersectionResult:
    """Result of a plane-line intersection.

    A small class is used instead of a plain dict so that callers can
    check the type of a result (e.g., point vs. coincident vs. no_hit)
    and access fields in a tab-completion-friendly way.
    """

    __slots__ = ("kind", "point", "t", "message")

    def __init__(self, kind, point=None, t=None, message=None):
        self.kind = kind
        self.point = point
        self.t = t
        self.message = message

    def __repr__(self):
        return f"IntersectionResult(kind={self.kind!r}, point={self.point!r}, t={self.t!r})"

    def __eq__(self, other):
        if isinstance(other, IntersectionResult):
            return (
                self.kind == other.kind
                and self.point == other.point
                and self.t == other.t
            )
        return NotImplemented


def _make_error(kind, message):
    """Create an error result or raise an exception, depending on config.

    The application may be configured to raise explicit exceptions for
    errors (e.g., in CLI tools that should abort on the first error) or
    to return error values (the default, which is convenient for
    interactive exploration).
    """
    if Config.raise_on_error:
        raise ValueError(f"{kind}: {message}")
    _STARTUP_LOG.append((kind, message))
    return IntersectionResult(kind=kind, message=message)


def _nearly_equal(a, b):
    """Relative and absolute tolerance comparison.

    Absolute tolerance handles numbers close to zero where the relative
    error can be misleading.  Relative tolerance catches errors that scale
    with the magnitude of the numbers.
    """
    abs_tol = 1e-10
    rel_tol = 1e-9
    return abs(a - b) <= max(abs_tol, rel_tol * max(abs(a), abs(b)))


def _intersect_impl(a, b, c, d, x0, y0, z0, u, v, w):
    denom = a * u + b * v + c * w

    if _nearly_equal(denom, 0.0):
        line_const = a * x0 + b * y0 + c * z0
        if _nearly_equal(line_const, d):
            return IntersectionResult(kind="coincident")
        return _make_error("no_hit", "Line does not intersect plane")

    t = (d - a * x0 - b * y0 - c * z0) / denom
    px = x0 + u * t
    py = y0 + v * t
    pz = z0 + w * t

    return IntersectionResult(kind="point", point=(px, py, pz), t=t)


def intersect(a, b, c, d, x0, y0, z0, u, v, w):
    """Compute the intersection of a line with a plane.

    The plane is defined by the implicit equation

        a*x + b*y + c*z = d

    and the line is defined by the parametric equations

        x = x0 + u * t
        y = y0 + v * t
        z = z0 + w * t

    Args:
        a, b, c: Plane normal coefficients.
        d: Plane offset.
        x0, y0, z0: Line origin.
        u, v, w: Line direction.

    Returns:
        IntersectionResult: A result object with a ``kind`` field of
        ``"point"``, ``"coincident"``, or ``"no_hit"``.  For ``"point"``,
        the ``point`` field is a tuple ``(x, y, z)`` and the ``t`` field is
        the parametric value.  For ``"no_hit"`` errors, an error is
        logged in memory and may be retrieved via :func:`get_startup_log`.
    """
    return _intersect_impl(a, b, c, d, x0, y0, z0, u, v, w)


def get_startup_log():
    """Return the in-memory error log.

    The log is a list of ``(kind, message)`` tuples.  It is not persistent
    across application restarts.
    """
    return list(_STARTUP_LOG)


def clear_startup_log():
    """Clear the in-memory error log."""
    _STARTUP_LOG.clear()
