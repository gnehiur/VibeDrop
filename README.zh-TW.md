[简体中文](README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Русский](README.ru.md) | [Kiswahili](README.sw.md) | [Runasimi](README.qu.md)

<div align="center">

<img src="docs/logo.png" width="120" alt="VibeDrop logo">

# VibeDrop

**手機與 Mac 之間的剪貼簿同步、文字與檔案傳輸工具 —— 區域網路直接連線，不依賴雲端**

[![release](https://img.shields.io/github/v/release/gnehiur/VibeDrop?color=2f6fed)](https://github.com/gnehiur/VibeDrop/releases)
[![license](https://img.shields.io/github/license/gnehiur/VibeDrop?color=green)](LICENSE)
![platform](https://img.shields.io/badge/platform-macOS%20%7C%20Android%20%7C%20iOS-8a63d2)
![i18n](https://img.shields.io/badge/languages-11-2f6fed)
![tauri](https://img.shields.io/badge/Tauri-2.x-ffc131?logo=tauri&logoColor=white)
![rust](https://img.shields.io/badge/Rust-stable-e43717?logo=rust)

[下載 Release](https://github.com/gnehiur/VibeDrop/releases) · [功能一覽](#功能一覽) · [訊息自我研究](#訊息自我研究詞頻統計報告)

</div>

---

VibeDrop 由三端組成，透過 **WebSocket** 在區域網路內直接連線通訊，不需要網際網路，也不需要雲端服務：

- **Mac 桌面端**（`desktop/`）— 接收文字／檔案、廣播剪貼簿、系統匣
- **手機端**（`mobile/`，Android + iOS）— 傳送文字／圖片／影片／檔案、歷史時間軸
- **Home Vault**（`scripts/`）— 家用伺服器：跨裝置歷史合併、媒體原始檔倉庫、探針日誌回收

---

## 截圖

**智慧發送卡「跟隨遊標發送」**——對手機說話，文字就會自動落到遊標所在的那台電腦（通用控制使用情境）：

<div align="center">
<table>
  <tr>
    <td align="center" colspan="2"><img src="assets/screenshots/desktop-overview.jpg" width="680" alt="macOS 桌面端概覽"><br><sub>macOS 桌面端 — 裝置總覽 · 配對 · 拖入即傳</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/screenshots/ios-smart-card.png" width="320" alt="iOS 智慧發送卡"><br><sub>iOS (iPhone 17 Pro Max)</sub></td>
    <td align="center"><img src="assets/screenshots/android-smart-card.jpg" width="320" alt="Android 智慧發送卡"><br><sub>Android (一加 Ace 5)</sub></td>
  </tr>
</table>
</div>

---

## 功能一覽

| 功能 | Mac 端 | 手機端（Android + iOS） |
|------|--------|------------------------|
| 🎯 智慧發送卡「跟隨遊標發送」 | ✅ 回報鍵盤與滑鼠活動（`CGEventSource`，零權限） | ✅ 文字／圖片／檔案自動傳往遊標所在的 Mac，1 秒內跟隨，也可手動切換 |
| 📝 文字傳輸（手機 → Mac） | ✅ 接收並模擬鍵盤輸入 | ✅ 傳送後保持鍵盤與語音輸入，連續口述不需要多餘操作 |
| 📋 剪貼簿同步（Mac → 手機） | ✅ 監聽變更並廣播 | ✅ 原生背景服務寫入剪貼簿 |
| 🌍 多語言 | ✅ 跟隨系統 | ✅ 11 種語言（簡／繁中、英、日、韓、西、法、德、俄、斯瓦希里、克丘亞），gettext 式缺譯時回退中文 |
| 🤝 自動探索與配對 | ✅ 顯示待確認配對、已連線裝置 | ✅ 掃描附近的 Mac、以驗證碼配對；裝置可重新命名，並跨手機自動同步 |
| 📜 歷史時間軸 | ✅ 合併所有裝置的檢視 + 縮圖 | ✅ 合併所有裝置、篩選（來源／目標／類型／原始檔／時間）、搜尋醒目提示 |
| 📈 活躍熱力圖 | ✅ 接收熱力圖 + 點選方格篩選 | ✅ 傳送熱力圖 + 點選方格篩選 |
| 🔬 訊息自我研究 | —（報告由 Home Vault 產生） | ✅ 歷史頁內嵌完整報告：文字雲／口頭禪／傳送趨勢長條圖（滑動查看明細） |
| 📁 檔案傳輸（雙向） | ✅ 拖放 / Finder 服務 / Finder 分享 | ✅ 傳送至收件匣 / 圖片進相簿，批次內容自動打包 |
| 🗄 Home Vault | 家用伺服器：跨裝置歷史合併 · 媒體原始檔倉庫（雜湊去重 + Range 串流）· 探針日誌回收 | ✅ 增量推送 + SSE 即時同步 |
| 🔒 PIN 碼驗證 | ✅ 隨機產生，持久化到檔案 | ✅ 以驗證碼配對後自動儲存 |
| 🕰 顯示時區設定 | ✅ 本機／北京／美西，顯示與統計基準一致 | — |
| 📡 前景保活 / 系統匣 | ✅ 系統匣 + 開機自動啟動 | ✅ Android 通知列常駐 |

---

## 技術架構總覽

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

三條通訊路徑，全都在區域網路內直接連線，不依賴雲端：

1. **手機 ↔ Mac**：WebSocket（`:9001/ws`），通過 PIN 驗證後傳輸文字／檔案／剪貼簿／活動查詢；
2. **所有端 → Home Vault**：HTTP（`:8788`），推送歷史增量、上傳媒體、取得報告；
3. **Vault → 用戶端**：SSE 長連線（`/api/events`），歷史寫入磁碟後立即廣播，以 25 秒心跳保持連線。

---

## 核心流程詳解

### 智慧發送卡「跟隨遊標發送」

1. 桌面端收到 `activity_query` 時呼叫 `CGEventSourceSecondsSinceLastEventType`，
   以零權限、零執行緒的方式——讀取系統為螢幕保護程式維護的現成記錄——回答「距離上次鍵盤或滑鼠活動有幾秒」；
2. 手機每 1 秒輪詢所有已連線的 Mac，比較**相對閒置秒數**（不受兩台電腦時鐘誤差影響）。
   最新鮮的那台就是遊標所在的電腦——通用控制會把真實的鍵盤與滑鼠事件送到遊標所在的電腦，因此訊號與事實緊密相連；
3. 在傳送文字／圖片／檔案的瞬間鎖定目標；點選指示器可在自動／手動之間循環切換。

### 探索與配對

手機端同時透過兩條路徑掃描：UDP 廣播 + HTTP 探測（`discover_desktops`）。探索到桌面端後進行驗證碼配對（桌面端顯示待確認卡片，雙方核對相同驗證碼），通過後立即儲存並自動連線。
儲存自訂裝置名稱後，透過 Vault 公告板（`/api/device-names`，以 serverId 為鍵，LWW）在不同手機間同步。

### 文字與檔案

- 文字：使用 `type` / `type_enter` 動作，由桌面端透過 enigo 模擬鍵盤輸入；外出模式則改走
  `clipboard_text`（只寫入剪貼簿，搭配 UU 遠端等遠端控制工具）；
- 檔案：使用分塊傳輸協定（begin/append/finish/cancel），手機端存入收件匣或相簿，
  Mac 端透過拖放／Finder 服務立即傳送；全鏈路附帶 `transferId` 傳輸單號，能精確合併收發兩端的記錄；
- 傳送按鈕不搶焦點（mousedown preventDefault）：傳送後繼續保持鍵盤與語音輸入工作階段，
  連續口述不需要多餘操作。

### 歷史同步（增量 + 即時）

- 每一端都有本機歷史 + 推送游標（`lastPushedEntryId`），只推送增量（實測單筆 3 ms/188 B）；
- Vault 合併所有裝置的時間軸（`/api/history/merged`），用戶端平時輕量拉取 2,000 筆，
  每個工作階段進行一次 10,000 筆深度拉取；收到 SSE 後立即重新整理；
- 同名身分會自動合併（重新安裝後產生的隨機 ID「前世」會摺入本機）；名稱屬於顯示層，身分則依靠指紋。

### 媒體原始檔倉庫

原始檔依 SHA-256 存入倉庫（`/api/media/upload`，串流 + 去重，上限 2 GB），任何裝置都能憑雜湊在線取得原始檔（`/api/media/blob/<hash>`，支援 Range 串流播放）——「本機遺失 ≠ 全網遺失」。

### 啟動自我檢查探針（黑盒子）

`app.js` 頂端安裝 window.onerror 捕捉 + probe() 埋點，啟動 6 秒後／出錯 1.5 秒後 POST 到 Vault `/api/client-log`，依裝置寫入磁碟。遇到真機黑畫面／白畫面問題時不靠猜測，直接讀日誌定位。

---

## 程式碼地圖

### Mac 桌面端 `desktop/`

| 檔案 | 行數 | 職責 |
|------|------|------|
| `src-tauri/src/main.rs` | ~4900 | HTTP/WS 伺服器、PIN 驗證、enigo 鍵盤、arboard 剪貼簿、檔案收發、系統匣、探索回應、活動回報 |
| `src/main.js` | ~2600 | 桌面 UI：裝置總覽、配對確認、合併歷史 + 縮圖、接收熱力圖、時區設定、拖放傳送 |
| `src/style.css` | ~2000 | 桌面樣式 |
| `static/*` | — | `mobile/src/` 的逐位元組鏡像（修改手機端後必須同步複製，請參閱建置章節） |

### 手機端 `mobile/`（Android + iOS 共用同一份程式碼）

| 檔案 | 行數 | 職責 |
|------|------|------|
| `src/app.js` | ~11500 | 所有前端邏輯：智慧發送卡、多裝置連線、歷史時間軸（篩選／搜尋醒目提示／虛擬捲動）、熱力圖、Vault 同步、媒體檢視器、探針 |
| `src/i18n.js` | ~110 | gettext 式多語言執行階段：t()/回退/插值/語言偵測/字典快取 |
| `src/locales/*.json` | ×10 | 語言套件（中文原文即為鍵，新增語言 = 增加一個檔案） |
| `src-tauri/src/lib.rs` | ~1900 | 16 個原生命令：歷史持久化、分塊接收檔案、探索配對、機型辨識、上傳 Vault 媒體、路徑解析；iOS 捲動鎖（KVO 觀察 contentOffset，在呈現前歸零） |
| `gen/android/.../MainActivity.kt` | — | 主控台轉送（VibeDropConsole）+ 委派原有 WebChromeClient（檔案選擇器等） |
| `gen/android/.../KeepAliveService.kt` | — | 前景保活 |
| `gen/android/.../VideoPlayerActivity.kt` | — | ExoPlayer（Media3）原生全螢幕播放器 |
| `gen/android/.../BackgroundClipboardSyncManager.kt` | — | 原生背景剪貼簿寫入 |

### Home Vault 與工具 `scripts/`

| 指令碼 | 職責 |
|------|------|
| `home-vault-receiver.py`（約 1000 行） | 家用伺服器所有端點（見下表）；由 launchd 常駐執行 |
| `message-self-study.py` | 完整的 jieba 語料分析 → 自包含 HTML 報告（包含傳送趨勢長條圖） |
| `vault-media-uploader.py` / `sync-home-vault.py` | 補傳既有媒體 / 歷史寫入磁碟同步 |
| `i18n-check.py` | 多語言品質閘門：掃描所有 t()/data-i18n 鍵，對照語言套件回報缺漏與冗餘 |
| `deploy-android.sh` / `deploy-desktop.sh` / `deploy-ios.sh` | 三端一鍵建置與部署 |
| `generate-app-icons.py` / `generate-tray-frames.py` | 產生品牌素材 |

### Home Vault 端點速查

| 端點 | 作用 |
|------|------|
| `POST /api/history/append` · `GET /api/history/merged` | 增量入庫 / 合併時間軸 |
| `GET /api/events` | SSE：寫入磁碟後立即廣播 |
| `POST /api/media/upload` · `/lookup` · `GET /api/media/blob/<hash>` | 媒體倉庫：去重入庫／查詢／Range 串流取得 |
| `GET/POST /api/device-names` | 裝置名稱公告板（LWW） |
| `POST /api/client-log` | 回收探針黑盒子資料 |
| `GET /report/self-study` | 自我研究報告（SWR：快取立即顯示，過期後在背景重新計算，`?refresh=1` 強制重新整理） |

---

## 平台實務心得

### WebView 核心差異（重要）

| | Android | iOS | macOS 桌面 |
|---|---------|-----|-----------|
| 核心 | Chromium | **WKWebView** | **WKWebView（與 iOS 相同！）** |
| `content-visibility: auto` | ✅ 原生虛擬化 | ❌ 黑畫面 | ❌ 捲動時空白 |
| 長列表方案 | content-visibility | JS 虛擬捲動 | 分片掛載 |
| `Intl.Segmenter` 中文斷詞 | ❌ 切成單字 | ✅ 完整字典 | ✅ |

**結論：跨核心的中文斷詞只能使用伺服器端 jieba；content-visibility 只允許用在 Android。**

### iOS

- **固定版面配置**：依應用程式外殼架構停用外層 WKWebView 捲動（`isScrollEnabled=false` 只能阻擋手勢，
  WebKit 為顯示鍵盤會進行程式化捲動，因此還必須用 **KVO 觀察 contentOffset，並在呈現前歸零**；
  固定的「原點」是 `-adjustedContentInset` 所代表的系統靜止位置，而不是 (0,0)）；每次回到前景時都要補掛鎖定；
- 封裝鐵則：`cargo tauri ios build --export-method debugging`，不能直接使用 Xcode Run；
- 免費簽章有效期為 7 天（從建立日起算），需要搭配自動續簽流程。

### Android

- 自訂 WebChromeClient **必須委派給原本的 client**（onShowFileChooser 等），整體取代會讓檔案選擇器失效；
- console 的真實輸出請看 `adb logcat -d VibeDropConsole:I "*:S"`；
- 啟動時的 5 條「Cannot redefine property」錯誤，是 Tauri 注入指令碼重複執行產生的無害雜訊，不需要追查。

### Mac

- enigo 鍵盤模擬在獨立執行緒中執行；剪貼簿每 500 ms 輪詢 → broadcast channel → 各 WS 連線；
- 桌面端二進位檔的內部名稱仍是 `voicedrop`（使用 pgrep 時請注意）。

---

## 多語言（i18n）

採用 gettext 流派：**中文原文即為鍵**。`t('发送并回车')` 會查詢目前語言的字典，缺少翻譯時回退中文原文（翻譯只完成一半也永遠可以發布）。帶有變數時使用預留位置 `t('已改名为 {name}', {name})`，嚴禁串接字串。
目前有 11 種語言；新增語言 = 增加一個 `locales/<lang>.json` 檔案 + 在 `i18n.js` 對照表加入一行。

- 品質閘門：`python3 scripts/i18n-check.py --strict`（鍵覆蓋率／預留位置完整性）；
- 語意驗收：人工精讀每種語言的 30 個核心詞（機器無法保證語意，詳見 `docs/i18n-规范.md`）；
- 語言選擇器中的語言名稱使用**語言自稱**，並附上中英文注音，任何語言套件都不翻譯這些名稱。

---

## 建置與部署

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

**兩條規則**：

1. 修改 `mobile/src/` 的 app.js / index.html / style.css / i18n.js / locales/ 後，
   **必須同步複製到 `desktop/static/`**（桌面端 HTTP 服務提供的手機瀏覽器版本）；
2. **兩個 Tauri 建置不能並行執行**（共用本機 IPC 通道會發生衝突），必須循序執行。

---

## GitHub 發布

推送 `v*` 標籤會觸發 `release.yml`：自動建置簽署過的 APK + macOS dmg，並發布 GitHub Release；
`ci.yml` 會在每次 push 時執行建置檢查與 Python 單元測試。

```bash
git tag -a v0.x.y -m "说明" && git push origin v0.x.y
```

---

## 訊息自我研究（詞頻統計報告）

針對你自己的 Home Vault 歷史語料進行斷詞詞頻／口頭禪／高頻片語／每月主題演變（TF-IDF）／傳送趨勢（小時／日粒度長條圖，以手指滑動查看明細）分析，產生自包含 HTML 報告。全程在本機處理，資料不會外傳。

**直接在 App 內檢視**：歷史 →「訊息自我研究」卡片 → 開啟完整報告（Home Vault 端點 `/report/self-study`，SWR 快取可立即開啟；過期後在背景重新計算；`?refresh=1` 強制重新執行）。

也可以手動產生：

```bash
python3 -m venv .venv && .venv/bin/pip install jieba
.venv/bin/python scripts/message-self-study.py http://<你的vault地址>:8788
```

報告輸出到 `~/Downloads/`。多語言施工契約請參閱 `docs/i18n-规范.md`。
