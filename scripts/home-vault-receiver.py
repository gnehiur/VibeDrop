#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import queue
import re
import subprocess
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


DEFAULT_VAULT_ROOT = "/Volumes/SN850X/VibeDropVault"
DEFAULT_PORT = 8788
MAX_REQUEST_BYTES = 80 * 1024 * 1024


sync_lock = threading.Lock()

# ---- SSE 订阅者(设备连上后挂着,有新历史时被唤醒)----
subscribers_lock = threading.Lock()
subscribers: set = set()


def broadcast_event(payload: dict[str, Any]) -> None:
    data = json.dumps(payload, ensure_ascii=False)
    with subscribers_lock:
        targets = list(subscribers)
    for pending in targets:
        try:
            pending.put_nowait(data)
        except queue.Full:
            pass


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def safe_segment(value: str, fallback: str = "android") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip()).strip("._-")
    return cleaned[:80] or fallback


def read_json_body(handler: BaseHTTPRequestHandler, max_bytes: int) -> Any:
    raw_length = handler.headers.get("Content-Length", "0")
    try:
        length = int(raw_length)
    except ValueError as exc:
        raise ValueError("Content-Length 无效") from exc
    if length <= 0:
        raise ValueError("请求体为空")
    if length > max_bytes:
        raise ValueError(f"请求体过大: {length} bytes")
    payload = handler.rfile.read(length)
    return json.loads(payload.decode("utf-8"))


def normalize_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, list):
        history = payload
        envelope: dict[str, Any] = {
            "schemaVersion": 1,
            "app": "VibeDrop",
            "deviceId": "android",
            "deviceName": "Android",
            "exportedAt": iso_now(),
            "history": history,
        }
        return envelope
    if not isinstance(payload, dict):
        raise ValueError("JSON 必须是对象或历史数组")
    history = payload.get("history")
    if not isinstance(history, list):
        raise ValueError("history 必须是数组")
    return {
        **payload,
        "schemaVersion": payload.get("schemaVersion") or 1,
        "app": payload.get("app") or "VibeDrop",
        "deviceId": payload.get("deviceId") or payload.get("clientId") or "android",
        "deviceName": payload.get("deviceName") or payload.get("clientName") or "Android",
        "exportedAt": payload.get("exportedAt") or iso_now(),
        "history": history,
    }


def save_payload(vault_root: pathlib.Path, payload: dict[str, Any]) -> pathlib.Path:
    device_id = safe_segment(str(payload.get("deviceId") or payload.get("deviceName") or "android"))
    now = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    inbox_dir = vault_root / "inbox" / "android" / device_id
    inbox_dir.mkdir(parents=True, exist_ok=True)
    path = inbox_dir / f"{now}-{digest}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def run_sync(sync_script: pathlib.Path, vault_root: pathlib.Path, viewer_url: str, timeout: int) -> dict[str, Any]:
    cmd = [
        sys.executable,
        str(sync_script),
        "--local-vault-root",
        str(vault_root),
        "--skip-local-history",
        "--skip-android",
        "--include-vault-inbox",
        "--viewer-url",
        viewer_url,
    ]
    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"sync failed ({result.returncode}): {result.stderr.strip() or result.stdout.strip()}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"sync returned non-json output: {result.stdout[:500]}") from exc


def load_json_file(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def find_latest_android_payload(
    vault_root: pathlib.Path,
    device_id: str = "",
) -> tuple[dict[str, Any], pathlib.Path]:
    android_inbox = vault_root / "inbox" / "android"
    if not android_inbox.exists():
        raise FileNotFoundError("Android inbox 不存在")

    candidate_groups: list[list[pathlib.Path]] = []
    if device_id:
        candidate_groups.append(list((android_inbox / safe_segment(device_id)).glob("*.json")))
    candidate_groups.append(list(android_inbox.glob("*/*.json")))

    seen_paths: set[pathlib.Path] = set()
    for candidates in candidate_groups:
        unique_candidates = [path for path in candidates if path not in seen_paths]
        seen_paths.update(unique_candidates)
        unique_candidates.sort(key=lambda path: (path.stat().st_mtime, path.name), reverse=True)
        for path in unique_candidates:
            try:
                payload = normalize_payload(load_json_file(path))
            except Exception:
                continue
            return payload, path

    raise FileNotFoundError("没有找到 Android 历史快照")


def entry_sort_key(entry: dict[str, Any]) -> float:
    """尽力从条目里解析时间,用于全设备时间线排序;解析不了排最旧。"""
    for candidate in (entry.get("timestamp_iso"), entry.get("timestamp")):
        if candidate in (None, ""):
            continue
        # 数字时间戳(秒或毫秒)
        if isinstance(candidate, (int, float)) or str(candidate).strip().lstrip("-").isdigit():
            try:
                value = float(candidate)
                return value / 1000.0 if value > 1e11 else value
            except (TypeError, ValueError):
                pass
        # ISO 文本时间(历史条目实际用的就是这种)
        try:
            return dt.datetime.fromisoformat(str(candidate).replace("Z", "+00:00")).timestamp()
        except ValueError:
            continue
    return 0.0


def entry_dedupe_key(entry: dict[str, Any], device_id: str) -> str:
    explicit = str(entry.get("id") or "").strip()
    if explicit:
        return f"{device_id}:{explicit}"
    basis = f"{device_id}|{entry.get('timestamp') or entry.get('timestamp_iso') or ''}|{entry.get('text') or entry.get('fileName') or ''}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:24]


DELTA_FILE_NAME = "deltas.jsonl"
DEVICE_META_NAME = "device.json"
DELTA_COMPACT_THRESHOLD = 800
delta_lock = threading.Lock()


def device_dir_for(vault_root: pathlib.Path, device_id: str) -> pathlib.Path:
    return vault_root / "inbox" / "android" / safe_segment(device_id)


def append_delta_entries(
    vault_root: pathlib.Path,
    device_id: str,
    device_name: str,
    entries: list[Any],
) -> int:
    """把增量条目追加进设备的 deltas.jsonl;超过阈值时压实成新快照。"""
    target_dir = device_dir_for(vault_root, device_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    delta_path = target_dir / DELTA_FILE_NAME

    with delta_lock:
        with delta_path.open("a", encoding="utf-8") as handle:
            for entry in entries:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        (target_dir / DEVICE_META_NAME).write_text(
            json.dumps(
                {"deviceId": device_id, "deviceName": device_name, "updatedAt": iso_now()},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        line_count = sum(1 for _ in delta_path.open("r", encoding="utf-8"))
        if line_count >= DELTA_COMPACT_THRESHOLD:
            compact_device_deltas(vault_root, device_id, device_name)
    return len(entries)


def compact_device_deltas(vault_root: pathlib.Path, device_id: str, device_name: str) -> None:
    """把快照 + 增量合并写成一份新快照,清空增量,避免读取时越来越慢。"""
    payload = load_device_payload(vault_root, device_dir_for(vault_root, device_id))
    if not payload:
        return
    payload["deviceName"] = device_name or payload.get("deviceName") or device_id
    save_payload(vault_root, payload)
    (device_dir_for(vault_root, device_id) / DELTA_FILE_NAME).unlink(missing_ok=True)


def load_device_payload(vault_root: pathlib.Path, device_dir: pathlib.Path) -> dict[str, Any] | None:
    """一台设备的完整历史 = 最新快照 + 之后追加的增量,按 id 去重。"""
    snapshots = [
        path
        for path in device_dir.glob("*.json")
        if path.name != DEVICE_META_NAME
    ]
    payload: dict[str, Any] | None = None
    if snapshots:
        snapshots.sort(key=lambda path: (path.stat().st_mtime, path.name), reverse=True)
        for path in snapshots:
            try:
                payload = normalize_payload(load_json_file(path))
                break
            except Exception:
                continue

    delta_entries: list[Any] = []
    delta_path = device_dir / DELTA_FILE_NAME
    if delta_path.exists():
        for line in delta_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                delta_entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if payload is None:
        if not delta_entries:
            return None
        meta_path = device_dir / DEVICE_META_NAME
        meta = {}
        if meta_path.exists():
            try:
                meta = load_json_file(meta_path)
            except Exception:
                meta = {}
        payload = {
            "schemaVersion": 1,
            "app": "VibeDrop",
            "deviceId": meta.get("deviceId") or device_dir.name,
            "deviceName": meta.get("deviceName") or device_dir.name,
            "exportedAt": meta.get("updatedAt") or iso_now(),
            "history": [],
        }

    seen_ids: set[str] = set()
    combined: list[Any] = []
    for entry in delta_entries + list(payload.get("history") or []):
        key = str(entry.get("id") or "") if isinstance(entry, dict) else ""
        if key:
            if key in seen_ids:
                continue
            seen_ids.add(key)
        combined.append(entry)
    payload["history"] = combined
    return payload


def collect_latest_payload_per_device(vault_root: pathlib.Path) -> list[dict[str, Any]]:
    """遍历各设备目录,每台设备取"最新快照 + 增量"的合并结果。"""
    android_inbox = vault_root / "inbox" / "android"
    if not android_inbox.exists():
        return []
    payloads: list[dict[str, Any]] = []
    for device_dir in sorted(path for path in android_inbox.iterdir() if path.is_dir()):
        payload = load_device_payload(vault_root, device_dir)
        if payload:
            payloads.append(payload)
    return payloads


def build_merged_history(vault_root: pathlib.Path, mode: str, limit: int) -> dict[str, Any]:
    payloads = collect_latest_payload_per_device(vault_root)
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    devices: list[dict[str, Any]] = []
    for payload in payloads:
        device_id = str(payload.get("deviceId") or "unknown")
        device_name = str(payload.get("deviceName") or device_id)
        devices.append({
            "deviceId": device_id,
            "deviceName": device_name,
            "exportedAt": payload.get("exportedAt") or "",
            "historyCount": len(payload.get("history") or []),
        })
        for raw_entry in payload.get("history") or []:
            entry = compact_history_entry(raw_entry) if mode != "full" else (
                raw_entry if isinstance(raw_entry, dict) else compact_history_entry(raw_entry)
            )
            key = entry_dedupe_key(entry, device_id)
            if key in seen:
                continue
            seen.add(key)
            tagged = dict(entry)
            tagged["sourceDeviceId"] = device_id
            tagged["sourceDeviceName"] = device_name
            merged.append(tagged)
    merged.sort(key=entry_sort_key, reverse=True)
    if limit:
        merged = merged[:limit]
    by_name_size, by_name = build_media_lookups(load_media_index(vault_root))
    for entry in merged:
        stamp_entry_media(entry, by_name_size, by_name)
    return {
        "ok": True,
        "schemaVersion": 1,
        "generatedAt": iso_now(),
        "devices": sorted(devices, key=lambda item: item["deviceName"]),
        "mergedCount": len(merged),
        "history": merged,
    }



# ---- 媒体仓:原件按内容哈希存储去重,供跨设备"复活"查看 ----
MEDIA_MAX_BYTES = 2 * 1024 * 1024 * 1024  # 单文件上限 2GB
MEDIA_CHUNK = 1024 * 1024
THUMBNAIL_MAX_CHARS = 48000
media_lock = threading.Lock()
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def media_dir(vault_root: pathlib.Path) -> pathlib.Path:
    return vault_root / "media"


def media_blob_path(vault_root: pathlib.Path, digest: str) -> pathlib.Path:
    return media_dir(vault_root) / "blobs" / digest[:2] / digest


def media_index_path(vault_root: pathlib.Path) -> pathlib.Path:
    return media_dir(vault_root) / "index.json"


def load_media_index(vault_root: pathlib.Path) -> dict[str, Any]:
    path = media_index_path(vault_root)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def build_media_lookups(index: dict[str, Any]) -> tuple[dict[str, str], dict[str, set]]:
    """名字+大小 → 哈希;纯名字 → 哈希集合(唯一时才可用作兜底匹配)。"""
    by_name_size: dict[str, str] = {}
    by_name: dict[str, set] = {}
    for digest, meta in index.items():
        if not isinstance(meta, dict):
            continue
        size = meta.get("sizeBytes")
        for name in meta.get("names") or []:
            if size:
                by_name_size[f"{name}|{size}"] = digest
            by_name.setdefault(name, set()).add(digest)
    return by_name_size, by_name


def register_media(vault_root: pathlib.Path, digest: str, size: int, name: str, mime: str) -> None:
    with media_lock:
        index = load_media_index(vault_root)
        meta = index.get(digest)
        if not isinstance(meta, dict):
            meta = {"sizeBytes": size, "mimeType": mime or "", "names": [], "storedAt": iso_now()}
        if name and name not in (meta.get("names") or []):
            meta.setdefault("names", []).append(name)
        if mime and not meta.get("mimeType"):
            meta["mimeType"] = mime
        meta["sizeBytes"] = size
        index[digest] = meta
        path = media_index_path(vault_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(path)


def find_media_hash(name: str, size: Any, by_name_size: dict[str, str], by_name: dict[str, set]) -> str:
    if not name:
        return ""
    if size:
        hit = by_name_size.get(f"{name}|{size}")
        if hit:
            return hit
    candidates = by_name.get(name)
    if candidates and len(candidates) == 1:
        return next(iter(candidates))
    return ""


MEDIA_KINDS = {"image", "video", "media", "file"}


def stamp_entry_media(entry: dict[str, Any], by_name_size: dict[str, str], by_name: dict[str, set]) -> None:
    """给条目/子项盖上 vaultMediaHash 章:客户端据此判断"vault 有原件,可点开"。"""
    items = entry.get("items")
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            digest = find_media_hash(
                str(item.get("fileName") or item.get("file_name") or ""),
                item.get("sizeBytes") or item.get("size_bytes"),
                by_name_size,
                by_name,
            )
            if digest:
                item["vaultMediaHash"] = digest
    if str(entry.get("kind") or "") in MEDIA_KINDS:
        digest = find_media_hash(
            str(entry.get("fileName") or entry.get("file_name") or ""),
            entry.get("sizeBytes") or entry.get("size_bytes"),
            by_name_size,
            by_name,
        )
        if digest:
            entry.setdefault("vaultMediaHash", digest)


def compact_history_item(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {"fileName": str(item)}
    allowed_keys = (
        "kind",
        "fileName",
        "mimeType",
        "sizeBytes",
        "saveTarget",
        "durationMs",
        "width",
        "height",
    )
    result = {key: item[key] for key in allowed_keys if item.get(key) not in (None, "")}
    thumb = item.get("thumbnailDataUrl") or item.get("thumbnail_data_url") or ""
    if isinstance(thumb, str) and 0 < len(thumb) <= THUMBNAIL_MAX_CHARS:
        result["thumbnailDataUrl"] = thumb
    return result


def compact_history_entry(entry: Any) -> dict[str, Any]:
    if not isinstance(entry, dict):
        return {
            "timestamp": iso_now(),
            "text": str(entry),
            "status": "success",
            "kind": "text",
        }

    allowed_keys = (
        "id",
        "timestamp",
        "timestamp_iso",
        "text",
        "status",
        "target",
        "targetHost",
        "targetAlias",
        "targetName",
        "targetDeviceName",
        "targetServerId",
        "serverId",
        "direction",
        "kind",
        "saveTarget",
        "fileName",
        "mimeType",
        "itemCount",
    )
    result = {key: entry[key] for key in allowed_keys if entry.get(key) not in (None, "")}
    items = entry.get("items")
    if isinstance(items, list) and items:
        compact_items = [compact_history_item(item) for item in items]
        result["items"] = compact_items
        result.setdefault("itemCount", len(compact_items))

    result.setdefault("text", entry.get("fileName") or entry.get("file_name") or "")
    result.setdefault("status", "success")
    result.setdefault("kind", "text")
    if not result.get("fileName") and entry.get("file_name"):
        result["fileName"] = entry.get("file_name")
    if str(result.get("kind") or "") in MEDIA_KINDS:
        thumb = entry.get("thumbnailDataUrl") or entry.get("thumbnail_data_url") or ""
        if isinstance(thumb, str) and 0 < len(thumb) <= THUMBNAIL_MAX_CHARS:
            result["thumbnailDataUrl"] = thumb
    return result


def clamp_limit(value: str, default: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if parsed <= 0:
        return default
    return min(parsed, maximum)


def prepare_restore_history(history: list[Any], mode: str, limit: int) -> list[Any]:
    selected = history[:limit] if limit else history
    if mode == "full":
        return selected
    return [compact_history_entry(entry) for entry in selected]


def make_handler(config: argparse.Namespace) -> type[BaseHTTPRequestHandler]:
    vault_root = pathlib.Path(config.vault_root).expanduser().resolve()
    sync_script = pathlib.Path(config.sync_script).expanduser().resolve()
    viewer_url = config.viewer_url
    max_bytes = config.max_bytes
    token = config.token
    sync_timeout = config.sync_timeout

    class HomeVaultHandler(BaseHTTPRequestHandler):
        server_version = "VibeDropHomeVault/1.0"

        def log_message(self, fmt: str, *args: Any) -> None:
            sys.stderr.write(f"{self.log_date_time_string()} {self.address_string()} {fmt % args}\n")

        def send_json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-VibeDrop-Token")
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:
            self.send_json(204, {})

        def do_GET(self) -> None:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path.rstrip("/") or "/"
            if path == "/health":
                self.send_json(
                    200,
                    {
                        "ok": True,
                        "service": "vibedrop-home-vault-receiver",
                        "vaultRoot": str(vault_root),
                        "viewerUrl": viewer_url,
                        "time": iso_now(),
                    },
                )
                return

            if path == "/api/events":
                # SSE 长连接:挂着不动,有新历史时推一行;25 秒无事发一个心跳保活
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                pending: queue.Queue = queue.Queue(maxsize=64)
                with subscribers_lock:
                    subscribers.add(pending)
                try:
                    self.wfile.write(b": connected\n\n")
                    self.wfile.flush()
                    while True:
                        try:
                            data = pending.get(timeout=25)
                            chunk = f"data: {data}\n\n".encode("utf-8")
                        except queue.Empty:
                            chunk = b": ping\n\n"
                        self.wfile.write(chunk)
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, OSError):
                    pass
                finally:
                    with subscribers_lock:
                        subscribers.discard(pending)
                return

            if path == "/api/history/merged":
                if token and self.headers.get("X-VibeDrop-Token") != token:
                    self.send_json(401, {"ok": False, "error": "unauthorized"})
                    return
                try:
                    query = urllib.parse.parse_qs(parsed_path.query)
                    mode = ((query.get("mode") or ["compact"])[0] or "compact").lower()
                    if mode not in {"compact", "full"}:
                        raise ValueError("mode 只能是 compact 或 full")
                    limit = clamp_limit((query.get("limit") or ["500"])[0], 500, 10000)
                    self.send_json(200, build_merged_history(vault_root, mode, limit))
                except Exception as exc:
                    self.send_json(500, {"ok": False, "error": str(exc)})
                return

            if path == "/api/android-history/latest":
                if token and self.headers.get("X-VibeDrop-Token") != token:
                    self.send_json(401, {"ok": False, "error": "unauthorized"})
                    return
                try:
                    query = urllib.parse.parse_qs(parsed_path.query)
                    device_id = (query.get("deviceId") or query.get("device_id") or [""])[0]
                    mode = ((query.get("mode") or ["compact"])[0] or "compact").lower()
                    if mode not in {"compact", "full"}:
                        raise ValueError("mode 只能是 compact 或 full")
                    limit = clamp_limit((query.get("limit") or ["0"])[0], 0, 10000)
                    payload, source_path = find_latest_android_payload(vault_root, device_id)
                    history = payload["history"]
                    restored_history = prepare_restore_history(history, mode, limit)
                    self.send_json(
                        200,
                        {
                            "ok": True,
                            "schemaVersion": 1,
                            "app": "VibeDrop",
                            "deviceId": payload.get("deviceId") or "",
                            "deviceName": payload.get("deviceName") or "",
                            "exportedAt": payload.get("exportedAt") or "",
                            "sourcePath": source_path.relative_to(vault_root).as_posix(),
                            "mode": mode,
                            "historyCount": len(history),
                            "returnedCount": len(restored_history),
                            "history": restored_history,
                        },
                    )
                except Exception as exc:
                    self.send_json(500, {"ok": False, "error": str(exc)})
                return

            if path.startswith("/api/media/blob/"):
                digest = path.rsplit("/", 1)[-1].lower()
                if not HEX64.match(digest):
                    self.send_json(400, {"ok": False, "error": "invalid hash"})
                    return
                blob = media_blob_path(vault_root, digest)
                if not blob.exists():
                    self.send_json(404, {"ok": False, "error": "media not found"})
                    return
                meta = load_media_index(vault_root).get(digest) or {}
                mime = str(meta.get("mimeType") or "application/octet-stream")
                total = blob.stat().st_size
                start, end = 0, total - 1
                range_header = self.headers.get("Range", "")
                is_partial = False
                if range_header.startswith("bytes="):
                    spec = range_header[6:].split(",")[0].strip()
                    try:
                        if spec.startswith("-"):
                            suffix = int(spec[1:])
                            start = max(0, total - suffix)
                        else:
                            parts = spec.split("-")
                            start = int(parts[0])
                            if len(parts) > 1 and parts[1]:
                                end = min(int(parts[1]), total - 1)
                        if start > end or start >= total:
                            self.send_response(416)
                            self.send_header("Content-Range", f"bytes */{total}")
                            self.end_headers()
                            return
                        is_partial = True
                    except ValueError:
                        start, end, is_partial = 0, total - 1, False
                length = end - start + 1
                self.send_response(206 if is_partial else 200)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(length))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "public, max-age=86400")
                if is_partial:
                    self.send_header("Content-Range", f"bytes {start}-{end}/{total}")
                self.end_headers()
                try:
                    with blob.open("rb") as handle:
                        handle.seek(start)
                        remaining = length
                        while remaining > 0:
                            chunk = handle.read(min(MEDIA_CHUNK, remaining))
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                            remaining -= len(chunk)
                except (BrokenPipeError, ConnectionResetError, OSError):
                    pass
                return

            self.send_json(404, {"ok": False, "error": "not_found"})

        def do_POST(self) -> None:
            request_path = urllib.parse.urlparse(self.path).path.rstrip("/")

            if request_path == "/api/history/append":
                # 增量推送:只收新增条目,追加进设备增量文件,立刻广播通知
                if token and self.headers.get("X-VibeDrop-Token") != token:
                    self.send_json(401, {"ok": False, "error": "unauthorized"})
                    return
                try:
                    body = read_json_body(self, max_bytes)
                    if not isinstance(body, dict):
                        raise ValueError("请求体必须是对象")
                    device_id = str(body.get("deviceId") or "").strip()
                    if not device_id:
                        raise ValueError("缺少 deviceId")
                    entries = body.get("entries")
                    if not isinstance(entries, list):
                        raise ValueError("entries 必须是数组")
                    device_name = str(body.get("deviceName") or device_id)
                    appended = append_delta_entries(vault_root, device_id, device_name, entries)
                    broadcast_event({
                        "type": "history-updated",
                        "deviceId": device_id,
                        "deviceName": device_name,
                        "historyCount": appended,
                        "mode": "append",
                        "at": iso_now(),
                    })
                    self.send_json(200, {"ok": True, "appended": appended})
                except Exception as exc:
                    self.send_json(500, {"ok": False, "error": str(exc)})
                return

            if request_path == "/api/media/upload":
                # 原件上传:按内容哈希落盘去重;流式写入避免大文件占内存
                if token and self.headers.get("X-VibeDrop-Token") != token:
                    self.send_json(401, {"ok": False, "error": "unauthorized"})
                    return
                try:
                    query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                    digest = ((query.get("hash") or [""])[0] or "").lower()
                    if not HEX64.match(digest):
                        raise ValueError("缺少合法的 hash 参数(sha256 hex)")
                    name = (query.get("name") or [""])[0]
                    mime = (query.get("mime") or [""])[0]
                    length = int(self.headers.get("Content-Length", "0"))
                    if length <= 0:
                        raise ValueError("请求体为空")
                    if length > MEDIA_MAX_BYTES:
                        raise ValueError(f"文件超过单文件上限 2GB: {length}")

                    blob = media_blob_path(vault_root, digest)
                    hasher = hashlib.sha256()
                    tmp_dir = media_dir(vault_root) / "tmp"
                    tmp_dir.mkdir(parents=True, exist_ok=True)
                    tmp_path = tmp_dir / f"{digest}.{os.getpid()}.{threading.get_ident()}.part"
                    remaining = length
                    with tmp_path.open("wb") as handle:
                        while remaining > 0:
                            chunk = self.rfile.read(min(MEDIA_CHUNK, remaining))
                            if not chunk:
                                raise ValueError("请求体不完整")
                            hasher.update(chunk)
                            handle.write(chunk)
                            remaining -= len(chunk)
                    actual = hasher.hexdigest()
                    if actual != digest:
                        tmp_path.unlink(missing_ok=True)
                        raise ValueError(f"哈希不匹配: 声明 {digest[:12]}… 实际 {actual[:12]}…")

                    existed = blob.exists()
                    if existed:
                        tmp_path.unlink(missing_ok=True)
                    else:
                        blob.parent.mkdir(parents=True, exist_ok=True)
                        tmp_path.replace(blob)
                    register_media(vault_root, digest, length, name, mime)
                    self.send_json(200, {"ok": True, "hash": digest, "existed": existed, "sizeBytes": length})
                except Exception as exc:
                    self.send_json(500, {"ok": False, "error": str(exc)})
                return

            if request_path == "/api/media/lookup":
                # 批量查询:哪些哈希已入库 / 按 文件名+大小 匹配哈希
                if token and self.headers.get("X-VibeDrop-Token") != token:
                    self.send_json(401, {"ok": False, "error": "unauthorized"})
                    return
                try:
                    body = read_json_body(self, max_bytes)
                    if not isinstance(body, dict):
                        raise ValueError("请求体必须是对象")
                    index = load_media_index(vault_root)
                    hashes = body.get("hashes")
                    existing = []
                    if isinstance(hashes, list):
                        existing = [
                            h for h in hashes
                            if isinstance(h, str) and HEX64.match(h.lower())
                            and media_blob_path(vault_root, h.lower()).exists()
                        ]
                    matches: dict[str, str] = {}
                    keys = body.get("keys")
                    if isinstance(keys, list):
                        by_name_size, by_name = build_media_lookups(index)
                        for key in keys:
                            if not isinstance(key, dict):
                                continue
                            name = str(key.get("fileName") or "")
                            size = key.get("sizeBytes")
                            digest = find_media_hash(name, size, by_name_size, by_name)
                            if digest:
                                matches[f"{name}|{size or ''}"] = digest
                    self.send_json(200, {"ok": True, "existing": existing, "matches": matches, "indexCount": len(index)})
                except Exception as exc:
                    self.send_json(500, {"ok": False, "error": str(exc)})
                return

            if request_path != "/api/android-history":
                self.send_json(404, {"ok": False, "error": "not_found"})
                return
            if token and self.headers.get("X-VibeDrop-Token") != token:
                self.send_json(401, {"ok": False, "error": "unauthorized"})
                return
            try:
                payload = normalize_payload(read_json_body(self, max_bytes))
                history_count = len(payload["history"])
                saved_path = save_payload(vault_root, payload)
                broadcast_event({
                    "type": "history-updated",
                    "deviceId": payload.get("deviceId") or "",
                    "deviceName": payload.get("deviceName") or "",
                    "historyCount": history_count,
                    "at": iso_now(),
                })
                with sync_lock:
                    sync_report = run_sync(sync_script, vault_root, viewer_url, sync_timeout)
                self.send_json(
                    200,
                    {
                        "ok": True,
                        "historyCount": history_count,
                        "savedPath": saved_path.relative_to(vault_root).as_posix(),
                        "syncReport": sync_report,
                    },
                )
            except Exception as exc:
                self.send_json(500, {"ok": False, "error": str(exc)})

    return HomeVaultHandler


def main() -> int:
    parser = argparse.ArgumentParser(description="Receive Android VibeDrop history uploads into Home Vault.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--vault-root", default=DEFAULT_VAULT_ROOT)
    parser.add_argument(
        "--sync-script",
        default=str(pathlib.Path(__file__).with_name("sync-home-vault.py")),
    )
    parser.add_argument("--viewer-url", default="http://192.168.3.2:8787/viewer/")
    parser.add_argument("--max-bytes", type=int, default=MAX_REQUEST_BYTES)
    parser.add_argument("--sync-timeout", type=int, default=180)
    parser.add_argument("--token", default=os.environ.get("VIBEDROP_VAULT_TOKEN", ""))
    args = parser.parse_args()

    pathlib.Path(args.vault_root).expanduser().resolve().mkdir(parents=True, exist_ok=True)
    handler = make_handler(args)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"VibeDrop Home Vault receiver listening on {args.host}:{args.port}", flush=True)
    print(f"Vault root: {pathlib.Path(args.vault_root).expanduser().resolve()}", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
