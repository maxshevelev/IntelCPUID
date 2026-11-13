#!/usr/bin/env python3
"""Check the two published files before they are pushed.

ByteRipper reads `IntelCPUIDBrandNames.json` and `IntelMicrocodeSignatures.json`
from this repository at run time and keeps the last pair it read whole. A file
it cannot read is refused and the cached one kept, so a broken push does no
harm on a bench — but it does not reach anyone either. This checks what the
app checks, and a little more:

- `formatVersion` is 1 (the app refuses a newer one);
- every entry's fields have the types the app decodes, a CPUID is five hex
  digits (an X for any one), a model has a name and a list of codes;
- an S-SPEC is SRxxx, SAxxx or Qxxx, and no code added from ARK, Wikipedia
  or an Intel document belongs to two models (the article's own may: it
  writes one code for the J3355 and J3355E);
- every update's signature is five hex digits with a two-digit platform mask,
  and every file it names is a platomav path.

Usage:
    check.py            exit 0 when both files are right, else the problems

stdlib only.
"""

import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
CPUID = re.compile(r"^[0-9A-FX]{5}$")
CODE = re.compile(r"^(S[RA][0-9A-Z]{3}|Q[0-9A-Z]{3})$")


def strings(value):
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def check_names(doc, problems):
    if doc.get("formatVersion") != 1:
        problems.append(f"IntelCPUIDBrandNames.json: formatVersion {doc.get('formatVersion')!r}, not 1")
    owners = {}
    for i, e in enumerate(doc.get("entries", [])):
        where = f"entry {i} {e.get('cpuids')}"
        if not strings(e.get("cpuids")) or not all(CPUID.match(c) for c in e["cpuids"]):
            problems.append(f"{where}: cpuids")
        for key in ("codeNames", "productFamilies", "steppings", "segments"):
            if not strings(e.get(key)):
                problems.append(f"{where}: {key} is not a list of strings")
        if "cores" in e and not strings(e["cores"]):
            problems.append(f"{where}: cores")
        for p in e.get("processors", []):
            if not isinstance(p.get("name"), str) or not strings(p.get("sSpec")):
                problems.append(f"{where}: processor {p}")
                continue
            for code in p["sSpec"]:
                if not CODE.match(code):
                    problems.append(f"{where}: {p['name']} {code!r} is not an S-SPEC")
                if code in p.get("sSpecSource", {}):      # added here; the article's own are its own
                    owners.setdefault(code, set()).add(p["name"])
    for code, names in owners.items():
        if len(names) > 1:
            problems.append(f"{code} is written for {sorted(names)}")


def check_signatures(doc, problems):
    if doc.get("formatVersion") != 1:
        problems.append(f"IntelMicrocodeSignatures.json: formatVersion {doc.get('formatVersion')!r}, not 1")
    for i, u in enumerate(doc.get("updates", [])):
        where = f"update {i} {u.get('revision')}"
        if not isinstance(u.get("revision"), str) or not isinstance(u.get("date"), str):
            problems.append(f"{where}: revision or date")
        for s in u.get("signatures", []):
            if not re.fullmatch(r"[0-9A-F]{5}", s.get("cpuid", "")) or not re.fullmatch(r"[0-9A-F]{2}", s.get("platforms", "")):
                problems.append(f"{where}: signature {s}")
        if not strings(u.get("files")) or not all(f.startswith("Intel/cpu") for f in u["files"]):
            problems.append(f"{where}: files")


def main():
    problems = []
    with open(os.path.join(ROOT, "IntelCPUIDBrandNames.json"), encoding="utf-8") as f:
        names = json.load(f)
    with open(os.path.join(ROOT, "IntelMicrocodeSignatures.json"), encoding="utf-8") as f:
        signatures = json.load(f)
    check_names(names, problems)
    check_signatures(signatures, problems)
    if problems:
        sys.exit("not ready to push:\n  " + "\n  ".join(problems))
    processors = [p for e in names["entries"] for p in e["processors"] if not p.get("series")]
    print(f"ok: {len(names['entries'])} entries, {len(processors)} processors, "
          f"{len(signatures['updates'])} shared updates")


if __name__ == "__main__":
    main()
