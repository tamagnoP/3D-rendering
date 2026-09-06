"""Step 1: read a stack of image slices from disk into a 3D array.

Two layouts are supported and detected from the files themselves:
  - one file per slice (a sorted sequence of 2D images), and
  - a single multi-page file that already contains the whole stack.
Nothing about the file names, the bit depth or the image size is assumed.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import tifffile

from vis3d.errors import DataError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImageStack:
    """Intensity volume in (z, y, x) order plus where it came from."""

    values: np.ndarray
    source_files: tuple[Path, ...]

    @property
    def shape_zyx(self) -> tuple[int, int, int]:
        return (self.values.shape[0], self.values.shape[1], self.values.shape[2])


def read_image_stack(directory: Path, pattern: str) -> ImageStack:
    """Read the files in `directory` matching `pattern`, sorted by name, into one volume."""
    if not directory.is_dir():
        raise DataError(f"Input directory does not exist: {directory}")

    files = sorted(directory.glob(pattern))
    if not files:
        raise DataError(f"No file in {directory} matches the pattern '{pattern}'.")

    logger.info("Reading %d file(s) from %s matching '%s'", len(files), directory, pattern)

    slices = []
    for file in files:
        image = read_single_file(file)
        if image.ndim == 3:
            # A multi-page file: each page is one slice of the volume.
            slices.extend(image)
        elif image.ndim == 2:
            slices.append(image)
        else:
            raise DataError(f"File {file} holds a {image.ndim}D image; expected 2D or 3D.")

    first_shape = slices[0].shape
    for file, image in zip(files, slices, strict=False):
        if image.shape != first_shape:
            raise DataError(
                f"Slice shapes differ: {file} has shape {image.shape}, "
                f"expected {first_shape} like the first slice."
            )

    volume = np.stack(slices, axis=0)
    logger.info("Stack shape (z, y, x): %s, dtype: %s", volume.shape, volume.dtype)

    return ImageStack(values=volume, source_files=tuple(files))


def read_single_file(file: Path) -> np.ndarray:
    """Read one image file into an array. Raises DataError if the file cannot be read."""
    try:
        return np.asarray(tifffile.imread(file))
    except (OSError, ValueError) as error:
        raise DataError(f"Cannot read image file {file}: {error}") from error
