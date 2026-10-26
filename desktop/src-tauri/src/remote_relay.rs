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
