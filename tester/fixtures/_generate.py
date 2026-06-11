"""Generate tester upload fixtures, reproducibly and with no deps.

Run from the repo root (or anywhere):

    python tester/fixtures/_generate.py

Produces files under `tester/fixtures/` (or a custom directory). Every byte
is hand-assembled so fixtures stay tiny and identical across machines.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path
from typing import Any

FIXTURES_DIR = Path(__file__).resolve().parent


def minimal_pdf(title: str) -> bytes:
    """A valid 1-page PDF that renders `title` as visible text."""
    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
    )
    text = title.replace("(", r"\(").replace(")", r"\)")
    stream = b"BT /F1 24 Tf 72 700 Td (" + text.encode("latin-1") + b") Tj ET"
    objects.append(
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
    )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += str(i).encode() + b" 0 obj\n" + body + b"\nendobj\n"

    xref_pos = len(out)
    n = len(objects) + 1
    out += b"xref\n0 " + str(n).encode() + b"\n"
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        b"trailer\n<< /Size " + str(n).encode() + b" /Root 1 0 R >>\n"
        b"startxref\n" + str(xref_pos).encode() + b"\n%%EOF\n"
    )
    return bytes(out)


def one_px_png() -> bytes:
    """A 1x1 opaque PNG, hand-assembled."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    raw = b"\x00\x4a\x90\xa0"
    idat = zlib.compress(raw)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def make_pdf(path: Path, *, title: str | None = None) -> None:
    stem = path.stem.replace("-", " ").replace("_", " ").title()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(minimal_pdf(title or f"SpecterX Test {stem}"))


def make_txt(path: Path, *, body: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = body or f"SpecterX tester fixture\nSample file: {path.name}\n"
    path.write_text(text, encoding="utf-8")


def make_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(one_px_png())


def ensure_fixture_file(path: Path) -> None:
    """Create a single fixture file if missing, based on extension."""
    if path.exists():
        return
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        make_pdf(path)
    elif suffix == ".txt":
        make_txt(path)
    elif suffix == ".png":
        make_png(path)
    else:
        make_txt(path, body=f"SpecterX tester fixture ({path.name})\n")


def ensure_configured_fixtures(
    fixtures_dir: Path,
    config: dict[str, Any],
) -> None:
    """Ensure all files referenced in test config exist under fixtures_dir."""
    files = config.get("files") or {}
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    names: list[str] = []
    default = files.get("default")
    if isinstance(default, str) and default.strip():
        names.append(default.strip())
    lst = files.get("list")
    if isinstance(lst, list):
        names.extend(str(x).strip() for x in lst if str(x).strip())
    folder = files.get("folder")
    folder_files = files.get("folder_files")
    folder_name = folder.strip() if isinstance(folder, str) and folder.strip() else None
    if folder_name and isinstance(folder_files, list):
        folder_path = fixtures_dir / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        for name in folder_files:
            clean = str(name).strip()
            if clean:
                ensure_fixture_file(folder_path / clean)

    seen: set[str] = set()
    for name in names:
        if not name or name in seen:
            continue
        seen.add(name)
        ensure_fixture_file(fixtures_dir / name)


def generate_default_fixtures(fixtures_dir: Path | None = None) -> None:
    """Write the legacy default fixture set (for backwards compatibility)."""
    root = fixtures_dir or FIXTURES_DIR
    root.mkdir(parents=True, exist_ok=True)

    pdfs = {
        "test-document.pdf": "SpecterX Test Document",
        "test-document-2.pdf": "SpecterX Test Document 2",
        "test-document-3.pdf": "SpecterX Test Document 3",
    }
    for name, title in pdfs.items():
        (root / name).write_bytes(minimal_pdf(title))

    make_txt(root / "test-report.txt", body=(
        "SpecterX tester fixture\nThis is a sample report used for upload tests.\n"
    ))
    make_png(root / "test-image.png")

    folder = root / "sample-folder"
    folder.mkdir(parents=True, exist_ok=True)
    make_pdf(folder / "doc-a.pdf", title="Folder Doc A")
    make_pdf(folder / "doc-b.pdf", title="Folder Doc B")
    make_txt(folder / "notes.txt", body="Folder upload fixture file.\n")


def main() -> None:
    generate_default_fixtures()
    print(f"fixtures written under {FIXTURES_DIR}")


if __name__ == "__main__":
    main()
