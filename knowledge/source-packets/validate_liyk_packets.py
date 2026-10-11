"""Validate the six liYK source packets without network requests or dependencies."""
import hashlib
import json
from pathlib import Path


PACKETS = (
    "reasoningbank-2509.25140", "expel-2308.10144",
    "agentrewind-2608.14380", "statefork-2609.38648",
    "agentscope-2508.16279", "nora-2605.02092",
)


def main():
    root = Path(__file__).resolve().parent
    official_files = 0
    for slug in PACKETS:
        packet_root = root / slug
        packet = json.loads((packet_root / "source-packet.json").read_text())
        for field in ("paper_version", "official_code_version", "exact_source_anchors",
                      "configs_and_examples", "tests_and_reported_results"):
            assert field in packet, (slug, field)
        paper = packet["paper_version"]
        for kind in ("pdf", "text"):
            path = packet_root / paper["local_" + kind]
            assert path.resolve().is_relative_to(packet_root.resolve()), path
            assert hashlib.sha256(path.read_bytes()).hexdigest() == paper[kind + "_sha256"], path
        for revision in packet["official_code_version"]:
            assert len(revision["revision"]) == 40, slug
            for entry in revision["files"]:
                path = packet_root / entry["file"]
                assert path.resolve().is_relative_to(packet_root.resolve()), path
                assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], path
                official_files += 1
        for field in ("exact_source_anchors", "configs_and_examples", "tests_and_reported_results"):
            assert (packet_root / packet[field]).is_file(), (slug, field)
        assert not packet["validation"]["full_official_reproduction_completed"]
    assert official_files == 38
    print("PASS: 6 packets, 6 PDFs, 6 texts, 38 pinned official files and required source documents")


if __name__ == "__main__":
    main()
