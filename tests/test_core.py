import math
import unittest

from plane_line_intersection import intersect, PlaneLineIntersection, IntersectionResult
from plane_line_intersection.core import Config, get_startup_log, clear_startup_log


class TestPointIntersection(unittest.TestCase):

    def setUp(self):
        Config.reset()
        clear_startup_log()

    def test_basic_intersection(self):
        # Plane: x=2 (normal=(1,0,0), offset=2)
        # Line: origin=(0,0,0), direction=(1,0,0) -> x=t; t=2 gives (2,0,0)
        result = intersect(1, 0, 0, 2, 0, 0, 0, 1, 0, 0)
        self.assertEqual(result.kind, "point")
        self.assertAlmostEqual(result.t, 2.0)
        self.assertAlmostEqual(result.point[0], 2.0)
        self.assertAlmostEqual(result.point[1], 0.0)
        self.assertAlmostEqual(result.point[2], 0.0)

    def test_diagonal_intersection(self):
        # Plane: x+y+z=3, normal=(1,1,1), offset=3
        # Line: origin=(0,0,0), direction=(1,1,1)
        # t*3 = 3 -> t=1, point=(1,1,1)
        result = intersect(1, 1, 1, 3, 0, 0, 0, 1, 1, 1)
        self.assertEqual(result.kind, "point")
        self.assertAlmostEqual(result.t, 1.0)
        self.assertAlmostEqual(result.point[0], 1.0)
        self.assertAlmostEqual(result.point[1], 1.0)
        self.assertAlmostEqual(result.point[2], 1.0)

    def test_negative_t(self):
        # Line from (5,0,0) heading in -x direction, plane x=2
        # t = (2 - 5)/(-1) = 3, point=(2,0,0)
        result = intersect(1, 0, 0, 2, 5, 0, 0, -1, 0, 0)
        self.assertEqual(result.kind, "point")
        self.assertAlmostEqual(result.t, 3.0)

    def test_arbitrary_origin(self):
        # Plane: 2x + 3y + z = 10
        # Line: origin=(1,1,1), direction=(2,1,0)
        # denom = 2*2 + 3*1 + 1*0 = 7
        # numerator = 10 - 2 - 3 - 1 = 4
        # t = 4/7
        result = intersect(2, 3, 1, 10, 1, 1, 1, 2, 1, 0)
        self.assertEqual(result.kind, "point")
        self.assertAlmostEqual(result.t, 4.0 / 7.0)
        self.assertAlmostEqual(result.point[0], 1.0 + 2.0 * 4.0 / 7.0)

    def test_zero_t(self):
        # Line starts on the plane with nonzero direction component
        result = intersect(1, 0, 0, 5, 5, 0, 0, 1, 0, 0)
        self.assertEqual(result.kind, "point")
        self.assertAlmostEqual(result.t, 0.0)


class TestParallelNoHit(unittest.TestCase):

    def setUp(self):
        Config.reset()
        clear_startup_log()

    def test_parallel_no_hit(self):
        # Plane x=5, line at x=0 moving in y direction
        result = intersect(1, 0, 0, 5, 0, 0, 0, 0, 1, 0)
        self.assertEqual(result.kind, "no_hit")
        self.assertIsNone(result.point)

    def test_parallel_logs_error(self):
        clear_startup_log()
        intersect(1, 0, 0, 5, 0, 0, 0, 0, 1, 0)
        log = get_startup_log()
        self.assertEqual(len(log), 1)
        self.assertIn("no_hit", log[0])


class TestCoincident(unittest.TestCase):

    def setUp(self):
        Config.reset()
        clear_startup_log()

    def test_line_on_plane(self):
        # Plane x=5, line at x=5 moving in y direction
        result = intersect(1, 0, 0, 5, 5, 0, 0, 0, 1, 0)
        self.assertEqual(result.kind, "coincident")


class TestConfigRaiseOnError(unittest.TestCase):

    def setUp(self):
        Config.reset()
        clear_startup_log()

    def test_raises_when_configured(self):
        Config.configure(raise_on_error=True)
        with self.assertRaises(ValueError):
            intersect(1, 0, 0, 5, 0, 0, 0, 0, 1, 0)

    def test_no_raise_by_default(self):
        result = intersect(1, 0, 0, 5, 0, 0, 0, 0, 1, 0)
        self.assertEqual(result.kind, "no_hit")


class TestPersistentClass(unittest.TestCase):

    def setUp(self):
        Config.reset()
        clear_startup_log()

    def test_persistent_intersection(self):
        pli = PlaneLineIntersection(1, 0, 0, 2)
        result = pli.intersect(0, 0, 0, 1, 0, 0)
        self.assertEqual(result.kind, "point")
        self.assertAlmostEqual(result.t, 2.0)

    def test_persistent_parallel(self):
        pli = PlaneLineIntersection(1, 0, 0, 2)
        result = pli.intersect(0, 0, 0, 0, 1, 0)
        self.assertEqual(result.kind, "no_hit")


if __name__ == "__main__":
    unittest.main()
