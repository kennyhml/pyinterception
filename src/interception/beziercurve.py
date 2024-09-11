from dataclasses import dataclass
from typing import Callable, Optional
from . import exceptions

try:
    from pyclick.humancurve import HumanCurve  # type: ignore[import]
except ImportError:

    class HumanCurve:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:
            # If pyclick isnt installed this dummy class will be initialized instead,
            # so just use that to throw the exception.
            raise exceptions.PyClickNotInstalled


@dataclass
class BezierCurveParams:

    knots: int = 2
    distortion_mean: int = 1
    distortion_stdev: int = 1
    distortion_frequency: float = 0.5
    tween: Optional[Callable[[None], None]] = None
    target_points: int = 100


_g_params: Optional[BezierCurveParams] = None


def set_default_params(params: BezierCurveParams) -> None:
    global _g_params
    _g_params = params


def get_default_params() -> Optional[BezierCurveParams]:
    return _g_params
