# 3Dvis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Two steps, nothing else:

1. read an image stack from disk (TIFF slices or one multi-page TIFF),
2. render it as a 3D volume.

## Install

```bash
python -m venv .venv
.venv/bin/pip install -e .
```

## Run

Copy `config/default.yaml`, point `input.dir` at your slices, then:

```bash
3Dvis --config my_run.yaml
```

The command and the project are called `3Dvis`; the importable package is `vis3d`,
because a Python package name cannot start with a digit.

All parameters live in that YAML file: input directory and glob pattern, colormap,
intensity range, opacity transfer function, camera position, window size, and an
optional screenshot path.

## Configuration

| Key | Meaning |
| --- | --- |
| `input.dir` | directory holding the image slices |
| `input.pattern` | glob selecting the slices, sorted by file name (e.g. `*.TIF`) |
| `render.colormap` | any matplotlib colormap name |
| `render.value_range` | `[min, max]` intensity range; `null` = data min/max |
| `render.opacity` | PyVista opacity transfer function name or a list of values |
| `render.camera_position` | `iso` \| `xy` \| `xz` \| `yz` |
| `render.window_size` | window size in pixels, `[width, height]` |
| `render.off_screen` | `true` = no interactive window, only the screenshot |
| `render.screenshot` | path of a PNG to save; `null` = do not save |
| `logging.level` | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` |

## Layout

```
config/default.yaml                        reference configuration
src/vis3d/cli.py                           argparse entry point
src/vis3d/config.py                        YAML -> validated dataclasses
src/vis3d/errors.py                        ConfigError / DataError / RenderError
src/vis3d/pipeline.py                      step 1 then step 2
src/vis3d/io/image_stack.py                step 1: read slices into a (z, y, x) array
src/vis3d/visualization/volume_render.py   step 2: PyVista volume rendering
tests/                                     mirrors src/vis3d/
```

## Tests

```bash
pytest -q
```

## License

Released under the MIT License, see [LICENSE](LICENSE).

