import math

def curvePoints(n: int, points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Generates n points along a bezier curve defined by the given control points.

    Uses the Bernstein polynomial to calculate points on the curve.

    ### Parameters:
    - `n` (int): The number of points to generate along the curve.
    - `points` (list[tuple[float, float]]): A list of control points (x, y) defining the bezier curve.

    ### Returns:
    - `list[tuple[float, float]]`: A list of (x, y) points along the bezier curve.

    ### Examples:
    ```py
    # Define control points
    control_points = [(0, 0), (1, 2), (3, 3)]
    # Generate 50 points along the bezier curve defined by these control points
    bezier_curve = curvePoints(50, control_points)
    ```
    """
    
    def binomial(n: int, k: int) -> float:
        """Calculates the binomial coefficient 'n choose k'."""
        return math.factorial(n) / float(math.factorial(k) * math.factorial(n - k))
    
    def bernsteinPolynomialPoint(x: float, i: int, n: int) -> float:
        """Calculates a point on the Bernstein polynomial for a given index and order."""
        return binomial(n, i) * (x ** i) * ((1 - x) ** (n - i))

    def bernsteinPolynomial(points: list[tuple[float, float]]):
        """Generates a Bernstein polynomial function based on the given control points."""
        def bern(t: float) -> tuple[float, float]:
            n = len(points) - 1  # Degree of the polynomial
            x = y = 0  # Initialize curve point coordinates
            for i, point in enumerate(points):
                bern = bernsteinPolynomialPoint(t, i, n)  # Calculate Bernstein coefficient
                x += point[0] * bern
                y += point[1] * bern
            return x, y
        return bern

    curvePoints = []
    bernstein_polynomial = bernsteinPolynomial(points)  # Create the polynomial function from control points

    for i in range(n):
        t = i / (n - 1)  # Parameter t ranges from 0 to 1
        curvePoints.append(bernstein_polynomial(t))  # Calculate the curve point for this t
    return curvePoints

def find_duration(x: int, y: int, current_points, MOVE_SPEED: int) -> float:
    """Calculates the duration required to move the mouse to a given (x, y) coordinate
    based on the current position and a specified move speed.

    This function ensures a minimum duration of 0.15 seconds to avoid
    overly fast mouse movements that may not be human-like.

    ### Parameters:
    - `x`: The target x-coordinate.
    - `y`: The target y-coordinate.
    - `MOVE_SPEED`: The speed at which the mouse should move.

    ### Returns:
    - The calculated duration for the mouse movement.
    """
    current_x, current_y = current_points
    return max(0.15, math.sqrt((x - current_x) ** 2 + (y - current_y) ** 2) / MOVE_SPEED)
