from __future__ import annotations

import struct
from typing import Iterable, Dict, List


def parse_dbf(path: str, encoding: str = "cp932") -> Iterable[Dict[str, str]]:
    """Yield records from a DBF file as dictionaries.

    This is a very small subset of the dBASE III reader sufficient for tests.
    Only character fields are supported.
    """
    with open(path, "rb") as f:
        header = f.read(32)
        record_count = struct.unpack("<I", header[4:8])[0]
        header_length = struct.unpack("<H", header[8:10])[0]
        record_length = struct.unpack("<H", header[10:12])[0]

        fields: List[tuple[str, str, int]] = []
        while True:
            first = f.read(1)
            if first == b"\r":
                break
            data = first + f.read(31)
            name = data[:11].split(b"\x00")[0].decode("ascii")
            typ = data[11:12].decode("ascii")
            length = data[16]
            fields.append((name, typ, length))

        f.seek(header_length)
        for _ in range(record_count):
            record = f.read(record_length)
            if not record:
                break
            if record[0] == 0x2A:  # deleted record
                continue
            pos = 1
            row: Dict[str, str] = {}
            for name, typ, length in fields:
                raw = record[pos:pos + length]
                pos += length
                value = raw.decode(encoding, errors="ignore").strip()
                row[name] = value
            yield row

__all__ = ["parse_dbf"]
