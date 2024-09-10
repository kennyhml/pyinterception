from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class BezierCurveParams:

    knots: int = 2
    distortion_mean: int = 1
    distortion_stdev: int = 1
    distortion_frequency: float = 0.5
    tween: Optional[Callable[[None], None]] = None
    target_points: int = 100
