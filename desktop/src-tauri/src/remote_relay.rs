//! 远程控制转发(1.6.2,2026-10-26)
//!
//! 场景:用户在 MacBook 上开着 UU远程控制 Mini,手机把字发给 MacBook。以前 MacBook 照常「写剪贴板 + ⌘V」,
//! 字要靠 UU 的剪贴板同步才到 Mini;UU 的按键比剪贴板内容先到,Mini 贴出的是上一次同步过去的旧内容(用户实测贴出上一条)。
//! 现在:最前面是远程桌面工具时,MacBook 直接连被控电脑上的 VibeDrop(WebSocket,跟手机同一套协议:auth → type*),
//! 让它在本机贴,完全不经远控工具的剪贴板。被控电脑地址与 PIN 存 ~/.vibedrop/remote-relay.json(设置页「远程控制转发」)。
//! 没配置或连不上 → 退回「写剪贴板,等远控工具同步完再按 ⌘V」(lazy_paste 的 remote 模式)。
use std::path::PathBuf;
use std::time::{Duration, Instant};

use futures_util::{SinkExt, StreamExt};
use serde::{Deserialize, Serialize};
use tokio_tungstenite::tungstenite::Message as WsMessage;

/// 远程桌面工具的 bundle id 前缀(小写比较)
const REMOTE_DESKTOP_BUNDLE_PREFIXES: &[&str] = &[
    "com.netease.uuremote", // UU远程
    "com.youqu.todesk",     // ToDesk
    "com.oray.sunlogin",    // 向日葵
    "com.teamviewer",
    "com.philandro.anydesk",
    "com.microsoft.rdc", // 微软远程桌面 / Windows App
    "com.apple.screensharing",
    "com.p5sys.jump", // Jump Desktop
    "tv.parsec",
    "com.carriez.rustdesk",
    "com.realvnc",
];

const CONNECT_TIMEOUT: Duration = Duration::from_secs(4);
const AUTH_TIMEOUT: Duration = Duration::from_secs(4);
const DELIVER_TIMEOUT: Duration = Duration::from_secs(10);

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct RelayConfig {
    #[serde(default)]
    pub url: String,
    #[serde(default)]
    pub pin: String,
}

fn config_path() -> PathBuf {
    let home = std::env::var("HOME").unwrap_or_else(|_| "/tmp".to_string());
    PathBuf::from(home).join(".vibedrop").join("remote-relay.json")
}

pub fn load() -> Option<RelayConfig> {
    let raw = std::fs::read_to_string(config_path()).ok()?;
    let cfg: RelayConfig = serde_json::from_str(&raw).ok()?;
    if cfg.url.trim().is_empty() {
        None
    } else {
        Some(cfg)
    }
}

pub fn save(cfg: &RelayConfig) -> Result<(), String> {
    let path = config_path();
    if let Some(dir) = path.parent() {
        std::fs::create_dir_all(dir).map_err(|e| e.to_string())?;
    }
    if cfg.url.trim().is_empty() {
        let _ = std::fs::remove_file(&path); // 清空 = 关掉转发(配置文件里没别的东西)
        return Ok(());
    }
    let body = serde_json::to_string_pretty(cfg).map_err(|e| e.to_string())?;
    std::fs::write(&path, body).map_err(|e| e.to_string())
}

/// 「100.1.2.3」「host:9001」「ws://host:9001/ws」都认,补齐成 ws://host:port/ws
pub fn normalize_url(raw: &str) -> String {
    let trimmed = raw.trim().trim_end_matches('/');
    if trimmed.is_empty() {
        return String::new();
    }
    let rest = trimmed.strip_prefix("ws://").unwrap_or(trimmed);
    let (host_port, path) = match rest.find('/') {
        Some(i) => (&rest[..i], &rest[i..]),
        None => (rest, "/ws"),
    };
    let host_port = if host_port.contains(':') { host_port.to_string() } else { format!("{host_port}:9001") };
    format!("ws://{host_port}{path}")
}

/// 最前面 App 的 bundle id(lsappinfo 输出形如 `"CFBundleIdentifier"="com.apple.Terminal"`)
pub fn front_bundle_id() -> String {
    let run = |args: &[&str]| -> String {
        std::process::Command::new("/usr/bin/lsappinfo")
            .args(args)
            .output()
            .ok()
            .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string())
            .unwrap_or_default()
    };
    let asn = run(&["front"]);
    if asn.is_empty() {
        return String::new();
    }
    let line = run(&["info", "-only", "bundleid", &asn]);
    line.lines().next().and_then(|l| l.split('"').nth(3)).unwrap_or("").to_string()
}

pub fn is_remote_desktop(bundle_id: &str) -> bool {
    let id = bundle_id.to_ascii_lowercase();
    !id.is_empty() && REMOTE_DESKTOP_BUNDLE_PREFIXES.iter().any(|prefix| id.starts_with(prefix))
}

pub enum RelayError {
    /// 字还没交出去(连不上、PIN 错):可以退回本机粘贴
    BeforeSend(String),
    /// 字已交出去,但没等到结果:被控电脑可能已经贴了,不能再本机贴一遍
    AfterSend(String),
}

type Ws = tokio_tungstenite::WebSocketStream<tokio_tungstenite::MaybeTlsStream<tokio::net::TcpStream>>;

/// 等下一条带 status 的回复(期间对方可能推剪贴板等别的消息,跳过)
async fn wait_status(ws: &mut Ws, limit: Duration) -> Result<serde_json::Value, String> {
    let deadline = Instant::now() + limit;
    loop {
        let left = deadline.saturating_duration_since(Instant::now());
        if left.is_zero() {
            return Err("等回复超时".to_string());
        }
        match tokio::time::timeout(left, ws.next()).await {
            Err(_) => return Err("等回复超时".to_string()),
            Ok(None) => return Err("连接被关闭".to_string()),
            Ok(Some(Err(e))) => return Err(format!("连接出错: {e}")),
            Ok(Some(Ok(WsMessage::Text(text)))) => {
                if let Ok(value) = serde_json::from_str::<serde_json::Value>(text.as_str()) {
                    if value.get("status").is_some() {
                        return Ok(value);
                    }
                }
            }
            Ok(Some(Ok(_))) => {}
        }
    }
}

async fn connect_and_auth(cfg: &RelayConfig, device_id: &str, device_name: &str) -> Result<(Ws, String), String> {
    let url = normalize_url(&cfg.url);
    let (mut ws, _) = tokio::time::timeout(CONNECT_TIMEOUT, tokio_tungstenite::connect_async(url.as_str()))
        .await
        .map_err(|_| "连接被控电脑超时".to_string())?
        .map_err(|e| format!("连接被控电脑失败: {e}"))?;
    let auth = serde_json::json!({
        "action": "auth",
        "pin": cfg.pin.trim(),
        "device_id": device_id,
        "device_name": device_name,
        "device_role": "relay",
    });
    ws.send(WsMessage::Text(auth.to_string().into())).await.map_err(|e| format!("发送认证失败: {e}"))?;
    let reply = wait_status(&mut ws, AUTH_TIMEOUT).await?;
    if reply.get("status").and_then(|s| s.as_str()) != Some("ok") {
        let error = reply.get("error").and_then(|e| e.as_str()).unwrap_or("认证失败").to_string();
        return Err(error);
    }
    let host = reply.get("hostname").and_then(|h| h.as_str()).unwrap_or("").to_string();
    Ok((ws, host))
}

/// 设置页「测试连接」:只认证,返回对方主机名
pub async fn check(cfg: &RelayConfig, device_id: &str, device_name: &str) -> Result<String, String> {
    let (mut ws, host) = connect_and_auth(cfg, device_id, device_name).await?;
    let _ = ws.close(None).await;
    Ok(host)
}

/// 把文字交给被控电脑的 VibeDrop 在它本机输入。action:type / type_enter / type_cmd_enter
pub async fn relay_text(
    cfg: &RelayConfig,
    action: &str,
    text: &str,
    device_id: &str,
    device_name: &str,
) -> Result<String, RelayError> {
    let (mut ws, host) = connect_and_auth(cfg, device_id, device_name).await.map_err(RelayError::BeforeSend)?;
    let message = serde_json::json!({ "action": action, "text": text });
    ws.send(WsMessage::Text(message.to_string().into()))
        .await
        .map_err(|e| RelayError::BeforeSend(format!("发送失败: {e}")))?;
    let reply = wait_status(&mut ws, DELIVER_TIMEOUT).await.map_err(RelayError::AfterSend)?;
    let _ = ws.close(None).await;
    if reply.get("status").and_then(|s| s.as_str()) == Some("ok") {
        Ok(host)
    } else {
        // 对方明确报错(如辅助功能权限没给)= 没贴上,可以退回本机
        Err(RelayError::BeforeSend(
            reply.get("error").and_then(|e| e.as_str()).unwrap_or("被控电脑输入失败").to_string(),
        ))
    }
}

// ---- 剪贴板图片转发(1.8.0,2026-10-26)----
// 场景:iPhone 上复制图片 → 苹果通用剪贴板放进 MacBook 剪贴板 → 想在 UU远程里的 Mini 上 ⌘V。
// UU 不传图片内容:只在 Mini 上建个 0 字节占位文件(~/Library/Application Support/com.netease.uuremote.server/Clipboard/.uuremote_*),
// 把它的文件地址放进剪贴板,贴出来是一行路径(用户实测)。
// 现在:MacBook 剪贴板出现图片、最前面又是远控工具、且配了转发时,把图片原始数据(不重新编码,TIFF/HEIC 也行)转给被控电脑的
// VibeDrop,由它写进自己的剪贴板;UU 随后写来的占位文件会被盖回去(put_clipboard_image + rewrite_if_placeholder)。
// 不打转:UU 把 Mini 剪贴板反向同步回 MacBook 时是文件地址不是图片;同一张图只转一次;VibeDrop 自己粘贴/恢复引起的变化不算。
use base64::Engine as _;
use objc2_app_kit::NSPasteboard;
use objc2_foundation::{NSData, NSString};

/// 按优先级挑剪贴板里的图片格式;同一张图多种格式都在时取最小的那份(WebSocket 单帧上限 16MB)
const IMAGE_TYPES: &[&str] = &["public.png", "public.jpeg", "public.heic", "public.tiff"];
const IMAGE_MAX_BYTES: usize = 11 * 1024 * 1024; // base64 后约 15MB,留在 16MB 帧上限内
const UU_PLACEHOLDER_MARK: &str = "com.netease.uuremote.server/Clipboard";

fn pasteboard_types(pb: &NSPasteboard) -> Vec<String> {
    pb.types().map(|types| types.iter().map(|t| t.to_string()).collect()).unwrap_or_default()
}

/// 剪贴板里的图片(格式, 原始字节);有文件地址的(拷文件、UU 占位)不算
fn read_clipboard_image(pb: &NSPasteboard) -> Option<(String, Vec<u8>)> {
    let types = pasteboard_types(pb);
    if types.iter().any(|t| t == "public.file-url") {
        return None;
    }
    let mut best: Option<(String, Vec<u8>)> = None;
    for ty in IMAGE_TYPES {
        if !types.iter().any(|t| t == ty) {
            continue;
        }
        if let Some(data) = pb.dataForType(&NSString::from_str(ty)) {
            let bytes = data.to_vec();
            if !bytes.is_empty() && best.as_ref().map(|(_, b)| bytes.len() < b.len()).unwrap_or(true) {
                best = Some((ty.to_string(), bytes));
            }
        }
    }
    best
}

/// 被控电脑一侧:图片原样写进剪贴板,返回写完后的 changeCount
pub fn put_clipboard_image(uti: &str, bytes: &[u8]) -> Result<isize, String> {
    if !IMAGE_TYPES.contains(&uti) {
        return Err(format!("不认识的图片格式: {uti}"));
    }
    let pb = NSPasteboard::generalPasteboard();
    pb.clearContents();
    if !pb.setData_forType(Some(&NSData::with_bytes(bytes)), &NSString::from_str(uti)) {
        return Err("写入剪贴板失败".to_string());
    }
    Ok(pb.changeCount())
}

/// UU 晚到一步、用占位文件盖掉了刚写进去的图片 → 写回。返回是否写回了
pub fn rewrite_if_placeholder(uti: &str, bytes: &[u8], ours: isize) -> bool {
    let pb = NSPasteboard::generalPasteboard();
    if pb.changeCount() == ours {
        return false;
    }
    let url = pb.stringForType(&NSString::from_str("public.file-url")).map(|s| s.to_string()).unwrap_or_default();
    let decoded = url.replace("%20", " ");
    if !decoded.contains(UU_PLACEHOLDER_MARK) {
        return false; // 是用户自己又复制了别的,不碰
    }
    put_clipboard_image(uti, bytes).is_ok()
}

async fn relay_image(
    cfg: &RelayConfig,
    uti: &str,
    bytes: &[u8],
    device_id: &str,
    device_name: &str,
) -> Result<String, String> {
    let (mut ws, host) = connect_and_auth(cfg, device_id, device_name).await?;
    let message = serde_json::json!({
        "action": "relay_clipboard_image",
        "mime_type": uti,
        "image_base64": base64::engine::general_purpose::STANDARD.encode(bytes),
    });
    ws.send(WsMessage::Text(message.to_string().into())).await.map_err(|e| format!("发送失败: {e}"))?;
    let reply = wait_status(&mut ws, Duration::from_secs(20)).await?;
    let _ = ws.close(None).await;
    if reply.get("status").and_then(|s| s.as_str()) == Some("ok") {
        Ok(host)
    } else {
        Err(reply.get("error").and_then(|e| e.as_str()).unwrap_or("被控电脑写剪贴板失败").to_string())
    }
}

/// MacBook 一侧常驻线程:每 0.5 秒看一次剪贴板,满足条件就把图片转给被控电脑
pub fn watch_clipboard_images(device_id: String, device_name: String) {
    let Ok(rt) = tokio::runtime::Builder::new_current_thread().enable_all().build() else {
        return;
    };
    let pb = NSPasteboard::generalPasteboard();
    let mut last_count = pb.changeCount();
    let mut last_hash: u64 = 0;
    loop {
        std::thread::sleep(Duration::from_millis(500));
        let count = pb.changeCount();
        if count == last_count {
            continue;
        }
        last_count = count;
        if crate::lazy_paste::in_flight() || crate::lazy_paste::is_own_change(count) {
            continue;
        }
        let Some(cfg) = load() else { continue };
        let front = front_bundle_id();
        if !is_remote_desktop(&front) {
            continue;
        }
        let started = Instant::now();
        let Some((uti, bytes)) = read_clipboard_image(&pb) else { continue };
        let hash = {
            use std::hash::{Hash, Hasher};
            let mut hasher = std::collections::hash_map::DefaultHasher::new();
            bytes.hash(&mut hasher);
            hasher.finish()
        };
        if hash == last_hash {
            continue;
        }
        last_hash = hash;
        let read_ms = started.elapsed().as_millis();
        let result = if bytes.len() > IMAGE_MAX_BYTES {
            Err(format!("图片太大({} 字节),跳过", bytes.len()))
        } else {
            rt.block_on(relay_image(&cfg, &uti, &bytes, &device_id, &device_name))
        };
        crate::append_debug_log(
            "relay",
            "clipboard_image",
            serde_json::json!({
                "type": uti,
                "bytes": bytes.len(),
                "read_ms": read_ms,
                "total_ms": started.elapsed().as_millis(),
                "remote_app": front,
                "ok": result.is_ok(),
                "host": result.as_ref().ok(),
                "error": result.as_ref().err(),
            }),
        );
    }
}
