from pathlib import Path

import numpy as np

from vis3d.io.image_stack import ImageStack
from vis3d.visualization.volume_render import build_grid


def test_grid_dimensions_are_x_y_z_and_values_match_the_stack() -> None:
    values = np.arange(2 * 3 * 4, dtype=np.uint16).reshape(2, 3, 4)
    stack = ImageStack(values=values, source_files=(Path("volume.TIF"),))

    grid = build_grid(stack)

    assert grid.dimensions == (4, 3, 2)
    np.testing.assert_array_equal(grid.point_data["intensity"], values.flatten(order="C"))
