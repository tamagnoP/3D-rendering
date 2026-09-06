"""Command line entry point. Collects the config path and calls the pipeline."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from vis3d.config import load_config
from vis3d.errors import Vis3DError
from vis3d.pipeline import run

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read an image stack and render it in 3D.")
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to the YAML configuration file (see config/default.yaml).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.config)
        logging.basicConfig(
            level=config.logging_level,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
        run(config)
    except Vis3DError as error:
        logging.getLogger(__name__).error("%s", error)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
