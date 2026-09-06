"""The whole run: read the image stack, then render it in 3D."""

from __future__ import annotations

import logging

from vis3d.config import Config
from vis3d.io.image_stack import read_image_stack
from vis3d.visualization.volume_render import render_volume

logger = logging.getLogger(__name__)


def run(config: Config) -> None:
    logger.info("Step 1/2: reading image stack")
    stack = read_image_stack(config.input.dir, config.input.pattern)

    logger.info("Step 2/2: rendering 3D volume")
    render_volume(stack, config.render)
