"""Big-endian stream primitives matching fheroes2's StreamBase operators.

Encodings (with bigendian=true, as the map format uses):
- bool/char/int8/uint8 : 1 byte
- (u)int16             : 2 bytes big-endian
- (u)int32             : 4 bytes big-endian
- string               : uint32 length prefix + raw bytes
- vector/list/map/array: uint32 count prefix + elements (map = count of key/value pairs)
- optional<T>          : bool present + T if present
- pair<A,B>            : A then B
- enum                 : its underlying integer type
"""
from __future__ import annotations

import struct


class StreamError(ValueError):
    pass


class StreamReader:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self.pos = 0

    def remaining(self) -> int:
        return len(self._data) - self.pos

    def read_raw(self, n: int) -> bytes:
        if self.pos + n > len(self._data):
            raise StreamError(f"read past end ({n} bytes at {self.pos})")
        out = self._data[self.pos : self.pos + n]
        self.pos += n
        return out

    def u8(self) -> int:
        return self.read_raw(1)[0]

    def bool(self) -> bool:
        return self.u8() != 0

    def i8(self) -> int:
        return struct.unpack(">b", self.read_raw(1))[0]

    def u16(self) -> int:
        return struct.unpack(">H", self.read_raw(2))[0]

    def i16(self) -> int:
        return struct.unpack(">h", self.read_raw(2))[0]

    def u32(self) -> int:
        return struct.unpack(">I", self.read_raw(4))[0]

    def i32(self) -> int:
        return struct.unpack(">i", self.read_raw(4))[0]

    def string(self) -> str:
        length = self.u32()
        return self.read_raw(length).decode("utf-8", errors="surrogateescape")


class StreamWriter:
    def __init__(self) -> None:
        self._chunks: list[bytes] = []

    def getvalue(self) -> bytes:
        return b"".join(self._chunks)

    def write_raw(self, data: bytes) -> None:
        self._chunks.append(data)

    def u8(self, v: int) -> None:
        self._chunks.append(struct.pack(">B", v & 0xFF))

    def bool(self, v: bool) -> None:
        self.u8(1 if v else 0)

    def i8(self, v: int) -> None:
        self._chunks.append(struct.pack(">b", v))

    def u16(self, v: int) -> None:
        self._chunks.append(struct.pack(">H", v & 0xFFFF))

    def i16(self, v: int) -> None:
        self._chunks.append(struct.pack(">h", v))

    def u32(self, v: int) -> None:
        self._chunks.append(struct.pack(">I", v & 0xFFFFFFFF))

    def i32(self, v: int) -> None:
        self._chunks.append(struct.pack(">i", v))

    def string(self, v: str) -> None:
        raw = v.encode("utf-8", errors="surrogateescape")
        self.u32(len(raw))
        self._chunks.append(raw)
