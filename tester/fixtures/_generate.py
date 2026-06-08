"""Generate the tester upload fixtures, reproducibly and with no deps.

Run from the repo root (or anywhere):

    python tester/fixtures/_generate.py

Produces, under `tester/fixtures/`:
  - test-document.pdf, test-document-2.pdf, test-document-3.pdf  (1-page PDFs)
  - test-report.txt                                              (plain text)
  - test-image.png                                               (1x1 PNG)
  - sample-folder/  with a couple of the files above             (folder upload)

Every byte is hand-assembled so the fixtures stay tiny and identical
across machines. file_upload steps in the test plans reference these by
name; see `tester/browser_runner.py` (_resolve_upload_files).
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent


def _minimal_pdf(title: str) -> bytes:
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
    objects.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
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


def _one_px_png() -> bytes:
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
    raw = b"\x00\x4a\x90\xa0"  # filter byte + one RGB pixel
    idat = zlib.compress(raw)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def main() -> None:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    pdfs = {
        "test-document.pdf": "SpecterX Test Document",
        "test-document-2.pdf": "SpecterX Test Document 2",
        "test-document-3.pdf": "SpecterX Test Document 3",
    }
    for name, title in pdfs.items():
        (FIXTURES_DIR / name).write_bytes(_minimal_pdf(title))

    (FIXTURES_DIR / "test-report.txt").write_text(
        "SpecterX tester fixture\nThis is a sample report used for upload tests.\n",
        encoding="utf-8",
    )
    (FIXTURES_DIR / "test-image.png").write_bytes(_one_px_png())

    folder = FIXTURES_DIR / "sample-folder"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "doc-a.pdf").write_bytes(_minimal_pdf("Folder Doc A"))
    (folder / "doc-b.pdf").write_bytes(_minimal_pdf("Folder Doc B"))
    (folder / "notes.txt").write_text("Folder upload fixture file.\n", encoding="utf-8")

    print(f"fixtures written under {FIXTURES_DIR}")


if __name__ == "__main__":
    main()
