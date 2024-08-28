import numpy as np
from . import _beziercurve
import random

OFFSET_X = 100
OFFSET_Y = 100

def generate_curve(x: int, y: int, current_points: tuple[int, int]) -> list[tuple[float, float]]:
    """Generates a random bezier curve path from the current position to a target (x, y) location.

    The path is generated using random control points within a defined offset range around
    the start and target coordinates. It includes optional distortion and easing to smooth the curve.

    ### Parameters:
    - `x` (int): The x-coordinate of the target location.
    - `y` (int): The y-coordinate of the target location.
    - `current_points` (tuple[int, int]): The current (x, y) coordinates of the starting location.

    ### Returns:
    - `list[tuple[float, float]]`: A list of (x, y) points representing the generated bezier curve path.

    ### Notes:
    - The generated curve path is influenced by a random set of control points, which can lead to 
      varying curve shapes on each call.
    - The curve also applies an optional distortion to each mid-point for added randomness.

    ### Examples:
    ```py
    # Generate a curve from current position (400, 300) to target position (800, 600)
    current_pos = (400, 300)
    target_x, target_y = 800, 600
    path = generate_curve(target_x, target_y, current_pos)
    ```
    """
    
    current_x, current_y = current_points

    left_limit = min(current_x, x) - OFFSET_X
    right_limit = max(current_x, x) + OFFSET_X
    down_limit = min(current_y, y) - OFFSET_Y
    up_limit = max(current_y, y) + OFFSET_Y

    def generate_knots(left_limit: int, right_limit: int, down_limit: int, up_limit: int) -> list[tuple[int, int]]:
        """Generates two random control points (knots) within the given limits."""
        knotsX = np.random.choice(range(left_limit, right_limit), size=2)
        knotsY = np.random.choice(range(down_limit, up_limit), size=2)
        return list(zip(knotsX, knotsY))

    def generate_points(knots: list[tuple[int, int]], current_coords: tuple[int, int], target_coords: tuple[int, int]) -> list[tuple[float, float]]:
        """Generates the bezier curve points from the control points."""
        mid_points_count = max(
            abs(current_coords[0] - target_coords[0]),
            abs(current_coords[1] - target_coords[1]),
            2)
        knots = [current_coords] + knots + [target_coords]
        return _beziercurve.curvePoints(mid_points_count, knots)

    def distort_points(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Applies random distortion to the mid-points of the curve."""
        distorted = []
        for i in range(1, len(points)-1):
            x, y = points[i]
            delta = np.random.normal(0, 1) if random.random() < 0.5 else 0
            distorted.append((x, y + delta))
        distorted = [points[0]] + distorted + [points[-1]]
        return distorted

    def tween_points(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Smooths the curve by applying easing to the points."""
        res = []
        for i in range(100):
            index = int(_beziercurve.easeOutQuad(float(i) / (100 - 1)) * (len(points) - 1))
            res.append(points[index])
        return res
    
    knots = generate_knots(left_limit, right_limit, down_limit, up_limit)
    points = generate_points(knots, current_points, (x, y))
    points = distort_points(points)
    points = tween_points(points)

    return points
