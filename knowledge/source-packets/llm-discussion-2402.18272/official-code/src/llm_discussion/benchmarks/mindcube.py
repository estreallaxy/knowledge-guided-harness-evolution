"""Prepare the official MindCube holdout with revision-checked local images.

Only ZIP metadata is downloaded eagerly. Images from the project viewer are
checked against the pinned archive and fall back to ranged archive downloads.
"""

from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import struct
from urllib.parse import quote
import zipfile
import zlib

import httpx


REVISION = "9c941b46a6bd65b6914669ef7a579948fc9c8467"
ARCHIVE_URL = f"https://huggingface.co/datasets/MLL-Lab/MindCube/resolve/{REVISION}/data.zip"
ARCHIVE_SIZE = 643961690
ARCHIVE_SHA256 = "714c8961d66e9662c826d2202493a7d86cbe31797cf41e3a0567cb4d72b0aaa8"
VIEWER_URL = "https://mind-cube.github.io/data_viewer/"
SPLITS = {"tiny": "MindCube_tinybench.jsonl", "full": "MindCube.jsonl"}


def _client() -> httpx.Client:
    return httpx.Client(follow_redirects=True, timeout=60,
                        limits=httpx.Limits(max_connections=8))


def _range(client: httpx.Client, start: int, size: int) -> bytes:
    if size == 0:
        return b""
    end = start + size - 1
    if start < 0 or end >= ARCHIVE_SIZE:
        raise ValueError("Invalid MindCube archive byte range")
    with client.stream("GET", ARCHIVE_URL, headers={"Range": f"bytes={start}-{end}"}) as response:
        expected = f"bytes {start}-{end}/{ARCHIVE_SIZE}"
        if response.status_code != 206 or response.headers.get("content-range") != expected:
            raise ValueError("MindCube archive server did not honor the requested byte range")
        chunks, received = [], 0
        for chunk in response.iter_bytes():
            received += len(chunk)
            if received > size:
                raise ValueError("MindCube archive range exceeded its expected size")
            chunks.append(chunk)
    if received != size:
        raise ValueError("Incomplete MindCube archive range")
    return b"".join(chunks)


class _ArchiveReader(io.RawIOBase):
    def __init__(self, client: httpx.Client):
        self.client, self.position = client, 0

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        self.position = offset if whence == 0 else (self.position if whence == 1 else ARCHIVE_SIZE) + offset
        return self.position

    def read(self, size=-1):
        size = ARCHIVE_SIZE - self.position if size < 0 else min(size, ARCHIVE_SIZE - self.position)
        data = _range(self.client, self.position, size)
        self.position += len(data)
        return data


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".part")
    temporary.write_bytes(data)
    temporary.replace(path)


def _index(client: httpx.Client, cache: Path) -> dict:
    path = cache / "archive-index.json"
    if path.exists():
        saved = json.loads(path.read_text())
        if saved.get("revision") == REVISION:
            return saved["entries"]
    with zipfile.ZipFile(_ArchiveReader(client)) as archive:
        entries = {i.filename: {"offset": i.header_offset, "size": i.file_size,
                   "compressed_size": i.compress_size, "method": i.compress_type,
                   "crc": i.CRC} for i in archive.infolist() if not i.is_dir()}
    _write(path, json.dumps({"revision": REVISION, "entries": entries}).encode())
    return entries


def _valid(data: bytes, info: dict) -> bool:
    return len(data) == info["size"] and zlib.crc32(data) == info["crc"]


def _member(client: httpx.Client, info: dict) -> bytes:
    header = _range(client, info["offset"], 30)
    if header[:4] != b"PK\x03\x04":
        raise ValueError("Invalid MindCube ZIP member header")
    name_size, extra_size = struct.unpack_from("<HH", header, 26)
    packed = _range(client, info["offset"] + 30 + name_size + extra_size, info["compressed_size"])
    if info["method"] == zipfile.ZIP_DEFLATED:
        data = zlib.decompress(packed, -zlib.MAX_WBITS)
    elif info["method"] == zipfile.ZIP_STORED:
        data = packed
    else:
        raise ValueError("Unsupported MindCube ZIP compression")
    if not _valid(data, info):
        raise ValueError("MindCube archive member failed size/CRC validation")
    return data


def _category(row: dict) -> str:
    name = row["id"].split("_", 1)[0]
    return "around" if name == "aroundnew" else name


def _select(rows: list[dict], limit: int | None) -> list[dict]:
    if limit is None:
        return rows
    groups = defaultdict(deque)
    for row in rows:
        groups[_category(row)].append(row)
    selected = []
    while len(selected) < min(limit, len(rows)):
        for group in groups.values():
            if group and len(selected) < limit:
                selected.append(group.popleft())
    return selected


def _image_path(name: str) -> str:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != "other_all_image":
        raise ValueError(f"Invalid MindCube image path: {name}")
    return str(PurePosixPath("images", *path.parts[1:]))


def _task(row: dict) -> dict:
    question = row["question"]
    matches = list(re.finditer(r"(?<!\S)([A-Z])\.\s+", question))
    options = {}
    for index, match in enumerate(matches):
        label = match.group(1)
        if label in options:
            raise ValueError(f"Duplicate option {label} in {row['id']}")
        end = matches[index + 1].start() if index + 1 < len(matches) else len(question)
        options[label] = question[match.end():end].strip()
    labels = sorted(options)
    if (len(labels) < 2 or labels != list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:len(labels)])
            or row["gt_answer"] not in options or not all(options.values())):
        raise ValueError(f"Invalid MindCube options in {row['id']}")
    return {"id": row["id"], "question": question[:matches[0].start()].strip(),
            "reference": row["gt_answer"], "answer_type": "choice",
            "options": [options[label] for label in labels],
            "images": [_image_path(name) for name in row["images"]],
            "category": _category(row)}


def prepare(output: Path, *, split: str = "tiny", limit: int | None = None) -> Path:
    """Prepare tiny's 1,050 held-out questions, or explicitly request the full corpus.

    Limited subsets cycle through categories in source order. The full corpus
    contains training examples and is not a held-out evaluation split.
    """
    if split not in SPLITS:
        raise ValueError("MindCube split must be 'tiny' or 'full'")
    if limit is not None and (type(limit) is not int or limit < 1):
        raise ValueError("MindCube limit must be a positive integer")
    output = Path(output)
    cache = output / ".cache"
    with _client() as client:
        index = _index(client, cache)
        member_name = "data/raw/" + SPLITS[split]
        metadata = cache / SPLITS[split]
        raw = metadata.read_bytes() if metadata.exists() else b""
        if not _valid(raw, index[member_name]):
            raw = _member(client, index[member_name])
            _write(metadata, raw)
        rows = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
        selected = _select(rows, limit)
        tasks = [_task(row) for row in selected]
        image_names = sorted({name for row in selected for name in row["images"]})

        def download(name: str) -> dict:
            info = index["data/" + name]
            relative = _image_path(name)
            destination = output / relative
            data = destination.read_bytes() if destination.exists() else b""
            if not _valid(data, info):
                try:
                    response = client.get(VIEWER_URL + quote(name, safe="/"))
                    response.raise_for_status()
                    data = response.content
                except httpx.HTTPError:
                    data = b""
                if not _valid(data, info):
                    data = _member(client, info)
                _write(destination, data)
            return {"path": relative, "archive_member": "data/" + name,
                    "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

        with ThreadPoolExecutor(max_workers=8) as pool:
            images = list(pool.map(download, image_names))
    tasks_path = output / "tasks.jsonl"
    _write(tasks_path, ("\n".join(json.dumps(task, ensure_ascii=False) for task in tasks) + "\n").encode())
    provenance = {
        "benchmark": "MindCube", "split": split, "revision": REVISION,
        "source": "https://huggingface.co/datasets/MLL-Lab/MindCube",
        "archive_url": ARCHIVE_URL, "archive_bytes": ARCHIVE_SIZE,
        "published_archive_sha256": ARCHIVE_SHA256,
        "integrity": "Each downloaded member is checked against the pinned ZIP index by size and CRC; the full archive is not downloaded.",
        "metadata_member": member_name, "metadata_sha256": hashlib.sha256(raw).hexdigest(),
        "license": "MIT", "license_source": f"https://huggingface.co/datasets/MLL-Lab/MindCube/blob/{REVISION}/README.md",
        "source_tasks": len(rows), "prepared_tasks": len(tasks),
        "selection": "all" if limit is None else "round-robin by category, retaining source order within each category",
        "evaluation_split": split == "tiny",
        "note": "Tiny is the official holdout. Full includes training data and is not a held-out benchmark.",
        "tasks_sha256": hashlib.sha256(tasks_path.read_bytes()).hexdigest(),
        "categories": dict((name, sum(t["category"] == name for t in tasks)) for name in sorted({t["category"] for t in tasks})),
        "images": images,
    }
    _write(output / "provenance.json", (json.dumps(provenance, indent=2) + "\n").encode())
    return tasks_path
