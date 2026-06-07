#!/usr/bin/env python3
"""
Run detect_label against the small and large DOCX samples and record the
approximate peak RAM usage and runtime for each run.

Usage:
    python measure_detect_label.py
"""

import importlib.machinery
import time
import tracemalloc
import types
from pathlib import Path
from typing import Dict, List


BASE_DIR = Path(__file__).resolve().parent
DETECT_LABEL_PATH = BASE_DIR / "detect_label.py"


def load_detect_label_module():
    """Dynamically load the detect_label module from its path."""
    loader = importlib.machinery.SourceFileLoader(
        "detect_label_module", str(DETECT_LABEL_PATH)
    )
    module = types.ModuleType(loader.name)
    loader.exec_module(module)
    return module


def measure_file(module, doc_path: Path) -> Dict[str, float]:
    """
    Run detect_label.print_report on the given DOCX and capture timing +
    peak memory via tracemalloc.
    """
    tracemalloc.start()
    start = time.perf_counter()
    module.print_report(str(doc_path))
    duration = time.perf_counter() - start
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "file": doc_path.name,
        "duration_s": duration,
        "peak_bytes": float(peak_bytes),
    }


def main():
    module = load_detect_label_module()
    doc_paths: List[Path] = [
        BASE_DIR / "Small Doc Exmaple.docx",
        BASE_DIR / "Large Doc Exmaple.docx",
    ]

    results: List[Dict[str, float]] = []
    for doc in doc_paths:
        if not doc.exists():
            print(f"Missing DOCX: {doc}")
            continue
        print(f"\n=== Running detect_label on {doc.name} ===")
        res = measure_file(module, doc)
        results.append(res)

    print("\n=== Measurements ===")
    if not results:
        print("No results recorded.")
        return
    for res in results:
        peak_mb = res["peak_bytes"] / (1024 * 1024)
        print(f"{res['file']}: peak ~{peak_mb:.2f} MB, duration {res['duration_s']:.3f}s")


if __name__ == "__main__":
    main()
