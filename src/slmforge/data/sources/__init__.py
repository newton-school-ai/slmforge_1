from __future__ import annotations

from slmforge.data.sources.base import Record, Source
from slmforge.data.sources.internal import InternalSource
from slmforge.data.sources.local import LocalSource
from slmforge.data.sources.public import PublicHFSource
from slmforge.data.sources.registry import get_source
from slmforge.data.sources.synthetic import SyntheticSource

__all__ = [
    "Source",
    "Record",
    "SyntheticSource",
    "PublicHFSource",
    "LocalSource",
    "InternalSource",
    "get_source",
]
