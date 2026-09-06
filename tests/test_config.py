from pathlib import Path

import pytest

from vis3d.config import load_config
from vis3d.errors import ConfigError

VALID_YAML = """
input:
  dir: /tmp/slices
  pattern: "*.TIF"
render:
  colormap: viridis
  value_range: [100, 4000]
  opacity: sigmoid
  camera_position: iso
  window_size: [800, 600]
  off_screen: false
  screenshot: null
logging:
  level: INFO
"""


def write_config(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "run.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_valid_config_is_loaded(tmp_path: Path) -> None:
    config = load_config(write_config(tmp_path, VALID_YAML))

    assert config.input.dir == Path("/tmp/slices")
    assert config.input.pattern == "*.TIF"
    assert config.render.value_range == (100.0, 4000.0)
    assert config.render.screenshot is None
    assert config.logging_level == "INFO"


def test_missing_key_is_rejected(tmp_path: Path) -> None:
    text = VALID_YAML.replace('  pattern: "*.TIF"\n', "")

    with pytest.raises(ConfigError, match="pattern"):
        load_config(write_config(tmp_path, text))


def test_unknown_key_is_rejected(tmp_path: Path) -> None:
    text = VALID_YAML + "extra_stage:\n  enabled: true\n"

    with pytest.raises(ConfigError, match="extra_stage"):
        load_config(write_config(tmp_path, text))


def test_reversed_value_range_is_rejected(tmp_path: Path) -> None:
    text = VALID_YAML.replace("value_range: [100, 4000]", "value_range: [4000, 100]")

    with pytest.raises(ConfigError, match="min < max"):
        load_config(write_config(tmp_path, text))


def test_off_screen_without_screenshot_is_rejected(tmp_path: Path) -> None:
    text = VALID_YAML.replace("off_screen: false", "off_screen: true")

    with pytest.raises(ConfigError, match="screenshot"):
        load_config(write_config(tmp_path, text))


def test_default_config_is_valid() -> None:
    default = Path(__file__).resolve().parents[1] / "config" / "default.yaml"

    config = load_config(default)

    assert config.input.pattern
