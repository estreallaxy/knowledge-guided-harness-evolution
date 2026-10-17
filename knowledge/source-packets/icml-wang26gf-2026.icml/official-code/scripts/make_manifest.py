#!/usr/bin/env python3
"""Write SHA256SUMS for every released artifact under data/."""

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "SHA256SUMS"

paths = sorted(p for p in (ROOT / "data").rglob("*.json") if p.is_file())
lines = [f"# SHA-256 manifest for released artifacts ({len(paths)} files)",
         "# verify with: python3 scripts/verify_artifacts.py --sha"]
for p in paths:
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    lines.append(f"{digest}  {p.relative_to(ROOT)}")
OUT.write_text("\n".join(lines) + "\n")
print(f"wrote {OUT} ({len(paths)} files)")
