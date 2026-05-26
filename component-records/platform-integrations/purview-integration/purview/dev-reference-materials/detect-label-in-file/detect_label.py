#!/usr/bin/env python3
"""
Inspect a DOCX file for Microsoft Information Protection (MIP) sensitivity
label metadata and print a readable report.

What it does
- Opens the DOCX as a zip archive and reads both core document properties and
  custom properties, grouping any MSIP_Label_* entries by label GUID.
- Scans /customXml/*.xml parts for additional MSIP_Label_* mentions that some
  Office builds store outside of docProps/custom.xml.
- Produces a console report with the raw properties plus a brief summary of the
  detected label (name, GUID, applied date) when present.

Usage
    python detect_label.py /path/to/file.docx

The script relies only on the Python standard library (zipfile and ElementTree)
and exits with status 1 when the DOCX path is missing.
"""

import sys
import zipfile
import datetime
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Helper: parse XML text safely
def _parse_xml(xml_bytes: bytes) -> Optional[ET.Element]:
    try:
        return ET.fromstring(xml_bytes)
    except ET.ParseError:
        return None

def _read_zip_member(zf: zipfile.ZipFile, name: str) -> Optional[bytes]:
    try:
        with zf.open(name) as f:
            return f.read()
    except KeyError:
        return None

def read_core_properties(zf: zipfile.ZipFile) -> Dict[str, str]:
    """
    Reads core properties from /docProps/core.xml (title, subject, creator, etc.)
    """
    core = _read_zip_member(zf, "docProps/core.xml")
    if not core:
        return {}
    ns = {
        "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
        "dc": "http://purl.org/dc/elements/1.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }
    root = _parse_xml(core)
    if root is None:
        return {}
    props = {}
    # Common fields
    fields = [
        ("dc:title", "title"),
        ("dc:subject", "subject"),
        ("dc:creator", "creator"),
        ("cp:lastModifiedBy", "last_modified_by"),
        ("dcterms:created", "created"),
        ("dcterms:modified", "modified"),
        ("cp:contentStatus", "content_status"),
        ("cp:category", "category"),
        ("cp:keywords", "keywords"),
        ("cp:revision", "revision"),
    ]
    for xpath, key in fields:
        el = root.find(xpath, ns)
        if el is not None and el.text:
            props[key] = el.text
    return props

def read_custom_properties(zf: zipfile.ZipFile) -> Dict[str, str]:
    """
    Reads custom document properties from /docProps/custom.xml.
    MIP sensitivity labels are typically stored here with names like:
      MSIP_Label_<GUID>_Name
      MSIP_Label_<GUID>_Enabled
      MSIP_Label_<GUID>_SetDate
      MSIP_Label_<GUID>_Method
      MSIP_Label_<GUID>_SiteId
      MSIP_Label_<GUID>_ActionId
    """
    custom = _read_zip_member(zf, "docProps/custom.xml")
    if not custom:
        return {}
    ns = {
        "cp": "http://schemas.openxmlformats.org/officeDocument/2006/custom-properties",
        "vt": "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes",
    }
    root = _parse_xml(custom)
    if root is None:
        return {}
    props = {}
    for prop in root.findall("cp:property", ns):
        name = prop.attrib.get("name") or ""
        # Each property has a single vt:* child holding the value
        val = None
        for child in prop:
            # child.tag is like '{namespace}lpwstr' etc.
            if child.text is not None:
                val = child.text
                break
        if name:
            props[name] = val
    return props

def search_customxml_for_msip(zf: zipfile.ZipFile) -> Dict[str, List[Tuple[str, str]]]:
    """
    Some Office builds also stash MIP info under /customXml/*.xml.
    This scans those XML parts for elements whose tag OR text mentions 'MSIP_Label_'.
    Returns a dict: filename -> list of (path, text) hits.
    """
    hits: Dict[str, List[Tuple[str, str]]] = {}
    for info in zf.infolist():
        if info.filename.startswith("customXml/") and info.filename.endswith(".xml"):
            b = _read_zip_member(zf, info.filename)
            if not b:
                continue
            root = _parse_xml(b)
            if root is None:
                continue
            local_hits: List[Tuple[str, str]] = []
            # Walk all elements
            for elem in root.iter():
                tag_local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                text = (elem.text or "").strip()
                if ("MSIP_Label_" in tag_local) or ("MSIP_Label_" in text):
                    # Build a simple path
                    path_parts = []
                    cur = elem
                    while cur is not None:
                        t = cur.tag.split("}")[-1] if "}" in cur.tag else cur.tag
                        path_parts.append(t)
                        cur = cur.getparent() if hasattr(cur, "getparent") else None
                        # xml.etree in stdlib doesn't have getparent; so just store the leaf tag
                        break
                    path = "/".join(reversed(path_parts)) if path_parts else tag_local
                    local_hits.append((path, text))
            if local_hits:
                hits[info.filename] = local_hits
    return hits

def extract_mip_labels(custom_props: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """
    Group MSIP label properties by GUID and return a dict:
      guid -> { 'Name': ..., 'Enabled': ..., 'SetDate': ..., ... }
    """
    labels = defaultdict(dict)
    for key, val in custom_props.items():
        if not key.startswith("MSIP_Label_"):
            continue
        parts = key.split("_")
        # Expect: MSIP_Label_<GUID>_<FieldName>
        if len(parts) < 4:
            # Sometimes names look like MSIP_Label_<GUID> (no suffix) — keep them too
            guid = parts[2] if len(parts) > 2 else "UNKNOWN"
            field = "_".join(parts[3:]) if len(parts) > 3 else "Value"
        else:
            guid = parts[2]
            field = "_".join(parts[3:])
        labels[guid][field] = val or ""
    return dict(labels)

def print_report(docx_path: str) -> None:
    with zipfile.ZipFile(docx_path, "r") as zf:
        core = read_core_properties(zf)
        custom = read_custom_properties(zf)
        msip = extract_mip_labels(custom)
        customxml_hits = search_customxml_for_msip(zf)

    print("=" * 70)
    print(f"FILE: {docx_path}")
    print("=" * 70)

    print("\n[Core Properties]")
    if core:
        for k, v in core.items():
            print(f"  {k}: {v}")
    else:
        print("  (none)")

    print("\n[Custom Properties]")
    if custom:
        # Show a few common non-MIP props first, then MSIP props
        non_mip = {k: v for k, v in custom.items() if not k.startswith("MSIP_Label_")}
        if non_mip:
            for k, v in non_mip.items():
                print(f"  {k}: {v}")
        else:
            print("  (no non-MIP custom properties)")
        print("\n  -- MSIP (Sensitivity Label) Properties --")
        if msip:
            for guid, fields in msip.items():
                print(f"  Label GUID: {guid}")
                for fk, fv in sorted(fields.items()):
                    print(f"    {fk}: {fv}")
        else:
            print("  (no MSIP_Label_* properties found)")
    else:
        print("  (none)")

    print("\n[customXml scan for MSIP_Label_*]")
    if customxml_hits:
        for fname, entries in customxml_hits.items():
            print(f"  {fname}:")
            for path, text in entries:
                print(f"    {path}: {text}")
    else:
        print("  (no MSIP hits under customXml)")

    # Friendly summary
    print("\n[Summary]")
    if msip:
        # Pick the first enabled label (if any), otherwise first one
        chosen = None
        for guid, fields in msip.items():
            enabled = fields.get("Enabled", "").lower() in ("true", "1", "yes")
            name = fields.get("Name") or "(no name)"
            setdate = fields.get("SetDate", "")
            if enabled and not chosen:
                chosen = (name, guid, setdate)
        if not chosen:
            # fallback to any label present
            guid, fields = next(iter(msip.items()))
            chosen = (fields.get("Name") or "(no name)", guid, fields.get("SetDate", ""))

        name, guid, setdate = chosen
        print(f"  Detected Sensitivity Label: {name}")
        print(f"  Label GUID: {guid}")
        if setdate:
            print(f"  Applied (SetDate): {setdate}")
    else:
        print("  No sensitivity label metadata detected.")

def main(argv: List[str]):
    if len(argv) != 2:
        print("Usage: python detect_label.py <path/to/file.docx>")
        sys.exit(1)
    path = argv[1]
    print_report(path)

if __name__ == "__main__":
    main(sys.argv)
