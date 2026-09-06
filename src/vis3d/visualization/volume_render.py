"""Step 2: render an image stack as a 3D volume with PyVista."""

from __future__ import annotations

import logging

import numpy as np
import pyvista

from vis3d.config import RenderConfig
from vis3d.errors import RenderError
from vis3d.io.image_stack import ImageStack

logger = logging.getLogger(__name__)


def render_volume(stack: ImageStack, settings: RenderConfig) -> None:
    """Show the stack as a 3D volume and, if configured, save a screenshot."""
    grid = build_grid(stack)
    value_range = settings.value_range or (float(stack.values.min()), float(stack.values.max()))
    logger.info("Rendering volume with intensity range %s", value_range)

    plotter = pyvista.Plotter(
        off_screen=settings.off_screen,
        window_size=list(settings.window_size),
    )
    plotter.show_axes()
    plotter.add_volume(
        grid,
        cmap=settings.colormap,
        opacity=settings.opacity,
        clim=list(value_range),
    )
    plotter.camera_position = settings.camera_position

    screenshot = str(settings.screenshot) if settings.screenshot else None
    if settings.screenshot:
        settings.screenshot.parent.mkdir(parents=True, exist_ok=True)

    try:
        plotter.show(screenshot=screenshot)
    except (RuntimeError, ValueError) as error:
        raise RenderError(f"Rendering failed: {error}") from error
    finally:
        plotter.close()

    if settings.screenshot:
        logger.info("Screenshot written to %s", settings.screenshot)


def build_grid(stack: ImageStack) -> pyvista.ImageData:
    """Wrap the (z, y, x) array in a VTK uniform grid, whose dimensions are (x, y, z)."""
    depth, height, width = stack.shape_zyx
    grid = pyvista.ImageData()
    grid.dimensions = (width, height, depth)
    # C-order flattening makes x vary fastest, which is the order VTK expects.
    grid.point_data["intensity"] = np.asarray(stack.values).flatten(order="C")
    return grid
