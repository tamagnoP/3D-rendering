from pathlib import Path

import numpy as np
import pytest
import tifffile

from vis3d.errors import DataError
from vis3d.io.image_stack import read_image_stack


def write_slices(directory: Path, count: int, shape: tuple[int, int] = (4, 5)) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for index in range(count):
        image = np.full(shape, index, dtype=np.uint16)
        tifffile.imwrite(directory / f"slice_{index:03d}.TIF", image)


def test_sequence_of_slices_is_stacked_in_file_name_order(tmp_path: Path) -> None:
    write_slices(tmp_path, count=3)

    stack = read_image_stack(tmp_path, "*.TIF")

    assert stack.shape_zyx == (3, 4, 5)
    assert [int(plane[0, 0]) for plane in stack.values] == [0, 1, 2]
    assert len(stack.source_files) == 3


def test_multi_page_file_is_expanded_into_slices(tmp_path: Path) -> None:
    volume = np.arange(2 * 3 * 4, dtype=np.uint16).reshape(2, 3, 4)
    tifffile.imwrite(tmp_path / "volume.TIF", volume)

    stack = read_image_stack(tmp_path, "*.TIF")

    assert stack.shape_zyx == (2, 3, 4)
    np.testing.assert_array_equal(stack.values, volume)


def test_missing_directory_is_reported(tmp_path: Path) -> None:
    with pytest.raises(DataError, match="does not exist"):
        read_image_stack(tmp_path / "absent", "*.TIF")


def test_no_matching_file_is_reported(tmp_path: Path) -> None:
    write_slices(tmp_path, count=1)

    with pytest.raises(DataError, match="matches the pattern"):
        read_image_stack(tmp_path, "*.png")


def test_inconsistent_slice_shapes_are_reported(tmp_path: Path) -> None:
    write_slices(tmp_path, count=1)
    tifffile.imwrite(tmp_path / "slice_001.TIF", np.zeros((7, 7), dtype=np.uint16))

    with pytest.raises(DataError, match="Slice shapes differ"):
        read_image_stack(tmp_path, "*.TIF")
