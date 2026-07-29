#!/usr/bin/env python3
"""扫描本机 VibeDrop 桌面历史,把还存在的媒体原件补传进 Home Vault 媒体仓。

历史里只存了文件路径;原件可能已被删。本脚本只上传"本机还在"的文件,
按内容 sha256 去重(vault 侧同哈希只存一份)。跑完后其他设备的历史条目
就能通过 文件名+大小 匹配到这些原件,实现跨设备"复活"查看。

用法:
  python3 vault-media-uploader.py                       # 默认端点 http://127.0.0.1:8788
  python3 vault-media-uploader.py --endpoint http://192.168.3.2:8788
  python3 vault-media-uploader.py --dry-run             # 只统计不上传
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import pathlib
import sys
import urllib.parse
import urllib.request

CHUNK = 1024 * 1024
MAX_BYTES = 2 * 1024 * 1024 * 1024


def default_history_paths() -> list[pathlib.Path]:
    home = pathlib.Path.home()
    return [
        home / ".vibedrop" / "history.jsonl",
        home / ".voicedrop" / "history.jsonl",
    ]


def iter_entries(paths: list[pathlib.Path]):
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(entry, dict):
                yield entry


def collect_media_files(entries) -> dict[pathlib.Path, str]:
    """路径 → 展示文件名。覆盖单媒体老字段和多项 items 两种形态。"""
    found: dict[pathlib.Path, str] = {}

    def add(raw_path, name):
        raw_path = str(raw_path or "").strip()
        if not raw_path or raw_path.startswith("content://"):
            return
        path = pathlib.Path(raw_path)
        found.setdefault(path, str(name or path.name))

    for entry in entries:
        for key in ("image_path", "saved_path", "file_path", "imagePath", "savedPath", "filePath"):
            if entry.get(key):
                add(entry[key], entry.get("file_name") or entry.get("fileName"))
        items = entry.get("items")
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                for key in ("saved_path", "file_path", "savedPath", "filePath"):
                    if item.get(key):
                        add(item[key], item.get("file_name") or item.get("fileName"))
    return found


def sha256_of(path: pathlib.Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(CHUNK)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def post_json(endpoint: str, api: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{endpoint}{api}", data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def upload_file(endpoint: str, path: pathlib.Path, digest: str, name: str) -> dict:
    mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
    query = urllib.parse.urlencode({"hash": digest, "name": name, "mime": mime})
    url = f"{endpoint}/api/media/upload?{query}"
    size = path.stat().st_size
    with path.open("rb") as handle:
        request = urllib.request.Request(url, data=handle, method="POST")
        request.add_header("Content-Type", "application/octet-stream")
        request.add_header("Content-Length", str(size))
        with urllib.request.urlopen(request, timeout=3600) as response:
            return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8788")
    parser.add_argument("--history", action="append", default=[], help="额外的历史 jsonl 路径")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    endpoint = args.endpoint.rstrip("/")

    history_paths = default_history_paths() + [pathlib.Path(p).expanduser() for p in args.history]
    candidates = collect_media_files(iter_entries(history_paths))

    present: list[tuple[pathlib.Path, str, int]] = []
    missing = 0
    oversize = 0
    for path, name in sorted(candidates.items()):
        if not path.exists():
            missing += 1
            continue
        size = path.stat().st_size
        if size <= 0:
            missing += 1
            continue
        if size > MAX_BYTES:
            oversize += 1
            print(f"  跳过(超2GB): {path}")
            continue
        present.append((path, name, size))

    print(f"历史引用媒体文件 {len(candidates)} 个:本机还在 {len(present)},已丢失 {missing},超限 {oversize}")
    if not present:
        return 0

    print("计算哈希…")
    hashed: list[tuple[pathlib.Path, str, int, str]] = []
    for path, name, size in present:
        try:
            hashed.append((path, name, size, sha256_of(path)))
        except OSError as exc:
            print(f"  读取失败跳过: {path} ({exc})")

    all_hashes = sorted({digest for *_rest, digest in hashed})
    existing: set[str] = set()
    for start in range(0, len(all_hashes), 200):
        result = post_json(endpoint, "/api/media/lookup", {"hashes": all_hashes[start:start + 200]})
        existing.update(result.get("existing") or [])

    todo = [item for item in hashed if item[3] not in existing]
    skip = len(hashed) - len(todo)
    total_bytes = sum(size for _p, _n, size, _d in todo)
    print(f"vault 已有 {skip} 个,需上传 {len(todo)} 个,共 {total_bytes / 1024 / 1024:.1f} MB")

    if args.dry_run:
        for path, name, size, digest in todo:
            print(f"  [dry-run] {name} ({size / 1024 / 1024:.1f} MB) {digest[:12]}… ← {path}")
        return 0

    uploaded = 0
    failed = 0
    done_hashes: set[str] = set()
    for path, name, size, digest in todo:
        if digest in done_hashes:
            continue
        try:
            result = upload_file(endpoint, path, digest, name)
            if result.get("ok"):
                uploaded += 1
                done_hashes.add(digest)
                print(f"  ✓ {name} ({size / 1024 / 1024:.1f} MB)")
            else:
                failed += 1
                print(f"  ✗ {name}: {result.get('error')}")
        except Exception as exc:
            failed += 1
            print(f"  ✗ {name}: {exc}")

    print(f"完成:上传 {uploaded},失败 {failed},vault 原有 {skip}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
