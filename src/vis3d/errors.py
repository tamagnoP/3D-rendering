"""Exceptions raised by this package. Every failure is one of these."""


class Vis3DError(Exception):
    """Base class for all errors raised by vis3d."""


class ConfigError(Vis3DError):
    """The YAML configuration is missing a key, has an unknown key or a bad value."""


class DataError(Vis3DError):
    """The input images are missing, unreadable or do not form a consistent stack."""


class RenderError(Vis3DError):
    """The 3D rendering could not be produced."""
