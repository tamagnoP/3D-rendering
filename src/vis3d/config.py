"""Load the YAML configuration into frozen dataclasses and validate every value."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import yaml

from vis3d.errors import ConfigError

logger = logging.getLogger(__name__)

CAMERA_POSITIONS = ("iso", "xy", "xz", "yz")
LOGGING_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


@dataclass(frozen=True)
class InputConfig:
    dir: Path
    pattern: str


@dataclass(frozen=True)
class RenderConfig:
    colormap: str
    value_range: tuple[float, float] | None
    opacity: str | list[float]
    camera_position: str
    window_size: tuple[int, int]
    off_screen: bool
    screenshot: Path | None


@dataclass(frozen=True)
class Config:
    input: InputConfig
    render: RenderConfig
    logging_level: str


def load_config(path: Path) -> Config:
    """Read the YAML file at `path` and return a validated configuration."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ConfigError(f"Cannot read config file {path}: {error}") from error

    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise ConfigError(f"Config file {path} is not valid YAML: {error}") from error

    if not isinstance(raw, dict):
        raise ConfigError(f"Config file {path} must contain a mapping at the top level.")

    check_keys(raw, required=("input", "render", "logging"), where="top level")

    input_config = build_input_config(raw["input"])
    render_config = build_render_config(raw["render"])
    logging_level = read_logging_level(raw["logging"])

    logger.debug("Configuration loaded from %s", path)
    return Config(input=input_config, render=render_config, logging_level=logging_level)


def check_keys(section: object, required: tuple[str, ...], where: str) -> dict:
    """Return `section` as a dict, failing if a required key is missing or a key is unknown."""
    if not isinstance(section, dict):
        raise ConfigError(f"Config section '{where}' must be a mapping.")

    missing = [key for key in required if key not in section]
    if missing:
        raise ConfigError(f"Config section '{where}' is missing key(s): {', '.join(missing)}")

    unknown = [key for key in section if key not in required]
    if unknown:
        raise ConfigError(f"Config section '{where}' has unknown key(s): {', '.join(unknown)}")

    return section


def build_input_config(raw_section: object) -> InputConfig:
    section = check_keys(raw_section, required=("dir", "pattern"), where="input")

    directory = Path(str(section["dir"])).expanduser()
    pattern = section["pattern"]
    if not isinstance(pattern, str) or not pattern:
        raise ConfigError("Config key 'input.pattern' must be a non-empty string, e.g. '*.TIF'.")

    return InputConfig(dir=directory, pattern=pattern)


def build_render_config(raw_section: object) -> RenderConfig:
    required = (
        "colormap",
        "value_range",
        "opacity",
        "camera_position",
        "window_size",
        "off_screen",
        "screenshot",
    )
    section = check_keys(raw_section, required=required, where="render")

    colormap = section["colormap"]
    if not isinstance(colormap, str) or not colormap:
        raise ConfigError("Config key 'render.colormap' must be a non-empty string.")

    value_range = read_value_range(section["value_range"])

    opacity = section["opacity"]
    if not isinstance(opacity, (str, list)):
        raise ConfigError(
            "Config key 'render.opacity' must be a transfer function name or a list of numbers."
        )

    camera_position = section["camera_position"]
    if camera_position not in CAMERA_POSITIONS:
        raise ConfigError(
            f"Config key 'render.camera_position' must be one of {CAMERA_POSITIONS}, "
            f"got '{camera_position}'."
        )

    window_size = section["window_size"]
    if (
        not isinstance(window_size, list)
        or len(window_size) != 2
        or not all(isinstance(value, int) and value > 0 for value in window_size)
    ):
        raise ConfigError("Config key 'render.window_size' must be two positive integers.")

    off_screen = section["off_screen"]
    if not isinstance(off_screen, bool):
        raise ConfigError("Config key 'render.off_screen' must be true or false.")

    screenshot_value = section["screenshot"]
    screenshot = None if screenshot_value is None else Path(str(screenshot_value)).expanduser()
    if screenshot is None and off_screen:
        raise ConfigError(
            "Config key 'render.off_screen' is true but 'render.screenshot' is null: "
            "the run would produce nothing."
        )

    return RenderConfig(
        colormap=colormap,
        value_range=value_range,
        opacity=opacity,
        camera_position=camera_position,
        window_size=(window_size[0], window_size[1]),
        off_screen=off_screen,
        screenshot=screenshot,
    )


def read_value_range(value: object) -> tuple[float, float] | None:
    """Return the intensity range as (min, max), or None when the data range should be used."""
    if value is None:
        return None

    if (
        not isinstance(value, list)
        or len(value) != 2
        or not all(isinstance(item, (int, float)) for item in value)
    ):
        raise ConfigError("Config key 'render.value_range' must be null or two numbers [min, max].")

    minimum, maximum = float(value[0]), float(value[1])
    if minimum >= maximum:
        raise ConfigError(
            f"Config key 'render.value_range' needs min < max, got [{minimum}, {maximum}]."
        )

    return (minimum, maximum)


def read_logging_level(raw_section: object) -> str:
    section = check_keys(raw_section, required=("level",), where="logging")

    level = section["level"]
    if level not in LOGGING_LEVELS:
        raise ConfigError(f"Config key 'logging.level' must be one of {LOGGING_LEVELS}.")

    return level
