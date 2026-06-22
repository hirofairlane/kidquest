"""Read / patch / write the fheroes2 ``.fh2m`` map format.

Ported from the fheroes2 source (``src/engine/serialize.{h,cpp}``,
``src/fheroes2/maps/map_format_info.{h,cpp}``, ``src/engine/zzlib.cpp``):
a 6-byte magic + uncompressed big-endian header, then a plain zlib stream
(``compress2`` / ``uncompress``, no custom framing) containing the map body.

Pinned to format version 13.
"""

from .body import MapBody, Sphinx, assert_fully_parsable
from .container import (
    FORMAT_VERSION,
    MAGIC,
    Fh2mContainer,
    Fh2mError,
)
from .stream import StreamReader, StreamWriter

__all__ = [
    "FORMAT_VERSION",
    "MAGIC",
    "Fh2mContainer",
    "Fh2mError",
    "MapBody",
    "Sphinx",
    "StreamReader",
    "StreamWriter",
    "assert_fully_parsable",
]
