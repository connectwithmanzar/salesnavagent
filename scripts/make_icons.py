#!/usr/bin/env python3
"""Write simple navy PNG icons for the Chrome extension."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "extension" / "icons"
NAVY = (15, 39, 68, 255)
CYAN = (62, 198, 255, 255)
WHITE = (255, 255, 255, 255)


def png(width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> bytes:
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(pixels[y * width + x])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            chunk(b"IEND", b""),
        ]
    )


def icon(size: int) -> bytes:
    pixels = []
    arrow_top = int(size * 0.28)
    arrow_bot = int(size * 0.72)
    stem_l = int(size * 0.42)
    stem_r = int(size * 0.58)
    for y in range(size):
        for x in range(size):
            dx = (x + 0.5) / size - 0.5
            dy = (y + 0.5) / size - 0.5
            if dx * dx + dy * dy > 0.46 * 0.46:
                pixels.append((0, 0, 0, 0))
                continue
            color = NAVY
            if stem_l <= x < stem_r and arrow_top <= y <= int(size * 0.52):
                color = WHITE
            head = arrow_bot - y
            half = int(size * 0.22) - int(head * 0.9)
            if int(size * 0.48) <= y <= arrow_bot and abs(x - size / 2) <= max(half, 1):
                color = WHITE
            if color == NAVY and dx * dx + dy * dy > 0.40 * 0.40:
                color = CYAN
            pixels.append(color)
    return png(size, size, pixels)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for size in (16, 48, 128):
        (OUT / f"icon{size}.png").write_bytes(icon(size))
        print(OUT / f"icon{size}.png")


if __name__ == "__main__":
    main()
