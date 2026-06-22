"""File-level container for ``.fh2m``: magic + uncompressed header + zlib body.

The header (a serialized ``BaseMapFormat``) is kept as opaque bytes here; the body
is the zlib-decompressed payload that section/metadata parsing operates on. This
split alone already supports patching the body (Sphinx/Sign/Event metadata) without
touching the header.

fheroes2 re-reads the body with size-agnostic ``uncompress``, so the recompressed
bytes need not be identical to the original — only the *uncompressed body* must be.
"""
from __future__ import annotations

import struct
import zlib

MAGIC = b"h2map\x00"
FORMAT_VERSION = 13


class Fh2mError(ValueError):
    pass


class Fh2mContainer:
    def __init__(self, version: int, header: bytes, body: bytes) -> None:
        # `header` is the raw bytes from the magic through to the start of the zlib
        # body (inclusive of magic + version). `body` is the decompressed payload.
        self.version = version
        self.header = header
        self.body = body

    @classmethod
    def parse(cls, data: bytes) -> "Fh2mContainer":
        if data[:6] != MAGIC:
            raise Fh2mError("not a .fh2m file (bad magic)")
        version = struct.unpack(">H", data[6:8])[0]
        if version != FORMAT_VERSION:
            raise Fh2mError(f"unsupported .fh2m version {version} (expected {FORMAT_VERSION})")

        body_start, body = _find_zlib_body(data)
        return cls(version=version, header=data[:body_start], body=body)

    def serialize(self) -> bytes:
        return self.header + zlib.compress(self.body, zlib.Z_DEFAULT_COMPRESSION)

    def with_body(self, body: bytes) -> "Fh2mContainer":
        return Fh2mContainer(self.version, self.header, body)


def _find_zlib_body(data: bytes) -> tuple[int, bytes]:
    """Locate the trailing zlib stream and return (offset, decompressed body).

    The body is the unique trailing zlib stream: the right offset decompresses
    cleanly and consumes every remaining byte (zlib's Adler-32 makes false starts
    extremely unlikely to validate).
    """
    for off in range(8, min(len(data), 8192)):
        if data[off] != 0x78:  # zlib CMF for 32K window / deflate
            continue
        d = zlib.decompressobj()
        try:
            body = d.decompress(data[off:])
            body += d.flush()
        except zlib.error:
            continue
        if d.unused_data == b"" and len(body) > 0:
            return off, body
    raise Fh2mError("could not locate the zlib body")
