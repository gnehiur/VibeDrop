//! 惰性粘贴(1.6.1,2026-10-25)
//!
//! 1.6.0 及以前:写剪贴板 → ⌘V → 固定等 400ms → 恢复原剪贴板。可 ⌘V 只是个按键,目标 App 什么时候来剪贴板取字由它自己定;
//! Claude 桌面端忙时超过 400ms 才取,取到的已是恢复回去的旧内容——用户实测「发送并排队回车」贴出了上一条。
//! 旧内容恰好是上一条,是因为旧恢复只认纯文字/图片:剪贴板里是文件、富文本等就不恢复,上一条消息就一直留在剪贴板里。
//!
//! 现在:
//! - 剪贴板里只登记「有字符串,来取时再给」(NSPasteboardItemDataProvider)。目标 App 真来取时系统回调我们
//!   (实测回调在主线程,Tauri 主线程一直转 run loop;注入线程只等信号),交出文字、记下时刻,之后才恢复。
//! - 恢复用完整快照:每个条目的每种格式原样放回。
//! - 恢复前看 changeCount:这期间用户自己复制了新东西就不覆盖。
//! - 坑:数据被取过一次系统就缓存,再取不再回调。所以本 App 自己的剪贴板轮询在粘贴期间要停(`in_flight()`);
//!   若 ⌘V 前已被别人(剪贴板管理器之类)抢先取走,退回固定等 1.5 秒。原型与实测记录:Mini ~/Documents/vibedrop/research/1.6.1-lazy-paste/
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Condvar, Mutex};
use std::time::{Duration, Instant};

use objc2::rc::Retained;
use objc2::runtime::ProtocolObject;
use objc2::{define_class, msg_send, AllocAnyThread, DefinedClass};
use objc2_app_kit::{
    NSPasteboard, NSPasteboardItem, NSPasteboardItemDataProvider, NSPasteboardType, NSPasteboardTypeString,
    NSPasteboardWriting,
};
use objc2_foundation::{NSArray, NSData, NSObject, NSObjectProtocol, NSString};

const SETTLE_MS: u64 = 60; // 写完剪贴板到按 ⌘V
const GRACE_MS: u64 = 150; // 目标 App 取完字后再等一会儿才恢复(它可能接着取别的格式)
const EAGER_FALLBACK_MS: u64 = 1500; // ⌘V 前已被别人取走、感知不到目标 App 时的固定等待
const TIMEOUT_MS: u64 = 4000; // 一直没人来取(没贴上)也要恢复
const SNAPSHOT_MAX_BYTES: usize = 64 * 1024 * 1024;

static IN_FLIGHT: AtomicBool = AtomicBool::new(false);

/// 粘贴进行中:剪贴板轮询此时别去读(一读就把惰性数据取走缓存,感知不到目标 App 了)
pub fn in_flight() -> bool {
    IN_FLIGHT.load(Ordering::SeqCst)
}

type Signal = Arc<(Mutex<Vec<Instant>>, Condvar)>;

pub struct ProviderIvars {
    text: String,
    signal: Signal,
}

define_class!(
    // SAFETY: NSObject 没有子类化要求;本类不实现 Drop。
    #[unsafe(super = NSObject)]
    #[name = "VibeDropLazyPasteProvider"]
    #[ivars = ProviderIvars]
    pub struct LazyPasteProvider;

    unsafe impl NSObjectProtocol for LazyPasteProvider {}

    unsafe impl NSPasteboardItemDataProvider for LazyPasteProvider {
        #[unsafe(method(pasteboard:item:provideDataForType:))]
        fn provide(&self, _pasteboard: Option<&NSPasteboard>, item: &NSPasteboardItem, ty: &NSPasteboardType) {
            item.setString_forType(&NSString::from_str(&self.ivars().text), ty);
            let (lock, cv) = &*self.ivars().signal;
            if let Ok(mut times) = lock.lock() {
                times.push(Instant::now());
            }
            cv.notify_all();
        }
    }
);

impl LazyPasteProvider {
    fn new(text: &str, signal: Signal) -> Retained<Self> {
        let this = Self::alloc().set_ivars(ProviderIvars { text: text.to_string(), signal });
        unsafe { msg_send![super(this), init] }
    }
}

type Snapshot = Vec<Vec<(Retained<NSString>, Retained<NSData>)>>;

fn snapshot(pb: &NSPasteboard) -> Snapshot {
    let mut out = Vec::new();
    let mut total = 0usize;
    if let Some(items) = pb.pasteboardItems() {
        for item in items.iter() {
            let mut entry = Vec::new();
            for ty in item.types().iter() {
                if total >= SNAPSHOT_MAX_BYTES {
                    break;
                }
                if let Some(data) = item.dataForType(&ty) {
                    total += data.length();
                    entry.push((ty.clone(), data));
                }
            }
            out.push(entry);
        }
    }
    out
}

fn restore(pb: &NSPasteboard, snap: &Snapshot) {
    pb.clearContents();
    let objects: Vec<Retained<ProtocolObject<dyn NSPasteboardWriting>>> = snap
        .iter()
        .filter(|entry| !entry.is_empty())
        .map(|entry| {
            let item = NSPasteboardItem::new();
            for (ty, data) in entry {
                item.setData_forType(data, ty);
            }
            ProtocolObject::from_retained(item)
        })
        .collect();
    if !objects.is_empty() {
        pb.writeObjects(&NSArray::from_retained_slice(&objects));
    }
}

/// 剪贴板原内容里的纯文字(登记进广播抑制表,恢复后别被轮询当成新复制广播给手机)
fn snapshot_text(snap: &Snapshot) -> Option<String> {
    snap.iter().flatten().find(|(ty, _)| ty.to_string() == "public.utf8-plain-text").map(|(_, data)| {
        String::from_utf8_lossy(&data.to_vec()).to_string()
    })
}

fn snapshot_summary(snap: &Snapshot) -> String {
    if snap.is_empty() {
        return "empty".to_string();
    }
    let mut kinds: Vec<String> = Vec::new();
    for (ty, _) in snap.iter().flatten() {
        let name = ty.to_string();
        let kind = match name.as_str() {
            "public.utf8-plain-text" => "text",
            "public.rtf" | "public.html" | "com.apple.webarchive" => "rich",
            "public.file-url" => "file",
            "public.png" | "public.tiff" | "public.jpeg" => "image",
            _ => continue,
        };
        if !kinds.iter().any(|k| k == kind) {
            kinds.push(kind.to_string());
        }
    }
    let total: usize = snap.iter().flatten().map(|(_, d)| d.length()).sum();
    format!("{} items {} [{}] {}B", snap.len(), snap.iter().map(|e| e.len()).sum::<usize>(), kinds.join(","), total)
}

pub struct PasteReport {
    /// 原剪贴板概况
    pub prev: String,
    /// ⌘V 后目标 App 隔多久来取(毫秒);None = 没感知到
    pub served_ms: Option<u128>,
    /// ⌘V 前就被别人取走了(走固定等待)
    pub eager: bool,
    /// restored / skipped-user-copied
    pub restore: &'static str,
}

struct InFlightGuard;
impl Drop for InFlightGuard {
    fn drop(&mut self) {
        IN_FLIGHT.store(false, Ordering::SeqCst);
    }
}

/// 惰性写入 text → 调 send_cmd_v 按 ⌘V → 等目标 App 来取 → 完整恢复原剪贴板。
/// on_prev_text:原剪贴板里的纯文字(调用方登记广播抑制)。
pub fn paste_text(
    text: &str,
    on_prev_text: impl FnOnce(&str),
    send_cmd_v: impl FnOnce() -> Result<(), String>,
) -> Result<PasteReport, String> {
    IN_FLIGHT.store(true, Ordering::SeqCst);
    let _guard = InFlightGuard;

    let pb = NSPasteboard::generalPasteboard();
    let snap = snapshot(&pb);
    if let Some(prev_text) = snapshot_text(&snap) {
        on_prev_text(&prev_text);
    }

    let signal: Signal = Arc::new((Mutex::new(Vec::new()), Condvar::new()));
    let provider = LazyPasteProvider::new(text, signal.clone());
    let item = NSPasteboardItem::new();
    let types = NSArray::from_slice(&[unsafe { NSPasteboardTypeString }]);
    if !item.setDataProvider_forTypes(ProtocolObject::from_ref(&*provider), &types) {
        return Err("无法登记剪贴板内容".to_string());
    }
    pb.clearContents();
    if !pb.writeObjects(&NSArray::from_retained_slice(&[ProtocolObject::from_retained(item)])) {
        restore(&pb, &snap);
        return Err("无法写入剪贴板".to_string());
    }
    let ours = pb.changeCount();
    std::thread::sleep(Duration::from_millis(SETTLE_MS));

    let (lock, cv) = &*signal;
    let eager = lock.lock().map(|times| !times.is_empty()).unwrap_or(false);
    let sent = Instant::now();
    if let Err(error) = send_cmd_v() {
        restore(&pb, &snap);
        return Err(error);
    }

    let mut served_ms = None;
    if eager {
        std::thread::sleep(Duration::from_millis(EAGER_FALLBACK_MS));
    } else {
        let deadline = sent + Duration::from_millis(TIMEOUT_MS);
        let mut times = lock.lock().map_err(|_| "剪贴板信号锁失效".to_string())?;
        loop {
            if let Some(at) = times.iter().find(|at| **at >= sent) {
                served_ms = Some(at.duration_since(sent).as_millis());
                break;
            }
            let now = Instant::now();
            if now >= deadline {
                break;
            }
            times = cv.wait_timeout(times, deadline - now).map_err(|_| "剪贴板信号锁失效".to_string())?.0;
        }
        drop(times);
        if served_ms.is_some() {
            std::thread::sleep(Duration::from_millis(GRACE_MS));
        }
    }

    let restore_state = if pb.changeCount() == ours {
        restore(&pb, &snap);
        "restored"
    } else {
        "skipped-user-copied"
    };
    drop(provider);
    Ok(PasteReport { prev: snapshot_summary(&snap), served_ms, eager, restore: restore_state })
}
