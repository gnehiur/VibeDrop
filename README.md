[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md)

<div align="center">

<img src="docs/logo.png" width="120" alt="VibeDrop logo">

# VibeDrop

**手机与 Mac 之间的剪贴板同步、文字与文件传输工具 —— 局域网直连，无云依赖**

[![release](https://img.shields.io/github/v/release/jncdke/VibeDrop?color=2f6fed)](https://github.com/jncdke/VibeDrop/releases)
[![license](https://img.shields.io/github/license/jncdke/VibeDrop?color=green)](LICENSE)
![platform](https://img.shields.io/badge/platform-macOS%20%7C%20Android%20%7C%20iOS-8a63d2)
![i18n](https://img.shields.io/badge/languages-11-2f6fed)
![tauri](https://img.shields.io/badge/Tauri-2.x-ffc131?logo=tauri&logoColor=white)
![rust](https://img.shields.io/badge/Rust-stable-e43717?logo=rust)

[下载 Release](https://github.com/jncdke/VibeDrop/releases) · [功能一览](#功能一览) · [消息自我研究](#消息自我研究词频统计报告)

</div>

---

VibeDrop 由三端组成，通过 **WebSocket** 在局域网内直连通信，无需互联网、无需云服务：

- **Mac 桌面端**（`desktop/`）— 接收文字/文件、剪贴板广播、系统托盘
- **手机端**（`mobile/`，Android + iOS）— 发送文字/图片/视频/文件、历史时间线
- **Home Vault**（`scripts/`）— 家庭服务器:跨设备历史合并、媒体原件仓、探针日志回收

---

## 截图

**智能发送卡「跟随光标发送」**——手机说话,文字自动落到光标所在的那台电脑(通用控制场景):

<div align="center">
<table>
  <tr>
    <td align="center" colspan="2"><img src="assets/screenshots/desktop-overview.jpg" width="680" alt="macOS 桌面端概览"><br><sub>macOS 桌面端 — 设备总览 · 配对 · 拖入即发</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/screenshots/ios-smart-card.png" width="320" alt="iOS 智能发送卡"><br><sub>iOS (iPhone 17 Pro Max)</sub></td>
    <td align="center"><img src="assets/screenshots/android-smart-card.jpg" width="320" alt="Android 智能发送卡"><br><sub>Android (一加 Ace 5)</sub></td>
  </tr>
</table>
</div>

---

## 功能一览

| 功能 | Mac 端 | 手机端 (Android + iOS) |
|------|--------|------------------------|
| 🎯 智能发送卡「跟随光标发送」 | ✅ 上报键鼠活动（`CGEventSource`，零权限） | ✅ 文字/图片/文件自动发往光标所在的 Mac，1 秒跟随，可手动切换 |
| 📝 文字传输（手机 → Mac） | ✅ 接收并模拟键盘输入 | ✅ 发送后键盘与语音输入保持，连续口述零多余动作 |
| 📋 剪贴板同步（Mac → 手机） | ✅ 监听变化广播 | ✅ 原生后台服务写入剪贴板 |
| 🌍 多语言 | ✅ 跟随系统 | ✅ 11 门语言（简繁中/英/日/韩/西/法/德/俄/斯瓦希里/克丘亚），gettext 式缺译回退中文 |
| 🤝 自动发现与配对 | ✅ 展示待确认配对、已连接设备 | ✅ 扫描附近电脑、验证码配对；设备可改名并跨手机自动同步 |
| 📜 历史时间线 | ✅ 合并全设备视图 + 缩略图 | ✅ 全设备合并、筛选（来源/目标/类型/原件/时间）、搜索高亮 |
| 📈 活跃热力图 | ✅ 接收热力图 + 点格筛选 | ✅ 发送热力图 + 点格筛选 |
| 🔬 消息自我研究 | —（报告由 Home Vault 生成） | ✅ 历史页内嵌完整报告：词云/口头禅/发送趋势柱状图（scrub 查明细） |
| 📁 文件传输（双向） | ✅ 拖拽 / Finder 服务 / Finder 共享 | ✅ 传到收件箱 / 图片进相册，批量自动打包 |
| 🗄 Home Vault | 家庭服务器：跨设备历史合并 · 媒体原件仓（哈希去重 + Range 流式） · 探针日志回收 | ✅ 增量推送 + SSE 实时同步 |
| 🔒 PIN 码认证 | ✅ 随机生成，持久化到文件 | ✅ 验证码配对后自动保存 |
| 🕰 显示时区设置 | ✅ 本机/北京/美西，显示与统计口径统一 | — |
| 📡 前台保活 / 托盘 | ✅ 系统托盘 + 开机自启 | ✅ Android 通知栏常驻 |

---

## 技术架构总览

```
        ┌────────────────────────────┐      ┌────────────────────────────┐
        │   Mac 桌面端 × N (Tauri 2) │      │  手机端 × N (Tauri 2 Mobile)│
        │  ├ Axum HTTP/WS :9001      │◄────►│  ├ app.js  单文件前端       │
        │  ├ enigo 键盘模拟          │  WS  │  ├ lib.rs  16 个原生命令    │
        │  ├ arboard 剪贴板监听      │      │  ├ Kotlin  保活/播放器/剪贴板│
        │  ├ CGEventSource 活动上报  │      │  └ iOS     滚动锁(KVO)      │
        │  └ UDP/HTTP 发现应答       │      └──────────────┬─────────────┘
        └──────────────┬─────────────┘                     │
                       │              HTTP :8788           │
                       ▼                                   ▼
        ┌──────────────────────────────────────────────────────────┐
        │        Home Vault (家庭服务器, home-vault-receiver.py)     │
        │  跨设备历史合并 · 媒体原件仓(哈希去重+Range) · SSE 广播     │
        │  设备名公告板 · 探针日志回收 · 自我研究报告(SWR)            │
        └──────────────────────────────────────────────────────────┘
```

三条通信路径,全部局域网直连、无云依赖:

1. **手机 ↔ Mac**:WebSocket(`:9001/ws`),PIN 认证后传文字/文件/剪贴板/活动查询;
2. **所有端 → Home Vault**:HTTP(`:8788`),历史增量推送、媒体上传、报告获取;
3. **Vault → 客户端**:SSE 长连接(`/api/events`),历史落盘即广播,25s 心跳保活。

---

## 核心流程详解

### 智能发送卡「跟随光标发送」

1. 桌面端收到 `activity_query` 时调用 `CGEventSourceSecondsSinceLastEventType`
   (零权限、零线程——读系统为屏保维护的现成账本)回答"距上次键鼠活动几秒";
2. 手机每 1 秒轮询所有已连接 Mac,比较**相对空闲秒数**(免疫两机时钟偏差),
   最新鲜者即光标所在——通用控制把键鼠事件真实送达光标所在的机器,信号与事实强耦合;
3. 发送(文字/图片/文件)瞬间锁定目标;指示器可点击在自动/手动间循环。

### 发现与配对

手机端并行两路扫描:UDP 广播 + HTTP 探测(`discover_desktops`),发现桌面端后走
验证码配对(桌面端弹待确认卡,双方核对同一验证码),通过即保存并自动连接。
设备自定义名保存后经 Vault 公告板(`/api/device-names`,serverId 为键,LWW)跨手机同步。

### 文字与文件

- 文字:`type` / `type_enter` 动作,桌面端 enigo 模拟键盘落字;外出模式改走
  `clipboard_text`(只写剪贴板,配合 UU 远程等远控工具);
- 文件:分块传输协议(begin/append/finish/cancel),手机端进收件箱或相册,
  Mac 端拖拽/Finder 服务即发;全链路带 `transferId` 传输单号,收发两端记录可精确归并;
- 发送按钮拒抢焦点(mousedown preventDefault):键盘与语音输入会话在发送后保持,
  连续口述零多余动作。

### 历史同步(增量 + 实时)

- 每端本地历史 + 推送游标(`lastPushedEntryId`),只推增量(实测单条 3ms/188B);
- Vault 合并全设备时间线(`/api/history/merged`),客户端平时拉 2000 条轻量、
  每会话一次 10000 条深拉;SSE 一到即刷;
- 同名身份自动归并(重装换随机 ID 的"前世"折进本机),名字是展示层、身份靠指纹。

### 媒体原件仓

原件按 SHA-256 入仓(`/api/media/upload`,流式+去重,2GB 上限),任何设备凭哈希
在线取原件(`/api/media/blob/<hash>`,支持 Range 流式播放)——"本机丢≠全网丢"。

### 启动自检探针(黑匣子)

`app.js` 顶端安装 window.onerror 捕获 + probe() 打点,启动 6 秒/出错 1.5 秒
POST 到 Vault `/api/client-log` 按设备落盘。真机黑屏/白屏类问题不猜,读日志定位。

---

## 代码地图

### Mac 桌面端 `desktop/`

| 文件 | 行数 | 职责 |
|------|------|------|
| `src-tauri/src/main.rs` | ~4900 | HTTP/WS 服务器、PIN 认证、enigo 键盘、arboard 剪贴板、文件收发、托盘、发现应答、活动上报 |
| `src/main.js` | ~2600 | 桌面 UI:设备总览、配对确认、合并历史+缩略图、接收热力图、时区设置、拖拽发送 |
| `src/style.css` | ~2000 | 桌面样式 |
| `static/*` | — | `mobile/src/` 的逐字节镜像(改手机端后必须同步拷贝,见构建一节) |

### 手机端 `mobile/`(Android + iOS 同一份代码)

| 文件 | 行数 | 职责 |
|------|------|------|
| `src/app.js` | ~11500 | 全部前端逻辑:智能卡、多设备连接、历史时间线(筛选/搜索高亮/虚拟滚动)、热力图、vault 同步、媒体查看器、探针 |
| `src/i18n.js` | ~110 | gettext 式多语言运行时:t()/回退/插值/语言检测/词典缓存 |
| `src/locales/*.json` | ×10 | 语言包(中文原文即钥匙,新语言=加一个文件) |
| `src-tauri/src/lib.rs` | ~1900 | 16 个原生命令:历史持久化、分块收文件、发现配对、机型识别、vault 媒体上传、路径解析;iOS 滚动锁(KVO 观察 contentOffset 渲染前归零) |
| `gen/android/.../MainActivity.kt` | — | 控制台转发(VibeDropConsole)+ 委托原 WebChromeClient(文件选择器等) |
| `gen/android/.../KeepAliveService.kt` | — | 前台保活 |
| `gen/android/.../VideoPlayerActivity.kt` | — | ExoPlayer(Media3)原生全屏播放器 |
| `gen/android/.../BackgroundClipboardSyncManager.kt` | — | 原生后台剪贴板写入 |

### Home Vault 与工具 `scripts/`

| 脚本 | 职责 |
|------|------|
| `home-vault-receiver.py` (~1000 行) | 家庭服务器全部端点(见下表);launchd 常驻 |
| `message-self-study.py` | jieba 全套语料分析 → 自包含 HTML 报告(含发送趋势柱状图) |
| `vault-media-uploader.py` / `sync-home-vault.py` | 存量媒体补传 / 历史落盘同步 |
| `i18n-check.py` | 多语言质检门:扫 t()/data-i18n 全部钥匙,对照语言包报缺漏冗余 |
| `deploy-android.sh` / `deploy-desktop.sh` / `deploy-ios.sh` | 三端一键构建部署 |
| `generate-app-icons.py` / `generate-tray-frames.py` | 品牌资产生成 |

### Home Vault 端点速查

| 端点 | 作用 |
|------|------|
| `POST /api/history/append` · `GET /api/history/merged` | 增量入库 / 合并时间线 |
| `GET /api/events` | SSE:落盘即广播 |
| `POST /api/media/upload` · `/lookup` · `GET /api/media/blob/<hash>` | 媒体仓:去重入库/查询/Range 流式取 |
| `GET/POST /api/device-names` | 设备名公告板(LWW) |
| `POST /api/client-log` | 探针黑匣子回收 |
| `GET /report/self-study` | 自我研究报告(SWR:秒出缓存,过期后台重算,`?refresh=1` 强刷) |

---

## 平台要点(踩坑结晶)

### WebView 内核差异(重要)

| | Android | iOS | macOS 桌面 |
|---|---------|-----|-----------|
| 内核 | Chromium | **WKWebView** | **WKWebView(同 iOS!)** |
| `content-visibility: auto` | ✅ 原生虚拟化 | ❌ 黑屏 | ❌ 滚动空白 |
| 长列表方案 | content-visibility | JS 虚拟滚动 | 分片挂载 |
| `Intl.Segmenter` 中文分词 | ❌ 切单字 | ✅ 完整词典 | ✅ |

**结论:跨内核的中文分词只能服务端 jieba;content-visibility 只许用在 Android。**

### iOS

- **固定布局**:外层 WKWebView 滚动为应用壳架构禁用(`isScrollEnabled=false` 只挡手势,
  WebKit 键盘揭示走程序化滚动,须再用 **KVO 观察 contentOffset 渲染前归零**;
  钉的"原点"是 `-adjustedContentInset` 系统静止位,不是 (0,0));锁在每次回前台补挂;
- 出包铁律:`cargo tauri ios build --export-method debugging`,不能直接 Xcode Run;
- 免费签名 7 天有效(自创建日起算),需自动续签流水线配合。

### Android

- 定制 WebChromeClient **必须委托原 client**(onShowFileChooser 等),整体替换会弄哑文件选择器;
- console 真身看 `adb logcat -d VibeDropConsole:I "*:S"`;
- 启动时 5 条 "Cannot redefine property" 报错是 Tauri 注入脚本双重执行的良性噪音,勿追查。

### Mac

- enigo 键盘模拟跑独立线程;剪贴板 500ms 轮询 → broadcast channel → 各 WS 连接;
- 桌面端二进制内部名仍是 `voicedrop`(pgrep 时注意)。

---

## 多语言(i18n)

gettext 流派:**中文原文即钥匙**,`t('发送并回车')` 查当前语言词典,缺译回退中文原文
(改一半也永远可发布)。带变量用占位符 `t('已改名为 {name}', {name})`,严禁字符串拼接。
现有 11 门语言;新增语言 = `locales/<lang>.json` 一个文件 + `i18n.js` 映射表一行。

- 质检门:`python3 scripts/i18n-check.py --strict`(键覆盖/占位符完整性);
- 语义验收:每门语言 30 核心词人工精读(机器保不了语义,详见 `docs/i18n-规范.md`);
- 语言选择器中语言名用**语言自称**并附中英注音,任何语言包不翻译它们。

---

## 构建与部署

```bash
# Android(需 cargo + Android SDK 于 PATH)
./scripts/deploy-android.sh          # 构建签名 APK + adb 安装启动

# macOS 桌面端
./scripts/deploy-desktop.sh          # 构建 + 本地自签 + 装入 /Applications
#   --skip-build --skip-icons        # 复用现成产物只重装(异机编译后拷贝场景)

# iOS(必须走 Tauri 管线)
cd mobile/src-tauri && cargo tauri ios build --export-method debugging
xcrun devicectl device install app --device <UDID> gen/apple/build/arm64/VibeDrop.ipa
```

**纪律两条**:

1. `mobile/src/` 的 app.js / index.html / style.css / i18n.js / locales/ 改动后
   **必须同步拷贝到 `desktop/static/`**(桌面端 HTTP 服务的手机浏览器版);
2. **两个 Tauri 构建不能并发**(共用本地 IPC 通道会撞),必须串行。

---

## GitHub 发布

推 `v*` tag 触发 `release.yml`:自动构建签名 APK + macOS dmg 并发布 GitHub Release;
`ci.yml` 每次 push 跑构建检查与 Python 单测。

```bash
git tag -a v0.x.y -m "说明" && git push origin v0.x.y
```

---

## 消息自我研究(词频统计报告)

对你自己的 Home Vault 历史语料做分词词频/口头禅/高频短语/月度话题演变(TF-IDF)/发送趋势(时/天粒度柱状图,手指 scrub 查明细)分析,生成自包含 HTML 报告(全程本地,数据不外发)。

**App 内直接看**:历史页 →「消息自我研究」卡 → 打开完整报告(Home Vault 端点 `/report/self-study`,SWR 缓存秒开,过期后台重算,`?refresh=1` 强制重跑)。

也可手动生成:

```bash
python3 -m venv .venv && .venv/bin/pip install jieba
.venv/bin/python scripts/message-self-study.py http://<你的vault地址>:8788
```

报告输出到 `~/Downloads/`。多语言施工契约见 `docs/i18n-规范.md`。
